import pandas as pd
import os

INPUT = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
OUTPUT = "data/processed/final_training.csv"

def clean_dataset():
    print(f"📥 Loading dataset for cleaning: {INPUT}")
    
    # Read in chunks for safety, though 2.2M rows usually fits in RAM
    # But for cleaning and dropping columns, memory can spike.
    df = pd.read_csv(INPUT)
    initial_rows = len(df)
    
    # 1. Identify and Drop Redundant Coordinate Columns
    # The dataset has lat_x/lon_x, lat_y/lon_y, and lat/lon.
    # From previous investigation:
    # - lat_x/lon_x: City center / centroid
    # - lat_y/lon_y and lat/lon: Grid indices or duplicates from merge
    
    print("🧹 Cleaning redundant columns...")
    # List of columns to keep (The "Essentials")
    essential_cols = [
        "date",
        "city",
        "lat_x",  # Actual latitude degrees
        "lon_x",  # Actual longitude degrees
        "rain_mm",
        "elevation_m",
        "distance_to_river_m",
        "rain3_mm",
        "rain7_mm",
        "population_2026",
        "flood"
    ]
    
    # Check which of these are present and drop others
    current_cols = df.columns.tolist()
    to_keep = [c for c in essential_cols if c in current_cols]
    
    df = df[to_keep]
    
    # Rename lat_x/lon_x to simple lat/lon for the final model
    df = df.rename(columns={"lat_x": "lat", "lon_x": "lon"})
    
    # 2. Drop Literal Duplicate Rows (entire row match)
    print("🧹 Dropping exact duplicate rows...")
    df = df.drop_duplicates()
    
    # 3. Drop Data/Location duplicates (if any)
    # Keeping only the first occurrence of city+date
    print("🧹 Ensuring physical uniqueness per city per date...")
    df = df.drop_duplicates(subset=["date", "lat", "lon"])
    
    final_rows = len(df)
    removed = initial_rows - final_rows
    
    print(f"✅ Cleaned {removed} rows.")
    print(f"📊 Final Dataset: {final_rows} rows across {len(df.columns)} columns.")
    
    # 4. Save
    print(f"💾 Saving to {OUTPUT}...")
    df.to_csv(OUTPUT, index=False)
    print("✨ Process Complete")

if __name__ == "__main__":
    clean_dataset()
