"""
visualization_toolkit.py
========================
Bloomberg-style dark intraday shock charts and Shock Score dashboard PNGs
for the survey assembly pipeline.

Functions
---------
plot_shock_chart   – 2-day intraday chart with shock annotation
plot_dashboard     – 6×3-inch Shock Score dashboard panel

Helpers (module-private)
------------------------
_infer_shock_direction
_colour_for_sentiment / _severity / _protocol / _horizon
"""

from __future__ import annotations

import warnings
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Dashboard colour palette ──────────────────────────────────────────────────

_C_RED    = "#c0392b"
_C_AMBER  = "#e67e22"
_C_GREEN  = "#27ae60"
_C_BLUE   = "#1f4e79"
_C_GREY   = "#7f8c8d"
_C_STRIPE = "#f2f3f4"
_C_CHART  = "#1f4e79"

# ── Colour helpers ────────────────────────────────────────────────────────────

def _colour_for_sentiment(label: str) -> str:
    if "Negative" in label:
        return _C_RED
    if "Positive" in label:
        return _C_GREEN
    return _C_GREY


def _colour_for_severity(label: str) -> str:
    return {"Low": _C_GREEN, "Medium": _C_AMBER, "High": _C_RED}.get(label, _C_GREY)


def _colour_for_protocol(label: str) -> str:
    return {
        "Standard Process": _C_GREEN,
        "Enhanced Review": _C_AMBER,
        "Cooling-Off and Second Review": _C_RED,
    }.get(label, _C_GREY)


def _colour_for_horizon(label: str) -> str:
    return {
        "Intraday":      _C_GREEN,
        "Several Days":  _C_AMBER,
        "Several Weeks": _C_RED,
    }.get(label, _C_GREY)


# ── Shock direction inference ─────────────────────────────────────────────────

def _infer_shock_direction(
    price_df: pd.DataFrame,
    event_date,
    event_time_et: str,
) -> str:
    """
    Derive shock direction from the immediate post-shock price move.
    Returns 'positive' if the bar after the shock bar closed higher, else 'negative'.
    """
    try:
        shock_ts  = pd.Timestamp(f"{event_date} {event_time_et}", tz="America/New_York")
        shock_utc = shock_ts.tz_convert("UTC")
        sorted_df = price_df.sort_values("time")
        at_or_after = sorted_df[sorted_df["time"] >= shock_utc]
        if len(at_or_after) < 2:
            return "positive"
        shock_close = float(at_or_after.iloc[0]["close"])
        next_close  = float(at_or_after.iloc[1]["close"])
        return "positive" if next_close >= shock_close else "negative"
    except Exception:
        return "positive"


# ── Intraday shock chart ──────────────────────────────────────────────────────

