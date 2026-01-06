import pandas as pd

# List of your category CSVs
files = {
    "skin-care": "output/skincare.csv",
    "beauty-styling": "output/beauty.csv",
    "health-beauty": "output/health.csv",
    "personal-care": "output/personal.csv"
}

dfs = []
for category, path in files.items():
    df = pd.read_csv(path)
    # Ensure category column exists
    if "category" not in df.columns:
        df["category"] = category
    dfs.append(df)

# Combine all categories into one master dataframe
master_df = pd.concat(dfs, ignore_index=True)

# Report counts per category
print("Counts per category:")
print(master_df["category"].value_counts())

# Save master file (with duplicates)
master_df.to_csv("output/jumia_beauty_master.csv", index=False)

# Deduplicate by product_url
unique_df = master_df.drop_duplicates(subset=["product_url"])
print(f"\nUnique products across all categories: {len(unique_df)}")

# Save deduplicated file
unique_df.to_csv("output/jumia_beauty_unique.csv", index=False)

print("\nFiles created:")
print("- output/jumia_beauty_master.csv (all products, with duplicates)")
print("- output/jumia_beauty_unique.csv (unique products only)")
