import pandas as pd
import os
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.metrics import classification_report, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import xgboost as xgb
from imblearn.over_sampling import SMOTE

# ----------------------
# paths
# ----------------------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data/processed/training_dataset_gujarat_advanced_labeled.csv"
)

MODEL_DIR = os.path.join(BASE_DIR, "models")
PLOT_DIR = os.path.join(BASE_DIR, "plots")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# ----------------------
# load data
# ----------------------
print("📥 Loading dataset...")
df = pd.read_csv(DATA_FILE)

TARGET = "flood"

# =========================================================
# ⚡ STAGE 1: FAST TUNING (SMALL DATA)
# =========================================================
print("\n⚡ Stage 1: Hyperparameter Tuning (FAST MODE)")

df_small = df.sample(300000, random_state=42)

X_small = df_small[[
    "rain3_mm",
    "rain7_mm",
    "elevation_m",
    "distance_to_river_m"
]].copy()

y_small = df_small[TARGET]

# cleaning
X_small = X_small.replace([float("inf"), -float("inf")], None)
X_small = X_small.fillna(X_small.median()).fillna(0)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X_small, y_small,
    test_size=0.2,
    random_state=42,
    stratify=y_small
)

# SMOTE (small data only)
sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

# ----------------------
# Random Forest tuning
# ----------------------
rf = RandomForestClassifier(random_state=42, n_jobs=-1)

rf_params = {
    "n_estimators": [100, 200],
    "max_depth": [10, 15, None],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "class_weight": ["balanced"]
}

rf_search = RandomizedSearchCV(
    rf,
    rf_params,
    n_iter=3,
    scoring="f1",
    cv=cv,
    verbose=1,
    n_jobs=-1
)

rf_search.fit(X_train, y_train)
rf_best_params = rf_search.best_params_

print("\n✅ Best RF Params:", rf_best_params)

# =========================================================
# ⚡ STAGE 2: FINAL TRAINING (FULL DATA)
# =========================================================
print("\n🚀 Stage 2: Final Training (FULL DATA)")

X = df[[
    "rain3_mm",
    "rain7_mm",
    "elevation_m",
    "distance_to_river_m"
]].copy()

y = df[TARGET]

# cleaning
X = X.replace([float("inf"), -float("inf")], None)
X = X.fillna(X.median()).fillna(0)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# SMOTE (full training)
print("⚖️ Applying SMOTE (final)...")
sm = SMOTE(random_state=42)
X_train, y_train = sm.fit_resample(X_train, y_train)

# ----------------------
# Final RF model
# ----------------------
print("\n🌲 Training Final Random Forest...")

rf_final = RandomForestClassifier(
    **rf_best_params,
    random_state=42,
    n_jobs=-1
)

rf_final.fit(X_train, y_train)

rf_pred = rf_final.predict(X_test)

print("\n📊 Final Model Report:")
print(classification_report(y_test, rf_pred))

# save model
joblib.dump(rf_final, os.path.join(MODEL_DIR, "flood_model_final.pkl"))

# =========================================================
# 📊 FEATURE IMPORTANCE
# =========================================================
print("\n📊 Feature Importance...")

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": rf_final.feature_importances_
}).sort_values(by="importance", ascending=False)

print(importance_df)

plt.figure()
plt.barh(importance_df["feature"], importance_df["importance"])
plt.xlabel("Importance")
plt.title("Feature Importance")
plt.gca().invert_yaxis()

plot_path = os.path.join(PLOT_DIR, "feature_importance.png")
plt.savefig(plot_path)

print("📈 Saved:", plot_path)

print("\n✅ TRAINING COMPLETE")