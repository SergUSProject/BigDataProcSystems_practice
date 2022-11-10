# -*- coding: utf-8 -*-

import os

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext


# Application name
APP_NAME = "WordCountStateful"

# Batch interval (10 seconds)
BATCH_INTERVAL = 10

# Source of stream
STREAM_HOST = "localhost"
STREAM_PORT = 9999

# Checkpoint directory
# Note: For HDFS it's equal to /user/<YOUR_USER>/tmp_spark_streaming
CHECKPOINT_DIR = "tmp_spark_streaming"

# Control a master type using environment variable
SPARK_MASTER = os.environ.get("SPARK_MASTER")

conf = SparkConf()

if SPARK_MASTER:
    conf.setMaster(SPARK_MASTER)

# Create Spark Context
sc = SparkContext(appName=APP_NAME, conf=conf)

# Set log level
#sc.setLogLevel("INFO")

# Create Streaming Context
ssc = StreamingContext(sc, BATCH_INTERVAL)

# Add checkpoint to preserve the states
ssc.checkpoint(CHECKPOINT_DIR)

# Create a stream
lines = ssc.socketTextStream(STREAM_HOST, STREAM_PORT)

# TRANSFORMATION FOR EACH BATCH

words = lines.flatMap(lambda line: line.split())
word_tuples = words.map(lambda word: (word, 1))
counts = word_tuples.reduceByKey(lambda x1, x2: x1 + x2)


# function for updating values
def update_total_count(currentCount, countState):
    """
    Update the previous value by a new ones.
    Each key is updated by applying the given function 
    on the previous state of the key (count_state) and the new values 
    for the key (current_count).
    """
    if countState is None:
        countState = 0
    return sum(currentCount, countState)


# Update current values
total_counts = counts.updateStateByKey(update_total_count)

# Print the result (10 records)
total_counts.pprint()
#counts.transform(lambda rdd: rdd.coalesce(1)).saveAsTextFiles("/YOUR_PATH/output/wordCount")

# Start Spark Streaming
ssc.start()

# Await termination
ssc.awaitTermination()