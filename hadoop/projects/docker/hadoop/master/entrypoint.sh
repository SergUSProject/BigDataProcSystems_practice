#!/bin/bash

echo "Start SSH service"
sudo service ssh start

echo "Start Hadoop daemons"
hdfs --daemon start namenode
hdfs --daemon start secondarynamenode
yarn --daemon start resourcemanager
mapred --daemon start historyserver

if [ -d "$HOME/data" ]; then
    # Wait for binding datanodes
    sleep 5
    echo "Copy files to HDFS"
    hdfs dfs -copyFromLocal /home/bigdata/data /
fi

echo "The entrypoint script is completed"

tail -f /dev/null