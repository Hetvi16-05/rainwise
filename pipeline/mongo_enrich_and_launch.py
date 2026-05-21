"""
RAINWISE — MongoDB Enrichment Script
Syncs live HDFS realtime data into MongoDB city_summaries collection
so the dashboard shows real flood risk scores, live rain stats, and trends.
"""

import pymongo
import pandas as pd
import numpy as np
import os, datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REALTIME_CSV  = os.path.join(BASE_DIR, "data", "raw",       "realtime", "realtime_dataset.csv")
PROCESSED_CSV = os.path.join(BASE_DIR, "data", "processed", "bi_dashboard_ready_PERFECT.csv")

# ── Connect ──────────────────────────────────────────────────────────────────
client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
db     = client["rainwise_db"]
col    = db["city_summaries"]

print(f"🍃 Connected to MongoDB  |  rainwise_db  |  city_summaries: {col.count_documents({})} docs")

# ── 1. Build live stats from realtime HDFS data ───────────────────────────────
print("\n📂 Loading realtime HDFS dataset …")
rt = pd.read_csv(REALTIME_CSV, low_memory=False)
# Normalize column names to what actually exists
HUM_COL  = "humidity_percent" if "humidity_percent" in rt.columns else "humidity"
RAIN_COL = "rain_mm" if "rain_mm" in rt.columns else "rainfall_mm"

rt[RAIN_COL]  = pd.to_numeric(rt[RAIN_COL],  errors="coerce")
rt[HUM_COL]   = pd.to_numeric(rt[HUM_COL],   errors="coerce")
rt["elevation_m"]           = pd.to_numeric(rt.get("elevation_m",          pd.Series()), errors="coerce")
rt["distance_to_river_m"]   = pd.to_numeric(rt.get("distance_to_river_m",  pd.Series()), errors="coerce")
rt["timestamp"]  = pd.to_datetime(rt["timestamp"], errors="coerce")

# Latest snapshot per city
latest = rt.sort_values("timestamp").groupby("city").last().reset_index()

# Per-city aggregates across ALL history
agg = rt.groupby("city").agg(
    avg_rain     = (RAIN_COL, "mean"),
    max_rain     = (RAIN_COL, "max"),
    avg_humidity = (HUM_COL,  "mean"),
    total_cycles = (RAIN_COL, "count"),
).reset_index()

# Select available columns for merge
keep_cols = ["city", RAIN_COL, HUM_COL, "elevation_m", "distance_to_river_m", "timestamp"]
keep_cols = [c for c in keep_cols if c in latest.columns]
live_stats = latest[keep_cols].merge(agg, on="city", how="left")
# Standardise rain column name
if RAIN_COL != "rain_mm" and RAIN_COL in live_stats.columns:
    live_stats["rain_mm"] = live_stats[RAIN_COL]
if HUM_COL != "humidity" and HUM_COL in live_stats.columns:
    live_stats["humidity"] = live_stats[HUM_COL]

# ── 2. Build flood risk from processed BI data ────────────────────────────────
print("📂 Loading processed BI dataset …")
bi = pd.read_csv(PROCESSED_CSV, low_memory=False)
bi["Flood_Risk_Score"] = pd.to_numeric(bi["Flood_Risk_Score"], errors="coerce")
risk_agg = bi.groupby("city").agg(
    Flood_Risk_Score = ("Flood_Risk_Score", "mean"),
    rain_24h         = ("rain_mm",          "mean"),
    humidity_avg     = ("humidity_percent",  "mean"),
).reset_index()

# ── 3. Merge everything ───────────────────────────────────────────────────────
merged = live_stats.merge(risk_agg, on="city", how="left")

# Derive Risk_Level label
def risk_label(score):
    if pd.isna(score): return "Unknown"
    if score >= 80:    return "Critical"
    if score >= 50:    return "Warning"
    return "Low"

merged["Risk_Level"]  = merged["Flood_Risk_Score"].apply(risk_label)
merged["last_updated"]= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── 4. Upsert into MongoDB ────────────────────────────────────────────────────
print(f"\n🔄 Upserting {len(merged)} city documents into MongoDB …")
updated = 0
for _, row in merged.iterrows():
    doc = {k: (None if pd.isna(v) else v) for k, v in row.items()}
    result = col.update_one(
        {"city": row["city"]},
        {"$set": doc},
        upsert=True
    )
    updated += 1

print(f"✅ MongoDB Updated!  {updated} cities written.")

# ── 5. Create indexes for fast dashboard queries ──────────────────────────────
try:
    col.drop_index("city_1")
except Exception:
    pass
col.create_index("city",            unique=True)
col.create_index([("Flood_Risk_Score", pymongo.DESCENDING)])
col.create_index([("projected_pop_2026", pymongo.DESCENDING)])
print("🗂️  Indexes created: city (unique), Flood_Risk_Score, projected_pop_2026")

# ── 6. Quick verification ─────────────────────────────────────────────────────
print("\n📊 Sample verification (top 5 highest risk cities):")
for doc in col.find({"Flood_Risk_Score": {"$gt": 0}}, {"_id":0,"city":1,"Flood_Risk_Score":1,"Risk_Level":1,"rain_mm":1}).sort("Flood_Risk_Score",-1).limit(5):
    print(f"   {doc['city']:<20}  Risk: {doc.get('Flood_Risk_Score',0):.1f}  Level: {doc.get('Risk_Level','?')}  Rain: {doc.get('rain_mm',0):.1f} mm")

total = col.count_documents({})
with_risk = col.count_documents({"Flood_Risk_Score": {"$gt": 0}})
print(f"\n✅ Total docs: {total}  |  With Risk Score: {with_risk}  |  Ready for dashboard!")
