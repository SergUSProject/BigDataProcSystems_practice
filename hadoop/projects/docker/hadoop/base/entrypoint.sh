#!/bin/bash

# NOTE: This entrypoint script will be replace later for 
# master and worker images

# Create pivate and public keys
mkdir .ssh
ssh-keygen -t rsa -b 4096 -f .ssh/id_rsa -P ""
chmod 400 .ssh/id_rsa

# Format Namenode
hdfs namenode -format -force

# Start SSH Service
if [ -n "$1" ] && [ $1 == "alpine" ]; then
    echo "Start SSH on Alpine"
    sudo /usr/sbin/sshd -D &
else
    echo "Start SSH"
    sudo service ssh start
fi

# Start namenode and datanode
echo "Start namenode"
hdfs --daemon start namenode
echo "Start datanode"
hdfs --daemon start datanode

echo "The entrypoint script is completed"

tail -f /dev/null