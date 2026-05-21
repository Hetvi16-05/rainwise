#!/usr/bin/env python3
import sys
import os
from src.bigdata.hdfs_simulator import HDFSSimulator

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "dfs":
        print("Usage: ./hdfs.sh dfs -<cmd> [args]")
        print("Supported cmds: -ls, -mkdir, -put, -get, -rm")
        return

    cmd = sys.argv[2]
    args = sys.argv[3:]

    if cmd == "-ls":
        if not args:
            HDFSSimulator.ls("hdfs://")
        else:
            HDFSSimulator.ls(args[0])
    
    elif cmd == "-mkdir":
        if not args:
            print("Error: -mkdir requires a path")
        else:
            HDFSSimulator.mkdir(args[0])
            
    elif cmd == "-put":
        if len(args) < 2:
            print("Usage: ./hdfs.sh dfs -put <local_src> <hdfs_dest>")
        else:
            HDFSSimulator.put(args[0], args[1])
            
    elif cmd == "-get":
        if len(args) < 2:
            print("Usage: ./hdfs.sh dfs -get <hdfs_src> <local_dest>")
        else:
            HDFSSimulator.get(args[0], args[1])
            
    elif cmd == "-rm":
        if not args:
            print("Error: -rm requires a path")
        else:
            HDFSSimulator.rm(args[0])
            
    else:
        print(f"Error: Unknown HDFS command {cmd}")

if __name__ == "__main__":
    main()
