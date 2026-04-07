import pandas as pd
import numpy as np
import joblib
import logging
import os

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# =========================
# CREATE FOLDERS
# =========================
os.makedirs("models", exist_ok=True)
os.makedirs("outputs/rain_visuals", exist_ok=True)

# =========================
# LOAD DATA
# =========================
logger.info("📂 Loading dataset...")
df = pd.read_csv("data/processed/gujarat_rainfall_history.csv")

# =========================
# PREPROCESS
# =========================
df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
df = df.sort_values("date")

# =========================
# FEATURE ENGINEERING (NO LEAKAGE)
# =========================
logger.info("⚙️ Creating advanced features...")

# Lag features
df["rain_lag_1"] = df["rain_mm"].shift(1)
df["rain_lag_2"] = df["rain_mm"].shift(2)
df["rain_lag_3"] = df["rain_mm"].shift(3)
df["rain_lag_7"] = df["rain_mm"].shift(7)

# Rolling features (POWERFUL)
df["rolling_mean_3"] = df["rain_mm"].shift(1).rolling(3).mean()
df["rolling_sum_7"] = df["rain_mm"].shift(1).rolling(7).sum()

# Seasonality features
df["month"] = df["date"].dt.month
df["day_of_year"] = df["date"].dt.dayofyear

# Target
df["target"] = df["rain_mm"]

df = df.dropna()

# =========================
# FEATURES
# =========================
features = [
    "rain_lag_1",
    "rain_lag_2",
    "rain_lag_3",
    "rain_lag_7",
    "rolling_mean_3",
    "rolling_sum_7",
    "month",
    "day_of_year",
    "lat",
    "lon"
]

X = df[features]
y = df["target"]

# =========================
# TIME SPLIT
# =========================
logger.info("🔀 Time-based split...")
split = int(len(df) * 0.8)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]

# =========================
# MODEL (IMPROVED)
# =========================
logger.info("🌧️ Training improved model...")

model = XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# PREDICTIONS
# =========================
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# =========================
# METRICS
# =========================
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

print("\n📊 TRAIN METRICS")
print("R2:", train_r2)
print("MAE:", train_mae)
print("RMSE:", train_rmse)

print("\n📊 TEST METRICS")
print("R2:", test_r2)
print("MAE:", test_mae)
print("RMSE:", test_rmse)

# =========================
# VISUALS
# =========================

# Correlation Heatmap
plt.figure(figsize=(10,7))
corr = df[features + ["target"]].corr()
sns.heatmap(corr, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.savefig("outputs/rain_visuals/correlation_heatmap.png")
plt.close()

# Actual vs Predicted
plt.figure(figsize=(6,6))
plt.scatter(y_test, y_test_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         'r--')
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Actual vs Predicted")
plt.savefig("outputs/rain_visuals/actual_vs_pred.png")
plt.close()

# Residual Plot
errors = y_test - y_test_pred
plt.figure(figsize=(6,4))
plt.scatter(y_test_pred, errors, alpha=0.5)
plt.axhline(0, linestyle='--')
plt.title("Residual Plot")
plt.savefig("outputs/rain_visuals/residual_plot.png")
plt.close()

# Error Distribution
plt.figure(figsize=(6,4))
sns.histplot(errors, bins=50)
plt.title("Error Distribution")
plt.savefig("outputs/rain_visuals/error_distribution.png")
plt.close()

# Feature Importance
importances = model.feature_importances_
plt.figure(figsize=(6,4))
sns.barplot(x=importances, y=features)
plt.title("Feature Importance")
plt.savefig("outputs/rain_visuals/feature_importance.png")
plt.close()

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "models/rain_model.pkl")

print("\n✅ Improved model saved!")
print("📁 Visuals saved in: outputs/rain_visuals/")