"""
🔧 Feature Compatibility Module for RAINWISE
=============================================
Ensures satellite & geospatial data maps correctly to model inputs.

The flood model expects: [rain_mm, elevation_m, distance_to_river_m, lat, lon]
The rainfall model expects: [temperature, humidity, pressure, wind_speed, cloud_cover]

This module handles:
- Feature name mapping from different sources
- Value clipping to training data ranges
- Missing value imputation
- Feature validation
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# ----------------------
# Training data ranges (from actual dataset)
# ----------------------
FLOOD_MODEL_RANGES = {
    "rain_mm":              {"min": 0.0,    "max": 93.46,   "default": 0.0},
    "elevation_m":          {"min": -5.0,   "max": 1200.0,  "default": 50.0},
    "distance_to_river_m":  {"min": 0.0,    "max": 500000.0,"default": 50000.0},
    "lat":                  {"min": 20.0,   "max": 24.6,    "default": 22.3},
    "lon":                  {"min": 68.5,   "max": 74.5,    "default": 71.9},
}

RAINFALL_MODEL_RANGES = {
    "temperature":  {"min": 15.0,  "max": 48.0,   "default": 32.0},
    "humidity":     {"min": 20.0,  "max": 100.0,  "default": 55.0},
    "pressure":     {"min": 985.0, "max": 1035.0, "default": 1012.0},
    "wind_speed":   {"min": 0.0,   "max": 80.0,   "default": 12.0},
    "cloud_cover":  {"min": 0.0,   "max": 100.0,  "default": 30.0},
}


# ----------------------
# Map satellite rainfall to model input
# ----------------------
def prepare_flood_features(rain_mm, elevation_m, distance_to_river_m, lat, lon):
    """
    Prepare and validate features for the flood model.

    Args:
        rain_mm: Rainfall in mm (from satellite or manual)
        elevation_m: Elevation in meters
        distance_to_river_m: Distance to nearest river in meters
        lat: Latitude
        lon: Longitude

    Returns:
        numpy array of shape (1, 5) ready for model.predict()
    """
    features = {
        "rain_mm": rain_mm,
        "elevation_m": elevation_m,
        "distance_to_river_m": distance_to_river_m,
        "lat": lat,
        "lon": lon
    }

    # Handle None/NaN with defaults
    for key, ranges in FLOOD_MODEL_RANGES.items():
        val = features.get(key)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            features[key] = ranges["default"]
            logger.warning(f"Missing {key}, using default: {ranges['default']}")

    # Clip to training data range
    for key, ranges in FLOOD_MODEL_RANGES.items():
        features[key] = np.clip(features[key], ranges["min"], ranges["max"])

    return np.array([[
        features["rain_mm"],
        features["elevation_m"],
        features["distance_to_river_m"],
        features["lat"],
        features["lon"]
    ]])


def prepare_rainfall_features(temperature, humidity, pressure, wind_speed, cloud_cover):
    """
    Prepare and validate features for the rainfall model.

    Returns:
        numpy array of shape (1, 5) ready for model.predict()
    """
    features = {
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "cloud_cover": cloud_cover
    }

    for key, ranges in RAINFALL_MODEL_RANGES.items():
        val = features.get(key)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            features[key] = ranges["default"]
            logger.warning(f"Missing {key}, using default: {ranges['default']}")

    for key, ranges in RAINFALL_MODEL_RANGES.items():
        features[key] = np.clip(features[key], ranges["min"], ranges["max"])

    return np.array([[
        features["temperature"],
        features["humidity"],
        features["pressure"],
        features["wind_speed"],
        features["cloud_cover"]
    ]])


# ----------------------
# Map satellite data to model-compatible DataFrame
# ----------------------
def satellite_to_model_input(satellite_df, gis_df=None):
    """
    Convert satellite rainfall DataFrame to flood model input.

    Args:
        satellite_df: Output from gpm_fetcher with 'rainfall_mm', 'city', 'lat', 'lon'
        gis_df: Optional GIS data with 'elevation_m', 'distance_to_river_m'

    Returns:
        DataFrame with model-compatible columns
    """
    df = satellite_df.copy()

    # Rename if needed
    if "precipitation_mm" in df.columns and "rainfall_mm" not in df.columns:
        df["rainfall_mm"] = df["precipitation_mm"]

    # Ensure rain_mm column
    if "rainfall_mm" in df.columns:
        df["rain_mm"] = df["rainfall_mm"].fillna(0.0).clip(0, 93.46)
    else:
        df["rain_mm"] = 0.0
        logger.warning("No rainfall column found, using 0.0")

    # Merge GIS data if provided
    if gis_df is not None and not gis_df.empty:
        if "city" in gis_df.columns:
            df = df.merge(
                gis_df[["city", "elevation_m", "distance_to_river_m"]].drop_duplicates(),
                on="city", how="left"
            )

    # Fill missing GIS features with defaults
    if "elevation_m" not in df.columns:
        df["elevation_m"] = FLOOD_MODEL_RANGES["elevation_m"]["default"]
    if "distance_to_river_m" not in df.columns:
        df["distance_to_river_m"] = FLOOD_MODEL_RANGES["distance_to_river_m"]["default"]

    df["elevation_m"] = df["elevation_m"].fillna(FLOOD_MODEL_RANGES["elevation_m"]["default"])
    df["distance_to_river_m"] = df["distance_to_river_m"].fillna(
        FLOOD_MODEL_RANGES["distance_to_river_m"]["default"]
    )

    return df


# ----------------------
# Validate dataset for model compatibility
# ----------------------
def validate_dataset(df, model_type="flood"):
    """
    Validate that a DataFrame has all required columns and valid ranges.

    Args:
        df: DataFrame to validate
        model_type: 'flood' or 'rainfall'

    Returns:
        tuple: (is_valid: bool, issues: list[str])
    """
    issues = []
    ranges = FLOOD_MODEL_RANGES if model_type == "flood" else RAINFALL_MODEL_RANGES

    for col, r in ranges.items():
        if col not in df.columns:
            issues.append(f"Missing column: {col}")
        else:
            nulls = df[col].isna().sum()
            if nulls > 0:
                issues.append(f"{col}: {nulls} null values")

            below = (df[col] < r["min"]).sum()
            above = (df[col] > r["max"]).sum()
            if below > 0:
                issues.append(f"{col}: {below} values below min ({r['min']})")
            if above > 0:
                issues.append(f"{col}: {above} values above max ({r['max']})")

    is_valid = len(issues) == 0

    if is_valid:
        logger.info(f"✅ Dataset valid for {model_type} model")
    else:
        logger.warning(f"⚠️ Dataset issues for {model_type} model: {issues}")

    return is_valid, issues
