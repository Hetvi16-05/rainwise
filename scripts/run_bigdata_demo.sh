#!/bin/bash

# ==============================================================================
# 🎯 RAINWISE BIG DATA DEMO
# ==============================================================================
# This script demonstrates the full Big Data flow using the HDFS Simulator
# and the enhanced PySpark pipeline.
# ==============================================================================

# 1. SETUP COLORS
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🚀 RAINWISE BIG DATA DEMONSTRATION${NC}"
echo -e "${BLUE}================================================================${NC}"

# 2. HDFS INITIALIZATION
echo -e "\n${YELLOW}🏗️ Step 1: Initializing HDFS Structure...${NC}"
python3 -c "from src.bigdata.hdfs_simulator import HDFSSimulator; HDFSSimulator.mkdir('hdfs://bigdata/')"
python3 -c "from src.bigdata.hdfs_simulator import HDFSSimulator; HDFSSimulator.mkdir('hdfs://processed/spark_output/')"

# 3. DATA EXPANSION (Big Data Generation)
echo -e "\n${YELLOW}📊 Step 2: Generating Simulated Big Data (Duplication & Perturbation)...${NC}"
python3 src/bigdata/expand_bigdata.py

# 4. DATA INGESTION INTO HDFS
echo -e "\n${YELLOW}📥 Step 3: Ingesting Data into HDFS Raw Zone...${NC}"
# In current setup, expand_bigdata.py writes directly to data/bigdata/
# We simulate a move/put operation
python3 -c "from src.bigdata.hdfs_simulator import HDFSSimulator; HDFSSimulator.ls('hdfs://bigdata/')"

# 5. RUN SPARK PIPELINE
echo -e "\n${YELLOW}⚡ Step 4: Running Enhanced PySpark Pipeline...${NC}"
python3 src/bigdata/spark_pipeline.py

# 6. RESULTS VERIFICATION
echo -e "\n${YELLOW}🔍 Step 5: Verifying HDFS Output...${NC}"
python3 -c "from src.bigdata.hdfs_simulator import HDFSSimulator; HDFSSimulator.ls('hdfs://processed/')"

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ BIG DATA DEMO COMPLETE${NC}"
echo -e "${GREEN}================================================================${NC}"
