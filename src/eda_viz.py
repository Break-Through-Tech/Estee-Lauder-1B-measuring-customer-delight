"""Revenue-per-session visualizations for the fragrance-advisor DiD project.

Two deliverables live here, plus the helpers they need:

    plot_rps_all_markets(df)        finding E, headline: every market over time,
                                    US emphasised, rollout marked
    plot_rps_pairwise(df, market)   US vs one candidate control, raw or indexed

The module is standalone on purpose. It imports nothing from the rest of the
project, so it can be dropped into any notebook with two lines:

    import sys; sys.path.append("../src")
    from viz import load_panel, plot_rps_all_markets, plot_rps_pairwise
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

__all__ = [
    "find_repo_root",
    "load_panel",
    "launch_week",
    "rank_similarity_to_us",
    "plot_rps_all_markets",
    "plot_rps_pairwise",
]

PILOT = "United States"
METRIC = "revenue_per_session"
METRIC_LABEL = "Revenue per session (simulated currency units)"

# --- theme tokens ----------------------------------------------------------
# Light and dark are each selected against their own surface, not flipped.
THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "ink_2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "accent": "#2a78d6",   # categorical slot 1
        "compare": "#eb6834",  # categorical slot 2
        "wash": "#0b0b0b",
        "wash_alpha": 0.035,
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "ink_2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "accent": "#3987e5",
        "compare": "#d95926",
        "wash": "#ffffff",
        "wash_alpha": 0.05,
    },
}

_SANS = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]


# --- data ------------------------------------------------------------------
def find_repo_root(start=None) -> Path:
    """Walk up from `start` (default: cwd) to the directory holding data/.

    Notebooks live at varying depths and get moved around; resolving the root
    by looking for the data file means none of them carry a relative path that
    breaks the next time the tree is reorganised.
    """
    start = Path(start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "data" / "market_week_data.csv").exists():
            return candidate
    raise FileNotFoundError(
        f"No data/market_week_data.csv found in {start} or any parent."
    )


def load_panel(path=None) -> pd.DataFrame:
    """Read the market-week panel with week_start as datetimes.

    With no argument, locates the data file relative to the repo root, so the
    call works from any notebook depth.
    """
    if path is None:
        path = find_repo_root() / "data" / "market_week_data.csv"
    return pd.read_csv(path, parse_dates=["week_start"])


def launch_week(df: pd.DataFrame) -> pd.Timestamp:
    """First week the advisor was actually live, read from the data.

    Uses digital_feature_available rather than post_launch: post_launch is 1 for
    all seven markets and marks *when*, not *where*. Deriving it beats hardcoding
    2026-04-06 -- if the panel is ever regenerated the charts follow it.
    """
    live = df.loc[df["digital_feature_available"] == 1, "week_start"]
    if live.empty:
        raise ValueError("No rows with digital_feature_available == 1.")
    return live.min()


def rank_similarity_to_us(df: pd.DataFrame, metric: str = METRIC) -> pd.DataFrame:
    """Rank non-pilot markets by pre-launch similarity to the US.

    Two views, because they answer different questions:
      level_corr  -- do the series track each other week to week?
      delta_corr  -- do the week-over-week *changes* move together? This is the
                     one that speaks to parallel trends; levels can correlate
                     just from shared seasonality.
      gap_sd      -- volatility of the US-minus-market gap. Smaller is steadier.

    A starting point for choosing which markets to plot, not a finished control
    -- selection deserves more than a correlation sort. Note that the three
    measures disagree past first place, so the ranking depends on which column
    you sort by. The plot functions take any market name, so pass in whatever
    the team settles on.
    """
    launch = launch_week(df)
    pre = df[df["week_start"] < launch]
    wide = pre.pivot(index="week_start", columns="market", values=metric)
    deltas = wide.diff()

    rows = []
    for market in wide.columns:
        if market == PILOT:
            continue
        rows.append(
            {
                "market": market,
                "level_corr": wide[PILOT].corr(wide[market]),
                "delta_corr": deltas[PILOT].corr(deltas[market]),
                "gap_sd": (wide[PILOT] - wide[market]).std(),
                "pre_mean": wide[market].mean(),
            }
        )
    out = pd.DataFrame(rows).sort_values("level_corr", ascending=False)
    return out.reset_index(drop=True)


# --- chart chrome ----------------------------------------------------------
def _style_axes(ax, t, ylabel=METRIC_LABEL, xlabel=None):
    ax.set_facecolor(t["surface"])
    ax.figure.set_facecolor(t["surface"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(t["axis"])
        ax.spines[side].set_linewidth(0.8)
    # Hairline, solid, y-only. Dashed grid reads as a threshold it isn't.
    ax.grid(axis="y", color=t["grid"], linewidth=0.8, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(colors=t["muted"], labelsize=9, length=0)
    if ylabel:
        ax.set_ylabel(ylabel, color=t["ink_2"], fontsize=10, labelpad=10)
    ax.set_xlabel(xlabel or "", color=t["ink_2"], fontsize=10)


def _mark_launch(ax, launch, t, end, label="Advisor live in US", show_label=True):
    """Solid rule at the rollout plus a wash over the treated period.

    The wash carries duration (39 weeks) that a bare line does not.
    """
    ax.axvspan(launch, end, color=t["wash"], alpha=t["wash_alpha"], lw=0, zorder=0)
    ax.axvline(launch, color=t["ink_2"], linewidth=1.0, zorder=1)
    if show_label:
        ax.annotate(
            f"{label}\n{launch:%b %-d, %Y}",
            xy=(launch, 1.0),
            xycoords=("data", "axes fraction"),
            xytext=(10, -2),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=9,
            color=t["ink_2"],
            linespacing=1.4,
        )


def _time_axis(ax, t):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))


def _end_label(ax, x, y, text, t, dot_color, text_color, weight="normal", size=9,
               y_label=None):
    """A colored dot carries identity; the text stays in an ink token.

    The dot wears a 2px surface ring so it stays legible where lines cross. If
    y_label differs from y the label has been nudged to avoid a collision, so a
    hairline leader connects it back to its own line-end.
    """
    y_label = y if y_label is None else y_label
    ax.plot(
        [x], [y], marker="o", markersize=6, color=dot_color,
        markeredgecolor=t["surface"], markeredgewidth=2, zorder=5, clip_on=False,
    )
    if abs(y_label - y) > 1e-9:
        ax.annotate(
            "", xy=(x, y), xycoords="data", xytext=(x, y_label), textcoords="data",
            arrowprops=dict(arrowstyle="-", color=t["axis"], linewidth=0.8,
                            shrinkA=0, shrinkB=0),
            annotation_clip=False, zorder=4,
        )
    ax.annotate(
        text, xy=(x, y_label), xytext=(14, 0), textcoords="offset points",
        va="center", ha="left", fontsize=size, color=text_color,
        fontweight=weight, zorder=5, annotation_clip=False,
    )


def _declutter(values, min_gap):
    """Nudge end-labels apart while keeping their original order."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    placed = list(values)
    for n, i in enumerate(order):
        if n == 0:
            continue
        prev = placed[order[n - 1]]
        if placed[i] - prev < min_gap:
            placed[i] = prev + min_gap
    return placed


