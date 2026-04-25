import pandas as pd
import os

INPUT = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
OUTPUT = "data/processed/final_tarining.csv"

def clean_final():
    print(f"📥 Loading dataset: {INPUT}")
    df = pd.read_csv(INPUT)
    initial_rows = len(df)
    
    # 1. Drop redundant/duplicate coordinate columns
    # We keep 'lat' and 'lon' (the ones from the grid) and 'city', 'date'
    print("🧹 Pruning redundant columns (lat_x, lon_x, lat_y, lon_y)...")
    cols_to_drop = ["lat_x", "lon_x", "lat_y", "lon_y", "state"] # State is constant
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    # 2. Key Uniqueness
    # The user noted "duplicate lat and lon". 
    # We ensure each date has only one record per lat/lon pair.
    print("🧹 Dropping duplicates based on (date, lat, lon)...")
    df = df.drop_duplicates(subset=["date", "lat", "lon"])
    
    final_rows = len(df)
    removed = initial_rows - final_rows
    
    print(f"✅ Cleaned {removed} duplicate spatial-temporal entries.")
    print(f"📊 Final Dataset: {final_rows} rows.")
    
    # 3. Save as per user's specific naming
    print(f"💾 Saving to {OUTPUT}...")
    df.to_csv(OUTPUT, index=False)
    print("✨ Cleaned dataset ready.")

if __name__ == "__main__":
    clean_final()