def plot_shock_chart(
    df: pd.DataFrame,
    shock_timestamp,
    ticker: str,
    shock_direction: str,
    save_path=None,
    company_name: str = "",
    gics_sector: str = "",
    price_reaction_pct: float | None = None,
    event_type: str = "",
):
    """
    Bloomberg-style dark intraday shock chart — 2 trading days at 30-min granularity.

    Parameters
    ----------
    df              : DataFrame[time (UTC tz-aware), close, volume] — full price series.
                      The function selects the prior trading day + event day automatically.
    shock_timestamp : pd.Timestamp (ET tz-aware) for the shock bar
    ticker          : stock ticker (used in chart title)
    shock_direction : 'positive' or 'negative' (controls colour encoding)
    save_path       : if provided, saved as PNG at 200 DPI with tight bounding box

    Returns
    -------
    matplotlib Figure object, or None if no data available.
    """
    # ── Colour encoding ───────────────────────────────────────────────────
    if price_reaction_pct is not None:
        clr = "#00cc66" if price_reaction_pct >= 0 else "#ff4444"
    else:
        clr = "#00cc66" if shock_direction == "positive" else "#ff4444"

    # ── Filter to 2 trading days ──────────────────────────────────────────
    tdf = df.copy()
    tdf["date_et"] = tdf["time"].dt.tz_convert("America/New_York").dt.date
    event_date = shock_timestamp.date()
    all_dates  = sorted(tdf["date_et"].unique())

    if event_date not in all_dates:
        warnings.warn(
            f"{ticker}: event date {event_date} not in price data — chart skipped"
        )
        return None

    idx = all_dates.index(event_date)
    if idx > 0:
        prior_date = all_dates[idx - 1]
        two_day = tdf[tdf["date_et"].isin([prior_date, event_date])]
    else:
        prior_date = None
        two_day = tdf[tdf["date_et"] == event_date]

    two_day = two_day.sort_values("time").reset_index(drop=True)
    if two_day.empty:
        warnings.warn(f"{ticker}: no bars for 2-day window — chart skipped")
        return None

    # ── Shock position (pre-truncation) ──────────────────────────────────
    shock_utc  = shock_timestamp.tz_convert("UTC")
    time_diffs = np.abs((two_day["time"] - shock_utc).dt.total_seconds().values)
    shock_pos  = int(np.argmin(time_diffs))

    # ── Truncate to shock bar + 1 confirmation bar ────────────────────────
    cutoff  = min(shock_pos + 2, len(two_day))
    two_day = two_day.iloc[:cutoff].reset_index(drop=True)

    closes    = two_day["close"].values.astype(float)
    volumes   = two_day["volume"].values.astype(float)
    positions = np.arange(len(two_day))
    times_et  = two_day["time"].dt.tz_convert("America/New_York")

    # ── Recompute shock position after truncation ─────────────────────────
    time_diffs  = np.abs((two_day["time"] - shock_utc).dt.total_seconds().values)
    shock_pos   = int(np.argmin(time_diffs))
    shock_display_pos = max(0, shock_pos - 1)   # dot one bar before shock

    # ── Day boundary (first bar of event day) ─────────────────────────────
    boundary_pos = (
        int((two_day["date_et"] == event_date).argmax())
        if prior_date is not None else None
    )

    # ── Figure ────────────────────────────────────────────────────────────
    with plt.style.context("dark_background"):
        fig, (ax_p, ax_v) = plt.subplots(
            2, 1, figsize=(12, 7.2),
            gridspec_kw={"height_ratios": [3, 1]},
            sharex=True,
        )

        fig.patch.set_facecolor("#000000")
        ax_p.set_facecolor("#1a1a2e")
        ax_v.set_facecolor("#1a1a2e")

        # ── Price line + fill ─────────────────────────────────────────────
        ax_p.plot(positions, closes, color=clr, linewidth=1.8, zorder=3,
                  solid_capstyle="round")
        ax_p.fill_between(positions, closes.min(), closes,
                          color=clr, alpha=0.15, zorder=1)

        # ── Grids ─────────────────────────────────────────────────────────
        for ax in (ax_p, ax_v):
            ax.grid(True, color="#333333", linewidth=0.5, linestyle="--", zorder=0)
            ax.set_axisbelow(True)

        # ── Volume bars (all grey; shock bar in directional colour) ───────
        vol_colors = ["#666666"] * len(volumes)
        vol_colors[shock_pos] = clr
        ax_v.bar(positions, volumes, color=vol_colors,
                 width=0.8, align="center", alpha=0.7, zorder=2)

        # ── Shock marker ──────────────────────────────────────────────────
        sv = closes[shock_display_pos]
        ax_p.scatter([shock_display_pos], [sv], s=90, color=clr, zorder=6,
                     edgecolors="white", linewidths=1.5)
        ann_x = -42 if shock_display_pos > len(positions) * 0.5 else 10
        ax_p.annotate(
            "News arrives\nnext bar",
            xy=(shock_display_pos, sv),
            xytext=(ann_x, -28), textcoords="offset points",
            fontsize=12, color="white", va="top", ha="left",
            arrowprops=dict(arrowstyle="->", color="white", lw=0.8),
        )

        # ── Day boundary line ─────────────────────────────────────────────
        if boundary_pos is not None and boundary_pos > 0:
            for ax in (ax_p, ax_v):
                ax.axvline(boundary_pos - 0.5, color="white", linewidth=1.0,
                           linestyle="--", alpha=0.6, zorder=4)
            xform = ax_p.get_xaxis_transform()
            if prior_date is not None:
                prior_mid = (boundary_pos - 1) / 2.0
                ax_p.text(prior_mid, 0.94, prior_date.strftime("%d %b"),
                          transform=xform, fontsize=13, color="#cccccc",
                          ha="center", va="top", style="italic")
            event_mid = (boundary_pos + len(two_day) - 1) / 2.0
            ax_p.text(event_mid, 0.94, event_date.strftime("%d %b  << Event"),
                      transform=xform, fontsize=13, color="#cccccc",
                      ha="center", va="top", style="italic")

        # ── x-axis ticks ──────────────────────────────────────────────────
        tick_step = 2 if prior_date is not None else 1
        tick_pos  = list(range(0, len(two_day), tick_step))
        tick_lbl  = [times_et.iloc[i].strftime("%H:%M") for i in tick_pos]
        ax_v.set_xticks(tick_pos)
        ax_v.set_xticklabels(tick_lbl, fontsize=13, color="#cccccc", rotation=0)
        ax_v.set_xlabel("Trading Time", fontsize=14, color="#cccccc")
        plt.setp(ax_p.get_xticklabels(), visible=False)

        # ── y-axis: price ─────────────────────────────────────────────────
        ax_p.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"{x:.2f}")
        )
        ax_p.tick_params(axis="y", labelsize=13, colors="#cccccc")
        ax_p.set_ylabel("Price (USD)", fontsize=14, color="#cccccc")

        # ── y-axis: volume ────────────────────────────────────────────────
        def _vol_fmt(x, _):
            if x >= 1_000_000:
                return f"{x / 1_000_000:.1f}M"
            if x >= 1_000:
                return f"{x / 1_000:.1f}K"
            return f"{x:.0f}"

        ax_v.yaxis.set_major_formatter(plt.FuncFormatter(_vol_fmt))
        ax_v.tick_params(axis="y", labelsize=13, colors="#cccccc")
        ax_v.set_ylabel("Volume", fontsize=14, color="#cccccc")

        # ── xlim ──────────────────────────────────────────────────────────
        ax_p.set_xlim(-0.5, len(two_day) - 0.5)

        # ── Two-line title ────────────────────────────────────────────────
        main_title = (f"{company_name} ({ticker})" if company_name else f"{ticker}")
        fig.suptitle(main_title, fontsize=22, fontweight="bold",
                     color="white", x=0.08, ha="left")

        subtitle = (f"{gics_sector} | Intraday Price (30-min bars)"
                    if gics_sector else "Intraday Price (30-min bars)")
        ax_p.set_title(subtitle, fontsize=15, color="#aaaaaa",
                       fontweight="normal", loc="left")

        fig.subplots_adjust(top=0.84)

        # ── Shock date label (upper-right) ────────────────────────────────
        ax_p.annotate(
            shock_timestamp.strftime("%d %b %Y"),
            xy=(1, 1), xycoords="axes fraction",
            xytext=(-8, -8), textcoords="offset points",
            fontsize=12, color="#cccccc", ha="right", va="top",
        )

        # ── Spine colours ─────────────────────────────────────────────────
        for ax in (ax_p, ax_v):
            for spine in ax.spines.values():
                spine.set_edgecolor("#333333")
            ax.tick_params(axis="x", colors="#cccccc")

        plt.tight_layout(pad=0.5)

        if save_path is not None:
            plt.savefig(save_path, dpi=200, bbox_inches="tight",
                        facecolor="#000000", edgecolor="none")

    return fig


