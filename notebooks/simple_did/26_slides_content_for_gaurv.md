# #26 · Slide content for Gaurv’s Milestone #3 results

Use this content for the slide deck. These numbers come from:

- `21_naive_estimate.ipynb`
- `22_manual_did.ipynb`
- `results/estimates.csv`

## Slide: Naive U.S. before/after estimate

**Headline:** U.S. revenue per session increased after launch, but before/after alone is not causal.

**Table / bullets:**

- U.S. pre-launch average RPS: **2.6809**
- U.S. post-launch average RPS: **3.0230**
- Naive before/after estimate: **+0.3421 RPS**
- Percent change vs. pre-launch mean: **+12.76%**

**Speaker note:**

The naive estimate is the simplest baseline: U.S. post-launch average revenue per session minus U.S. pre-launch average revenue per session. It shows that U.S. RPS rose after launch, but it likely overstates the feature effect because it does not account for seasonality, marketing, promotions, visitor mix, or broader market movement.

## Slide: Manual 2×2 DiD / ATT using Canada

**Headline:** After subtracting Canada’s baseline movement, the preliminary ATT is **+0.2459 RPS**.

**2×2 table:**

| Market | Pre-launch avg RPS | Post-launch avg RPS | Change |
|---|---:|---:|---:|
| United States | 2.6809 | 3.0230 | +0.3421 |
| Canada | 2.4461 | 2.5423 | +0.0962 |
| **DiD / ATT** |  |  | **+0.2459** |

**Formula:**

```text
ATT = (US_post − US_pre) − (Canada_post − Canada_pre)
ATT = 0.3421 − 0.0962 = 0.2459
```

**Speaker note:**

The manual DiD estimate is better than the naive estimate because it subtracts the movement that also happened in the control market. Using Canada as the selected control, the U.S. improved by about +0.2459 revenue per session beyond Canada’s baseline movement.

## Slide: Assumptions and caveat

**Headline:** The DiD estimate is the better preliminary business estimate, but still not final causal proof.

**Bullets:**

- Canada must be a credible counterfactual for the U.S.
- Parallel trends must be plausible.
- Canada should not receive spillover effects from the U.S. launch.
- No other U.S.-only shock should explain the extra lift.
- Prior EDA showed launch-context risks: paid media, promo intensity, and new visitor share moved around launch.

**Speaker note:**

At this stage, I would use the manual DiD estimate instead of the naive estimate for the business decision, because it is more conservative and aligned with the counterfactual question. But I would still present it as preliminary until pre-trends are formally tested and later regression/fixed-effects models account for uncertainty and launch-context variables.
