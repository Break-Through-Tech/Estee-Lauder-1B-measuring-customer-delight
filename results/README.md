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
