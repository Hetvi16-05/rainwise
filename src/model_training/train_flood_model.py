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

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

# 🔥 IMPORTANT IMPORT (NO PICKLE ERROR)
from src.utils.features import feature_engineering

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

df = pd.read_csv(
    "data/processed/training_dataset_gujarat_advanced_labeled.csv",
    low_memory=False
)

df.columns = df.columns.str.lower()
logger.info(f"Rows: {len(df)}")

# =========================
# CREATE RAW FEATURE
# =========================
df["rain_mm"] = df["rain3_mm"] / 3

# =========================
# FEATURES (RAW INPUT ONLY)
# =========================
features = [
    "rain_mm",
    "elevation_m",
    "distance_to_river_m",
    "lat",
    "lon"
]

target = "flood"

df = df[features + [target]].dropna()

X = df[features].values
y = df[target].values

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# HANDLE IMBALANCE
# =========================
logger.info("⚖️ Applying SMOTE...")
smote = SMOTE(sampling_strategy=0.3, random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# =========================
# PIPELINE MODEL
# =========================
logger.info("🚀 Building pipeline model...")

model = Pipeline([
    ("feature_engineering", FunctionTransformer(feature_engineering)),
    ("classifier", XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=3,
        eval_metric="logloss",
        n_jobs=-1
    ))
])

# =========================
# TRAIN
# =========================
logger.info("🏋️ Training model...")
model.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================
logger.info("📊 Evaluating model...")

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
y_test_proba = model.predict_proba(X_test)[:, 1]

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
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
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
importances = model.named_steps["classifier"].feature_importances_

feature_names = [
    "rain3", "rain7", "rain_intensity", "rain_ratio",
    "river_risk", "elevation", "distance", "lat", "lon"
]

indices = np.argsort(importances)[::-1]

plt.figure()
sns.barplot(
    x=importances[indices],
    y=np.array(feature_names)[indices]
)
plt.title("Feature Importance")
plt.savefig("outputs/flood_feature_importance.png")
plt.close()

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "models/flood_model.pkl")

logger.info("✅ Pipeline model saved successfully!")