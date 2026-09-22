# Milestone #3 — Simple DiD: control selection & manual 2x2

**Due Friday 2026-09-25.** Read this before starting. Humans and AI agents both.

## Already settled — do not redo

All of this is established in [`../eda_final.ipynb`](../eda_final.ipynb). Cite it, build
forward, do not re-derive it:

- **Canada is the control.** Leads on pre-launch `level_corr` (0.86), `delta_corr` (0.59)
  and gap stability. Control selection is closed.
- **All five rejected markets have written reasons** (§5). This already covers the deck's
  "which markets would fail as controls" bonus.
- **Media, promo and new-visitor share all jump at launch**, and paid media starts
  climbing the week *before* (§3). Any estimate here inherits that confound.
- **Why before/after misleads** is argued (§2–3). What's missing is the *number*.

## What's actually new this milestone

| Issue | Owner | Deliverable |
|---|---|---|
| [#17](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/17) | @atosic04 | Does an error metric add anything to control ranking? |
| [#18](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/18) | @yeekitc | Pre-launch regression + formal US–Canada pre-trend test |
| [#19](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/19) | @atosic04 | Control selection for the deck — *write-up, no notebook* |
| [#21](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/21) | @gaurvsingh095 | Naive before/after estimate — the number |
| [#22](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/22) | @gaurvsingh095 | Manual 2x2 DiD ATT + assumptions |
| [#24](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/24) | @anushatiwari | Naive vs DiD comparison + recommendation |
| [#25](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/25) [#26](https://github.com/Break-Through-Tech/Estee-Lauder-1B-measuring-customer-delight/issues/26) | @anushatiwari / all | Deck outline, then slides |

## Rules

1. **Analysis goes in [`../../src/simple_did.py`](../../src/simple_did.py), not in notebooks.** These
   notebooks get folded into `did_final.ipynb` the way `eda_tasks/` became `eda_final` —
   that only works if the final notebook can *call* the code instead of re-pasting it.
   Need a new helper? Add it to `did.py`.
2. **Every estimate goes through `save_estimate()`** into
   [`../../results/estimates.csv`](../../results/estimates.csv). Milestone #4 compares
   against these; an estimate only in a notebook output is lost.
3. **Control selection uses pre-launch data only** (deck slide 7).
4. **Figures for the deck** → `../../figures/simple_did/`, `dpi=200`, `bbox_inches="tight"`.
   Reuse `eda_viz` styling so both decks look like one project.
5. **Don't edit the shared setup cell** at the top of each notebook.

## Start

```bash
pip install -r ../../requirements.txt     # statsmodels needed for #18
jupyter lab                                # open your issue's notebook
```

Every notebook opens with its issue link, what the deck requires, what's already settled,
and a definition of done. Work top to bottom; `TODO` marks what's yours.

## Watch out

- `post_launch` is 1 for **every** market — it marks *when*, not *where*. Use
  `digital_feature_available`, or just call `launch_week()` / `pre_post_split()`.
- MSE and RMSE rank markets **identically** (`rmse = sqrt(mse)`). See #17.
- Lowest error ≠ best control. The UK is closest to the US in level but its weekly
  changes run opposite. Deck slide 7: *similar level ≠ good control*.
