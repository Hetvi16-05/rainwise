#!/bin/bash

# ==============================================================================
# 🚀 RAINWISE - Real-Time Ingestion & Spark Processing Test (PRO VERSION)
# ==============================================================================

set -e  # ❗ Stop script if any command fails

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Real-Time Big Data Integration Test...${NC}"

# =========================
# ENV SETUP
# =========================
export SPARK_HOME=/Users/HetviSheth/spark
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$(pwd)
export PYSPARK_PYTHON=/Applications/miniconda3/bin/python

# =========================
# STEP 1: INGESTION
# =========================
echo -e "\n📡 Step 1: Triggering Real-time Ingestion..."

if /Applications/miniconda3/bin/python src/data_collection/build_dataset.py; then
    echo -e "${GREEN}✅ Ingestion Successful${NC}"
else
    echo -e "${RED}❌ Ingestion Failed${NC}"
    exit 1
fi

# =========================
# STEP 2: HDFS CHECK
# =========================
echo -e "\n📂 Step 2: Verifying HDFS..."

./jps.sh

if ./jps.sh | grep -q "NameNode" && ./jps.sh | grep -q "DataNode"; then
    echo -e "${GREEN}✅ HDFS Running${NC}"
else
    echo -e "${RED}⚠️ HDFS Not Running → Restarting...${NC}"
    ./start-dfs.sh
fi

echo -e "Listing hdfs://raw/realtime/:"
/Applications/miniconda3/bin/python -c "
from src.bigdata.hdfs_simulator import HDFSSimulator
HDFSSimulator.ls('hdfs://raw/realtime/')
"

# =========================
# STEP 3: SPARK PIPELINE
# =========================
echo -e "\n⚡ Step 3: Running PySpark Pipeline..."

if ./pyspark.sh; then
    echo -e "${GREEN}✅ Spark Processing Completed${NC}"
else
    echo -e "${RED}❌ Spark Failed${NC}"
    exit 1
fi

# =========================
# STEP 4: CHECK OUTPUT
# =========================
echo -e "\n🏁 Step 4: Checking Results..."

python3 -c "
from src.bigdata.hdfs_simulator import HDFSSimulator
HDFSSimulator.ls('hdfs://processed/realtime_predictions/')
"

echo -e "\n${GREEN}🎉 Pipeline Completed Successfully!${NC}"