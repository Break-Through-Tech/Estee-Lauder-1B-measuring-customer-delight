"""Simple-DiD helpers for the fragrance-advisor project (Milestone #3).

Analysis lives here rather than in notebooks/simple_did/ so did_final.ipynb can call
it later instead of pasting a second copy, the way eda_final.ipynb reuses eda_viz.

    import sys; sys.path.append("../../src")
    import simple_did as sd

Control selection must use PRE-LAUNCH DATA ONLY; the selection helpers filter to the
pre period internally, so don't hand them a post-launch frame.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eda_viz import (
    METRIC,
    METRIC_LABEL,
    PILOT,
    THEMES,
    find_repo_root,
    launch_week,
    load_panel,
)

__all__ = [
    "PILOT", "METRIC", "find_repo_root", "load_panel", "launch_week",
    "pre_post_split", "fit_error", "pre_trend_slopes", "rank_pre_period_fit",
    "LAUNCH_CONTEXT", "smf_ols", "fit_market_model", "pre_trend_test",
    "pre_trend_bias_bound", "plot_model_fit", "plot_slope_comparison",
    "naive_estimate", "manual_did", "ESTIMATE_COLUMNS", "estimates_path",
    "save_estimate", "load_estimates",
]

LAUNCH_CONTEXT = ["paid_media_index", "promo_intensity", "new_visitor_share"]


def pre_post_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split at the launch week; the launch week itself counts as post."""
    launch = launch_week(df)
    return df[df["week_start"] < launch].copy(), df[df["week_start"] >= launch].copy()


def smf_ols(formula: str, data: pd.DataFrame, maxlags: int = 8):
    """OLS with Newey-West errors -- weekly revenue is serially correlated."""
    import statsmodels.formula.api as smf

    return smf.ols(formula, data=data).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})


