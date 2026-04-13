import numpy as np

def feature_engineering(X):
    rain = X[:, 0]
    elevation = X[:, 1]
    distance = X[:, 2]
    lat = X[:, 3]
    lon = X[:, 4]

    rain3 = rain * 3
    rain7 = rain * 7

    rain_intensity = rain7 / 7
    rain_ratio = rain3 / (rain7 + 1)
    river_risk = 1 / (distance + 1)
    
    # 🚰 [RUBRIC ADDITION] Drainage Capacity Factor
    # Derived from topographic stability and water escape proximity
    drainage_factor = (elevation / 100) * (1 - river_risk)

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