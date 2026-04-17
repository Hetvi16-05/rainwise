import numpy as np

def encode_seasonality(month):
    """Sine/Cosine encoding for month synchronization."""
    sin = np.sin(2 * np.pi * month / 12)
    cos = np.cos(2 * np.pi * month / 12)
    return sin, cos

def feature_engineering(X):
    # Standard format: [rain, elevation, distance, lat, lon]
    # In Advanced Simulation mode, we may pass more columns
    rain = X[:, 0]
    elevation = X[:, 1]
    distance = X[:, 2]
    lat = X[:, 3]
    lon = X[:, 4]
    
    # If X has extra columns, they are [..., rain3, rain7, month]
    if X.shape[1] >= 8:
        rain3 = X[:, 5]
        rain7 = X[:, 6]
        month = X[:, 7]
    else:
        # Lean Mode (Live Dashboard) - Approximations
        # This keeps the Live Dashboard functional even if it doesn't have lags
        rain3 = rain * 2.5
        rain7 = rain * 5.0
        month = np.ones_like(rain) * 7 # Assuming July for baseline

    # Engineering new features
    rain_intensity = (rain / (rain7 + 0.1)) * 10
    rain_ratio = rain3 / (rain7 + 0.1)
    
    # 🌊 [USER SPECIFIED FORMULA] Hybrid River Risk Proxy
    river_risk = (rain7 * 0.6 + rain3 * 0.4) / (distance + 1)
    
    # 🚰 Drainage Capacity Factor (Topographic evacuation)
    drainage_factor = (elevation / 100) * (1 - (1 / (distance + 1)))

    return np.column_stack([
        rain3,
        rain7,
        rain_intensity,
        rain_ratio,
        river_risk,
        drainage_factor,
        elevation,
        distance,
        lat,
        lon
    ])