"""Difference-in-Differences helpers for the fragrance-advisor project.

Milestone #3 work lives in notebooks/simple_did/, one notebook per GitHub issue. The
analysis itself lives here rather than in those notebooks, for the same reason
eda_viz.py exists: when the per-task notebooks are folded into did_final.ipynb,
the final notebook should *call* this code, not paste a second copy of it.

    pre_post_split(df)                  weeks before / from the launch week
    fit_error(a, b, kind)               rmse | mse | mae between two series
    pre_trend_slopes(df)                per-market pre-launch slope (issue #19)
    rank_pre_period_fit(df)             issues #17/#19 -- candidate controls
    naive_estimate(df)                  issue #21 -- before/after in the US
    manual_did(df, control=...)         issue #22 -- 2x2 ATT, four group means
    save_estimate(...) / load_estimates()   issue #23 -- the shared registry

Data loading is deliberately re-exported from eda_viz instead of redefined, so
there is exactly one implementation of "where is the repo root" in the project.

Two lines to use any of it from a notebook:

    import sys; sys.path.append("../../src")
    import simple_did as sd

Milestone #3 asks that the control be justified on PRE-LAUNCH DATA ONLY. Every
selection helper here (pre_trend_slopes, rank_pre_period_fit) therefore filters
to the pre period internally -- do not hand them a post-launch frame.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from eda_viz import PILOT, METRIC, find_repo_root, launch_week, load_panel

__all__ = [
    "PILOT",
    "METRIC",
    "find_repo_root",
    "load_panel",
    "launch_week",
    "pre_post_split",
    "fit_error",
    "pre_trend_slopes",
    "rank_pre_period_fit",
    "naive_estimate",
    "manual_did",
    "ESTIMATE_COLUMNS",
    "estimates_path",
    "save_estimate",
    "load_estimates",
]


# --- period handling -------------------------------------------------------
def pre_post_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the panel at the launch week into (pre, post).

    The launch week itself counts as post: it is the first week the advisor was
    actually reachable, so it belongs to the treated period even if only part of
    that week was exposed. Anticipation in the weeks *before* launch is a
    separate question -- Milestone #5, not this one.

    Uses digital_feature_available via launch_week(), not post_launch.
    post_launch is 1 for every market and marks *when*, not *where*.
    """
    launch = launch_week(df)
    return df[df["week_start"] < launch].copy(), df[df["week_start"] >= launch].copy()


# --- error metrics ---------------------------------------------------------
def fit_error(a: pd.Series, b: pd.Series, kind: str = "mae") -> float:
    """Distance between two aligned series.

    Issue #17 asks for MSE "to tolerate outliers". Worth knowing before you pick:

        rmse  sqrt(mean(d**2))  squares errors, then undoes the square -- same
                                units as the metric
        mse   mean(d**2)        squares errors -- a strictly increasing function
                                of rmse, so it *ranks markets identically to
                                rmse*, and it weights outlier weeks more, not
                                less
        mae   mean(|d|)         absolute errors -- this is the one that tolerates
                                outlier weeks, because a bad week contributes in
                                proportion to its size rather than its square

    So if the goal is genuinely robustness to a few odd weeks, mae is the choice;
    mse and rmse hand you the same ranking as each other. Default is mae for that
    reason -- pass kind explicitly to compare, and report which you used.
    """
    d = (a - b).dropna()
    if d.empty:
        raise ValueError("No overlapping weeks between the two series.")
    kind = kind.lower()
    if kind == "rmse":
        return float((d**2).mean() ** 0.5)
    if kind == "mse":
        return float((d**2).mean())
    if kind == "mae":
        return float(d.abs().mean())
    raise ValueError(f"Unknown error kind {kind!r}; use rmse, mse or mae.")


