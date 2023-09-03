# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


SPARK_APP_NAME = "WordCountKafkaTwitter"
SPARK_CHECKPOINT_TMP_DIR = "tmp_spark_streaming"
SPARK_BATCH_INTERVAL = 10
SPARK_LOG_LEVEL = "OFF"

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "tweets-kafka"


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


def create_streaming_context():
    """Create Spark streaming context."""

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
    return ssc


def create_stream(ssc):
    """
    Create subscriber (consumer) to the Kafka topic and
    extract only messages (works on RDD that is mini-batch).
    """
    return (
        KafkaUtils.createDirectStream(
            ssc, topics=[KAFKA_TOPIC],
            kafkaParams={"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
            .map(lambda x: x[1])
    )


def main():

    # Init Spark streaming context
    ssc = create_streaming_context()

    # Get message stream
    messages = create_stream(ssc)

    # Count words for each RDD (mini-batch)
    total_counts_sorted = (
        messages
            # Word count
            .flatMap(lambda line: line.split())
            .map(lambda word: (word, 1))
            .reduceByKey(lambda x1, x2: x1 + x2)
            # Update word counts
            .updateStateByKey(update_total_count)
            # Sort by counts
            .transform(lambda x_rdd: x_rdd.sortBy(lambda x: -x[1]))
    )

    # Print result
    total_counts_sorted.pprint()

    # Start Spark Streaming
    ssc.start()

    # Waiting for termination
    ssc.awaitTermination()


if __name__ == "__main__":
    main()