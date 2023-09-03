# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

import json

SPARK_APP_NAME = "WordCountServiceApp"
SPARK_CHECKPOINT_TMP_DIR = "tmp_spark_streaming"
SPARK_BATCH_INTERVAL = 10
SPARK_LOG_LEVEL = "OFF"

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "wordcount"

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_CHARSET = "utf-8"
REDIS_DECODE_RESPONSES = True

REDIS_KEY_WORD_COUNT = "word_counts"
REDIS_KEY_TOP_10_WORD = "top_10_words"


def update_total_count(current_count, count_state):
    """Update total word counts"""
    if count_state is None:
        count_state = 0
    return sum(current_count, count_state)


def save_partition_in_redis(partition):
    """
    Insert/update word count pairs in Redis for each partition

    Note: minus for the count variable in r.zadd() is a workaround to
    guarantee lex ordering when word counts have the same value.
    The sign should be removed when consume this Redis sorted set.
    """
    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset=REDIS_CHARSET, decode_responses=REDIS_DECODE_RESPONSES)
    for row in partition:
        r.zadd(REDIS_KEY_WORD_COUNT, {row[0]: -row[1]})


def save_rdd_in_redis(time, rdd):
    """Insert/update word count pairs in Redis"""
    rdd.foreachPartition(save_partition_in_redis)


def save_top_10_in_redis(time, rdd):
    """
    Insert/update top 10 words

    Note: minus for the count variable in r.zadd() is a workaround to
    guarantee lex ordering when word counts have the same value.
    The sign should be removed when consume this Redis sorted set.
    """
    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset=REDIS_CHARSET, decode_responses=REDIS_DECODE_RESPONSES)
    r.delete(REDIS_KEY_TOP_10_WORD)
    top_10_words = rdd.takeOrdered(10, key=lambda x: -x[1])
    for word, count in top_10_words:
        r.zadd(REDIS_KEY_TOP_10_WORD, {word: -count})


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

# Extract a content of messages from Kafka topic stream (per mini-batch)
lines = kafka_stream.map(lambda x: json.loads(x[1])["content"])

# Count words (per mini-batch)
counts = lines.flatMap(lambda line: line.split())\
    .map(lambda word: (word, 1))\
    .reduceByKey(lambda x1, x2: x1 + x2)

# Update total word counts
total_counts = counts.updateStateByKey(update_total_count)

# Save word counts in redis (job 1)
total_counts.foreachRDD(save_rdd_in_redis)

# Save top 10 words in redis (job 2)
total_counts.foreachRDD(save_top_10_in_redis)

# Output result in console (job 3)
total_counts.pprint()

# Start Spark Streaming
ssc.start()

# Wait for termination
ssc.awaitTermination()
