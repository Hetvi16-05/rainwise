"""
🌍 Geospatial Features Module for RAINWISE
============================================
Extracts terrain and vegetation features for flood risk assessment.

Features:
1. Elevation (DEM) — via Open Elevation API (free, no key)
2. Slope — calculated from elevation gradient
3. NDVI — Normalized Difference Vegetation Index (Sentinel-2 hook)

Usage:
    from src.features.geospatial_features import get_geospatial_features
    features = get_geospatial_features(lat, lon)
"""

import os
import time
import logging
import requests
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# API endpoints
OPEN_ELEVATION_API = "https://api.open-elevation.com/api/v1/lookup"
REQUEST_TIMEOUT = 15


# ================================================================
# 1. ELEVATION (DEM)
# ================================================================
def get_elevation(lat, lon, retries=3):
    """
    Get elevation in meters for a single lat/lon using Open Elevation API.

    Args:
        lat: Latitude
        lon: Longitude
        retries: Number of retry attempts

    Returns:
        float: Elevation in meters, or None if failed
    """
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                OPEN_ELEVATION_API,
                params={"locations": f"{lat},{lon}"},
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    elev = results[0].get("elevation")
                    logger.debug(f"Elevation at ({lat}, {lon}): {elev}m")
                    return float(elev) if elev is not None else None

            logger.warning(f"Elevation API HTTP {response.status_code} (attempt {attempt})")

        except Exception as e:
            logger.warning(f"Elevation API error (attempt {attempt}): {e}")

        if attempt < retries:
            time.sleep(1 * attempt)

    return None


