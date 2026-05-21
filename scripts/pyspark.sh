#!/bin/bash

# ==============================================================================
# 🐘 RAINWISE - Simulated pyspark.sh
# ==============================================================================

BLUE='\033[0;34m'
NC='\033[0m' 

echo -e "${BLUE}Welcome to RAINWISE Spark-Shell Simulator (PySpark 3.x)${NC}"
export SPARK_HOME=/Users/HetviSheth/spark
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$(pwd)
export PYSPARK_PYTHON=/Applications/miniconda3/bin/python

/Applications/miniconda3/bin/python src/bigdata/spark_pipeline.py
