#!/bin/bash

# ==============================================================================
# 🐘 RAINWISE - Simulated stop-dfs.sh
# ==============================================================================

RED='\033[0;31m'
NC='\033[0m' 

echo -e "${RED}Stopping RAINWISE Distributed Cluster...${NC}"

if [ -f /tmp/rainwise_hdfs.pid ]; then
    HDFS_PID=$(cat /tmp/rainwise_hdfs.pid)
    
    echo -ne "Stopping namenodes on [localhost] (PID: $HDFS_PID)... "
    kill $HDFS_PID 2>/dev/null
    rm /tmp/rainwise_hdfs.pid
    echo -e "${RED}DONE${NC}"
else
    echo -e "No active RAINWISE HDFS process found."
fi

echo -ne "Stopping datanodes... "
sleep 0.5
echo -e "${RED}DONE${NC}"

echo -ne "Stopping secondary namenodes... "
sleep 0.5
echo -e "${RED}DONE${NC}"

echo -e "\n${RED}HDFS Cluster has been SHUT DOWN.${NC}"
