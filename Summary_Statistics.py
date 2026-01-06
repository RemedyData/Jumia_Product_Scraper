# Calculating summary statistics per category for Jumia scraped data

import pandas as pd
import os

# Define file paths and corresponding categories
file_paths = {
    "skin-care": "output/skincare.csv",
    "beauty-styling": "output/beauty.csv",
    "health-beauty": "output/health.csv",
    "personal-care": "output/personal.csv"
}

# Load and label each dataset
dfs = []
for category, path in file_paths.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "category" not in df.columns:
            df["category"] = category
        dfs.append(df)

# Merge all dataframes
merged_df = pd.concat(dfs, ignore_index=True)

# --- Clean 'final_price' column ---
def parse_price(x):
    try:
        x = str(x).replace("₦", "").replace(",", "").strip()
        if "-" in x:  # handle ranges like "1200 - 2000"
            parts = [float(p.strip()) for p in x.split("-") if p.strip().isdigit()]
            if parts:
                return sum(parts) / len(parts)  # average of the range
            return None
        return float(x)
    except:
        return None

merged_df["final_price_clean"] = merged_df["final_price"].apply(parse_price)

# --- Clean 'rating' column ---
merged_df["rating"] = pd.to_numeric(merged_df["rating"], errors="coerce")

# --- Clean 'num_reviews' column ---
merged_df["num_reviews_clean"] = (
    merged_df["num_reviews"]
    .astype(str)
    .str.extract(r"(\d+)")[0]
    .astype(float)
)

# --- Compute summary statistics per category ---
summary = merged_df.groupby("category").agg(
    product_count=("product_url", "count"),
    average_price=("final_price_clean", "mean"),
    average_rating=("rating", "mean"),
    average_reviews=("num_reviews_clean", "mean")
).round(2)

print("Summary Statistics per Category:\n")
print(summary)

# --- Save summary stats to CSV ---
summary.to_csv("output/summary_stats.csv")

print("\nSummary statistics saved to: output/summary_stats.csv")
