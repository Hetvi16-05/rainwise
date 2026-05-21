#!/bin/bash

# ==============================================================================
# 🐘 RAINWISE - Simulated start-dfs.sh
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' 

echo -e "${BLUE}Starting RAINWISE Distributed Cluster...${NC}"

# 1. Start NameNode (Mock HDFS UI)
echo -ne "Starting namenodes on [localhost]... "
python3 src/bigdata/hdfs_web_ui.py > /tmp/hdfs_web_ui.log 2>&1 &
HDFS_PID=$!
echo $HDFS_PID > /tmp/rainwise_hdfs.pid
echo -e "${GREEN}DONE${NC}"

# 2. Simulate other nodes
echo -ne "Starting datanodes... "
sleep 1
echo -e "${GREEN}DONE${NC}"

echo -ne "Starting secondary namenodes [localhost]... "
sleep 0.5
echo -e "${GREEN}DONE${NC}"

echo -e "\n${GREEN}HDFS Cluster is now LIVE.${NC}"
echo -e "📖 Browse HDFS UI at: ${BLUE}http://localhost:9870${NC}"
echo -e "🔍 Use ${BLUE}./jps.sh${NC} to view running daemons."
