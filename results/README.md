# results/

`estimates.csv` is the shared estimate registry; every estimate goes in through `sd.save_estimate()`.

## Superseded

These Milestone #4 files use Newey-West/HAC errors. The team's corrected numbers use HC3 and come from
[`../notebooks/regression_did/regression_did_hc3_and_anticipation.ipynb`](../notebooks/regression_did/regression_did_hc3_and_anticipation.ipynb).
Kept for the record; don't cite their CIs or p-values.

- `m4_simple_regression_did_results.csv`
- `m4_two_way_fe_did_results.csv`
- `m4_att_estimates_comparison.csv`
- `m4_summary.json`
- The `simple_regression_did` and `two_way_fe_did` rows in `estimates.csv` (marked in `notes`)

`m4_prepost_us_canada.csv` (pre/post means) doesn't depend on the error structure and is still current.

## Current (HC3)

Written by `regression_did_hc3_and_anticipation.ipynb`:

- `m4_simple_regression_did_results_hc3.csv`, `m4_two_way_fe_did_results_hc3.csv`, `m4_summary_hc3.json`
- `m5_three_specifications_hc3.csv`, `m5_anticipation_gap_check.csv`, `m5_optional_anticipation_exclusion.csv`,
  `m5_results_and_interpretation.md`
- `estimates.csv` rows `simple_regression_did_hc3` (#29), `two_way_fe_did_hc3` (#31, same fit as Model A),
  `fe_model_b_anticipation_hc3` and `fe_model_c_anticipation_marketing_hc3` (Milestone #5)
