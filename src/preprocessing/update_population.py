import pandas as pd
import numpy as np
from scipy.spatial import KDTree
import os

# Paths
POP_DATA = "data/processed/final_gujarat_dataset.csv"
TRAIN_DATA = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
OUTPUT_FILE = "data/processed/training_dataset_gujarat_advanced_labeled.csv" # Overwriting

def update_population():
    print("📥 Loading population data...")
    pop_df = pd.read_csv(POP_DATA)
    
    # 1. Project Population from 2011 to 2026
    # Multiplier: (1 + 0.0135)^15 ≈ 1.23
    print("📈 Projecting population from 2011 to 2026 (Factor: 1.23)...")
    pop_df['population_2026'] = (pop_df['population'] * 1.23).round(0).astype(int)
    
    # 2. Build KDTree for spatial matching
    print("🎯 Building spatial index for cities...")
    city_coords = pop_df[['latitude', 'longitude']].values
    tree = KDTree(city_coords)
    
    # 3. Load Training Dataset in chunks to handle size (2.2M rows)
    chunk_size = 500000
    first_chunk = True
    
    print(f"🔄 Processing training dataset in chunks of {chunk_size}...")
    
    # Use a temporary file for safety then rename
    temp_output = OUTPUT_FILE + ".tmp"
    
    for chunk in pd.read_csv(TRAIN_DATA, chunksize=chunk_size):
        # We need to find the city for each row. 
        # Check which columns hold coordinates. 
        # Earlier investigation showed lat_x, lon_x might be fixed, 
        # while lat_y, lon_y or lat, lon might be the variables.
        # Let's use 'lat' and 'lon' if they exist, else 'lat_x', 'lon_x'.
        
        target_lat_col = 'lat' if 'lat' in chunk.columns else 'lat_x'
        target_lon_col = 'lon' if 'lon' in chunk.columns else 'lon_x'
        
        # Note: If these are grid indices (e.g. 6, 68), spatial lookup will fail.
        # Let's check the first row of coordinates to see if they are degrees.
        sample_lat = chunk[target_lat_col].iloc[0]
        if sample_lat < 100: # Typical degree range for India (8-37)
             # Try to find degrees if these are indices. 
             # Looking at previous logs, lat_x/lon_x were around 22/71.
             pass
        
        chunk_coords = chunk[[target_lat_col], [target_lon_col]].values if False else chunk[[target_lat_col, target_lon_col]].values

        # Find nearest city index
        _, indices = tree.query(chunk_coords)
        
        # Map population
        chunk['population_2026'] = pop_df['population_2026'].iloc[indices].values
        chunk['city'] = pop_df['city'].iloc[indices].values
        
        # Append to output
        chunk.to_csv(temp_output, mode='w' if first_chunk else 'a', header=first_chunk, index=False)
        first_chunk = False
        print(f"   ✅ Processed chunk...")

    # Replace original
    os.replace(temp_output, OUTPUT_FILE)
    print(f"\n✨ Success! Updated dataset saved to {OUTPUT_FILE}")
    print(f"📍 Added 'population_2026' and 'city' columns.")

if __name__ == "__main__":
    update_population()
