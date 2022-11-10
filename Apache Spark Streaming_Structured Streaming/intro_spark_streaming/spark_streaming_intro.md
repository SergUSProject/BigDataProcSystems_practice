# Введение в Spark Streaming

## Содержание

- [Конфигурация Spark](#Конфигурация-Spark)
- [Данные](#Данные)
- [Исходный код](#Исходный-код)
- [Использованная литература](#Использованная-литература)

## Конфигурация Spark

В этом описании используется конфигурация Spark on `YARN` по-умолчанию. Предварительно необходимо сконфигурировать и запустить `HDFS` and `YARN`.

The configuration files you can find [here](Apache Spark/Spark on YARN.md).

## Данные

- Набор данных: [samples_100.json](/data/samples_100.json)

## Исходный код

- преобразование без сохранения состояния (Stateless Transformation): [spark_streaming_stateless.py](../projects/wcountstreaming/spark_streaming_stateless.py)
- преобразование с сохранением состояния (Stateful Transformation): [spark_streaming_stateful.py](../projects/wcountstreaming/spark_streaming_stateful.py)
- оконное преобразование (Window Transformation): [spark_streaming_window.py](../projects/wcountstreaming/spark_streaming_window.py)
- TCP-сервер: [tcp_server.py](../projects/tcpserver/tcp_server.py)

## Преобразование без сохранения состояния (Stateless Transformation)


Исходный код приложения Spark Streaming ([spark_streaming_stateless.py](/spark_streaming_stateless.py)):

```python
# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext


# Application name
APP_NAME = "WordCount"

# Batch interval (10 seconds)
BATCH_INTERVAL = 10

# Source of stream
STREAM_HOST = "localhost"
STREAM_PORT = 9999


# Create Spark Context
sc = SparkContext(appName=APP_NAME)

# Set log level
sc.setLogLevel("ERROR")

# Batch interval (10 seconds)
batch_interval = 10

# Create Streaming Context
ssc = StreamingContext(sc, batch_interval)

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
# counts.transform(lambda rdd: rdd.coalesce(1))
# .saveAsTextFiles("/YOUR_PATH/output/wordCount")

# Start Spark Streaming
ssc.start()

# Await termination
ssc.awaitTermination()
```

Создайте тестовый источник с помощью инструмента netcat. Netcat прослушивает порт 9999, и текст, введенный в терминале будет прочитан Spark Streaming:

`nc -lk 9999`

Запустите spark streaming приложение (код выше):

`spark-submit /YOUR_PATH/spark_streaming_wordcount.py`


По-умолчанию используется режим YARN для запуска Spark-приложения. Для локального запуска используйте следующую команду:

`spark-submit --master local[2] /YOUR_PATH/spark_streaming_wordcount.py`

Теперь запустите два приложения terminal (одно для сообщений, другое для spark streaming приложения). Введите случайным образом текстовое сообщение в terminal с запущенным netcat и наблюдайте за terminal с запущенным spark streaming. Пронаблюдайте за поведением spark streaming приложения, рассмотрите его особенности. Почему преобразование определяется как "без сохранения состояния" (stateless)?

## Преобразование c сохранением состояния (Stateful Transformation)

Исходный код приложения Spark Streaming ([spark_streaming_stateful.py](./park_streaming_stateful.py)):

```python
...

# Add checkpoint to preserve the states
ssc.checkpoint(CHECKPOINT_DIR)

...

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

...
```

Запустите приложение spark streaming в terminal, как в предыдущем случае. Пронаблюдайте разницу в результах выполнения программы с предыдущим случаем.

## Оконное преобразование (Window Transformation)

Исходный код приложения Spark Streaming ([spark_streaming_window.py](/spark_streaming_window.py)):

```python
...

# Add checkpoint to preserve the states
ssc.checkpoint(CHECKPOINT_DIR)

...

counts = word_tuples.reduceByKey(lambda x1, x2: x1 + x2)

# Apply window
windowed_word_counts = counts.reduceByKeyAndWindow(
    lambda x, y: x + y, 
    lambda x, y: x - y, 
    20, 10)

# windowed_word_counts = counts.reduceByKeyAndWindow(
# lambda x, y: x + y, None, 20, 10)


# Print the result (10 records)
windowed_word_counts.pprint()
# windowed_word_counts.transform(lambda rdd: rdd.coalesce(1)).saveAsTextFiles("/YOUR_PATH/output/wordCount")
```


## TCP-сервер

В качестве источника потока данных мы будем использовать TCP-сервер. Сервер запускается на `localhost` и прослушивает `port 9999`. Когда соединение с клиентом установлено, сервер отправляет клиенту сообщения. В этом случае сообщения представляют собой отзывы, которые храняться json-файле. Каждый отзыв из файла отправляется клиенту с небольшой задержкой (по-умолчанию, 4 с.).


Исходный код TCP-сервер ([tcp_server.py](../projects/tcpserver/tcp_server.py)):
```python
# -*- coding: utf-8 -*-

import json
import socket
from time import sleep
import click


SERVER_HOST = "localhost"
SERVER_PORT = 9999
SERVER_WAIT_FOR_CONNECTION = 10
MESSAGE_DELAY = 4


def get_file_line(file_path):
    """Read a file line by line"""
    with open(file_path, "r") as f:
        for line in f:
            try:
                yield json.loads(line)["reviewText"]
            except json.JSONDecodeError:
                pass


@click.command()
@click.option("-h", "--host", default=SERVER_HOST, help="Server host.")
@click.option("-p", "--port", default=SERVER_PORT, help="Server port.")
@click.option("-f", "--file", help="File to send.")
@click.option("-d", "--delay", default=MESSAGE_DELAY, help="Delay between messages.")
def main(host, port, file, delay):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        print("Starting the server...")

        server_socket.bind((host, port))
        server_socket.listen()

        print("The server is running on {}:{} and listening to a new connection. "
              "To exit press CTRL+C.".format(host, port))

        while True:
            client_socket = None
            try:
                server_socket.settimeout(SERVER_WAIT_FOR_CONNECTION)
                print("Waiting for client connection...")
                client_socket, client_address = server_socket.accept()
                server_socket.settimeout(None)
                print("Connection established. Client: {}:{}".format(client_address[0], client_address[1]))
                print("Sending data...")
                for indx, review in enumerate(get_file_line(file)):
                    client_socket.send("{}\n".format(review).encode("utf-8"))
                    print("Sent line: {}".format(indx+1))
                    sleep(delay)
                print("Closing connection...")
                client_socket.close()

            except socket.timeout:
                print("No clients to connect.")
                break

            except KeyboardInterrupt:
                print("Interrupt")
                if client_socket:
                    client_socket.close()
                break

        print("Stopping the server...")


if __name__ == "__main__":
    main()

```

Запустите приложение spark streaming на стороне клиента, а затем запустите script с помощью следующей команды:

`python tcp_server.py --file /YOUR_PATH/samples_100.json`


## Использованная литература

[Spark Streaming Programming Guide](https://spark.apache.org/docs/2.3.0/streaming-programming-guide.html)