# --- deliverable 1: all markets, US emphasised ------------------------------
def plot_rps_all_markets(
    df: pd.DataFrame,
    metric: str = METRIC,
    theme: str = "light",
    figsize=(12.5, 6.0),
    # Titles name what is plotted, nothing more. At EDA we cannot yet say the
    # advisor caused anything -- spring is the US's seasonal high and the US was
    # already trending up year-over-year before launch. Pass title=/subtitle= to
    # make a pointed claim once the analysis supports one.
    title: str = "Weekly revenue per session by market",
    subtitle: str = "",
    label_controls: bool = True,
    ax=None,
    savepath: str | None = None,
):
    """Every market over time, with the pilot emphasised and the rollout marked.

    Emphasis form: the US wears the accent hue at full weight, the six control
    markets recede into one gray. They are still individually readable via
    direct end-labels, so identity never depends on telling six grays apart.
    """
    t = THEMES[theme]
    launch = launch_week(df)
    end = df["week_start"].max()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    controls = sorted(m for m in df["market"].unique() if m != PILOT)

    _mark_launch(ax, launch, t, end)

    for market in controls:
        g = df[df["market"] == market].sort_values("week_start")
        ax.plot(g["week_start"], g[metric], color=t["muted"], linewidth=0.9,
                alpha=0.5, solid_capstyle="round", zorder=2)

    us = df[df["market"] == PILOT].sort_values("week_start")
    ax.plot(us["week_start"], us[metric], color=t["accent"], linewidth=2.2,
            solid_joinstyle="round", solid_capstyle="round", zorder=4)

    # Direct end-labels: identity without seven hues.
    ends = [(PILOT, us[metric].iloc[-1])]
    if label_controls:
        ends += [(m, df[(df["market"] == m)].sort_values("week_start")[metric].iloc[-1])
                 for m in controls]
    ends.sort(key=lambda kv: kv[1])
    span = df[metric].max() - df[metric].min()
    placed = _declutter([v for _, v in ends], min_gap=span * 0.045)
    for (market, y), y_lab in zip(ends, placed):
        is_pilot = market == PILOT
        _end_label(
            ax, end, y,
            f"{market} (pilot)" if is_pilot else market,
            t,
            dot_color=t["accent"] if is_pilot else t["muted"],
            text_color=t["ink"] if is_pilot else t["muted"],
            weight="bold" if is_pilot else "normal",
            y_label=y_lab,
        )

    _style_axes(ax, t)
    _time_axis(ax, t)
    ax.set_xlim(df["week_start"].min(), end)
    ax.margins(x=0.02)

    # Legend is present for >= 2 series; direct labels supplement it.
    handles = [
        plt.Line2D([], [], color=t["accent"], lw=2.2, label="United States (pilot)"),
        plt.Line2D([], [], color=t["muted"], lw=0.9, alpha=0.5,
                   label="Control markets (feature never available)"),
    ]
    leg = ax.legend(handles=handles, loc="upper left", frameon=False,
                    fontsize=9, labelcolor=t["ink_2"], handlelength=1.8)
    for text in leg.get_texts():
        text.set_color(t["ink_2"])

    ax.set_title(title, color=t["ink"], fontsize=14, fontweight="bold",
                 loc="left", pad=28 if subtitle else 12)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1.0), xycoords="axes fraction",
                    xytext=(0, 12), textcoords="offset points", ha="left",
                    va="bottom", fontsize=10, color=t["ink_2"])

    fig.subplots_adjust(right=0.80)
    if savepath:
        fig.savefig(savepath, dpi=200, bbox_inches="tight", facecolor=t["surface"])
    return fig, ax


