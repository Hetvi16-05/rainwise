import streamlit as st
import joblib
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# 🔥 IMPORTANT IMPORT
from src.utils.features import feature_engineering

st.set_page_config(
    page_title="RAINWISE — Real-Time Flood Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------
# LOAD MODELS
# ----------------------
@st.cache_resource
def load_models():
    flood_model = joblib.load("models/flood_model.pkl")
    rainfall_model = joblib.load("models/rainfall_model.pkl")
    return flood_model, rainfall_model

@st.cache_data
def load_city_data():
    cities_df = pd.read_csv("data/config/gujarat_cities.csv")
    cities_df.columns = cities_df.columns.str.lower()
    return cities_df

@st.cache_data
def load_gis_data():
    river_df = pd.read_csv("data/processed/gujarat_river_distance.csv")
    elev_df = pd.read_csv("data/processed/gujarat_elevation.csv")
    river_df.columns = river_df.columns.str.lower()
    elev_df.columns = elev_df.columns.str.lower()
    return river_df, elev_df

flood_model, rainfall_model = load_models()
cities_df = load_city_data()
river_df, elev_df = load_gis_data()

def find_nearest(df, lat, lon):
    df = df.copy()
    df["dist"] = (df["lat"] - lat)**2 + (df["lon"] - lon)**2
    return df.loc[df["dist"].idxmin()]

# ----------------------
# WEATHER API (Open-Meteo — FREE, no API key)
# ----------------------
def fetch_weather(lat, lon):
    """Fetch real-time weather from Open-Meteo API."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,cloud_cover,precipitation",
            "timezone": "Asia/Kolkata"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "error" in data and data["error"]:
            return None, data.get("reason", "API error")

        current = data["current"]
        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "pressure": current["surface_pressure"],
            "wind_speed": current["wind_speed_10m"],
            "cloud_cover": current["cloud_cover"],
            "actual_precipitation": current["precipitation"],
            "time": current["time"]
        }, None

    except Exception as e:
        return None, str(e)


# ================================================================
# HEADER
# ================================================================
st.title("🌊 RAINWISE — Real-Time Flood Intelligence")
st.markdown("Live weather data → AI Rainfall Prediction → Flood Risk Assessment")
st.divider()

# ================================================================
# SIDEBAR
# ================================================================
st.sidebar.title("⚙️ Settings")

city = st.sidebar.selectbox("📍 Select City", cities_df["city"].unique())
row = cities_df[cities_df["city"] == city]
lat = float(row["lat"].values[0])
lon = float(row["lon"].values[0])

distance = float(find_nearest(river_df, lat, lon)["river_distance"])
elevation = float(find_nearest(elev_df, lat, lon)["elevation"])

threshold = st.sidebar.slider("🎯 Flood Alert Threshold", 0.1, 0.9, 0.5, step=0.05)

st.sidebar.divider()
st.sidebar.subheader("🌍 Geography")
st.sidebar.metric("Elevation", f"{elevation:.0f} m")
st.sidebar.metric("Distance to River", f"{distance:.0f} m")
st.sidebar.metric("Coordinates", f"{lat:.2f}, {lon:.2f}")

st.sidebar.divider()
st.sidebar.info(
    "**Data Source**: Open-Meteo API (free, no key required)\n\n"
    "**Rainfall Model**: XGBoost Regressor (R²=0.917)\n\n"
    "**Flood Model**: XGBoost Classifier (AUC=0.932)"
)

# ================================================================
# FETCH REAL-TIME WEATHER
# ================================================================
st.subheader(f"📡 Live Weather for {city}")

weather, error = fetch_weather(lat, lon)

if error:
    st.error(f"⚠️ Could not fetch live weather: {error}")
    st.info("💡 Use manual input below instead.")

    # --- Manual Fallback ---
    st.subheader("✏️ Manual Atmospheric Input")
    col_a, col_b, col_c = st.columns(3)
    temperature = col_a.number_input("🌡️ Temperature (°C)", value=32.0, step=0.5)
    humidity = col_b.number_input("💧 Humidity (%)", value=55.0, step=1.0)
    pressure = col_c.number_input("📊 Pressure (hPa)", value=1012.0, step=0.5)

    col_d, col_e = st.columns(2)
    wind_speed = col_d.number_input("💨 Wind Speed (km/h)", value=12.0, step=1.0)
    cloud_cover = col_e.number_input("☁️ Cloud Cover (%)", value=30.0, step=1.0)

    actual_precipitation = None
    weather_time = "Manual Input"

else:
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    pressure = weather["pressure"]
    wind_speed = weather["wind_speed"]
    cloud_cover = weather["cloud_cover"]
    actual_precipitation = weather["actual_precipitation"]
    weather_time = weather["time"]

    # --- Display Live Weather Cards ---
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🌡️ Temperature", f"{temperature}°C")
    col2.metric("💧 Humidity", f"{humidity}%")
    col3.metric("📊 Pressure", f"{pressure} hPa")
    col4.metric("💨 Wind", f"{wind_speed} km/h")
    col5.metric("☁️ Clouds", f"{cloud_cover}%")

    if actual_precipitation is not None and actual_precipitation > 0:
        st.info(f"🌧 Current actual precipitation: **{actual_precipitation} mm/h**")

    st.caption(f"📅 Last updated: {weather_time}")

# ================================================================
# AI PREDICTIONS
# ================================================================
st.divider()

col_left, col_right = st.columns(2)

# --- Stage 1: Rainfall Prediction ---
with col_left:
    st.subheader("🌧 Stage 1 — Rainfall Prediction")

    atmos_features = np.array([[temperature, humidity, pressure, wind_speed, cloud_cover]])
    predicted_rain = float(rainfall_model.predict(atmos_features)[0])
    predicted_rain = max(0.0, predicted_rain)

    st.metric("Predicted Rainfall", f"{predicted_rain:.2f} mm")

    if actual_precipitation is not None:
        st.metric("Actual (from API)", f"{actual_precipitation} mm/h")

    if predicted_rain > 50:
        st.error(f"🚨 **Very Heavy** — {predicted_rain:.1f} mm — Flash flood risk!")
    elif predicted_rain > 20:
        st.warning(f"⚠️ **Heavy** — {predicted_rain:.1f} mm — Stay alert!")
    elif predicted_rain > 5:
        st.info(f"🌦 **Moderate** — {predicted_rain:.1f} mm")
    else:
        st.success(f"☀️ **Light / None** — {predicted_rain:.1f} mm")

# --- Stage 2: Flood Prediction ---
with col_right:
    st.subheader("🌊 Stage 2 — Flood Prediction")

    flood_features = np.array([[predicted_rain, elevation, distance, lat, lon]])
    proba = flood_model.predict_proba(flood_features)[0][1]

    st.metric("Flood Probability", f"{proba:.2f}")

    if proba > threshold:
        if proba > 0.8:
            st.error("🚨 **HIGH RISK** — Evacuate low-lying areas!")
        elif proba > 0.6:
            st.error("🔴 **SIGNIFICANT RISK** — Take precautionary measures!")
        else:
            st.warning("⚠️ **MODERATE RISK** — Stay alert and monitor!")
    else:
        st.success("✅ **LOW RISK** — Conditions are safe.")

# ================================================================
# SUMMARY TABLE
# ================================================================
st.divider()
st.subheader("📋 Full Prediction Report")

report_df = pd.DataFrame({
    "Parameter": [
        "City", "Latitude", "Longitude", "Elevation", "Distance to River",
        "Temperature", "Humidity", "Pressure", "Wind Speed", "Cloud Cover",
        "Predicted Rainfall", "Flood Probability",
        "Data Source", "Timestamp"
    ],
    "Value": [
        city, f"{lat:.4f}", f"{lon:.4f}", f"{elevation:.0f} m", f"{distance:.0f} m",
        f"{temperature}°C", f"{humidity}%", f"{pressure} hPa",
        f"{wind_speed} km/h", f"{cloud_cover}%",
        f"{predicted_rain:.2f} mm", f"{proba:.2f}",
        "Open-Meteo API" if error is None else "Manual Input",
        weather_time
    ]
})
st.table(report_df)

# ================================================================
# MODEL EVALUATION
# ================================================================
st.divider()
st.subheader("📊 Model Evaluation")

tab1, tab2 = st.tabs(["🌊 Flood Model", "🌧 Rainfall Model"])

with tab1:
    col_e1, col_e2 = st.columns(2)
    col_e1.image("outputs/flood_confusion_matrix.png", caption="Confusion Matrix")
    col_e2.image("outputs/flood_feature_importance.png", caption="Feature Importance")

with tab2:
    col_e3, col_e4 = st.columns(2)
    col_e3.image("outputs/rainfall_actual_vs_predicted.png", caption="Actual vs Predicted (R²=0.917)")
    col_e4.image("outputs/rainfall_feature_importance.png", caption="Feature Importance")

# ================================================================
# MAP
# ================================================================
st.divider()
st.subheader("🗺 Location Map")
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
