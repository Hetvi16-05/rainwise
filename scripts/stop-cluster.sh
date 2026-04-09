#!/bin/bash

# ==============================================================================
# 🦁 RAINWISE - Cluster Shutdown
# ==============================================================================

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' 

export SPARK_HOME=/Users/HetviSheth/spark

echo -e "${RED}Shutting down RAINWISE Simulated Cluster...${NC}"

# 1. Stop Spark Workers
echo -e "\n🐝 [SPARK] Stopping all Workers..."
$SPARK_HOME/sbin/stop-workers.sh

# 2. Stop Spark Master
echo -e "\n👑 [SPARK] Stopping Master Node..."
$SPARK_HOME/sbin/stop-master.sh

# 3. Stop HDFS Simulator
echo -e "\n📂 [HDFS] Stopping Cluster Storage..."
./stop-dfs.sh

echo -e "\n${BLUE}✅ All nodes shut down successfully.${NC}"
