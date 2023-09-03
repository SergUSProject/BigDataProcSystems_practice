# -*- coding: utf-8 -*-

import os

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext


# Application name
APP_NAME = "WordCountStatefulWindow"

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

# Apply window
windowed_word_counts = counts.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 20, 10)
# windowed_word_counts = counts.reduceByKeyAndWindow(lambda x, y: x + y, None, 20, 10)


# Print the result (10 records)
windowed_word_counts.pprint()
# windowed_word_counts.transform(lambda rdd: rdd.coalesce(1)).saveAsTextFiles("/YOUR_PATH/output/wordCount")

# Start Spark Streaming
ssc.start()

# Await termination
ssc.awaitTermination()