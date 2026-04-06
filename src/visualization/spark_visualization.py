import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from pyspark.sql import SparkSession

# =========================
# START SPARK
# =========================
spark = SparkSession.builder \
    .appName("Visualization") \
    .getOrCreate()

print("🚀 Spark started for visualization")

# =========================
# LOAD DATA
# =========================
path = os.path.abspath("data/bigdata/final.parquet")
df = spark.read.parquet(f"file://{path}")

print("📊 Rows:", df.count())

# =========================
# SAMPLE DATA (IMPORTANT)
# =========================
df_sample = df.sample(fraction=0.05, seed=42)

pdf = df_sample.toPandas()

os.makedirs("plots", exist_ok=True)

# =========================
# 1. FLOOD DISTRIBUTION
# =========================
pdf["flood"].value_counts().plot(kind="bar")
plt.title("Flood Distribution")
plt.savefig("plots/flood_distribution.png")
plt.show()

# =========================
# 2. RAINFALL DISTRIBUTION
# =========================
plt.hist(pdf["rain7_mm"], bins=50)
plt.title("Rainfall Distribution")
plt.savefig("plots/rain_distribution.png")
plt.show()

# =========================
# 3. FEATURE CORRELATION
# =========================
corr = pdf.corr()

plt.figure(figsize=(10, 6))
sns.heatmap(corr, cmap="coolwarm")
plt.title("Feature Correlation")
plt.savefig("plots/correlation_heatmap.png")
plt.show()

# =========================
# 4. SCATTER: RAIN vs FLOOD
# =========================
plt.scatter(pdf["rain7_mm"], pdf["flood"], alpha=0.3)
plt.title("Rainfall vs Flood")
plt.xlabel("Rainfall")
plt.ylabel("Flood")
plt.savefig("plots/rain_vs_flood.png")
plt.show()

# =========================
# 5. BOXPLOT
# =========================
sns.boxplot(x=pdf["flood"], y=pdf["rain7_mm"])
plt.title("Rainfall vs Flood (Boxplot)")
plt.savefig("plots/boxplot_rain_flood.png")
plt.show()

# =========================
# STOP
# =========================
spark.stop()
print("✅ Visualization complete")