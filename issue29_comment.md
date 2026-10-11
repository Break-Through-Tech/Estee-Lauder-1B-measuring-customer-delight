Completed #29.

**Simple regression DiD using US + Canada only**

- Model: `revenue_per_session ~ pilot_market + post_launch + pilot_market:post_launch`
- Treatment-effect term: `pilot_market:post_launch`
- ATT coefficient: **+0.2459138462 RPS**
- 95% CI: **[-0.0203389836, +0.5121666759]**
- p-value: **0.070258**
- n = **208** observations
- Error structure: Newey-West / HAC via `sd.smf_ols(maxlags=8)`

Added/supplied row for `results/estimates.csv` with `ci_low` and `ci_high` filled.

This completes:
- [x] Simple regression DiD fitted on US + Canada only
- [x] Treatment-effect coefficient (ATT) and 95% CI reported
- [x] One row in `results/estimates.csv` via `sd.save_estimate()`, with `ci_low` / `ci_high` filled
