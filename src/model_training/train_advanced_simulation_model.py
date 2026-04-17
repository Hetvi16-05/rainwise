import pandas as pd
import numpy as np
import joblib
import logging
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

# IMPORT FEATURE LOGIC
from src.utils.features import feature_engineering

# SETUP LOGGING
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

INPUT_CSV = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
MODEL_PATH = "models/advanced_simulation_model.pkl"

def train():
    logger.info(f"📂 Loading dataset for advanced simulation training: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    
    # 🧹 PREPROCESSING: Extract Month from Date
    # date format is 20000101
    df['date_str'] = df['date'].astype(str)
    df['month'] = df['date_str'].apply(lambda x: int(x[4:6]))
    
    # 🧹 Clean naming inconsistencies from merge
    df = df.rename(columns={
        "river_distance": "river_distance_raw", # protect original
        "distance_to_river_m": "river_distance" 
    })

    # 🎯 TARGET FEATURES
    # Ordering must match the simulation loop EXACTLY:
    # [rain, elev, dist, lat, lon, rain3, rain7, month]
    features = [
        "rain_mm", 
        "elevation_m", 
        "river_distance", 
        "lat", 
        "lon", 
        "rain3_mm", 
        "rain7_mm", 
        "month"
    ]
    
    target = "flood"

    # Drop NaNs and select only required columns
    df_clean = df[features + [target]].dropna()
    
    X = df_clean[features].values
    y = df_clean[target].values
    
    logger.info(f"📊 Training on {len(X)} rows with 8 core features.")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Building Pipeline with Feature Engineering
    # Note: feature_engineering function transforms X from 8 cols into 10 cols
    model_pipeline = Pipeline([
        ("feature_engineering", FunctionTransformer(feature_engineering)),
        ("classifier", XGBClassifier(
            n_estimators=300,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            n_jobs=-1,
            random_state=42
        ))
    ])

    logger.info("🚀 Fitting Advanced Simulation Pipeline...")
    model_pipeline.fit(X_train, y_train)

    # Eval
    preds = model_pipeline.predict(X_test)
    proba = model_pipeline.predict_proba(X_test)[:, 1]
    
    logger.info(f"✅ Accuracy: {accuracy_score(y_test, preds):.4f}")
    logger.info(f"✅ ROC-AUC: {roc_auc_score(y_test, proba):.4f}")

    # Save
    os.makedirs("models", exist_ok=True)
    joblib.dump(model_pipeline, MODEL_PATH)
    logger.info(f"💾 Advanced Simulation Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
