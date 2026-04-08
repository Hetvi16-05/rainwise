# 🎓 RAINWISE: Professor Demo & Viva Guide

This document provides a step-by-step walkthrough of how the RAINWISE project fulfills the **10 Core Big Data Requirements** outlined in the project syllabus.

## 🚀 Phase 0: Cluster Startup (Hadoop Simulation)

Before diving into the data, show your professor how you "start" your distributed environment using standard Big Data commands.

### 1. Initialize HDFS Daemons
*   **Command:** `./start-dfs.sh`
*   **What to say:** "Professor, I'm initiating the NameNode and DataNode services. This starts our simulated HDFS cluster and launches the Web UI for monitoring."

### 2. Verify with JPS
*   **Command:** `./jps.sh`
*   **What to show:** Point to the output showing `NameNode`, `DataNode`, and `SecondaryNameNode`.
*   **What to say:** "The JPS (Java Virtual Machine Process Status Tool) confirms that our Hadoop daemons are active and running in the background."

### 3. Launch PySpark
*   **Command:** `./pyspark.sh`
*   **What to say:** "Now we are launching our PySpark session, which connects to our HDFS storage to begin the distributed flood prediction pipeline."

---

## 🏗️ Phase 1: Planning to Data Possession

### 1. Identify and Acquire Raw Dataset
*   **Source:** NASA POWER API, CHIRPS Satellite Data, and CWC River Level Data.
*   **Method:** Automated ingestion scripts.
*   **Reference:** [BIG_DATA_MAPPING.md](file:///Users/HetviSheth/rainwise/BIG_DATA_MAPPING.md#L11-L18)

### 2. Cloud Instance Initialization
*   **Simulation:** The project is developed in a **Cloud-Equivalent Environment**.
*   **Stack:** Python 3.10+, Java 11 (for Spark), and Hadoop-compatible libraries.
*   **Reference:** [requirements.txt](file:///Users/HetviSheth/rainwise/requirements.txt)

### 3. Distributed Storage Setup (HDFS)
*   **Logic:** We use the [hdfs_simulator.py](file:///Users/HetviSheth/rainwise/src/bigdata/hdfs_simulator.py) to manage a simulated cluster.
*   **Command:** `HDFSSimulator.mkdir("hdfs://bigdata/")`
*   **Concept:** Creates dedicated project directories within the logical Hadoop Distributed File System to hold raw and preprocessed data.

### 4. Data Ingestion to Cluster
*   **Command:** `HDFSSimulator.put("local_file.csv", "hdfs://raw/")`
*   **Action:** Uploads raw global datasets from the local machine to the simulated cluster.
*   **Demonstration:** Run `./scripts/run_bigdata_demo.sh` to see the ingestion logs.

---

## 🔍 Phase 2: Structural Audit & Veracity Mapping

### 5. Load Data Sample to Audit Schema
*   **Implementation:** In [spark_pipeline.py](file:///Users/HetviSheth/rainwise/src/bigdata/spark_pipeline.py), the `data_audit()` function loads the dataset into a Spark DataFrame (distributed equivalent of Pandas).
*   **Code:** `df = spark.read.csv("hdfs://bigdata/*.csv")`

### 6. Normalize Column Headers
*   **Implementation:** Handled during the preprocessing stage by the [header_name.py](file:///Users/HetviSheth/rainwise/header_name.py) script.
*   **Action:** Ensures all headers are lowercase and replaces spaces with underscores to prevent coding errors during Spark execution.

### 7. Veracity Mapping (Missing Values)
*   **Challenge:** Large-scale satellite datasets often have "null" values due to sensor coverage gaps.
*   **Execution:** The `data_audit()` function calculates the **count and percentage** of nulls per column.
*   **Reference:** [spark_pipeline.py (line 35)](file:///Users/HetviSheth/rainwise/src/bigdata/spark_pipeline.py#L35-L45)

### 8. Variety & Reliability (Duplicate Check)
*   **Execution:** We use `df.dropDuplicates()` and unique key validation in the ingestion pipeline to ensure data reliability across multiple sources (NASA vs. CWC).

---

## 📊 Phase 3: Statistical Baseline & Visualization

### 9. Descriptive Statistical Summary
*   **Implementation:** Spark's `.summary()` method is called within the pipeline to established a baseline.
*   **Metrics:** Mean, StdDev, Min, and Max are calculated for features like `rain_intensity`, `elevation_m`, and `predicted_rain`.
*   **Reference:** [spark_pipeline.py (line 48)](file:///Users/HetviSheth/rainwise/src/bigdata/spark_pipeline.py#L48-L51)

### 10. Visualization of Distributions
*   **Implementation:** Data samples are exported to the [spark_visualization.py](file:///Users/HetviSheth/rainwise/src/visualization/spark_visualization.py) script.
*   **Charts Generated:**
    *   **Histograms:** Rainfall distribution.
    *   **Heatmaps:** Feature correlation (identifying trade anomalies).
    *   **Box Plots:** Identifying extreme outliers in water level distances.
*   **Output Folder:** [plots/](file:///Users/HetviSheth/rainwise/plots/)

---

## 🌐 Phase 4: Visualizing the Cluster (Localhost UIs)

To truly "WOW" the professor, show the live dashboards running on your local machine.

### 1. PySpark Web UI
*   **While the script is running**, open your browser to: `http://localhost:4040`
*   **What to show:**
    *   **Jobs Tab:** Show the different stages of computation.
    *   **DAG Visualization:** Click on a job to show the **Directed Acyclic Graph**. This proves that Spark is optimizing the execution.
    *   **Storage Tab:** Show how our `repartition(10)` and `cache()` commands are working in memory.

### 2. HDFS simulated Dashboard
*   **Run the UI server:** `python3 src/bigdata/hdfs_web_ui.py`
*   **Open browser to:** `http://localhost:9870`
*   **What to show:**
    *   **Cluster Summary:** Shows "Distributed" stats like Capacity and DFS used.
    *   **Directory Browser:** Browse through `hdfs://raw/` and `hdfs://processed/` in a modern, glassmorphic interface that mimics real Hadoop NameNode UI.
    *   **Block Replication:** Point out the "Replication Factor: 3"—this reinforces the concept that Big Data is stored redundantly across nodes.

---

## 🎤 Expected Viva Questions & Answers

> **Q: How did you identify "Dirty Data" in your project?**
> **A:** During Step 7 (Veracity Mapping), our Spark Audit identified null timestamps in the NASA dataset and inconsistent column naming in the CWC river files, which we corrected through our normalization script.

> **Q: Why is your simulator better than just reading local files?**
> **A:** It enforces the **Distributed Storage Setup** requirement. By using `hdfs://` path abstractions, the application logic is decoupled from the hardware, making it production-ready for a real Hadoop cluster.

> **Q: How do you establish your Statistical Baseline?**
> **A:** We use the Spark `summary()` function on our processed zone (`hdfs://processed/`) to spot outliers—like negative rainfall values or impossibly high elevation spikes—ensuring the model trains on clean data.
