# Spark Structured Streaming: как включить метку времени

Усовик С.В. (usovik@bmstu.ru)

## Содержание

- [Требования](#Требования)
- [Исходный код](#Исходный-код)
- [Приложение Structured Streaming](#Приложение-Structured-Streaming)
    - [Основная часть](#Основная-часть)
    - [Включение элемента метки времени](#Включение-элемента-метки-времени)
    - [Включение отметки времени пакета](#Включение-отметки-времени-пакета)
    - [Встроенная метка времени](#Встроенная-метка-времени)
- [Рекомендации](#Рекомендации)

## Тпебования

Для запуска необходимо установить следующее ПО:  

- Ubuntu 14+
- Java 8
- Anaconda (Python 3.7)
- Spark 2.4+
- IntelliJ 2019+ с Python Plugin или PyCharm 2019+

## Исходный код

- Потоковый сервер ([stream_server.py](../projects/structuredstreaming/stream_server.py))
- Приложение Spark Structured Streaming ([append_timestamp_streaming.py](../projects/structuredstreaming/append_timestamp_streaming.py))


## Приложение Structured Streaming 

### Основная часть

Приложение имеет только одну опцию `timestamp_mode`, которая управляет тем, как мы добавляем столбец метки времени в фреймы данных.


Есть три значения опции:

- include (добавление метки времени при получении данных)
- include_batch (добавление одинаковых значений метки времени для всех элементов для каждой партии)
- embedded (с использованием временных меток самих данных, например, когда они были сгенерированы)



```python
def main(timestamp_mode):

    cleanup()
    spark_session = start_spark()

    if timestamp_mode == "include":
        query = main_include_timestamp(spark_session)
    elif timestamp_mode == "include_batch":
        query = main_include_batch_timestamp(spark_session)
    elif timestamp_mode == "embedded":
        query = main_embedded_timestamp(spark_session)
    else:
        raise Exception("Unsupported timestamp mode.")

    query.awaitTermination()
```

Для `include`:

```python
def main_include_timestamp(spark_session):
    lines = load_input_stream(spark_session, True)
    output = transformation_include_item(lines)
    return start_query(output)
```

Для `include_batch`:

```python
def main_include_batch_timestamp(spark_session):
    lines = load_input_stream(spark_session, False)
    output = transformation_include_batch(lines)
    return start_query(output)
```

Для `embedded`:

```python
def main_embedded_timestamp(spark_session):
    lines = load_input_stream(spark_session, False)
    output = transformations_embedded_steps(lines)
    return start_query(output)
```

Для загрузки входного потока мы будем использовать соединение через сокет:

```python
def load_input_stream(spark, include_timestamp=True):
    """Load stream."""
    return spark \
        .readStream \
        .format("socket") \
        .option("host", STREAM_HOST) \
        .option("port", STREAM_PORT) \
        .option("includeTimestamp", include_timestamp) \
        .load()
```


### Включение элемента метки времени

Чтобы продемонстрировать, как работают метки времени, мы будем использовать потоковый сервер, который генерирует поток случайных целых чисел:

```python
def random_output(delay):
    import random
    for i in range(1000):
        yield random.randint(0, 10)
        sleep(delay)
```

Используйте опцию `includeTimestamp`, чтобы добавить метку времени к каждому полученному значению:

```python
def load_input_stream(spark, include_timestamp=True):
    """Load stream."""
    return spark \
        .readStream \
        .format("socket") \
        .option("host", STREAM_HOST) \
        .option("port", STREAM_PORT) \
        .option("includeTimestamp", include_timestamp) \
        .load()
```

В этом случае поток данных будет иметь два столбца: значение, представляющее поток данных с сервера потоковой передачи, и отметка времени, включенная на стороне приложения Spark.

```python
def transformation_include_item(stream):
    """Raw input data with timestamp when an item arrived."""
    return stream \
        .withColumnRenamed("value", "number")
```

Чтобы запустить приложение, сначала запустите потоковый сервер для генерации случайных целых чисел:

`python stream_server.py --output random`

После этого запустите потоковое приложение Spark, используя `include` в качестве значения параметра `timestamp_mode`:

`spark-submit --master local[4] append_timestamp_streaming.py --timestamp_mode include`

Вывод:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+------+-----------------------+
|number|timestamp              |
+------+-----------------------+
|9     |2020-12-17 20:54:04.573|
|5     |2020-12-17 20:54:06.574|
|0     |2020-12-17 20:54:08.576|
+------+-----------------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+------+-----------------------+
|number|timestamp              |
+------+-----------------------+
|4     |2020-12-17 20:54:10.579|
|9     |2020-12-17 20:54:18.588|
|8     |2020-12-17 20:54:12.582|
|0     |2020-12-17 20:54:14.583|
|1     |2020-12-17 20:54:16.585|
+------+-----------------------+
```

### Включение отметки времени пакета


Прежде всего, необходимо отключить опцию `includeTimestamp` с помощью следующей строки кода:

```python
...
lines = load_input_stream(spark_session, False)
...
```

Чтобы включить метку времени пакета, мы добавим новый столбец с именем `timestamp` во время преобразования с текущим временем, возвращаемым функцией `F.current_timestamp()`. Таким образом, все элементы, принадлежащие к одной и той же партии, будут иметь одинаковые значения временных меток.


```python
def transformation_include_batch(stream):
    """Raw input data with timestamp when processing is started."""
    return stream \
        .withColumn("timestamp", F.current_timestamp()) \
        .withColumnRenamed("value", "number")
```

Запустите потоковый сервер со значением опции `random`:

`python stream_server.py --output random`

Затем запустите приложение spark:

`spark-submit --master local[4] append_timestamp_streaming.py --timestamp_mode include_batch`


Вывод:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+------+-----------------------+
|number|timestamp              |
+------+-----------------------+
|8     |2020-12-17 20:57:00.001|
|2     |2020-12-17 20:57:00.001|
|10    |2020-12-17 20:57:00.001|
|0     |2020-12-17 20:57:00.001|
|10    |2020-12-17 20:57:00.001|
+------+-----------------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+------+-----------------------+
|number|timestamp              |
+------+-----------------------+
|3     |2020-12-17 20:57:10.001|
|3     |2020-12-17 20:57:10.001|
|4     |2020-12-17 20:57:10.001|
|7     |2020-12-17 20:57:10.001|
|5     |2020-12-17 20:57:10.001|
+------+-----------------------+
```

### Встроенная метка времени

Иногда важно использовать встроенные временные метки данных во время преобразований, например, метки времени, когда данные были сгенерированы, а не когда они были получены. На стороне приложения spark streaming мы должны извлечь их и использовать соответствующим образом.

Для имитации данных, содержащих отметку времени, мы будем использовать следующий код:

```python
def random_json_with_timestamp(delay, random_timestamp=False, timestamp_delay=60):
    import random
    import datetime
    import json
    for i in range(1000):
        timestamp = datetime.datetime.today() if not random_timestamp \
            else datetime.datetime.today() - datetime.timedelta(seconds=random.randint(0, timestamp_delay))
        yield json.dumps({
            "number": random.randint(0, 10),
            "timestamp": timestamp.isoformat()
        })
        sleep(delay)
```

Пример вывода:

```json
{
    "number": 3, 
    "timestamp": "2020-12-17T20:54:44"
}
```

Для извлечения значений из json будет использоваться следующий код:


```python
def transformations_embedded(stream):
    """Transformation steps."""

    schema = StructType()
    schema.add("number", StringType())
    schema.add("timestamp", StringType())

    return stream \
        .select(F.from_json("value", schema).alias("data")) \
        .select("data.number", F.to_timestamp("data.timestamp").alias("timestamp"))
```

Давайте проверим, как это работает. Запустите потоковое приложение со значением опции `json_random_timestamp`:

`python stream_server.py --output json_random_timestamp`

А затем запустите приложение spark со значением `embedded` параметра `timestamp_mode`:

`spark-submit --master local[4] append_timestamp_streaming.py --timestamp_mode embedded`


Вывод:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+------+--------------------------+
|number|timestamp                 |
+------+--------------------------+
|1     |2020-12-17 21:00:35.21267 |
|5     |2020-12-17 21:00:35.215084|
+------+--------------------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+------+--------------------------+
|number|timestamp                 |
+------+--------------------------+
|9     |2020-12-17 21:00:40.218604|
|6     |2020-12-17 21:00:29.234105|
|6     |2020-12-17 21:00:09.220058|
|9     |2020-12-17 21:00:29.223873|
|4     |2020-12-17 20:59:58.23132 |
+------+--------------------------+
```

Чтобы прояснить, что происходит, когда мы применяем приведенные выше преобразования, используйте приведенную ниже функцию вместо `transformations_embedded()`:

```python
def transformations_embedded_steps(stream):
    """Transformation steps."""

    schema = StructType()
    schema.add("number", StringType())
    schema.add("timestamp", StringType())

    return stream \
        .select("*", F.from_json("value", schema).alias("data")) \
        .select("*", "data.*") \
        .select("*", F.to_timestamp("timestamp").alias("datetime"))

```

Примеры с потокового сервера:

```json
{"number": 1, "timestamp": "2020-12-17T21:03:58.363641"}
{"number": 3, "timestamp": "2020-12-17T21:03:42.366133"}
{"number": 10, "timestamp": "2020-12-17T21:04:35.369384"}
```

Сгенерированный вывод:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+---------------------------------------------------------+--------------------------------+------+--------------------------+--------------------------+
|value                                                    |data                            |number|timestamp                 |datetime                  |
+---------------------------------------------------------+--------------------------------+------+--------------------------+--------------------------+
|{"number": 1, "timestamp": "2020-12-17T21:03:58.363641"} |[1, 2020-12-17T21:03:58.363641] |1     |2020-12-17T21:03:58.363641|2020-12-18 21:03:58.363641|
|{"number": 3, "timestamp": "2020-12-17T21:03:42.366133"} |[3, 2020-12-17T21:03:42.366133] |3     |2020-12-17T21:03:42.366133|2020-12-18 21:03:42.366133|
|{"number": 10, "timestamp": "2020-12-17T21:04:35.369384"}|[10, 2020-12-17T21:04:35.369384]|10    |2020-12-17T21:04:35.369384|2020-12-17 21:04:35.369384|
+---------------------------------------------------------+--------------------------------+------+--------------------------+--------------------------+

```

## Рекомендации

[Structured Streaming Programming Guide](https://spark.apache.org/docs/2.4.7/structured-streaming-programming-guide.html) (Spark 2.4.7)