import pandas as pd
import numpy as np
import joblib
import logging
import os

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    confusion_matrix, classification_report,
    accuracy_score
)

from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

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
logger.info(f"Rows: {len(df)}")

# =========================
# FEATURE ENGINEERING
# =========================
logger.info("⚙️ Feature engineering...")

df["rain_intensity"] = df["rain7_mm"] / 7
df["rain_ratio"] = df["rain3_mm"] / (df["rain7_mm"] + 1)
df["river_risk"] = 1 / (df["distance_to_river_m"] + 1)

features = [
    "rain3_mm", "rain7_mm", "rain_intensity", "rain_ratio",
    "river_risk", "elevation_m", "distance_to_river_m",
    "lat", "lon"
]

df = df[features + ["flood"]].dropna()

X = df[features]
y = df["flood"]

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# SMOTE
# =========================
logger.info("⚖️ Applying SMOTE...")
smote = SMOTE(sampling_strategy=0.3, random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# =========================
# MODEL
# =========================
logger.info("🚀 Training XGBoost classifier...")
model = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    scale_pos_weight=3,
    eval_metric="logloss",
    n_jobs=-1
)

model.fit(X_train, y_train)

# =========================
# PREDICTIONS
# =========================
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
y_test_proba = model.predict_proba(X_test)[:, 1]

# =========================
# METRICS
# =========================
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)
auc = roc_auc_score(y_test, y_test_proba)

logger.info(f"Train Accuracy: {train_acc:.4f}")
logger.info(f"Test Accuracy: {test_acc:.4f}")
logger.info(f"ROC-AUC: {auc:.4f}")

logger.info("\n📄 Classification Report:\n" +
            classification_report(y_test, y_test_pred))

# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(y_test, y_test_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt="d")
plt.title("Confusion Matrix")
plt.savefig("outputs/flood_confusion_matrix.png")
plt.close()

# =========================
# ROC CURVE
# =========================
fpr, tpr, _ = roc_curve(y_test, y_test_proba)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC={auc:.3f}")
plt.plot([0,1],[0,1],'--')
plt.legend()
plt.title("ROC Curve")
plt.savefig("outputs/flood_roc_curve.png")
plt.close()

# =========================
# FEATURE IMPORTANCE
# =========================
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure()
sns.barplot(x=importances[indices], y=np.array(features)[indices])
plt.title("Feature Importance")
plt.savefig("outputs/flood_feature_importance.png")
plt.close()

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "models/flood_model.pkl")
logger.info("✅ Flood model saved successfully!")   