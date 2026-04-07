import pandas as pd
import numpy as np
import joblib
import logging
import os

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

os.makedirs("outputs", exist_ok=True)
os.makedirs("models", exist_ok=True)

# =========================
# LOAD DATA
# =========================
logger.info("📂 Loading dataset...")
df = pd.read_parquet("data/bigdata/final.parquet")

# =========================
# FEATURES
# =========================
features = [
    "lat", "lon",
    "elevation_m",
    "distance_to_river_m",
    "nasa_avg_rain",
    "nasa_max_rain",
    "nasa_std_rain"
]

target = "rain3_mm"

df = df[features + [target]].dropna()

X = df[features]
y = df[target]

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# MODEL
# =========================
logger.info("🌧️ Training XGBoost regressor...")
model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1
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

mae = mean_absolute_error(y_test, y_test_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

logger.info(f"Train R2: {train_r2:.4f}")
logger.info(f"Test R2: {test_r2:.4f}")
logger.info(f"MAE: {mae:.2f}")
logger.info(f"RMSE: {rmse:.2f}")

# =========================
# ACTUAL VS PREDICTED
# =========================
plt.figure()
plt.scatter(y_test, y_test_pred)
plt.xlabel("Actual Rain")
plt.ylabel("Predicted Rain")
plt.title("Actual vs Predicted")
plt.savefig("outputs/rain_actual_vs_pred.png")
plt.close()

# =========================
# ERROR DISTRIBUTION
# =========================
errors = y_test - y_test_pred

plt.figure()
sns.histplot(errors, bins=50)
plt.title("Error Distribution")
plt.savefig("outputs/rain_error_distribution.png")
plt.close()

# =========================
# FEATURE IMPORTANCE
# =========================
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure()
sns.barplot(x=importances[indices], y=np.array(features)[indices])
plt.title("Feature Importance (Rain)")
plt.savefig("outputs/rain_feature_importance.png")
plt.close()

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "models/rain_model.pkl")
logger.info("✅ Rain model saved successfully!")