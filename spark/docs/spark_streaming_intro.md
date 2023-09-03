# Введение в Spark Streaming

Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Конфигурация Spark
- Наборы данных
- Исходный код
- Преобразование без отслеживания состояния
- Преобразование с отслеживанием состояния
- Оконные преобразования
- TCP-сервер как источник потока
- Рекомендации

## Конфигурация Spark

В этом руководстве конфигурация по умолчанию включает развертывание Spark в кластере YARN. Таким образом, необходимо настроить и запустить `HDFS` и `YARN`.

Конфигурационные файлы можно найти [здесь](spark_basics.md).

## Наборы данных

- Небольшой набор данных: [samples_100.json](../data/samples_100.json)

## Исходный код

- Преобразование без отслеживания состояния: [spark_streaming_stateless.py](../projects/wcountstreaming/spark_streaming_stateless.py)
- Преобразование с отслеживанием состояния: [spark_streaming_stateful.py](../projects/wcountstreaming/spark_streaming_stateful.py)
- Оконные преобразования: [spark_streaming_window.py](../projects/wcountstreaming/spark_streaming_window.py)
- TCP-сервер: [tcp_server.py](../projects/tcpserver/tcp_server.py)

## Преобразование без отслеживания состояния


Исходный код приложения Spark Streaming ([spark_streaming_stateless.py](../projects/wcountstreaming/spark_streaming_stateless.py)):

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

Скопируйте и вставьте содержимое выше в отдельный файл py.

Создайте тестовый текстовый источник с помощью инструмента netcat. Netcat установит прослушиватель на порт 9999, и текст, введенный в терминале, будет прочитан Spark Streaming:

`nc -lk 9999`

Запустите приложение spark streaming (код выше):

`spark-submit /YOUR_PATH/spark_streaming_wordcount.py`


По умолчанию мы используем режим клиента YARN для развертывания приложения Spark. Для локального запуска используйте следующую команду с явным главным аргументом:

`spark-submit --master local[2] /YOUR_PATH/spark_streaming_wordcount.py`

Теперь имеется два терминала (один для сообщений, а другой для приложения spark streaming). Введите случайные текстовые сообщения в терминал с помощью netcat и посмотрите на терминал с spark streaming. Как можно описать поведение приложения spark streaming? Какие особенности вы заметили? Почему без отслеживания состояния?

## Преобразование с отслеживанием состояния

Исходный код приложения Spark Streaming ([spark_streaming_stateful.py](../projects/wcountstreaming/spark_streaming_stateful.py)):

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

Запустите это приложение spark streaming в терминале, как и в предыдущем случае. В чем разница между результатами двух приложений?

## Оконные преобразования

Исходный код приложения Spark Streaming ([spark_streaming_window.py](../projects/wcountstreaming/spark_streaming_window.py)):

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

Мы будем использовать TCP-сервер в качестве источника потока. Сервер запускается на «localhost» и прослушивает «порт 9999». Когда соединение с клиентом установлено, сервер отправляет клиенту сообщения. В этом случае сообщения представляют собой обзоры, которые хранятся в файле json. Каждый отзыв из файла мы отправляем клиенту с небольшой задержкой (по умолчанию 4 секунды).


Исходный код TCP-сервера ([tcp_server.py](../projects/tcpserver/tcp_server.py)):
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

Запустите приложение spark streaming в качестве клиента, а затем запустите скрипт сервера с помощью следующей команды:

`python tcp_server.py --file /YOUR_PATH/samples_100.json`


## Рекомендации

[Spark Streaming Programming Guide](https://spark.apache.org/docs/2.3.0/streaming-programming-guide.html)