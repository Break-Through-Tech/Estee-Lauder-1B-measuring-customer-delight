import pandas as pd
from pathlib import Path

# Resolve the repo root by walking up to the folder containing data/, so this
# script runs from any working directory.
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / "data" / "market_week_data.csv").exists())

# 1. Configure display settings for full visibility
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# 2. Load the panel from the repo
df = pd.read_csv(ROOT / "data" / "market_week_data.csv", parse_dates=["week_start"])

# 3. Dynamically identify the rollout launch date
launch = df.loc[df["digital_feature_available"] == 1, "week_start"].min()

# 4. Compute monthly average revenue per session (Seasonality Analysis)
monthly_avg = df.groupby([df["week_start"].dt.month, "market"])["revenue_per_session"].mean().unstack()

# 5. Compute pre-launch level correlation with the U.S. (Control Selection)
pre_launch_df = df[df["week_start"] < launch]
wide_pre = pre_launch_df.pivot(index="week_start", columns="market", values="revenue_per_session")
us_correlations = wide_pre.corr()["United States"].sort_values(ascending=False)

# 6. Compute pre vs. post launch performance jump
pre_post = df.groupby(["market", df["week_start"] >= launch])["revenue_per_session"].mean().unstack()
pre_post.columns = ["Pre-Launch Mean", "Post-Launch Mean"]
pre_post["Jump (Abs)"] = pre_post["Post-Launch Mean"] - pre_post["Pre-Launch Mean"]

# Print Outputs
print("--- Monthly Average Revenue Per Session (Seasonality) ---")
print(monthly_avg)

print("\n--- Pre-Launch Correlation Matrix with US ---")
print(us_correlations)

print("\n--- Pre vs Post Launch Performance Summary ---")
print(pre_post)
