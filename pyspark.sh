#!/bin/bash

# ==============================================================================
# 🐘 RAINWISE - Simulated pyspark.sh
# ==============================================================================

BLUE='\033[0;34m'
NC='\033[0m' 

echo -e "${BLUE}Welcome to RAINWISE Spark-Shell Simulator (PySpark 3.x)${NC}"
echo -e "Using Python 3.x and Spark SQL optimized for Flood Prediction.\n"

python3 src/bigdata/spark_pipeline.py