def get_elevation_batch(locations):
    """
    Get elevation for multiple locations in one API call.

    Args:
        locations: list of dicts with 'latitude' and 'longitude'

    Returns:
        list of elevation values (float or None)
    """
    try:
        response = requests.post(
            OPEN_ELEVATION_API,
            json={"locations": locations},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return [r.get("elevation") for r in data.get("results", [])]

    except Exception as e:
        logger.error(f"Batch elevation error: {e}")

    # Fallback: individual requests
    return [get_elevation(loc["latitude"], loc["longitude"]) for loc in locations]


# ================================================================
# 2. SLOPE CALCULATION
# ================================================================
def compute_slope(elevation_array, cell_size=30.0):
    """
    Compute slope in degrees from a 2D elevation grid (DEM).

    Uses numpy gradient to calculate slope from elevation differences.
    Standard GIS slope calculation: arctan(sqrt(dz/dx² + dz/dy²))

    Args:
        elevation_array: 2D numpy array of elevation values
        cell_size: Grid cell size in meters (default: 30m for SRTM)

    Returns:
        2D numpy array of slope values in degrees
    """
    if elevation_array is None or elevation_array.size == 0:
        return np.array([])

    elevation_array = np.array(elevation_array, dtype=float)

    # Calculate gradients
    dy, dx = np.gradient(elevation_array, cell_size)

    # Slope = arctan(sqrt(dz/dx² + dz/dy²)) in degrees
    slope = np.arctan(np.sqrt(dx**2 + dy**2)) * (180.0 / np.pi)

    return slope


def compute_slope_from_neighbors(center_elev, neighbor_elevs, distance=1000.0):
    """
    Compute approximate slope from a center point and its neighbors.
    Useful when you only have point elevation data (not a raster).

    Args:
        center_elev: Elevation at center point (meters)
        neighbor_elevs: List of neighbor elevations (meters)
        distance: Approximate distance between points (meters)

    Returns:
        float: Average slope in degrees
    """
    if center_elev is None or not neighbor_elevs:
        return 0.0

    slopes = []
    for n_elev in neighbor_elevs:
        if n_elev is not None:
            dz = abs(center_elev - n_elev)
            slope_deg = np.degrees(np.arctan(dz / distance))
            slopes.append(slope_deg)

    return round(np.mean(slopes), 2) if slopes else 0.0


# ================================================================
# 3. NDVI (Normalized Difference Vegetation Index)
# ================================================================
def compute_ndvi(red_band, nir_band):
    """
    Compute NDVI from red and near-infrared bands.

    NDVI = (NIR - Red) / (NIR + Red)
    Range: -1 to 1 (vegetation: 0.2-0.8, water: <0, bare: 0-0.2)

    Args:
        red_band: numpy array of red band values (Sentinel-2 Band 4)
        nir_band: numpy array of NIR band values (Sentinel-2 Band 8)

    Returns:
        numpy array of NDVI values
    """
    red = np.array(red_band, dtype=float)
    nir = np.array(nir_band, dtype=float)

    # Avoid division by zero
    denominator = nir + red
    ndvi = np.where(denominator > 0, (nir - red) / denominator, 0.0)

    return np.clip(ndvi, -1.0, 1.0)


def get_ndvi_estimate(lat, lon):
    """
    Estimate NDVI based on location.

    NOTE: This is a simplified estimation based on Gujarat geography.
    For production, integrate Sentinel-2 data via Google Earth Engine.

    Gujarat NDVI patterns:
    - Kutch/desert regions (north-west): 0.05-0.15
    - Agricultural plains: 0.3-0.6 (monsoon), 0.1-0.3 (dry)
    - Forest (Gir, Saputara): 0.5-0.8
    - Coastal: 0.1-0.3
    - Urban: 0.05-0.2
    """
    import datetime
    month = datetime.datetime.now().month
    is_monsoon = month in [6, 7, 8, 9, 10]

    # Estimate based on geography
    if lat < 21.0:  # Southern Gujarat (more vegetation)
        base_ndvi = 0.45 if is_monsoon else 0.25
    elif lat > 23.5:  # Northern Gujarat (arid)
        base_ndvi = 0.20 if is_monsoon else 0.10
    elif lon < 70.5:  # Western Kutch (desert)
        base_ndvi = 0.12 if is_monsoon else 0.05
    else:  # Central Gujarat
        base_ndvi = 0.35 if is_monsoon else 0.18

    return round(base_ndvi, 3)


# ================================================================
# COMBINED: Get all geospatial features for a location
# ================================================================
def get_geospatial_features(lat, lon):
    """
    Extract all geospatial features for a single location.

    Returns:
        dict: {
            'elevation_m': float,
            'slope_deg': float,
            'ndvi': float,
            'terrain_class': str  ('flat', 'gentle', 'moderate', 'steep')
        }
    """
    # Get elevation
    elevation = get_elevation(lat, lon)
    if elevation is None:
        elevation = 0.0
        logger.warning(f"Using default elevation 0m for ({lat}, {lon})")

    # Estimate slope from small offsets
    delta = 0.01  # ~1km offset
    neighbors = []
    for dlat, dlon in [(delta, 0), (-delta, 0), (0, delta), (0, -delta)]:
        n_elev = get_elevation(lat + dlat, lon + dlon)
        if n_elev is not None:
            neighbors.append(n_elev)

    slope = compute_slope_from_neighbors(elevation, neighbors, distance=1100.0)

    # NDVI estimate
    ndvi = get_ndvi_estimate(lat, lon)

    # Terrain classification
    if slope < 2:
        terrain = "flat"
    elif slope < 5:
        terrain = "gentle"
    elif slope < 15:
        terrain = "moderate"
    else:
        terrain = "steep"

    return {
        "elevation_m": round(elevation, 1),
        "slope_deg": slope,
        "ndvi": ndvi,
        "terrain_class": terrain
    }


def get_geospatial_batch(cities_df):
    """
    Get geospatial features for all cities.

    Args:
        cities_df: DataFrame with 'city', 'lat', 'lon'

    Returns:
        DataFrame with geospatial features added
    """
    rows = []
    total = len(cities_df)

    logger.info(f"🌍 Extracting geospatial features for {total} locations...")

    for idx, row in cities_df.iterrows():
        city = row.get("city", f"Location_{idx}")
        lat = float(row["lat"])
        lon = float(row["lon"])

        try:
            features = get_geospatial_features(lat, lon)
            features["city"] = city
            features["lat"] = lat
            features["lon"] = lon
            rows.append(features)
            logger.info(f"  ✅ [{idx+1}/{total}] {city}: elev={features['elevation_m']}m, "
                       f"slope={features['slope_deg']}°, ndvi={features['ndvi']}")
        except Exception as e:
            logger.error(f"  ❌ [{idx+1}/{total}] {city}: {e}")
            rows.append({
                "city": city, "lat": lat, "lon": lon,
                "elevation_m": 0.0, "slope_deg": 0.0, "ndvi": 0.0,
                "terrain_class": "unknown"
            })

        # Rate limit
        time.sleep(0.5)

    return pd.DataFrame(rows)


# ----------------------
# STANDALONE TEST
# ----------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Test single location
    print("\n🌍 Testing geospatial features for Surat...")
    features = get_geospatial_features(21.21, 72.83)
    print(f"  Elevation: {features['elevation_m']}m")
    print(f"  Slope: {features['slope_deg']}°")
    print(f"  NDVI: {features['ndvi']}")
    print(f"  Terrain: {features['terrain_class']}")
