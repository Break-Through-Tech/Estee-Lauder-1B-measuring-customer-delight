Completed #31.

**Two-way FE DiD using US + Canada only**

- Model: `revenue_per_session ~ digital_feature_available + C(market) + C(week_start)`
- Treatment-effect term: `digital_feature_available`
- ATT coefficient: **+0.2459138462 RPS**
- 95% CI: **[+0.1879309935, +0.3038966988]**
- p-value: **9.371e-17**
- n = **208** observations
- Error structure: Newey-West / HAC via `sd.smf_ols(maxlags=8)`

Added/supplied row for `results/estimates.csv` with `ci_low` and `ci_high` filled.

This completes:
- [x] Two-way FE DiD fitted on US + Canada only
- [x] Treatment-effect coefficient (ATT) and 95% CI reported
- [x] One row in `results/estimates.csv` via `sd.save_estimate()`, with `ci_low` / `ci_high` filled
