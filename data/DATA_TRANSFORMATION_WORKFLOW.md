# 🔄 Data Transformation Workflow: From Raw to Processed

This document provides a technical mapping of how **Raw Data** is transformed into the high-intelligence **Processed Data** files used by the RAINWISE models.

---

## 🏗️ 1. Geospatial & Static Transformations
These files provide the "Topographic Context" for flood prediction and are generated from static GIS layers.

| Processed File | Raw Source(s) | Transformation Script | Logic |
| :--- | :--- | :--- | :--- |
| **`gujarat_elevation.csv`** | `data/raw/elevation/*.tif` | `extract_elevation.py` | Maps lat/lon to height using GeoTIFF raster sampling. |
| **`gujarat_slope.csv`** | `data/raw/elevation/*.tif` | `extract_slope.py` | Calculates terrain gradient (steepness) via `rasterio`. |
| **`gujarat_river_distance.csv`** | `data/raw/static/hydrology/` | `compute_river_distance.py`| Euclidean distance calculation from each grid point to nearest river. |
| **`gujarat_landcover.csv`** | OSM Landuse Layers | `extract_landuse.py` | Categorizes soil permeability (Urban vs Agriculture). |

---

## 🌧️ 2. Meteorological & Time-Series Transformations
These files transform raw API pulses and satellite archives into organized weather histories.

| Processed File | Raw Source(s) | Transformation Script | Logic |
| :--- | :--- | :--- | :--- |
| **`nasa_rainfall_gujarat.csv`**| NASA POWER API Logs | `filter_gujarat.py` | Cleans timestamps and filters to Gujarat bounding box. |
| **`gujarat_rainfall_history.csv`**| CHIRPS Daily TIFs | `build_rainfall_history.py`| Aggregates global satellite pixels into regional CSV records. |
| **`state_daily_features.csv`** | CHIRPS / NASA | `build_state_daily.py` | Calculates district-level daily rainfall averages. |

---

## 🧠 3. Model-Ready & Training Transformations
These are the "Synthesized" files that combine multiple sources into a single row for the machine learning models.

| Processed File | Input Source(s) | Transformation Logic |
| :--- | :--- | :--- |
| **`training_dataset_gujarat_advanced_labeled.csv`** | Elevation + River Dist + NASA Rain + CWC Labels | **The Master Training Set.** Includes the essential **Lag Features** (`rain3_mm`, `rain7_mm`) to provide the model with "soil memory." |
| **`realtime_dataset.csv`** | Real-time Weather + Satellite + River Logs | **Live Inference Set.** Created by `build_dataset.py`. It bridges the "Latest Pulse" to the HDFS simulator for immediate prediction. |
| **`bi_dashboard_ready.csv`** | `realtime_dataset.csv` | Formats data for specialized PowerBI/Streamlit visualization widgets. |

---

## 🛠️ The "Secret Sauce": Feature Engineering
Every file in the `data/processed/` directory is standardized through a shared **Cleaning Protocol**:
1.  **Normalization:** Columns are converted to lowercase snake_case.
2.  **Imputation:** Missing elevation is set to a median (50m) and missing distance to a safe distance (50km).
3.  **Deduplication:** Coordinate pairs are checked for uniqueness via `drop_duplicates(subset=['lat', 'lon'])`.

This structured workflow ensures that whether we are training an **XGBoost** model or a **Deep Learning DNN**, the input data is of the highest possible **Veracity**.
