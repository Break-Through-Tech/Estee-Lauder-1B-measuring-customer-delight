# Evaluating a Digital Feature Rollout with Difference-in-Differences

**Company / Org:** Estee Lauder  
**Challenge Advisor:** Luis Saldana  
**Program:** Break Through Tech AI Studio - Fall 2026

---

## 🏢 About Estee Lauder

Estee Lauder is a leading global beauty company, specializing in skincare, makeup, fragrance, and hair care products. We are committed to innovation and quality, transforming the beauty industry with our diverse portfolio of brands.

---

## 🎯 The Challenge

### Project Summary
In this project, you will use a fully simulated, market-level e-commerce dataset and Difference-in-Differences causal inference techniques to estimate the business impact of a simulated digital fragrance-advisor feature. The scenario is inspired by (but does not use) a real advisor-feature rollout: a digital fragrance advisor is made available in a pilot market, and you must estimate whether this advisor-feature rollout improved fragrance performance. You are not evaluating a real product, a real AI model, or real customer data — you are analyzing simulated market-week panel data to reach a credible causal conclusion. Your analysis will help proxy Jo Malone London / ELC stakeholders decide whether to expand the rollout, proceed cautiously, or run a cleaner follow-up test.

### Success Criteria

Success should be measured by whether students can produce a credible causal analysis and business recommendation, not just a working model.   

A successful outcome by December would include:   
- A clear explanation of the business question, treatment, comparison group, and primary metric.
- Correct use of Difference-in-Differences to estimate the impact of the simulated advisor-feature rollout.
- Evidence that students assessed control-group credibility using pre-period trends and simple diagnostics.
- A thoughtful discussion of limitations, including anticipation effects, overlapping marketing activity, and possible spillover.
- A concise stakeholder-facing recommendation on whether to expand the rollout, proceed cautiously, or run a cleaner follow-up test.

Evaluation metrics may include the estimated lift in fragrance revenue per visitor, the confidence interval around the DiD estimate, and sensitivity of the estimate across reasonable specifications. The strongest final deliverable would show that students understand both the capabilities and limitations of DiD and can translate their findings into practical guidance for proxy Jo Malone London / ELC stakeholders.

### Project Milestones

Use these milestones to guide your work. Your team will create a **GitHub Projects board** to track tasks within each milestone.

| Month | Milestone | Key Activities |
| :--- | :--- | :--- |
| September | [TBD Title] | Students should understand the business question, simulated market-week dataset, and basic causal framing. They will complete initial EDA, define the pilot market and comparison markets, identify the primary metric, and compute simple before/after and pilot-vs-control comparisons to motivate why naive analyses may be misleading. |
| October | [TBD Title] | Students should learn and apply Difference-in-Differences. They will estimate the rollout impact using both manual DiD calculations and regression-based DiD, then evaluate whether Canada and any additional candidate markets are credible controls using pre-period plots and simple trend diagnostics. By the end of October, they should have a preferred control group and an initial causal estimate. |
| November | [TBD Title] | Students should refine and stress-test their estimate. They will examine anticipation effects, run a simple sensitivity analysis for overlapping paid media or promotional activity, and translate their preferred estimate into a business recommendation. By the end of November, they should complete a concise stakeholder-facing final presentation explaining whether the simulated advisor-feature rollout appears to have improved fragrance performance, how credible the estimate is, and what next steps the business should consider. |

### Stretch Goals

Natural stretch goals include: 

- Event-study analysis: estimate week-by-week effects around launch to better visualize pre-launch anticipation and post-launch impact over time.
- Additional control-market sensitivity: compare results using Canada alone versus a broader set of credible comparison markets.
- Secondary outcome analysis: repeat the analysis for fragrance conversion rate, average order value, or advisor engagement metrics to understand where the impact may be coming from.
- Simple business value calculation: translate estimated lift into incremental revenue or a rough rollout value under stated assumptions.
- Spillover discussion or exploratory sensitivity: examine whether nearby or highly connected comparison markets may have been indirectly exposed to the rollout, while keeping this as a qualitative limitation rather than a required estimate.
- Future experiment design proposal: recommend how ELC could design a cleaner rollout or holdout test to produce stronger causal evidence.

> **Note for the team:** Please create a GitHub Projects board in this repository to break these milestones into weekly tasks. Go to the **Projects** tab → **New project** → Choose **Board** → Add columns for each month.

---

