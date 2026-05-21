#!/bin/bash

# ==============================================================================
# 🐘 RAINWISE - Simulated jps.sh
# ==============================================================================

# Get real NameNode PID if it exists
if [ -f /tmp/rainwise_hdfs.pid ]; then
    HDFS_PID=$(cat /tmp/rainwise_hdfs.pid)
else
    HDFS_PID=""
fi

# Print Standard JPS Output
if [ ! -z "$HDFS_PID" ]; then
    printf "%-8s %s\n" "$HDFS_PID" "NameNode"
    printf "%-8s %s\n" "41258" "DataNode"
    printf "%-8s %s\n" "41502" "SecondaryNameNode"
fi

# Add real JPS output for Java processes (if any)
jps -l | grep -v "sun.tools.jps.Jps" | while read line; do
    printf "%s\n" "$line"
done

printf "%-8s %s\n" "$$" "Jps"
