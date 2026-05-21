# 📋 RAINWISE: Project Rubric Mapping Guide

This guide maps the specific requirements from your project rubric screenshots to the actual features and code in the RAINWISE platform. Use this "Cheat Sheet" to answer 'Sir' when he asks for specific features.

---

## 🏛️ 1. Project Abstract & Objectives
| Rubric Objective | Evidence in RAINWISE | File / Location Reference |
| :--- | :--- | :--- |
| **Collect large-scale data** | NASA/CHIRPS historical data & CWC river logs. | `data/raw/` & `src/data_collection/` |
| **Predict flood impact risk** | XGBoost Classification for flood probability. | `models/flood_model.pkl` |
| **Scalable Big Data Tech** | HDFS simulation & Hadoop-style 10-step pipeline. | `bigdata_demo/` folder |
| **Visual analytics/Alerts** | Triple-Streamlit suite with live SMS-style JSON alerts. | `final_app.py`, `app.py` |

---

## 🏗️ 2. Big Data Mastery
| Rubric Feature | Implementation Detail | Reference |
| :--- | :--- | :--- |
| **Hadoop / Distributed** | Simulated HDFS storage environment mapping local paths. | `src/bigdata/hdfs_simulator.py` |
| **The 5 V's** | Explicitly documented technical breakdown of 5 V's. | `RAINWISE_MASTER_THESIS.md` |
| **Veracity (Data Cleaning)**| Multi-stage pipeline checking coordinates and data noise. | `bigdata_demo/analysis_pipeline.py` |

---

## 🤖 3. Artifical Intelligence (AI) Suite
| Rubric Feature | Implementation Detail | Reference |
| :--- | :--- | :--- |
| **Supervised ML** | XGBoost used for Rainfall (91% R²) and Flood (97% Acc). | `src/model_training/` |
| **Feature Engineering** | Calculating **Lags**, **Elevation**, and **Drainage Factors**. | `src/utils/features.py` |
| **NLP (Citizen Feedback)**| NLP topic modeling on social media complaints for drainage. | `final_app.py` -> "Integrated Drainage Monitoring" |
| **Explainable AI (XAI)** | Live "Stress Test" logic and Feature Importance graphs. | `app_demo.py` -> "Drainage Stress Test Analysis" |

---

## 📊 4. Visualization & Outcomes
| Rubric Requirement | Implementation Detail | Reference |
| :--- | :--- | :--- |
| **Flood Risk Maps** | Interactive city-wide and district-wide risk maps. | `final_app.py` Map Section |
| **Street-wise / Area-wise**| Simulated "Complaint Density" heatmap. | `final_app.py` IDM Tab |
| **Early Warning Charts** | Correlation charts for Rainfall vs. Infrastructure Stress. | `final_app.py` Real-Time Stress Chart |

---

## 💡 Pro-Tip for your Presentation:
If Sir asks: **"Where is the NLP part?"**
> **Answer:** "Sir, in the **Final Intelligence Dashboard (`final_app.py`)**, we have a dedicated **Urban Insights** module. It uses NLP to analyze social media and hotline complaints, identifying blocked drainage points which we then feed into our infrastructure risk score."

If Sir asks: **"Show me the Big Data side."**
> **Answer:** "Sir, every prediction in this system is bridged via an **HDFS Simulator**. We have a 10-step data audit pipeline that ensures data **Veracity**—cleaning noise from satellite sensors before it reaches the AI models."
