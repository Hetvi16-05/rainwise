#!/bin/bash

# ==============================================================================
# 🦁 RAINWISE - Full Cluster Simulation (HDFS + Spark Master + 4 Workers)
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' 

export SPARK_HOME=/Users/HetviSheth/spark
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$(pwd)

echo -e "${BLUE}Starting RAINWISE Simulated Big Data Cluster...${NC}"

# 1. Start HDFS Simulator (Namenode/Datanode Simulation)
echo -e "\n📂 [HDFS] Starting Simulated Cluster Storage..."
./start-dfs.sh

# 2. Start Spark Master
echo -e "\n👑 [SPARK] Starting Master Node..."
$SPARK_HOME/sbin/start-master.sh
sleep 5
echo -e "${GREEN}✅ Spark Master started at spark://$(hostname):7077${NC}"
echo -e "🔗 Master UI: http://localhost:8080"

# 3. Start Spark Workers (Distributed Simulation)
echo -e "\n🐝 [SPARK] Starting 4 Distributed Workers..."
for i in {1..4}
do
    echo -e "  - Initializing Worker #$i..."
    $SPARK_HOME/sbin/start-worker.sh spark://$(hostname):7077
done

echo -e "\n${GREEN}🎉 Full Cluster Simulation is ACTIVE!${NC}"
echo -e "--------------------------------------------------------"
echo -e "🐘 HDFS UI:   http://localhost:9870"
echo -e "👑 Spark UI:  http://localhost:8080"
echo -e "--------------------------------------------------------"
echo -e "Use 'scripts/stop-cluster.sh' to shutdown all nodes."
