# Spark Streaming и Kafka

Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требования
- Конфигурация Spark
- Конфигурация Kafka
- Исходный код
- Приложение Spark Streaming
- Рекомендации

## Конфигурация Spark

В этом руководстве конфигурация по умолчанию включает развертывание Spark в кластере YARN. Таким образом, вы должны настроить и запустить `HDFS` и `YARN`.

Конфигурационные файлы можно найти [здесь](https://github.com/BigDataProcSystems/Spark/blob/master/docs/spark_basics.md).

## Конфигурация Kafka

В некоторых приведенных ниже примерах требуется сервер Kafka в качестве брокера сообщений, поэтому перейдите по [этой ссылке](kafka_basics.md) чтобы ознакомиться с инструкциями по установить, настроить и запустить `Kafka`

Создание Kafka topic:

`$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --topic kafka-word-count`

Запуск Kafka producer:

`$KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic kafka-word-count`

Запуск Kafka consumer:

`$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic kafka-word-count --from-beginning`

## Исходный код

- Spark Streaming при помощи Kafka: [spark_streaming_kafka_wcount.py](../projects/kakfastreaming/spark_streaming_kafka_wcount.py)

## Приложение Spark Streaming

Код приложения Spark Streaming ([spark_streaming_kafka_wcount.py](../projects/kakfastreaming/spark_streaming_kafka_wcount.py))

```python
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
counts = lines.flatMap(lambda line: line.split()).map(lambda word: (word, 1)).reduceByKey(lambda x1, x2: x1 + x2)

# Update word counts
total_counts = counts.updateStateByKey(update_total_count)

# Print result
total_counts.pprint()

# Start Spark Streaming
ssc.start()

# Waiting for termination
ssc.awaitTermination()

```

Запустите приложение spark streaming (код выше):

`spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 /YOUR_PATH/spark_streaming_kafka_wcount.py`

По умолчанию мы используем режим клиента YARN для развертывания приложения Spark. Для локального запуска используйте следующую команду с явным главным аргументом:

`spark-submit --master local[2] --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 /YOUR_PATH/spark_streaming_kafka_wcount.py`

Введите любой текст в терминале producer и посмотрите на вывод приложения.

## Рекомендации

1. [Spark Streaming Programming Guide](https://spark.apache.org/docs/2.4.0/streaming-programming-guide.html)
2. [Apache Kafka Quickstart](https://kafka.apache.org/quickstart)
