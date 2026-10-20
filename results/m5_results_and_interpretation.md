# Milestone 5 — Results (HC3)

US treated; Canada control; outcome revenue per session.
US pre-launch mean RPS: $2.6809.
Pre-launch gap in weeks -2/-1 minus earlier weeks: $+0.1105 per session (descriptive, not a causal test).

| Model | ATT ($/session) | Relative lift vs US pre | 95% HC3 CI | p-value |
|---|---:|---:|---|---:|
| A_baseline_FE | +0.2459 | +9.17% | [+0.1747, +0.3171] | 1.29e-11 |
| B_FE_anticipation | +0.2493 | +9.30% | [+0.1780, +0.3206] | 7.32e-12 |
| C_FE_anticipation_marketing | +0.2093 | +7.81% | [+0.1440, +0.2747] | 3.4e-10 |

Larger absolute treatment-estimate shift: marketing controls (B→C).
Caution: HC3 corrects heteroskedasticity, not serial correlation; marketing controls may be endogenous.
The feature-only causal reading remains conditional on parallel trends, no other US-only launch shocks, and valid controls.