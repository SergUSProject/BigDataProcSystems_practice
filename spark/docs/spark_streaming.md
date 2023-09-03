# Введение в Spark Streaming
Усовик С.В. (usovik@bmstu.ru)


## Содержание

- Требования
- Конфигурация Spark
- Конфигурация Kafka
- Практика
- Spark и Jupyter

## Требования

Для запуска необходимо следующее ПО 

- Установка Ubuntu 14+
- Установка Java 8
- Загрузка Hadoop 3+
- Загрузка Spark 2+
- [Опционально] Anaconda Python 3.7
- IntelliJ с Python Plugin или PyCharm
- Установка Jupyter (Python)

## Конфигурация Spark

IВ этом руководстве конфигурация по умолчанию включает развертывание Spark в кластере YARN. Таким образом, вы должны настроить и запустить `HDFS` и `YARN`.

TФайлы конфигурации можно найти [here](spark_basics.md).

## Конфигурация Kafka

В некоторых приведенных ниже примерах сервер Kafka требуется в качестве брокера сообщений, поэтому перейдите по [этой ссылке](kafka_basics.md), чтобы ознакомиться с инструкциями по установке, настройке и запуску Kafka.

## Практика

[Introduction to Spark Streaming](https://github.com/BigDataProcSystems/Spark_Streaming/blob/master/docs/spark_streaming_intro.md): Stateless/stateful and window transformations 

[Introduction to Kafka distributed message broker](../docs/kafka_basics.md): How to Set Up Kafka

[Spark Streaming with Kafka](https://github.com/BigDataProcSystems/Spark_Streaming/blob/master/docs/spark_streaming_kafka.md): Using Kafka as input source for Spark Streaming application

[Spark Streaming with Kafka and Twitter API](https://github.com/BigDataProcSystems/Spark_Streaming/blob/master/docs/spark_streaming_kafka_tweets.md): Using Kafka producer with messages received from Twitter API and Spark Steaming application with Kafka Consumer as input source to process tweets

[Spam Classification using Sklearn and Spark Streaming](https://github.com/BigDataProcSystems/Spark_Streaming/blob/master/docs/spark_streaming_classifier.md): Using spam classification model built with `sklearn` library in Spark Streaming application

[Updatable Broadcast in Spark Streaming Application](https://github.com/BigDataProcSystems/Spark_Streaming/blob/master/docs/spark_streaming_update.md): How to use ML models that change periodically in Spark Streaming applications 

