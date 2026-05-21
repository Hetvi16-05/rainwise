# 🌧️ RAINWISE — Real-Time Urban Flood Risk Intelligence System

> A Big Data-powered flood monitoring and prediction platform for Gujarat, India — integrating real-time sensor streams, NASA satellite rainfall data, and deep learning models for urban flood risk assessment.

---

## 📌 Project Overview

**RAINWISE** is a full-stack Big Data application designed to predict and monitor urban flood risk across Gujarat. It ingests multi-source real-time data (rainfall, weather, river discharge), processes it through an Apache Spark + HDFS pipeline, stores enriched city summaries in MongoDB, and serves predictions via an interactive Streamlit dashboard.

The system is built around the hypothesis that **combining geospatial features, real-time sensor data, and temporal deep learning** can produce significantly more accurate flood risk forecasts than traditional single-source models.

---

## 🏗️ Architecture

```
Real-Time Sources                Big Data Layer              ML/DL Layer
─────────────────                ──────────────              ───────────
NASA GPM / CHIRPS ──┐            ┌─────────────┐            ┌──────────────────┐
OpenWeatherMap API ─┼──► HDFS ──►│ Apache Spark│──► Models ►│ XGBoost / LogReg │
CWC River Gauges ───┘   (Raw)    │  Pipeline   │            │ TabTransformer   │
                                 └─────────────┘            │ TFT / DNN        │
                                        │                   └──────────────────┘
                                        ▼                           │
                                   MongoDB Atlas                    │
                                  (city_summaries)                  │
                                        │                           │
                                        └───────────► Streamlit Dashboard
```

---

## 📁 Project Structure

```
rainwise/
├── apps/                   # Streamlit dashboard entry points
│   ├── final_app.py        # Main production dashboard
│   ├── viva_realtime_dashboard.py  # Live demo dashboard
│   ├── app.py / app_demo.py        # Alternate app versions
│   └── dL_demoapp.py       # DL-only demo app
│
├── src/                    # Core source modules
│   ├── data_collection/    # Real-time API fetchers (rainfall, weather, river)
│   ├── ingestion/          # HDFS ingestion scripts
│   ├── preprocessing/      # CHIRPS, elevation, watershed processing
│   ├── feature_engineering/# Feature creation and merging
│   ├── model_training/     # ML model training (XGBoost, LogReg, SVM)
│   ├── bigdata/            # Spark pipeline and HDFS reader
│   ├── gis/                # GIS feature extraction (slope, elevation, rivers)
│   ├── utils/              # Config, helpers, simulation, realtime data
│   └── visualization/      # EDA plots, Spark viz, report generation
│
├── pipeline/               # Pipeline orchestration scripts
│   ├── command_center.py   # Master pipeline controller
│   ├── mongo_enrich_and_launch.py  # MongoDB enrichment + app launcher
│   ├── dL_pipeline_combined.py     # Combined DL training pipeline
│   └── update_mongo.py     # MongoDB city summary updater
│
├── model_trainingDL/       # Deep Learning model training scripts
│   ├── tft_model.py        # Temporal Fusion Transformer
│   └── ...
│
├── DLmodels/               # Saved DL model weights (.pth) and scalers (.pkl)
├── models/                 # Saved ML model artifacts
│
├── scripts/                # Shell scripts for Hadoop / pipeline management
│   ├── start-dfs.sh / stop-dfs.sh
│   ├── run_pipeline.sh
│   └── start_viva_demo.sh
│
├── bigdata_demo/           # HDFS root simulation (local demo data)
├── data/                   # Reference datasets (river distances, elevation, etc.)
├── visualizations/         # Generated EDA plots and Tableau workbooks
├── docs/                   # Project documentation and thesis write-ups
├── utils/                  # One-off utility scripts
├── logs/                   # Runtime logs (gitignored)
│
├── requirements.txt
└── .gitignore
```

---

## 🤖 Models

### Machine Learning
| Model | Task | Notes |
|---|---|---|
| **XGBoost** | Flood risk classification | Best ML accuracy; handles missing data natively |
| **Logistic Regression** | Flood risk classification | Baseline; interpretable coefficients |
| **SVM** | Flood risk classification | Used for comparison in model benchmarking |

### Deep Learning
| Model | Task | Notes |
|---|---|---|
| **DNN** | Flood risk + rainfall regression | Tabular baseline DL model |
| **TabTransformer** | Flood risk classification | Transformer attention over categorical features |
| **TFT** (Temporal Fusion Transformer) | Temporal rainfall forecasting | Multi-horizon; handles static + temporal covariates |

---

## 📡 Data Sources

| Source | Type | Features |
|---|---|---|
| NASA GPM / CHIRPS | Satellite rainfall | Historical + near-realtime precipitation |
| OpenWeatherMap API | REST | Temperature, humidity, wind speed |
| CWC River Gauges | API / scrape | River discharge levels |
| SRTM DEM | GeoTIFF | Elevation and slope |
| OpenStreetMap | OSMnx | River density, proximity |
| Census / WorldPop | Static | Population density per city |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Apache Hadoop 3.x (for HDFS)
- Apache Spark 3.x
- MongoDB (local or Atlas)

### Install dependencies
```bash
pip install -r requirements.txt
```

### Start Hadoop HDFS
```bash
bash scripts/start-dfs.sh
```

### Run the real-time data pipeline
```bash
python pipeline/command_center.py
```

### Launch the dashboard
```bash
streamlit run apps/final_app.py
```

### Quick viva demo (pipeline + dashboard in one)
```bash
bash scripts/start_viva_demo.sh
```

---

## 🗄️ MongoDB Collections

| Collection | Contents |
|---|---|
| `city_summaries` | Per-city flood risk scores, rainfall, elevation, demographics |
| `realtime_readings` | Live sensor ingestion logs |

---

## 📊 Key Features

- **Real-time ingestion** — rainfall, weather, and river data fetched every cycle
- **Big Data pipeline** — HDFS storage → Spark batch processing → feature enrichment
- **Multi-model prediction** — ML + DL ensemble with model comparison
- **Interactive dashboard** — Streamlit app with city-level flood risk maps
- **Temporal forecasting** — TFT model for multi-day ahead rainfall prediction
- **GIS integration** — Elevation, slope, river proximity as model features

---

## 👩‍💻 Author

**Hetvi Sheth**  
B.Tech — Big Data Analytics  
Project: RAINWISE — Urban Flood Risk Intelligence for Gujarat

---

## 📄 License

This project is for academic purposes. All rights reserved.
