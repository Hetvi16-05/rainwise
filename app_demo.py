import streamlit as st
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood Prediction Demo", layout="centered")

st.title("🌊 Flood Prediction System (Explainable AI)")
st.markdown("Machine Learning + GIS + SHAP Explainability")

# ----------------------
# LOAD MODEL
# ----------------------
model = joblib.load("models/flood_model.pkl")

# ----------------------
# LOAD CITY DATA
# ----------------------
cities_df = pd.read_csv("data/config/gujarat_cities.csv")
cities_df.columns = cities_df.columns.str.lower()

city = st.selectbox("📍 Select City", cities_df["city"].unique())

city_row = cities_df[cities_df["city"] == city]
city_lat = float(city_row["lat"].values[0])
city_lon = float(city_row["lon"].values[0])

# ----------------------
# LOAD GIS DATA
# ----------------------
river_df = pd.read_csv("data/processed/gujarat_river_distance.csv")
elev_df = pd.read_csv("data/processed/gujarat_elevation.csv")

def find_nearest(df, lat, lon):
    df["dist"] = (df["lat"] - lat)**2 + (df["lon"] - lon)**2
    return df.loc[df["dist"].idxmin()]

distance = float(find_nearest(river_df, city_lat, city_lon)["river_distance"])
elevation = float(find_nearest(elev_df, city_lat, city_lon)["elevation"])

st.write(f"📏 River Distance: {distance:.2f} m")
st.write(f"⛰ Elevation: {elevation:.2f} m")

# ----------------------
# INPUT
# ----------------------
rain = st.slider("Rain (1h mm)", 0.0, 100.0, 10.0)

# ----------------------
# PREDICT
# ----------------------
if st.button("🔍 Predict"):

    rain3 = rain * 3
    rain7 = rain * 7

    rain_intensity = rain7 / 7
    rain_ratio = rain3 / (rain7 + 1)

    heavy_rain_flag = int(rain3 > 150)
    extreme_rain_flag = int(rain7 > 300)
    river_risk = 1 / (distance + 1)

    nasa_avg = rain * 0.8
    nasa_max = rain * 1.2
    nasa_std = rain * 0.3

    features = pd.DataFrame([[
        rain3, rain7, rain_intensity, rain_ratio,
        heavy_rain_flag, extreme_rain_flag, river_risk,
        elevation, distance,
        city_lat, city_lon,
        nasa_avg, nasa_max, nasa_std
    ]], columns=[
        "rain3_mm","rain7_mm","rain_intensity","rain_ratio",
        "heavy_rain_flag","extreme_rain_flag","river_risk",
        "elevation_m","distance_to_river_m",
        "lat","lon",
        "nasa_avg_rain","nasa_max_rain","nasa_std_rain"
    ])

    proba = model.predict_proba(features)[0][1]

    st.write(f"🌊 Flood Probability: {proba:.2f}")

    if proba > 0.6:
        st.error("🚨 HIGH RISK")
    elif proba > 0.3:
        st.warning("⚠️ MODERATE RISK")
    else:
        st.success("✅ LOW RISK")

    # =========================
    # 🔥 SHAP EXPLAINABILITY
    # =========================
    st.subheader("🧠 Model Explanation (SHAP)")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features)

    fig, ax = plt.subplots()
    shap.plots.waterfall(shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=features.iloc[0]
    ), show=False)

    st.pyplot(fig)