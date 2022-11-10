# Spark Structured Streaming: Окно в режиме добавления



## Содержание

-  [Необходимое ПО](#Необходимое-ПО)
- [Исходный код](Исходный-код) 
- [Потоковый сервер](Потоковый-сервер)
- [Приложение Spark Structured Streaming](#Приложение-Spark-Structured-Streaming)
- [Запуск приложения](Запуск-приложения)
- [Использованная литература](Использованная-литература)

## Необходимое ПО

Для запуска необходима установка следующего программного обеспечения:

- Ubuntu 14+
- Java 8
- Anaconda (Python 3.7)
- Spark 2.4+
- IntelliJ 2019+ with Python Plugin or PyCharm 2019+


## Исходный код

- Потоковый сервер ([stream_server.py](./stream_server.py))
- Приложение Spark Structured Streaming ([window_append_streaming.py](./window_append_streaming.py))



## Потоковый сервер

```python
def send_messages(message_gen, send_func):
    for message in message_gen:
        send_func("{}\n".format(message).encode("utf-8"))
        print("Sent value: {}".format(message))


def random_output(delay):
    import random
    for i in range(1000):
        yield random.randint(0, 10)
        sleep(delay)


for i in range(repeat):
    send_messages(init_iterator(output, delay, file), client_socket.send)
```

## Приложение Spark Structured Streaming


```python
def main(sink):

    # Cleaning up all previous data (for the local mode only)
    cleanup()

    # Creating a Spark session
    spark_session = start_spark()

    # Loading input stream
    lines = load_input_stream(spark_session)

    # Transformations
    output = transformations(lines)

    # Writing to output sink
    if sink == "console":
        query = start_query_console(output)
    elif sink == "file":
        query = start_query_csv(output)
    else:
        raise Exception("Provided output sink type is not supported.")

    # Waiting for termination
    query.awaitTermination()
```


```python

def load_input_stream(spark):
    return spark \
        .readStream \
        .format("socket") \
        .option("host", STREAM_HOST) \
        .option("port", STREAM_PORT) \
        .option("includeTimestamp", "true") \
        .load()


def transformations(stream):
    """Group by value and window."""
    return stream.withWatermark("timestamp", "15 seconds") \
        .groupBy("value", F.window("timestamp", "30 seconds", "15 seconds")) \
        .count() \
        .select(stringify_window("window").alias("window"), "value", "count") \
        .coalesce(1)


def start_query_console(output):
    """Start a query with the console sink type."""
    return output.writeStream \
        .option("checkpointLocation", APP_CHECKPOINT_DIR) \
        .outputMode("append") \
        .format("console") \
        .queryName("wordcount_query") \
        .option("truncate", False) \
        .trigger(processingTime="15 seconds") \
        .start()


def start_query_csv(output):
    """Start a query with the console sink type."""
    return output.writeStream \
        .format("csv") \
        .partitionBy("window") \
        .option("checkpointLocation", APP_CHECKPOINT_DIR) \
        .option("path", APP_DATA_OUTPUT_DIR) \
        .trigger(processingTime="10 seconds") \
        .outputMode("append") \
        .start()
```

## Запуск приложения

Для имитации потока запустите сервер, который будет генерировать случайные целые числа от 0 до 10 включительно каждые 2 секунды:

`python stream_server.py --output random`

После этого запустите streaming приложение с консольным выводом с помощью следующей команды:

`spark-submit --master local[4] window_append_streaming.py --sink console`

В терминале должен получиться подобный вывод:

```
-------------------------------------------
Batch: 0
-------------------------------------------
+------+-----+-----+
|window|value|count|
+------+-----+-----+
+------+-----+-----+

...

-------------------------------------------
Batch: 3
-------------------------------------------
+-------------+-----+-----+
|window       |value|count|
+-------------+-----+-----+
|173300-173330|2    |2    |
|173300-173330|10   |1    |
|173300-173330|9    |2    |
|173300-173330|0    |1    |
|173300-173330|1    |1    |
+-------------+-----+-----+

-------------------------------------------
Batch: 4
-------------------------------------------
+-------------+-----+-----+
|window       |value|count|
+-------------+-----+-----+
|173315-173345|7    |2    |
|173315-173345|1    |1    |
|173315-173345|9    |4    |
|173315-173345|0    |2    |
|173315-173345|10   |1    |
|173315-173345|3    |1    |
|173315-173345|2    |3    |
+-------------+-----+-----+
```

Теперь запустим то же приложение, но врежиме вывода в файл:

`spark-submit --master local[4] window_append_streaming.py --sink file`


Выходной католог будет содержать файлы для каждого окна:

```
output
├── window=173930-174000
│   └── part-00000-28ff049b-1ebd-405a-8718-f7b18e330e74.c000.csv
├── window=173945-174015
│   └── part-00000-19768e0f-bfa0-4fbc-a8ed-7957af6bd093.c000.csv
├── window=174000-174030
│   └── part-00000-2cb0fc9f-113a-42b0-a996-0f4c81a6e082.c000.csv
└── window=174015-174045
    └── part-00000-ada6ad74-ffad-4e9f-a217-a2cdd75be268.c000.csv
```


Содержимое файла `part-00000-ada6ad74-ffad-4e9f-a217-a2cdd75be268.c000.csv` :
```
5,2
6,3
1,2
3,3
9,1
8,4
```


## Использованная литература

[Structured Streaming Programming Guide](https://spark.apache.org/docs/2.4.7/structured-streaming-programming-guide.html) (Spark 2.4.7)