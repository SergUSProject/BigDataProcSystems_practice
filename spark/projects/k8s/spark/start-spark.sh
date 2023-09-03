#!/bin/bash

case "$1" in
    master)
        echo "MASTER"
        exec tini -s -- /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master --host $HOSTNAME --port 7077 --webui-port 8080
        ;;
    worker)
        echo "WORKER"
        MASTER_IP_ADDRESSES=( $( nslookup $MASTER_IP_RESOLVER | awk '/^Address / { print $3 }') )
        if [ ${#MASTER_IP_ADDRESSES[@]} ] && [ -n ${MASTER_IP_ADDRESSES[0]} ]; 
        then
            echo ${MASTER_IP_ADDRESSES[0]} $MASTER_HOSTNAME >> /etc/hosts
            exec tini -s -- /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://$MASTER_HOSTNAME:7077 --webui-port 8081
        else
            echo "Master IP was not found" 1>&2
            exit 1
        fi
        ;;
    *)
        echo $"Usage: $0 {master|worker}" 1>&2
        exit 1
esac

#tail -f /dev/null
