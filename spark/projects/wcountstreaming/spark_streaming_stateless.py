# -*- coding: utf-8 -*-

import os

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext


# Application name
APP_NAME = "WordCount"

# Batch interval (10 seconds)
BATCH_INTERVAL = 10

# Source of stream
STREAM_HOST = "localhost"
STREAM_PORT = 9999

# Control a master type using environment variable
SPARK_MASTER = os.environ.get("SPARK_MASTER")

conf = SparkConf()

if SPARK_MASTER:
    conf.setMaster(SPARK_MASTER)

# Create Spark Context
sc = SparkContext(appName=APP_NAME, conf=conf)

# Set log level
sc.setLogLevel("ERROR")

# Create Streaming Context
ssc = StreamingContext(sc, BATCH_INTERVAL)

# Create a stream (DStream)
lines = ssc.socketTextStream(STREAM_HOST, STREAM_PORT)


# TRANSFORMATION FOR EACH BATCH


"""
MapFlat Transformation
Example: ["a a b", "b c"] => ["a", "a", "b", "b", "c"] 
"""
words = lines.flatMap(lambda line: line.split())


"""
Map Transformation
Example: ["a", "a", "b", "b", "c"] => [("a",1), ("a",1), ("b",1), ("b",1), ("c",1)] ] 
"""
word_tuples = words.map(lambda word: (word, 1))


"""
ReduceByKey Transformation
Example: [("a",1), ("a",1), ("b",1), ("b",1), ("c",1)] => [("a",3),("b",2), ("c",1)]
"""
counts = word_tuples.reduceByKey(lambda x1, x2: x1 + x2)


# Print the result (10 records)
counts.pprint()

# Save to permanent storage
# counts\
#     .transform(lambda rdd: rdd.coalesce(1))\
#     .saveAsTextFiles("/YOUR_PATH/output/wordCount")

# Start Spark Streaming
ssc.start()

# Await termination
ssc.awaitTermination()
