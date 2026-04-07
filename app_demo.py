import streamlit as st
import joblib
import pandas as pd
import numpy as np

# 🔥 IMPORTANT IMPORT
from src.utils.features import feature_engineering

st.set_page_config(page_title="Flood Prediction Demo", layout="centered")

st.title("🌊 Flood Prediction System")
st.markdown("Predict flood risk from **rainfall amount & geography** using XGBoost Classifier.")

# ----------------------
# LOAD MODEL
# ----------------------
flood_model = joblib.load("models/flood_model.pkl")

# ----------------------
# CITY DATA
# ----------------------
cities_df = pd.read_csv("data/config/gujarat_cities.csv")
cities_df.columns = cities_df.columns.str.lower()

city = st.selectbox("📍 Select City", cities_df["city"].unique())

row = cities_df[cities_df["city"] == city]
lat = float(row["lat"].values[0])
lon = float(row["lon"].values[0])

# ----------------------
# GIS DATA
# ----------------------
river_df = pd.read_csv("data/processed/gujarat_river_distance.csv")
elev_df = pd.read_csv("data/processed/gujarat_elevation.csv")

river_df.columns = river_df.columns.str.lower()
elev_df.columns = elev_df.columns.str.lower()

def find_nearest(df, lat, lon):
    df = df.copy()
    df["dist"] = (df["lat"] - lat)**2 + (df["lon"] - lon)**2
    return df.loc[df["dist"].idxmin()]

distance = float(find_nearest(river_df, lat, lon)["river_distance"])
elevation = float(find_nearest(elev_df, lat, lon)["elevation"])

# ----------------------
# LOCATION INFO
# ----------------------
st.subheader("🌍 Location & Geography")
col1, col2 = st.columns(2)
col1.metric("Latitude", f"{lat:.4f}")
col2.metric("Longitude", f"{lon:.4f}")

col3, col4 = st.columns(2)
col3.metric("Distance to River", f"{distance:.0f} m")
col4.metric("Elevation", f"{elevation:.0f} m")

# ----------------------
# RAINFALL INPUT
# ----------------------
st.subheader("🌧 Rainfall Input")
st.markdown("Enter the observed or predicted rainfall amount.")

rain = st.slider("Rainfall (mm)", 0.0, 100.0, 10.0, step=0.5)
threshold = st.slider("🎯 Alert Threshold", 0.1, 0.9, 0.5, step=0.05)

# ----------------------
# PREDICT
# ----------------------
if st.button("🔍 Predict Flood Risk"):
    features = np.array([[rain, elevation, distance, lat, lon]])
    proba = flood_model.predict_proba(features)[0][1]

    st.divider()
    st.subheader("📊 Flood Risk Assessment")

    col_f1, col_f2 = st.columns(2)
    col_f1.metric("Flood Probability", f"{proba:.2f}")

    if proba > threshold:
        if proba > 0.8:
            col_f2.metric("Risk Level", "🔴 HIGH")
            st.error("🚨 HIGH FLOOD RISK — Evacuate low-lying areas immediately!")
        elif proba > 0.6:
            col_f2.metric("Risk Level", "🟠 SIGNIFICANT")
            st.error("🔴 SIGNIFICANT FLOOD RISK — Take precautionary measures!")
        else:
            col_f2.metric("Risk Level", "🟡 MODERATE")
            st.warning("⚠️ MODERATE FLOOD RISK — Stay alert and monitor conditions!")
    else:
        col_f2.metric("Risk Level", "🟢 LOW")
        st.success("✅ LOW FLOOD RISK — Conditions are currently safe.")

    # --- Summary Table ---
    st.subheader("📋 Input Summary")
    summary_df = pd.DataFrame({
        "Parameter": ["City", "Rainfall", "Elevation", "Distance to River",
                      "Latitude", "Longitude", "Flood Probability"],
        "Value": [city, f"{rain} mm", f"{elevation:.0f} m", f"{distance:.0f} m",
                  f"{lat:.4f}", f"{lon:.4f}", f"{proba:.2f}"]
    })
    st.table(summary_df)

# ----------------------
# MODEL EVALUATION
# ----------------------
st.divider()
st.subheader("📊 Flood Model Evaluation")
st.image("outputs/flood_confusion_matrix.png", caption="Confusion Matrix")
st.image("outputs/flood_feature_importance.png", caption="Feature Importance")

# ----------------------
# MAP
# ----------------------
st.subheader("🗺 Map")
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))