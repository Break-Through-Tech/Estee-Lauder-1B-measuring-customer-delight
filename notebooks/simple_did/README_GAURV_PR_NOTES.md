# Gaurv PR notes — Milestone #3 simple DiD

## Files changed/added

- `notebooks/simple_did/21_naive_estimate.ipynb` — completes issue #21.
- `notebooks/simple_did/22_manual_did.ipynb` — completes issue #22.
- `notebooks/simple_did/23_estimate_records_schema.ipynb` — completes issue #23.
- `notebooks/simple_did/26_slides_content_for_gaurv.md` — slide-ready content for issue #26.
- `results/estimates.csv` — shared estimate registry with #21 and #22 rows.

## Current results

- Naive U.S. before/after estimate: **+0.3421 RPS**
- Manual 2×2 DiD / ATT using Canada: **+0.2459 RPS**

## PR note

I completed my assigned Milestone #3 estimate work. Issue #21 computes the naive U.S. before/after estimate, which is +0.3421 RPS. Issue #22 computes the manual 2×2 DiD / ATT using Canada as the selected control, which is +0.2459 RPS. Issue #23 records the estimates in the shared `results/estimates.csv` schema so later regression/fixed-effects estimates can be appended and compared. Slide-ready notes are included for issue #26. The manual DiD estimate is more appropriate than naive before/after because it subtracts Canada’s baseline movement, but it remains preliminary until parallel trends and later regression/fixed-effects models are validated.