# --- deliverable 2: US vs one candidate control -----------------------------
def plot_rps_pairwise(
    df: pd.DataFrame,
    comparison: str,
    metric: str = METRIC,
    theme: str = "light",
    index_to_pre: bool = False,
    figsize=(11.0, 5.2),
    title: str | None = None,
    subtitle: str = "",
    show_legend: bool = True,
    show_launch_label: bool = True,
    show_end_labels: bool = True,
    ax=None,
    savepath: str | None = None,
):
    """US against one candidate control market.

    index_to_pre=False plots raw levels -- honest about the gap between markets.
    index_to_pre=True rebases each market to its own pre-launch mean = 100, which
    is how you read parallel trends when the two sit at different levels. It is
    the alternative to a dual axis, which this project never uses.
    """
    t = THEMES[theme]
    launch = launch_week(df)
    end = df["week_start"].max()

    pair = df[df["market"].isin([PILOT, comparison])].copy()
    if pair["market"].nunique() < 2:
        raise ValueError(f"{comparison!r} not found in the panel.")

    value = metric
    ylabel = METRIC_LABEL
    if index_to_pre:
        pre_mean = (pair[pair["week_start"] < launch]
                    .groupby("market")[metric].mean())
        pair["indexed"] = 100 * pair[metric] / pair["market"].map(pre_mean)
        value = "indexed"
        ylabel = "Revenue per session (pre-launch mean = 100)"

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    _mark_launch(ax, launch, t, end, show_label=show_launch_label)
    if index_to_pre:
        ax.axhline(100, color=t["axis"], linewidth=0.8, zorder=1)

    series = [(PILOT, t["accent"], 2.2), (comparison, t["compare"], 2.0)]
    ends = []
    for market, color, lw in series:
        g = pair[pair["market"] == market].sort_values("week_start")
        ax.plot(g["week_start"], g[value], color=color, linewidth=lw,
                solid_capstyle="round", zorder=4)
        ends.append((market, color, g[value].iloc[-1]))

    span = pair[value].max() - pair[value].min()
    placed = _declutter([v for _, _, v in ends], min_gap=span * 0.07)
    for (market, color, y), y_lab in zip(ends, placed if show_end_labels else placed):
        if not show_end_labels:
            ax.plot([end], [y], marker="o", markersize=6, color=color,
                    markeredgecolor=t["surface"], markeredgewidth=2,
                    zorder=5, clip_on=False)
            continue
        is_pilot = market == PILOT
        _end_label(
            ax, end, y, f"{market} (pilot)" if is_pilot else market, t,
            dot_color=color,
            text_color=t["ink"] if is_pilot else t["ink_2"],
            weight="bold" if is_pilot else "normal",
            y_label=y_lab,
        )

    _style_axes(ax, t, ylabel=ylabel)
    _time_axis(ax, t)
    ax.set_xlim(pair["week_start"].min(), end)

    if show_legend:
        handles = [plt.Line2D([], [], color=c, lw=2.0, label=m)
                   for m, c, _ in series]
        leg = ax.legend(handles=handles, loc="upper left", frameon=False,
                        fontsize=9, handlelength=1.8)
        for text in leg.get_texts():
            text.set_color(t["ink_2"])

    if title is None:
        title = f"United States vs {comparison}: revenue per session"
    if title:
        ax.set_title(title, color=t["ink"], fontsize=13, fontweight="bold",
                     loc="left", pad=26 if subtitle else 10)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1.0), xycoords="axes fraction",
                    xytext=(0, 10), textcoords="offset points", ha="left",
                    va="bottom", fontsize=9.5, color=t["ink_2"])

    fig.subplots_adjust(right=0.82)
    if savepath:
        fig.savefig(savepath, dpi=200, bbox_inches="tight", facecolor=t["surface"])
    return fig, ax
