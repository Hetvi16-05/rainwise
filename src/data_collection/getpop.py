import pandas as pd
import os

# 📂 File paths
CITIES_FILE = "data/config/gujarat_cities.csv"
POP_FILE = "data/processed/gujarat_cities_population.csv"
OUTPUT_FILE = "data/processed/final_gujarat_dataset.csv"

os.makedirs("data/processed", exist_ok=True)

# 📥 Load datasets
cities_df = pd.read_csv(CITIES_FILE)
pop_df = pd.read_csv(POP_FILE)

# 🧹 Normalize column names
cities_df.columns = cities_df.columns.str.lower().str.strip()
pop_df.columns = pop_df.columns.str.lower().str.strip()

print("📊 Cities columns:", cities_df.columns.tolist())
print("📊 Population columns:", pop_df.columns.tolist())

# 🔍 Detect columns automatically
city_col = [c for c in cities_df.columns if "city" in c or "name" in c][0]
lat_col = [c for c in cities_df.columns if "lat" in c][0]
lon_col = [c for c in cities_df.columns if "lon" in c][0]

# 🧠 Create merge key
cities_df["city_clean"] = cities_df[city_col].astype(str).str.lower().str.strip()
pop_df["city_clean"] = pop_df["city"].astype(str).str.lower().str.strip()

# 🔗 Merge datasets
merged_df = cities_df.merge(pop_df, on="city_clean", how="left")

# ✅ Use correct columns after merge (IMPORTANT FIX)
final_df = merged_df[["city_x", lat_col, lon_col, "population_2011"]]

# ✏️ Rename columns
final_df.columns = ["city", "latitude", "longitude", "population"]

# ❗ Handle missing values
missing = final_df["population"].isna().sum()
print(f"⚠️ Missing population for {missing} cities")

final_df["population"] = final_df["population"].fillna(0)

# 💾 Save final dataset
final_df.to_csv(OUTPUT_FILE, index=False)

# 📊 Preview
print("\n✅ FINAL DATASET READY!")
print(f"📁 Saved at: {OUTPUT_FILE}")
print(final_df.head())