# ── Shock Score dashboard ─────────────────────────────────────────────────────

def plot_dashboard(
    row: "pd.Series",
    scenario_id: str,
    out_dir: "pathlib.Path | str",
) -> bool:
    """
    Render a compact 6×3-inch Shock Score dashboard panel.
    Four signal rows: Sentiment Direction, Shock Severity, Persistence Horizon, Protocol.
    Saves to out_dir/dashboard_{scenario_id}.png

    Parameters
    ----------
    row         : pd.Series with columns: sentiment_direction, severity_level,
                  horizon_bucket, protocol_recommendation
    scenario_id : used for the output filename
    out_dir     : directory where the PNG is saved

    Returns
    -------
    True on success, False on error.
    """
    from pathlib import Path
    out_dir = Path(out_dir)

    sentiment_dir = str(row.get("sentiment_direction", "Neutral"))
    severity      = str(row.get("severity_level", "Low"))
    horizon       = str(row.get("horizon_bucket", "N/A"))
    protocol      = str(row.get("protocol_recommendation", "Standard Process"))

    signal_rows = [
        ("Sentiment Direction", sentiment_dir,
         _colour_for_sentiment(sentiment_dir), False),
        ("Shock Severity",      severity,
         _colour_for_severity(severity), True),
        ("Persistence Horizon", horizon,
         _colour_for_horizon(horizon), True),
        ("Protocol",            protocol,
         _colour_for_protocol(protocol), True),
    ]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Outer border
    border = mpatches.FancyBboxPatch(
        (0.01, 0.01), 0.98, 0.98,
        boxstyle="round,pad=0.01",
        linewidth=1.0, edgecolor="#cccccc", facecolor="white",
        transform=ax.transAxes, zorder=0,
    )
    ax.add_patch(border)

    # Title
    ax.text(0.5, 0.91, "Shock Score Dashboard",
            ha="center", va="center", fontsize=12, fontweight="bold",
            transform=ax.transAxes, zorder=2)

    # Divider
    ax.plot([0.05, 0.95], [0.82, 0.82], color="#cccccc",
            linewidth=0.8, transform=ax.transAxes, zorder=2)

    y_positions = [0.68, 0.51, 0.34, 0.17]

    for (label, value, colour, use_pill), y_pos in zip(signal_rows, y_positions):
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.03, y_pos - 0.08), 0.94, 0.15,
            boxstyle="round,pad=0.005",
            facecolor=_C_STRIPE, edgecolor="none",
            transform=ax.transAxes, zorder=1,
        ))
        ax.text(0.07, y_pos, label,
                ha="left", va="center", fontsize=8.5,
                color="#555555", transform=ax.transAxes, zorder=2)

        if use_pill:
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.54, y_pos - 0.065), 0.42, 0.13,
                boxstyle="round,pad=0.005",
                facecolor=colour, edgecolor="none", alpha=0.85,
                transform=ax.transAxes, zorder=2,
            ))
            ax.text(0.75, y_pos, value,
                    ha="center", va="center", fontsize=8,
                    color="white", fontweight="bold",
                    transform=ax.transAxes, zorder=3)
        else:
            ax.text(0.75, y_pos, value,
                    ha="center", va="center", fontsize=8,
                    color=colour, fontweight="bold",
                    transform=ax.transAxes, zorder=2)

    out_path = out_dir / f"dashboard_{scenario_id}.png"
    plt.tight_layout(pad=0.2)
    plt.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    return True