# --- control selection -----------------------------------------------------
def fit_error(a: pd.Series, b: pd.Series, kind: str = "mae") -> float:
    """Distance between two aligned series: rmse | mse | mae.

    Issue #17: rmse = sqrt(mse), so mse ranks markets *identically* to rmse and
    weights outlier weeks more, not less. mae is the outlier-tolerant one, hence
    the default.
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


def pre_trend_slopes(df: pd.DataFrame, metric: str = METRIC) -> pd.DataFrame:
    """Unconditional pre-launch slope per market, in metric units per week."""
    pre, _ = pre_post_split(df)
    rows = [
        {
            "market": market,
            "pre_slope": float(g[metric].cov(g["week_index"]) / g["week_index"].var()),
            "pre_mean": float(g[metric].mean()),
        }
        for market, g in pre.groupby("market")
    ]
    return pd.DataFrame(rows).sort_values("pre_slope", ascending=False).reset_index(drop=True)


def rank_pre_period_fit(
    df: pd.DataFrame,
    metric: str = METRIC,
    kind: str = "mae",
    pilot: str = PILOT,
) -> pd.DataFrame:
    """Rank candidate controls by pre-launch fit to the pilot (issues #17/#19).

    Columns disagree past first place on purpose -- delta_corr and slope_gap speak
    to parallel trends, while levels can correlate on shared seasonality alone. Say
    in the write-up which one you sorted by.
    """
    pre, _ = pre_post_split(df)
    wide = pre.pivot(index="week_start", columns="market", values=metric)
    if pilot not in wide.columns:
        raise ValueError(f"{pilot!r} not in the panel; markets are {list(wide.columns)}")
    deltas = wide.diff()
    slopes = pre_trend_slopes(df, metric).set_index("market")["pre_slope"]

    rows = [
        {
            "market": market,
            "level_corr": wide[pilot].corr(wide[market]),
            "delta_corr": deltas[pilot].corr(deltas[market]),
            f"pre_{kind}": fit_error(wide[pilot], wide[market], kind),
            "slope_gap": float(slopes[pilot] - slopes[market]),
            "gap_sd": float((wide[pilot] - wide[market]).std()),
            "pre_mean": float(wide[market].mean()),
        }
        for market in wide.columns
        if market != pilot
    ]
    return pd.DataFrame(rows).sort_values(f"pre_{kind}").reset_index(drop=True)


# --- parallel-trends evidence (issue #18) ----------------------------------
def fit_market_model(
    df: pd.DataFrame,
    market: str,
    metric: str = METRIC,
    seasonal: bool = True,
    maxlags: int = 8,
):
    """Pre-launch model for one market: linear trend, optionally plus month effects.

    A bare line explains ~4% of US pre-launch variation because eda_final section 2's
    seasonality dominates; month effects take it to ~65%.
    """
    pre, _ = pre_post_split(df)
    d = pre[pre["market"] == market].copy()
    d["month"] = d["week_start"].dt.month
    return smf_ols(f"{metric} ~ week_index" + (" + C(month)" if seasonal else ""), d, maxlags)


def pre_trend_test(
    df: pd.DataFrame,
    control: str,
    treated: str = PILOT,
    metric: str = METRIC,
    log: bool = False,
    covariates: list[str] | None = None,
    seasonal: bool = True,
    cov_type: str = "HAC",
    maxlags: int = 8,
) -> dict:
    """Were treated and control on different pre-launch trends? (issue #18)

    Fits `y ~ week_index * is_treated [+ C(month)] [+ covariates]` on pre-launch
    weeks. The interaction is the difference in weekly slopes; parallel implies zero.

    Caveats that matter:
    - p > 0.05 is a failure to detect, not proof of none. Read the CI, and see
      pre_trend_bias_bound for what it fails to exclude.
    - p-values here are indicative only. On pairs of markets that were *both*
      untreated this rejects 13% (trend only) / 33% (with month effects) of the
      time against a correct 5%, so the analytic errors are too small even with
      HAC. Trust the slope estimates over the stars.
    - Don't cluster on market: two clusters degenerates the estimator and returns
      a CI collapsed onto the point estimate with p = 0.000.
    - Don't use C(month)*is_treated on two markets -- it flags 10 of 15 untreated
      pairs.
    - Common seasonality cancels in the difference, so `seasonal` buys precision,
      not a different answer.
    - `log=True` tests parallel *percent* trends; `covariates` changes the question
      to "parallel given these", and anything the rollout moved is post-treatment.
    """
    pre, _ = pre_post_split(df)
    d = pre[pre["market"].isin([treated, control])].copy()
    if d["market"].nunique() < 2:
        raise ValueError(f"Need both {treated!r} and {control!r} in the pre period.")
    d["is_treated"] = (d["market"] == treated).astype(int)
    d["month"] = d["week_start"].dt.month

    rhs = "week_index * is_treated"
    if seasonal:
        rhs += " + C(month)"
    if covariates:
        rhs += " + " + " + ".join(covariates)
    lhs = f"np.log({metric})" if log else metric

    import statsmodels.formula.api as smf

    fit_kw = {"cov_type": cov_type}
    if cov_type == "HAC":
        fit_kw["cov_kwds"] = {"maxlags": maxlags}
    model = smf.ols(f"{lhs} ~ {rhs}", data=d).fit(**fit_kw)

    term = "week_index:is_treated"
    ci = model.conf_int().loc[term]
    # Slopes come from THIS model so they subtract to the difference beside them.
    base = float(model.params["week_index"])
    return {
        "treated": treated,
        "control": control,
        "metric": metric,
        "scale": "log" if log else "levels",
        "seasonal": seasonal,
        "cov_type": cov_type,
        "covariates": list(covariates) if covariates else [],
        "slope_diff": float(model.params[term]),
        "std_err": float(model.bse[term]),
        "ci_low": float(ci[0]),
        "ci_high": float(ci[1]),
        "p_value": float(model.pvalues[term]),
        "n_weeks": int(d["week_index"].nunique()),
        "treated_slope": base + float(model.params[term]),
        "control_slope": base,
        "model": model,
    }


def pre_trend_bias_bound(
    df: pd.DataFrame,
    control: str,
    treated: str = PILOT,
    metric: str = METRIC,
    seasonal: bool = True,
    cov_type: str = "HAC",
    maxlags: int = 8,
) -> dict:
    """How much of the DiD an undetected pre-trend could account for (issue #18).

    A slope gap d compounds into the 2x2 DiD through the distance between the mean
    post week and the mean pre week, since the DiD differences period means:

        spurious_did = d * (mean_post_week - mean_pre_week)

    Evaluated at the CI ends, that is the effect the pre-trend evidence fails to
    exclude. Compare it with the ATT before calling parallel trends satisfied.
    """
    pre, post = pre_post_split(df)
    lever = float(post["week_index"].mean() - pre["week_index"].mean())
    test = pre_trend_test(df, control=control, treated=treated, metric=metric,
                          seasonal=seasonal, cov_type=cov_type, maxlags=maxlags)
    att = manual_did(df, control=control, treated=treated, metric=metric)["estimate"]

    out = {"treated": treated, "control": control, "lever_weeks": lever,
           "att": att, "p_value": test["p_value"], "cov_type": cov_type}
    for label in ("point", "ci_low", "ci_high"):
        slope = test["slope_diff"] if label == "point" else test[label]
        out[f"{label}_slope"] = slope
        out[f"{label}_spurious_did"] = slope * lever
        out[f"{label}_share_of_att"] = slope * lever / att if att else float("nan")
    return out


# --- charts ----------------------------------------------------------------
def _style(ax, t):
    ax.set_facecolor(t["surface"])
    ax.grid(True, color=t["grid"], lw=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["grid"])
    ax.tick_params(colors=t["muted"], labelsize=8)


def plot_model_fit(
    df: pd.DataFrame,
    control: str,
    treated: str = PILOT,
    metric: str = METRIC,
    seasonal: bool = True,
    theme: str = "light",
):
    """Observed vs fitted, pre-launch, one panel per market.

    Slide 1 of #18: the panels share a seasonal shape at different levels.
    """
    t = THEMES[theme]
    pre, _ = pre_post_split(df)
    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)

    for ax, market, colour in zip(axes, (treated, control), (t["accent"], t["compare"])):
        d = pre[pre["market"] == market].sort_values("week_index")
        fit = fit_market_model(df, market, metric, seasonal)
        ax.plot(d["week_index"], d[metric], lw=1.0, alpha=0.45, color=colour,
                label="observed")
        ax.plot(d["week_index"], fit.fittedvalues, lw=2.0, color=colour,
                label=f"fitted  (slope {fit.params['week_index']:+.5f}/wk, "
                      f"adj R2={fit.rsquared_adj:.2f})")
        ax.set_title(market, color=t["ink"], fontsize=11, loc="left", pad=8)
        _style(ax, t)
        ax.legend(frameon=False, fontsize=8.5, labelcolor=t["ink_2"], loc="upper left")

    axes[-1].set_xlabel("week index (pre-launch only)", color=t["ink_2"], fontsize=9)
    fig.supylabel(METRIC_LABEL, color=t["ink_2"], fontsize=9)
    fig.patch.set_facecolor(t["surface"])
    fig.tight_layout()
    return fig


def plot_slope_comparison(
    df: pd.DataFrame,
    control: str,
    treated: str = PILOT,
    metric: str = METRIC,
    seasonal: bool = True,
    theme: str = "light",
):
    """Each market's pre-launch slope with CI, plus the difference.

    Slide 2 of #18. All three rows come from one pooled model so they reconcile:
    control is week_index, treated adds the interaction, the difference IS the
    interaction. Separate per-market fits would not subtract correctly.
    """
    t = THEMES[theme]
    pre, _ = pre_post_split(df)
    d = pre[pre["market"].isin([treated, control])].copy()
    d["is_treated"] = (d["market"] == treated).astype(int)
    d["month"] = d["week_start"].dt.month
    fit = smf_ols(f"{metric} ~ week_index * is_treated" + (" + C(month)" if seasonal else ""), d)

    names = list(fit.params.index)
    term = "week_index:is_treated"

    def contrast(week=0.0, interaction=0.0):
        vec = np.zeros(len(names))
        vec[names.index("week_index")] = week
        vec[names.index(term)] = interaction
        res = fit.t_test(vec)
        lo, hi = res.conf_int()[0]
        return float(res.effect[0]), float(lo), float(hi)

    rows = [
        (treated, *contrast(week=1, interaction=1), t["accent"]),
        (control, *contrast(week=1), t["compare"]),
        (f"difference\n({treated} - {control})", *contrast(interaction=1), t["ink"]),
    ]

    fig, ax = plt.subplots(figsize=(8, 3.4))
    for i, (label, est, lo, hi, colour) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], lw=2.4, color=colour, solid_capstyle="round")
        ax.plot([est], [y], "o", ms=7, color=colour, zorder=3)
    ax.axvline(0, color=t["muted"], lw=1.0, ls="--", zorder=0)

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=9, color=t["ink_2"])
    ax.set_xlabel(f"pre-launch slope ({metric} per week), 95% CI",
                  color=t["ink_2"], fontsize=9)
    ax.set_title("Pre-launch trends are not measurably different",
                 color=t["ink"], fontsize=12, loc="left", pad=12)
    _style(ax, t)
    ax.spines["left"].set_visible(False)
    ax.grid(False, axis="y")
    fig.patch.set_facecolor(t["surface"])
    fig.tight_layout()
    return fig


# --- estimates -------------------------------------------------------------
def naive_estimate(df: pd.DataFrame, market: str = PILOT, metric: str = METRIC) -> dict:
    """Before/after change in the pilot, ignoring every other market (issue #21).

    Expected to overstate: it credits the advisor with seasonality, paid media and
    promotions too. Its job is to be the baseline the DiD improves on.
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
    """Hand-computed 2x2 DiD ATT (issue #22).

        att = (treated_post - treated_pre) - (control_post - control_pre)

    Returns the four group means so the arithmetic is auditable. No standard error:
    that needs serial-correlation handling, which is Milestone #4's job.
    """
    pre, post = pre_post_split(df)

    def mean_of(frame, market):
        vals = frame.loc[frame["market"] == market, metric]
        if vals.empty:
            raise ValueError(f"No rows for {market!r} in one of the periods.")
        return float(vals.mean())

    t_pre, t_post = mean_of(pre, treated), mean_of(post, treated)
    c_pre, c_post = mean_of(pre, control), mean_of(post, control)
    return {
        "treated": treated,
        "control": control,
        "metric": metric,
        "treated_pre": t_pre,
        "treated_post": t_post,
        "control_pre": c_pre,
        "control_post": c_post,
        "treated_change": t_post - t_pre,
        "control_change": c_post - c_pre,
        "estimate": (t_post - t_pre) - (c_post - c_pre),
    }


# Issue #23: one schema for every estimate, so Milestone #4's comparison is a lookup.
ESTIMATE_COLUMNS = [
    "method", "treated", "control", "metric", "window", "estimate",
    "ci_low", "ci_high", "issue", "author", "recorded_at", "notes",
]
_TEXT_COLUMNS = ["method", "treated", "control", "metric", "window",
                 "author", "recorded_at", "notes"]


def estimates_path() -> Path:
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

    Appends rather than overwrites, so re-running a notebook keeps the history of
    what was tried. Prune superseded rows by hand.
    """
    path = Path(path) if path else estimates_path()
    row = {
        "method": method, "treated": treated, "control": control, "metric": metric,
        "window": window, "estimate": estimate,
        "ci_low": "" if ci_low is None else ci_low,
        "ci_high": "" if ci_high is None else ci_high,
        "issue": issue, "author": author,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes,
    }
    existing = load_estimates(path)
    new = pd.DataFrame([row])
    out = (new if existing.empty else pd.concat([existing, new], ignore_index=True))[ESTIMATE_COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)
    return out


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
