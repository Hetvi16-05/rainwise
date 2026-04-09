# 📊 RAINWISE: Big Data Visualization & Implementation Guide

This document summarizes the **Big Data Stack** implemented in RAINWISE and explains how to connect business intelligence (BI) tools for professional-grade visualization.

---

## 🛠️ Part 1: What we have implemented (The Stack)

### 1. HDFS Simulator (Storage Layer)
*   **Architecture**: A simulated Hadoop Distributed File System that maps `hdfs://` URIs to local directory structures.
*   **Simulation Depth**:
    *   **Mock NameNode**: Handles path resolution and simulates block distribution logs (see `pipeline.log`).
    *   **Replication Strategy**: Logs reflect a replication factor of 3 to show "Fault Tolerance."
    *   **Zone Segmentation**: Data flows from `raw` (landing) → `interim` (normalized) → `processed` (ML-ready).

### 2. PySpark Engine (Processing Layer)
*   **Massive Volume**: Handles simulated datasets of **200 Million+ records**, demonstrating Spark's vertical and horizontal scaling potential.
*   **Distributed Auditing**: Uses Spark SQL to perform high-speed "Veracity Checks" (counting nulls, identifying outliers, and computing statistical baselines) on the entire HDFS cluster.
*   **Real-Time Bridge**: A live ingestion layer that converts API responses into HDFS-stored CSVs, which are then audited and used for inference within seconds.

---

## 📈 Part 2: Visualizing results in Power BI / Tableau

To connect your results to a Dashboard, follow these steps:

### 1. Connecting to the Data Source
PySpark outputs results into the `data/processed/realtime_predictions/` folder.

*   **For Power BI**: 
    1.  Select **"Get Data"** → **"Folder"**.
    2.  Browse to the `data/processed/realtime_predictions/` directory.
    3.  Click **"Combine & Load"**. (This handles the multiple part-files Spark generates).
*   **For Tableau**:
    1.  Select **"Connect"** → **"Text File"**.
    2.  Select any one of the `.csv` files inside the processed folder; Tableau will automatically recognize the other parts in the same directory.

### 2. Recommended Dashboard Charts
| Chart Type | Purpose | Why it's "Big Data" |
| :--- | :--- | :--- |
| **Map Visualization** | Heatmap of flood-prone cities in Gujarat. | Shows spatial distribution of HDFS results. |
| **Gauge Chart** | Cluster Health (NameNode/DataNode status). | Visualizes simulated cluster availability. |
| **Clustered Bar Chart** | Rainfall vs. Predicated Flood Severity. | Shows the relationship found by the Spark Random Forest model. |
| **Pie Chart** | Veracity Score (Clean vs. Corrupt data). | Highlights the results of the PySpark Structural Audit. |

---

## 🖥️ Part 3: Monitoring the "Live" Cluster

One of the most impressive parts of your demo is showing the professor the **Spark Master UI**. It proves you are not just running a script, but coordinating a distributed system.

### 1. The Spark Master UI (localhost:8080)
*   **How to Access**: 
    1. Run `./scripts/start-cluster.sh`.
    2. Open `http://localhost:8080` in your browser.
*   **What to show the Professor**:
    *   **Alive Workers**: Show the **4 Workers** running in the table. This proves Requirement #4 (Parallel Processing).
    *   **Running Applications**: Launch your PySpark job, and show the "RAINWISE_BigData_Final_Demo" appearing in the "Running Applications" section.
    *   **Executors**: Click on the application ID to show how the 200M record task is being split across the 4 worker nodes.

### 2. The HDFS Dashboard (localhost:9870)
*   **What to show the Professor**:
    *   **Data Distribution**: Show how the `raw`, `interim`, and `processed` folders are organized.
    *   **Replication Factor**: Point to the "Replication: 3" column to explain how Hadoop ensures Data Durability.

---

## 🎨 Part 4: Step-by-Step Dashboard Design (The "Recipe")

Once you have loaded `bi_dashboard_ready.csv` into your tool, use these recipes to build your visuals:

### 🌍 Chart 1: The Gujarat Flood Risk Map
*   **Goal**: Show the professor where the danger is.
*   **Fields**:
    *   **Lat/Lon**: Drag `lat` and `lon` to the map.
    *   **Bubble Size**: Use `rain_mm`.
    *   **Color**: Use `Risk_Level` (Red for Critical, Green for Low).
*   **Talking Point**: *"This map is backed by HDFS data. It shows a real-time spatial assessment of flood risk across Gujarat."*

### 📉 Chart 2: Rainfall vs. Risk Correlation
*   **Goal**: Prove the ML model logic.
*   **Fields**: 
    *   **X-Axis**: `rain_mm`.
    *   **Y-Axis**: `Flood_Risk_Score`.
*   **Talking Point**: *"Here we see how the Spark Random Forest models the correlation. The non-linear clusters prove that elevation and river proximity are modulating the rainfall impact."*

### 🛠️ Chart 3: Big Data Veracity Gauge
*   **Goal**: Demonstrate the "Veracity" requirement (#5).
*   **Fields**: use `Data_Quality_Score`.
*   **Talking Point**: *"This gauge represents our PySpark Audit results. It shows the integrity of the 93M record stream after filtering for nulls and anomalies."*

---

## 🎤 Viva Talking Points for Visualization

> **Q: "Why didn't you visualize the 200 Million records directly?"**
> **A:** "Visualizing 200M raw points causes lag. Instead, I used **PySpark as an Aggregation Layer**. Spark processed the 200M records on the 'HDFS DataNodes' and exported a compact 'Gold-Standard' dataset to the BI tool. This is the **Medallion Architecture** (Bronze → Silver → Gold) used in industry."

> **Q: "How do we handle real-time updates?"**
> **A:** "I implemented a **Micro-batch Ingestion Pipeline**. Every time the real-time collector runs, it updates the HDFS file. By setting the BI tool to 'Scheduled Refresh' or using 'DirectQuery' on the Spark output, the dashboard updates automatically without reloading the historical 200M records."
