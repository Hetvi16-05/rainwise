import streamlit as st
import joblib
import pandas as pd
import numpy as np

# 🔥 IMPORTANT IMPORT
from src.utils.features import feature_engineering

st.set_page_config(page_title="RAINWISE - Flood & Rainfall Prediction", layout="centered")

# ----------------------
# SIDEBAR NAVIGATION
# ----------------------
st.sidebar.title("🌊 RAINWISE")
st.sidebar.markdown("**AI Prediction System**")
page = st.sidebar.radio(
    "Select Model",
    ["🌧 Rainfall Prediction", "🌊 Flood Prediction"],
    index=0
)

st.sidebar.divider()
st.sidebar.markdown("**About**")
st.sidebar.info(
    "RAINWISE uses two independent ML models:\n\n"
    "🌧 **Rainfall Model** — Predicts rainfall from atmospheric conditions\n\n"
    "🌊 **Flood Model** — Predicts flood risk from rainfall & geography"
)

# ----------------------
# SHARED: CITY & GIS DATA
# ----------------------
cities_df = pd.read_csv("data/config/gujarat_cities.csv")
cities_df.columns = cities_df.columns.str.lower()

river_df = pd.read_csv("data/processed/gujarat_river_distance.csv")
elev_df = pd.read_csv("data/processed/gujarat_elevation.csv")
river_df.columns = river_df.columns.str.lower()
elev_df.columns = elev_df.columns.str.lower()

def find_nearest(df, lat, lon):
    df = df.copy()
    df["dist"] = (df["lat"] - lat)**2 + (df["lon"] - lon)**2
    return df.loc[df["dist"].idxmin()]


# ================================================================
# PAGE 1: RAINFALL PREDICTION
# ================================================================
if page == "🌧 Rainfall Prediction":

    st.title("🌧 Rainfall Prediction")
    st.markdown("Predict rainfall from current **atmospheric conditions** using XGBoost Regressor.")

    rainfall_model = joblib.load("models/rainfall_model.pkl")

    # --- City Selection ---
    city = st.selectbox("📍 Select City", cities_df["city"].unique(), key="rain_city")
    row = cities_df[cities_df["city"] == city]
    lat = float(row["lat"].values[0])
    lon = float(row["lon"].values[0])

    st.subheader("🌍 Location")
    col1, col2 = st.columns(2)
    col1.metric("Latitude", f"{lat:.4f}")
    col2.metric("Longitude", f"{lon:.4f}")

    # --- Atmospheric Inputs ---
    st.subheader("🌡️ Atmospheric Conditions")
    st.markdown("Adjust the sliders to match current weather conditions.")

    col_a, col_b = st.columns(2)
    temperature = col_a.slider("🌡️ Temperature (°C)", 15.0, 48.0, 32.0, step=0.5, key="rain_temp")
    humidity = col_b.slider("💧 Humidity (%)", 20.0, 100.0, 55.0, step=1.0, key="rain_hum")

    col_c, col_d = st.columns(2)
    pressure = col_c.slider("📊 Pressure (hPa)", 985.0, 1035.0, 1012.0, step=0.5, key="rain_pres")
    wind_speed = col_d.slider("💨 Wind Speed (km/h)", 0.0, 80.0, 12.0, step=1.0, key="rain_wind")

    cloud_cover = st.slider("☁️ Cloud Cover (%)", 0.0, 100.0, 30.0, step=1.0, key="rain_cloud")

    # --- Predict ---
    if st.button("🔍 Predict Rainfall", key="rain_btn"):
        atmos_features = np.array([[temperature, humidity, pressure, wind_speed, cloud_cover]])
        predicted_rain = float(rainfall_model.predict(atmos_features)[0])
        predicted_rain = max(0.0, predicted_rain)

        st.divider()
        st.subheader("📊 Predicted Rainfall")

        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Predicted Rainfall", f"{predicted_rain:.2f} mm")

        if predicted_rain > 50:
            col_r2.metric("Intensity", "🔴 Very Heavy")
            st.error(f"🚨 Very heavy rainfall predicted: {predicted_rain:.1f} mm — Flash flood risk!")
        elif predicted_rain > 20:
            col_r2.metric("Intensity", "🟠 Heavy")
            st.warning(f"⚠️ Heavy rainfall predicted: {predicted_rain:.1f} mm — Stay alert!")
        elif predicted_rain > 5:
            col_r2.metric("Intensity", "🟡 Moderate")
            st.info(f"🌦 Moderate rainfall predicted: {predicted_rain:.1f} mm")
        else:
            col_r2.metric("Intensity", "🟢 Light / None")
            st.success(f"☀️ Light or no rainfall predicted: {predicted_rain:.1f} mm")

        # --- Summary Table ---
        st.subheader("📋 Input Summary")
        summary_df = pd.DataFrame({
            "Parameter": ["City", "Temperature", "Humidity", "Pressure", "Wind Speed", "Cloud Cover", "Predicted Rainfall"],
            "Value": [city, f"{temperature}°C", f"{humidity}%", f"{pressure} hPa",
                      f"{wind_speed} km/h", f"{cloud_cover}%", f"{predicted_rain:.2f} mm"]
        })
        st.table(summary_df)

    # --- Model Evaluation ---
    st.divider()
    st.subheader("📊 Rainfall Model Evaluation")
    st.image("outputs/rainfall_actual_vs_predicted.png", caption="Actual vs Predicted Rainfall (R²=0.917)")
    st.image("outputs/rainfall_feature_importance.png", caption="Feature Importance")

    # --- Map ---
    st.subheader("🗺 Map")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))


# ================================================================
# PAGE 2: FLOOD PREDICTION
# ================================================================
elif page == "🌊 Flood Prediction":

    st.title("🌊 Flood Prediction")
    st.markdown("Predict flood risk from **rainfall amount & geography** using XGBoost Classifier.")

    flood_model = joblib.load("models/flood_model.pkl")

    # --- City Selection ---
    city = st.selectbox("📍 Select City", cities_df["city"].unique(), key="flood_city")
    row = cities_df[cities_df["city"] == city]
    lat = float(row["lat"].values[0])
    lon = float(row["lon"].values[0])

    distance = float(find_nearest(river_df, lat, lon)["river_distance"])
    elevation = float(find_nearest(elev_df, lat, lon)["elevation"])

    # --- Location Info ---
    st.subheader("🌍 Location & Geography")
    col1, col2 = st.columns(2)
    col1.metric("Latitude", f"{lat:.4f}")
    col2.metric("Longitude", f"{lon:.4f}")

    col3, col4 = st.columns(2)
    col3.metric("Distance to River", f"{distance:.0f} m")
    col4.metric("Elevation", f"{elevation:.0f} m")

    # --- Rainfall Input ---
    st.subheader("🌧 Rainfall Input")
    st.markdown("Enter the observed or predicted rainfall amount.")

    rain = st.slider("Rainfall (mm)", 0.0, 100.0, 10.0, step=0.5, key="flood_rain")
    threshold = st.slider("🎯 Alert Threshold", 0.1, 0.9, 0.5, step=0.05, key="flood_thresh")

    # --- Predict ---
    if st.button("🔍 Predict Flood Risk", key="flood_btn"):
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

    # --- Model Evaluation ---
    st.divider()
    st.subheader("📊 Flood Model Evaluation")
    st.image("outputs/flood_confusion_matrix.png", caption="Confusion Matrix")
    st.image("outputs/flood_feature_importance.png", caption="Feature Importance")

    # --- Map ---
    st.subheader("🗺 Map")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))