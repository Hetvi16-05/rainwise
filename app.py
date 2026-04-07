import streamlit as st
import joblib
import numpy as np
import requests
import shap
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flood AI", layout="centered")

st.title("🌊 Real-Time Flood Prediction + Explainability")

# ----------------------
# LOAD MODEL
# ----------------------
model = joblib.load("models/flood_model.pkl")

# ----------------------
# CITY INPUT
# ----------------------
city = st.text_input("Enter City (e.g. Surat)")

API_KEY = "YOUR_API_KEY"

# ----------------------
# WEATHER API
# ----------------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()

    rain = res.get("rain", {}).get("1h", 0)
    clouds = res.get("clouds", {}).get("all", 0)
    humidity = res.get("main", {}).get("humidity", 0)

    return rain, clouds, humidity

# ----------------------
# PREDICT
# ----------------------
if st.button("🌦️ Predict Live Flood Risk"):

    rain, clouds, humidity = get_weather(city)

    st.write(f"🌧 Rain: {rain} mm")
    st.write(f"☁ Clouds: {clouds}%")
    st.write(f"💧 Humidity: {humidity}%")

    # Feature engineering
    rain3 = rain * 3
    rain7 = rain * 7

    rain_intensity = rain7 / 7
    rain_ratio = rain3 / (rain7 + 1)
    river_risk = 1 / (500 + 1)

    features = np.array([[
        rain3, rain7, rain_intensity, rain_ratio,
        0, 0, river_risk,
        50, 500,
        22, 72,
        rain*0.8, rain*1.2, rain*0.3
    ]])

    proba = model.predict_proba(features)[0][1]

    st.write(f"🌊 Flood Probability: {proba:.2f}")

    if proba > 0.7:
        st.error("🚨 HIGH RISK")
    elif proba > 0.4:
        st.warning("⚠️ MODERATE RISK")
    else:
        st.success("✅ SAFE")

    # =========================
    # 🔥 SHAP EXPLAINABILITY
    # =========================
    st.subheader("🧠 Why this prediction?")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features)

    fig, ax = plt.subplots()
    shap.plots.waterfall(shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=features[0]
    ), show=False)

    st.pyplot(fig)