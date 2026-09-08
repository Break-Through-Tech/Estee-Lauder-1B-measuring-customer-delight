## 1. Markets and Date Ranges

**Markets Present:**

* Australia
* Canada
* France
* Germany
* Japan
* United Kingdom
* United States

**Date Range:** January 6, 2025 – December 28, 2026

---

## 2. Data Frequency and Completeness

* **Frequency:** Weekly observations, with each observation representing a 7-day interval beginning on Monday.
* **Observations per Market:** 104 weekly observations
* **Total Observations:** 728 rows (7 markets × 104 weeks)
* **Missing Values:** 0 across all columns
* **Duplicate Market-Weeks:** 0

The dataset is therefore complete, with one unique observation for each market-week combination.

---

## 3. Metric Definitions and Validation

The metric definitions were validated against their underlying components:

| Metric                | Definition           | Validation                                                       |
| --------------------- | -------------------- | ---------------------------------------------------------------- |
| `conversion_rate`     | `orders ÷ sessions`  | Reconciles exactly; stored unrounded                             |
| `average_order_value` | `revenue ÷ orders`   | Reconciles within ±0.005 due to rounding to 2 decimal places     |
| `revenue_per_session` | `revenue ÷ sessions` | Reconciles within rounding tolerance; stored to 4 decimal places |

`revenue_per_session` is the primary metric used in the analysis and visualizations.

---

## 4. Feature Availability

The feature was introduced as a pilot in the **United States**.

* **Pilot Market:** United States
* **Deployment Date:** April 6, 2026
* **Availability Period:** April 6, 2026 – December 28, 2026
* **Weeks Available:** 39 weeks
* **Other Markets:** The feature was not deployed in Australia, Canada, France, Germany, Japan, or the United Kingdom during the observed period.

This creates a natural comparison between the United States (pilot market) and the six markets where the feature was not deployed.