# --- control selection (pre-launch evidence only) --------------------------
def pre_trend_slopes(df: pd.DataFrame, metric: str = METRIC) -> pd.DataFrame:
    """Pre-launch trend slope per market, in metric units per week.

    Milestone #3 slide 7: a market at a similar *level* to the US is not thereby
    a good control -- what matters is whether it was moving the same way before
    launch. Comparing slopes is the check that distinguishes the two. Read this
    next to rank_pre_period_fit(): a small error with a very different slope is
    the classic bad control.
    """
    pre, _ = pre_post_split(df)
    rows = []
    for market, g in pre.groupby("market"):
        rows.append(
            {
                "market": market,
                "pre_slope": float(g[metric].cov(g["week_index"]) / g["week_index"].var()),
                "pre_mean": float(g[metric].mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values("pre_slope", ascending=False)
    return out.reset_index(drop=True)


def rank_pre_period_fit(
    df: pd.DataFrame,
    metric: str = METRIC,
    kind: str = "mae",
    pilot: str = PILOT,
) -> pd.DataFrame:
    """Rank candidate control markets by pre-launch fit to the pilot.

    Issues #17 and #19. One row per non-pilot market, carrying every check the
    Milestone #3 deck asks for so the choice can be defended on more than one
    number:

        level_corr   Pearson r on levels (slide 7: "co-movement, e.g. Pearson r")
        delta_corr   Pearson r on week-over-week changes -- the one that speaks
                     to parallel trends, since levels can correlate through
                     shared seasonality alone
        pre_<kind>   chosen error metric against the pilot
        slope_gap    pilot slope minus market slope; near zero is parallel
        gap_sd       volatility of the pilot-minus-market gap; smaller is steadier

    Sorted by the error metric, but the columns disagree past first place on
    purpose -- say in the write-up which column you sorted by and why.
    """
    pre, _ = pre_post_split(df)
    wide = pre.pivot(index="week_start", columns="market", values=metric)
    if pilot not in wide.columns:
        raise ValueError(f"{pilot!r} not in the panel; markets are {list(wide.columns)}")
    deltas = wide.diff()
    slopes = pre_trend_slopes(df, metric).set_index("market")["pre_slope"]

    rows = []
    for market in wide.columns:
        if market == pilot:
            continue
        rows.append(
            {
                "market": market,
                "level_corr": wide[pilot].corr(wide[market]),
                "delta_corr": deltas[pilot].corr(deltas[market]),
                f"pre_{kind}": fit_error(wide[pilot], wide[market], kind),
                "slope_gap": float(slopes[pilot] - slopes[market]),
                "gap_sd": float((wide[pilot] - wide[market]).std()),
                "pre_mean": float(wide[market].mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(f"pre_{kind}")
    return out.reset_index(drop=True)


# --- estimates -------------------------------------------------------------
def naive_estimate(df: pd.DataFrame, market: str = PILOT, metric: str = METRIC) -> dict:
    """Before/after change in the pilot market, ignoring every other market.

    Issue #21, deck slide 4 top line. This is the estimate we expect to be
    *wrong*: it credits the advisor with everything that changed between the two
    periods, including seasonality, paid media and promotions. Its job is to be
    the baseline the DiD improves on, so report it plainly rather than burying it.
    """
    pre, post = pre_post_split(df)
    pre_mean = pre.loc[pre["market"] == market, metric].mean()
    post_mean = post.loc[post["market"] == market, metric].mean()
    return {
        "market": market,
        "metric": metric,
        "pre_mean": float(pre_mean),
        "post_mean": float(post_mean),
        "estimate": float(post_mean - pre_mean),
    }


def manual_did(
    df: pd.DataFrame,
    control: str,
    treated: str = PILOT,
    metric: str = METRIC,
) -> dict:
    """Hand-computed 2x2 difference-in-differences ATT.

    Issue #22, deck slide 5. Returns the four group means alongside the ATT so
    the arithmetic is auditable -- a reader should be able to check the
    subtraction without rerunning anything:

        att = (treated_post - treated_pre) - (control_post - control_pre)

    The ATT is the causal quantity the deck asks for (slide 3): the effect on the
    market that actually got the feature, which is the one the rollout decision
    turns on.

    No standard error here on purpose. Getting one right means accounting for
    serial correlation within a market across weeks -- that is the regression /
    fixed-effects DiD's job in Milestone #4, not this function's.
    """
    pre, post = pre_post_split(df)

    def mean_of(frame, market):
        vals = frame.loc[frame["market"] == market, metric]
        if vals.empty:
            raise ValueError(f"No rows for {market!r} in one of the periods.")
        return float(vals.mean())

    t_pre, t_post = mean_of(pre, treated), mean_of(post, treated)
    c_pre, c_post = mean_of(pre, control), mean_of(post, control)

    treated_change = t_post - t_pre
    control_change = c_post - c_pre
    return {
        "treated": treated,
        "control": control,
        "metric": metric,
        "treated_pre": t_pre,
        "treated_post": t_post,
        "control_pre": c_pre,
        "control_post": c_post,
        "treated_change": treated_change,
        "control_change": control_change,
        "estimate": treated_change - control_change,
    }


# --- the shared results registry -------------------------------------------
# Issue #23. Every estimate any of us produces lands in one CSV with one schema,
# so Milestone #4's "compare to earlier estimations" is a groupby rather than an
# archaeology dig.
ESTIMATE_COLUMNS = [
    "method",         # naive | manual_did | regression_did | fe_did | ...
    "treated",        # treated market
    "control",        # control market, or "" where the method has none
    "metric",         # outcome column from the panel
    "window",         # which weeks were used, e.g. "all" or "-8..+8"
    "estimate",       # the point estimate
    "ci_low",         # leave blank where the method gives no interval
    "ci_high",
    "issue",          # GitHub issue number the estimate came from
    "author",         # GitHub handle
    "recorded_at",    # UTC timestamp, filled in automatically
    "notes",          # caveats a reader needs in order to interpret the number
]


def estimates_path() -> Path:
    """Location of the shared registry, resolved from the repo root."""
    return find_repo_root() / "results" / "estimates.csv"


def save_estimate(
    method: str,
    estimate: float,
    issue: int | str,
    author: str,
    treated: str = PILOT,
    control: str = "",
    metric: str = METRIC,
    window: str = "all",
    ci_low: float | None = None,
    ci_high: float | None = None,
    notes: str = "",
    path: Path | None = None,
) -> pd.DataFrame:
    """Append one estimate to results/estimates.csv and return the full table.

    Appending rather than overwriting is deliberate: re-running a notebook after
    a tweak should add a row, so the history of what we tried survives. Prune
    superseded rows by hand when a specification is genuinely abandoned.
    """
    path = Path(path) if path else estimates_path()
    row = {
        "method": method,
        "treated": treated,
        "control": control,
        "metric": metric,
        "window": window,
        "estimate": estimate,
        "ci_low": "" if ci_low is None else ci_low,
        "ci_high": "" if ci_high is None else ci_high,
        "issue": issue,
        "author": author,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    existing = load_estimates(path)
    new = pd.DataFrame([row])
    # Concatenating onto an empty frame warns about dtype inference in pandas 2,
    # and there is nothing to preserve in that case anyway.
    out = new if existing.empty else pd.concat([existing, new], ignore_index=True)
    out = out[ESTIMATE_COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return out


# Columns that are prose, not numbers: a blank one means "not applicable", which
# should survive a CSV round-trip as "" rather than turning into NaN.
_TEXT_COLUMNS = [
    "method", "treated", "control", "metric", "window", "author", "recorded_at", "notes",
]


def load_estimates(path: Path | None = None) -> pd.DataFrame:
    """Read the shared estimates table; empty with the right columns if absent."""
    path = Path(path) if path else estimates_path()
    if not path.exists():
        return pd.DataFrame(columns=ESTIMATE_COLUMNS)
    out = pd.read_csv(path)
    for col in _TEXT_COLUMNS:
        if col in out.columns:
            out[col] = out[col].fillna("")
    return out
