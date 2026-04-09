# 🤝 Multi-Node Cluster Setup: Team "RAINWISE" Edition

This guide explains how to connect your MacBook (Master) and your two friends' laptops (Slaves) to form a real, high-performance distributed cluster.

---

## 📋 Phase 1: Prerequisites (Do this FIRST)

1.  **Unity of Network**: All 3 laptops must be connected to the **same Wi-Fi network**.
2.  **Unity of Software**: All 3 laptops must have the same versions of:
    *   **Java 11** (OpenJDK)
    *   **Spark 3.x**
    *   **Python 3.x**
3.  **Unity of Paths**: Ensure the `rainwise` project folder is in the **exact same location** on all 3 laptops (e.g., `/Users/Username/rainwise`). This is vital so the workers can find the scripts.

---

## 👑 Phase 2: Configuration for YOU (The Master)

### 1. Find your Network IP
Open your terminal and run:
```bash
ipconfig getifaddr en0
```
*Note: Let's assume your IP is **192.168.1.15** for this guide.*

### 2. Start the Master Node
Navigate to your Spark folder and run:
```bash
./sbin/start-master.sh -h 192.168.1.15
```

### 3. Open the Brain (Web UI)
Open **http://192.168.1.15:8080** in your browser. You should see different sections. Currently, "Alive Workers" will be **0**.

---

## 🐝 Phase 3: Configuration for your FRIENDS (The Slaves)

### 1. Give them the "Secret Key"
Tell your friends your Master IP and the Spark port: `spark://192.168.1.15:7077`.

### 2. Connect the Workers
Each friend must open their terminal, navigate to their Spark folder, and run:
```bash
./sbin/start-worker.sh spark://192.168.1.15:7077
```

### 3. Verify Connection
Refresh your browser at **http://192.168.1.15:8080**. You should now see **2 Alive Workers** in the table!

---

## 📂 Phase 4: Big Data Sharing Strategy (Crucial)

In a real cluster, data is stored in **HDFS** across all machines. For your demo:
1.  **Option A (Recommended)**: Copy the `data/` folder to each of your friends' laptops at the same location.
2.  **Option B (Pro)**: Use a **Shared Network Folder**. If your friends can access your laptop's `data/` folder via SMB/Network share, Spark can read from it directly.

---

## 🚀 Phase 5: Running the Viva Demo

Now that the cluster is physically connected across 3 laptops:

1.  **Update `spark_pipeline.py`**:
    In your `src/bigdata/spark_pipeline.py`, ensure the master is set to your IP:
    ```python
    .master("spark://192.168.1.15:7077")
    ```

2.  **Run the Job**:
    Run `./pyspark.sh` on **your laptop only**. 

3.  **Watch the Parallelism**:
    Open the Spark UI on the projector. Show the professor how the tasks are being distributed among **3 laptops**. When one laptop finishes its task, the other laptop picks up the next one!

---

> [!IMPORTANT]
> **Firewall Tip:** If your friends cannot connect, you may need to **turn off your firewall** temporarily (System Settings → Network → Firewall) so they can "talk" to your Master node via port 7077.
