# Milestone #4 slide content — Regression DiD + two-way FE DiD

## Simple regression DiD (#29)

- Model: `revenue_per_session ~ pilot_market + post_launch + pilot_market:post_launch`
- Treatment-effect coefficient: `pilot_market:post_launch`
- ATT: **+0.2459 RPS**
- 95% CI: **[-0.0203, +0.5122]**
- p-value: **0.0703**
- Error structure: Newey-West / HAC via `sd.smf_ols(maxlags=8)`

**Slide language:** The simple regression DiD gives the same point estimate as the manual 2×2 DiD, about **+0.2459 revenue per session**, because both are estimating the same U.S.-minus-Canada before/after contrast. The regression version adds uncertainty. With Newey-West errors, the 95% confidence interval is **[-0.0203, +0.5122]**, so the estimate is positive but the interval crosses zero at the 5% level.

## Two-way FE DiD (#31)

- Model: `revenue_per_session ~ digital_feature_available + C(market) + C(week_start)`
- Treatment-effect coefficient: `digital_feature_available`
- ATT: **+0.2459 RPS**
- 95% CI: **[+0.1879, +0.3039]**
- p-value: **9.371e-17**
- Error structure: Newey-West / HAC via `sd.smf_ols(maxlags=8)`

**Slide language:** The two-way FE model also estimates an ATT of about **+0.2459 revenue per session**. This model absorbs stable market differences between the U.S. and Canada and common week-level shocks. Its 95% confidence interval is **[+0.1879, +0.3039]**, which stays above zero.

## Four-way comparison

| Method | Estimate | 95% CI | p-value | Use |
|---|---:|---:|---:|---|
| Naive U.S. before/after | +0.3421 | — | — | Descriptive only |
| Manual 2×2 DiD | +0.2459 | — | — | First adjusted ATT estimate |
| Simple regression DiD | +0.2459 | [-0.0203, +0.5122] | 0.0703 | Adds uncertainty |
| Two-way FE DiD | +0.2459 | [+0.1879, +0.3039] | <0.001 | Absorbs market/week FE |

## Main takeaway

The treatment-effect point estimate is stable at about **+0.246 RPS** across the manual DiD, simple regression DiD, and two-way FE DiD. The difference is not the point estimate; it is how uncertainty is handled. The simple regression DiD with Newey-West errors is wider and crosses zero, while the two-way FE model gives a tighter interval after absorbing market and week effects.
