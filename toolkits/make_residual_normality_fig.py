"""
make_residual_normality_fig.py
================================
Self-contained defence-appendix helper (NOT part of the pipeline).

Refits the exact primary H1 specification by reusing stage-8's
`run_h1_regression`, extracts its OLS residuals, and produces a
two-panel residual-normality diagnostic figure plus supporting statistics.

Primary H1 model = two-way cluster-robust OLS (clustered by respondent and
scenario), DV = NRS, key predictor = SC_total, block FE + experience/mandate/
discretion/event-type/regime controls. Matched by beta = -0.4874, p = 0.0015.
(cov_type only affects SEs, not residuals — residuals are the OLS fit's.)
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import FIGURES_DIR

# ── Import the stage-8 module (filename starts with a digit) ────────────────
_STAGE8 = Path(__file__).with_name("8_statistical_analysis.py")
_spec = importlib.util.spec_from_file_location("stage8", _STAGE8)
stage8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stage8)


def _diag(x: np.ndarray) -> tuple[float, float, float, float]:
    """Skewness, excess kurtosis (Fisher), Shapiro-Wilk W and p — no rounding."""
    x = np.asarray(x, dtype=float)
    skew = stats.skew(x, bias=False)
    exkurt = stats.kurtosis(x, fisher=True, bias=False)
    w, p = stats.shapiro(x)
    return float(skew), float(exkurt), float(w), float(p)


def main() -> None:
    # ── Refit exact primary spec via stage-8 ────────────────────────────────
    df = stage8.load_and_enrich()
    h1 = stage8.run_h1_regression(df)
    primary = h1["primary"]
    model = primary["model"]

    beta = primary["beta1"]
    assert abs(float(beta) - (-0.4874)) < 5e-4, (
        f"Spec mismatch: primary beta={beta} (expected ~ -0.4874)"
    )

    residuals = np.asarray(model.resid, dtype=float)
    nrs = np.asarray(model.model.endog, dtype=float)   # NRS entering the primary model

    assert np.all(np.isfinite(residuals)), "Non-finite residuals"
    assert np.all(np.isfinite(nrs)), "Non-finite NRS values"

    r_skew, r_exkurt, r_w, r_p = _diag(residuals)
    n_skew, n_exkurt, n_w, n_p = _diag(nrs)

    for name, val in [
        ("resid skew", r_skew), ("resid exkurt", r_exkurt), ("resid W", r_w), ("resid p", r_p),
        ("nrs skew", n_skew), ("nrs exkurt", n_exkurt), ("nrs W", n_w), ("nrs p", n_p),
    ]:
        assert np.isfinite(val), f"Non-finite diagnostic: {name}"

    # ── Figure: (a) residual histogram + normal overlay, (b) Q-Q plot ───────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Histogram with fitted normal density
    ax1.hist(residuals, bins=12, color="#abd9e9", edgecolor="#2c7bb6", density=True)
    x = np.linspace(residuals.min() - 0.5, residuals.max() + 0.5, 200)
    ax1.plot(x, stats.norm.pdf(x, residuals.mean(), residuals.std()),
             color="#d7191c", linewidth=2, label="Normal")
    ax1.set_xlabel("Residual")
    ax1.set_ylabel("Density")
    ax1.set_title("(a) Residual distribution with fitted normal")
    ax1.legend()
    stage8._apa_style(ax1)

    # (b) Normal Q-Q plot
    (osm, osr), (slope, intercept, _) = stats.probplot(residuals, dist="norm")
    ax2.scatter(osm, osr, s=18, color="#2c7bb6", alpha=0.7, zorder=3)
    ax2.plot(osm, slope * osm + intercept, color="#d7191c", linewidth=2, zorder=2)
    ax2.set_xlabel("Theoretical quantiles")
    ax2.set_ylabel("Ordered residuals")
    ax2.set_title("(b) Normal Q-Q plot of residuals")
    stage8._apa_style(ax2)

    fig.tight_layout()
    out_path = FIGURES_DIR / "fig_residual_normality.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    assert out_path.exists() and out_path.stat().st_size > 0, "Figure not written"

    # ── Report ──────────────────────────────────────────────────────────────
    print(f"Saved figure: {out_path}")
    print(f"Primary H1 spec confirmed: beta = {beta} (p = {primary['p']}), "
          f"n = {int(model.nobs)}, clustering = {primary['clustering']}")
    print("\nDiagnostics (skewness / excess kurtosis [Fisher] / Shapiro-Wilk W / p):")
    print(f"  Raw NRS response   : skew = {n_skew:.4f}, excess kurtosis = {n_exkurt:.4f}, "
          f"W = {n_w:.4f}, p = {n_p:.4f}")
    print(f"  Primary residuals  : skew = {r_skew:.4f}, excess kurtosis = {r_exkurt:.4f}, "
          f"W = {r_w:.4f}, p = {r_p:.4f}")


if __name__ == "__main__":
    main()