## 📊 Dataset

**Name and Source:** Simulated market-week e-commerce panel generated for this Break Through Tech AI Studio project. No real customer, transaction, or proprietary ELC data is used.  
**Format:** CSV  
**Size:** under 1gb  
**Location:** [data/market_week_data.csv](data/market_week_data.csv) in this repository

### Key Details
- The primary dataset is a tabular market-week panel covering pilot (treated) and control markets over time. It includes market and timing information (market ID, week index, week start date, pilot-market indicator, launch timing), advisor-feature availability, and business performance metrics such as sessions, fragrance orders, fragrance revenue, conversion rate, average order value (AOV), and revenue per session. It also includes context variables such as paid media activity, promotion depth, and new-visitor share. Provided in CSV format.
- Limitations / preprocessing: the data is fully simulated and intentionally includes causal-inference complications that you will need to reason about, including non-random control-group selection, anticipation effects around the launch, and overlapping marketing activity (promotions and paid media) that can confound a naive before/after comparison.
- Data dictionary: [data/DATA_DICTIONARY.md](data/DATA_DICTIONARY.md), covering the panel structure and all 16 columns.

---

## 🛠️ Suggested Approach

**ML Problem Type:** Regression, Causal Inference

**Recommended Libraries:**
- pandas
- numpy
- statsmodels
- matplotlib
- seaborn
- optional: linearmodels

**Evaluation Metrics:**
- Estimated lift in fragrance revenue per visitor
- Confidence intervals around DiD estimates

---

## 📚 Resources to Get Started

The following resources will help your team understand the problem space and potential technical approaches for this project:

**Background Reading:**
- [How to Use Quasi-experiments and Counterfactuals to Build Great Products](https://shopify.engineering/using-quasi-experiments-counterfactuals)
- [Regression and Other Stories — Chapter 19: Causal Inference Using Regression on the Treatment Variable](https://avehtari.github.io/ROS-Examples/)  
  Focus on Sections 19.1, 19.3, and 19.5–19.7: potential outcomes, adjustment for pre-treatment predictors, interpreting regression coefficients as treatment effects, post-treatment controls, and causal pathways.

**Technical Tutorials:**
- [Difference-in-Differences — Causal Inference for the Brave and True](https://matheusfacure.github.io/python-causality-handbook/13-Difference-in-Differences.html)
- [Fitting Models Using Formulas — statsmodels](https://www.statsmodels.org/stable/example_formulas.html)
- [Reading a statsmodels OLS Regression Output Table — Stanford Applied Statistics](https://stanford-mse-125.github.io/book/lec12-regression-inference.html#reading-a-regression-output-table)

**Code Examples:**
- [Difference-in-Differences Python Notebook](https://github.com/matheusfacure/python-causality-handbook/blob/master/causal-inference-for-the-brave-and-true/13-Difference-in-Differences.ipynb)
- [Panel Data and Fixed Effects Python Notebook](https://github.com/matheusfacure/python-causality-handbook/blob/master/causal-inference-for-the-brave-and-true/14-Panel-Data-and-Fixed-Effects.ipynb)
- [notebooks/scratch/simple_did_demo.ipynb](notebooks/scratch/simple_did_demo.ipynb) — a short setup aid I put together for this project, covering pandas, plotting, and statsmodels formula syntax on a small unrelated toy example. It is not a demonstration of the project analysis; you are expected to design, write, validate, and interpret your own.

*Feel free to explore beyond these, and share anything interesting you find with me!*

---

## 🤝 How We'll Work Together

**Check-ins:** During our biweekly 45-min AI Studio Lab Section meeting block (2nd and 4th week of every month)  
**Communication:** Discord (Break Through Tech workspace)  
**Response time:** Within 48 hours on weekdays  

**Recommended Tools:**
- **Coding:** Google Colab, VS Code
- **Collaboration:** GitHub, Notion
- **Virtual Meetings:** Zoom, Google Meet

---

## 🚀 Getting Started

1. **Review this overview document** and note any questions for our first meeting
2. **Begin exploring the dataset** in the [data folder](data) by reviewing the data dictionary, loading the market-week panel, and examining the key metrics by market and week
3. **Read the GitHub Projects documentation** [here](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)

I'm excited to work with you!

---

## ❓ Questions?

Please bring any questions to our first meeting during the week of August 24th (Break Through Tech's Bridge to Studio - Session C).

---
