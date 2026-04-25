import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Configurations
INPUT_CSV = "data/processed/final_tarining.csv"
OUT_DIR = "outputs/bigdata_analysis"
os.makedirs(OUT_DIR, exist_ok=True)

# Set visual style
sns.set_theme(style="whitegrid", palette="viridis")

def analyze_and_plot():
    print(f"📥 Loading 2.2M row dataset for Big Data Visualization...")
    # Loading in chunks to stay memory efficient
    chunks = pd.read_csv(INPUT_CSV, chunksize=500000)
    df_list = []
    
    # We only pull columns we need for viz to save RAM
    cols_to_use = ['date', 'rain_mm', 'elevation_m', 'distance_to_river_m', 'population_2026', 'flood', 'city', 'lat', 'lon']
    
    for chunk in chunks:
        df_list.append(chunk[cols_to_use])
    
    df = pd.concat(df_list)
    print("✅ Full Dataset Loaded")

    # Pre-processing
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # --- PLOT 1: Urban Flood Risk (Population vs Flood) ---
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df.sample(20000), x='population_2026', y='flood', logistic=True, scatter_kws={'alpha':0.1})
    plt.title("Plot 1: Urban Flood Risk (Population Density vs Flood Probability)")
    plt.savefig(f"{OUT_DIR}/01_urban_flood_risk.png")
    print("📈 Saved Plot 1")

    # --- PLOT 2: Monsoon peaks (Monthly Trends) ---
    plt.figure(figsize=(10, 6))
    monthly = df.groupby('month')[['rain_mm', 'flood']].mean().reset_index()
    sns.barplot(data=monthly, x='month', y='rain_mm', color='blue', alpha=0.6, label='Avg Rain (mm)')
    plt.twinx()
    sns.lineplot(data=monthly, x=monthly.index, y='flood', color='red', marker='o', label='Flood Prob')
    plt.title("Plot 2: Seasonal Trends (Monthly Rain vs Flood Probability)")
    plt.savefig(f"{OUT_DIR}/02_monsoon_peaks.png")
    print("📈 Saved Plot 2")

    # --- PLOT 3: Topography Hazard (Elevation) ---
    plt.figure(figsize=(10, 6))
    df['elev_bin'] = pd.cut(df['elevation_m'], bins=10)
    elev_impact = df.groupby('elev_bin', observed=True)['flood'].mean().reset_index()
    sns.lineplot(data=elev_impact, x=elev_impact.index, y='flood', marker='o')
    plt.title("Plot 3: Topographic Hazard (Elevation vs Flood Rate)")
    plt.savefig(f"{OUT_DIR}/03_topo_hazard.png")
    print("📈 Saved Plot 3")

    # --- PLOT 4: City Leaderboard (Top 10) ---
    plt.figure(figsize=(10, 8))
    top_cities = df.groupby('city')['flood'].sum().sort_values(ascending=False).head(10)
    top_cities.plot(kind='barh', color='darkred')
    plt.title("Plot 4: City Leaderboard (Top 10 Most Flood-Prone Cities)")
    plt.gca().invert_yaxis()
    plt.savefig(f"{OUT_DIR}/04_city_leaderboard.png")
    print("📈 Saved Plot 4")

    # --- PLOT 5: Multi-Year Trend ---
    plt.figure(figsize=(12, 6))
    yearly = df.groupby('year')['flood'].sum()
    yearly.plot(marker='x', color='black')
    plt.title("Plot 5: Multi-Year Trend (2000-2026 Total Floods)")
    plt.savefig(f"{OUT_DIR}/05_multi_year_trend.png")
    print("📈 Saved Plot 5")

    # --- PLOT 6: Socio-Spatial Bubble ---
    plt.figure(figsize=(10, 8))
    # Sample for performance in spatial bubble
    sample = df.sample(10000)
    plt.scatter(sample['lon'], sample['lat'], s=sample['population_2026']/10000, c=sample['flood'], cmap='coolwarm', alpha=0.5)
    plt.colorbar(label='Flood Probability')
    plt.title("Plot 6: Socio-Spatial Bubble (Location vs Pop-Size vs Risk)")
    plt.savefig(f"{OUT_DIR}/06_spatial_bubble.png")
    print("📈 Saved Plot 6")

    # --- PLOT 7: River Distance Decay ---
    plt.figure(figsize=(10, 6))
    df['dist_bin'] = pd.cut(df['distance_to_river_m'], bins=np.linspace(0, 10000, 20))
    dist_decay = df.groupby('dist_bin', observed=True)['flood'].mean()
    dist_decay.plot(kind='line', marker='.')
    plt.title("Plot 7: River Distance Decay (Proximity vs Risk)")
    plt.savefig(f"{OUT_DIR}/07_river_decay.png")
    print("📈 Saved Plot 7")

    # --- PLOT 8: Rainfall Distribution ---
    plt.figure(figsize=(10, 6))
    sns.histplot(df[df['rain_mm'] > 0]['rain_mm'], bins=50, kde=True, log_scale=True)
    plt.title("Plot 8: Rainfall Intensity Distribution (Log-Scale)")
    plt.savefig(f"{OUT_DIR}/08_rain_dist.png")
    print("📈 Saved Plot 8")

    # --- PLOT 9: Correlation Matrix ---
    plt.figure(figsize=(10, 8))
    corr = df[['rain_mm', 'elevation_m', 'distance_to_river_m', 'population_2026', 'flood']].corr()
    sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0)
    plt.title("Plot 9: Feature Correlation Matrix")
    plt.savefig(f"{OUT_DIR}/09_correlation.png")
    print("📈 Saved Plot 9")

    # --- PLOT 10: Population Impact Boxplot ---
    plt.figure(figsize=(10, 6))
    df['pop_scale'] = pd.qcut(df['population_2026'], q=4, labels=['Low', 'Medium', 'High', 'Metro'])
    sns.barplot(data=df, x='pop_scale', y='flood')
    plt.title("Plot 10: Population Impact Analysis (City Scale vs Risk)")
    plt.savefig(f"{OUT_DIR}/10_pop_impact.png")
    print("📈 Saved Plot 10")

    print(f"\n✨ All 10 Big Data Visualizations saved to: {OUT_DIR}")

if __name__ == "__main__":
    analyze_and_plot()
