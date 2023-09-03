# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

SPARK_APP_NAME = "KafkaWordCount"
SPARK_CHECKPOINT_TMP_DIR = "tmp_spark_streaming"
SPARK_BATCH_INTERVAL = 10
SPARK_LOG_LEVEL = "OFF"

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "kafka-word-count"


def update_total_count(current_count, count_state):
    """
    Update the previous value by a new ones.

    Each key is updated by applying the given function 
    on the previous state of the key (count_state) and the new values 
    for the key (current_count).
    """
    if count_state is None:
        count_state = 0
    return sum(current_count, count_state)


# Create Spark Context
sc = SparkContext(appName=SPARK_APP_NAME)

# Set log level
sc.setLogLevel(SPARK_LOG_LEVEL)

# Create Streaming Context
ssc = StreamingContext(sc, SPARK_BATCH_INTERVAL)

# Sets the context to periodically checkpoint the DStream operations for master
# fault-tolerance. The graph will be checkpointed every batch interval.
# It is used to update results of stateful transformations as well
ssc.checkpoint(SPARK_CHECKPOINT_TMP_DIR)

# Create subscriber (consumer) to the Kafka topic
kafka_stream = KafkaUtils.createDirectStream(ssc,
                                             topics=[KAFKA_TOPIC],
                                             kafkaParams={"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

# Extract only messages (works on RDD that is mini-batch)
lines = kafka_stream.map(lambda x: x[1])

# Count words for each RDD (mini-batch)
counts = lines\
    .flatMap(lambda line: line.split())\
    .map(lambda word: (word, 1))\
    .reduceByKey(lambda x1, x2: x1 + x2)

# Update word counts
total_counts = counts.updateStateByKey(update_total_count)

# Print result
total_counts.pprint()

# Start Spark Streaming
ssc.start()

# Waiting for termination
ssc.awaitTermination()

