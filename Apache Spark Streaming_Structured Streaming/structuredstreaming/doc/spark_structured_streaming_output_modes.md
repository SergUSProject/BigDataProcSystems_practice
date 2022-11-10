# Spark Structured Streaming: Выполнение и обновление режима вывода



## Содержание

- [Требуемое программное обеспечение](#Требуемое-ПО)
- [Исходный код](#Исходный-код)
- [Запуск приложения](#Запуск-приложения)
    - [Полный режим и консольный вывод](#Полный-режим-и-консольный-вывод)
    - [Режим обновления и консольный вывод](#Режим-обновления-и-консольный-вывод)
    - [Полный режим и попакетный вывод](#Полный-режим-и-попакетный-вывод)
    - [Режим обновления и попакетный вывод](#Режим-обновления-и-попакетный-вывод)
- [Использованная литература](#Использованная-литература)

## Требуемое ПО:

Для запуска необходимо установить следующее программное обеспечение:

- Install Ubuntu 14+
- Install Java 8
- Install Anaconda (Python 3.7)
- Install Spark 2.4+
- Install IntelliJ 2019+ with Python Plugin or PyCharm 2019+


## Исходный код

- Исходный код приложения Spark Structured Streaming ([complete_update_streaming.py](../code/complete_update_streaming.py))


## Запуск приложения



### Структура приложения


Main-функция:

```python
def main(mode, sink):

    spark_session = start_spark()
    lines = load_input_stream(spark_session)
    output = transformations(lines)

    if sink == "foreach":
        query = start_query_with_custom_sink(output, mode)
    elif sink == "console":
        # Note: sorting is available only in the complete mode.
        output = output.sort(F.desc("count")) if mode == "complete" else output
        query = start_query(output, mode)
    else:
        raise Exception("Unsupported sink.")

    query.awaitTermination()
```

Запуск Spark-сессии:

```python
def start_spark():

    # Note: spark.executor.* options are not the case in the local mode
    #  as all computation happens in the driver.
    conf = pyspark.SparkConf() \
        .set("spark.executor.memory", "1g") \
        .set("spark.executor.core", "2") \
        .set("spark.driver.memory", "2g")

    spark = SparkSession \
        .builder \
        .config(conf=conf) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    return spark
```

Загрузка потока:

```python
def load_input_stream(spark):
    """Load stream."""
    return spark \
        .readStream \
        .format("socket") \
        .option("host", STREAM_HOST) \
        .option("port", STREAM_PORT) \
        .load()
```

Преобразование потоков:

```python
def transformations(stream):
    """Count words."""
    return stream \
        .select(F.explode(F.split("value", " ")).alias("word")) \
        .groupBy("word") \
        .count()
```

### Полный режим и консольный вывод

Замечание: Вы не можете выполнять несколько запросов к одному источнику потока. Только первый запрос получит данные и будет выполнен. 

```python
def start_query(output, mode):

    return output \
        .writeStream \
        .outputMode(mode) \
        .format("console") \
        .trigger(processingTime="10 seconds") \
        .queryName("wordcount_query") \
        .option("truncate", False) \
        .start()
```

Откройте terminal и запустите прослушивание 9999 порта для нового клиентского соединения:

`nc -lk 9999`

Откройте другой terminal и запустите приложение spark streaming. Выполните следующую команду:

```
spark-submit --master local[2] complete_update_mode.py -m complete -s console
```

Замечание: Приложение имеет две опции: режим (`-m`) и вывод (`-s`).

В terminal с запущенной утилитой netcat введите следующий текст:

```
a a b c
b d e
```

Через некоторое время (через 10 секунд) введите еще текст: 

```
a b c
a c
```

В итоге, должен получиться результат, похожий на этот:

```
-------------------------------------------
Batch: 0
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
+----+-----+

-------------------------------------------
Batch: 1
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
|b   |2    |
|a   |2    |
|e   |1    |
|d   |1    |
|c   |1    |
+----+-----+

-------------------------------------------
Batch: 2
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
|a   |4    |
|c   |3    |
|b   |3    |
|e   |1    |
|d   |1    |
+----+-----+
```

Остановите приложение.


### Режим обновления и консольный вывод

Повторите предыдущие шаги, но используйте приведенную ниже команду для запуска приложения spark streaming:

```
spark-submit --master local[2] complete_update_mode.py -m update -s console
```

Вывод в терминале:

```
-------------------------------------------
Batch: 0
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
+----+-----+

-------------------------------------------
Batch: 1
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
|e   |1    |
|d   |1    |
|c   |1    |
|b   |2    |
|a   |2    |
+----+-----+

-------------------------------------------
Batch: 2
-------------------------------------------
+----+-----+
|word|count|
+----+-----+
|c   |3    |
|b   |3    |
|a   |4    |
+----+-----+
```

### Полный режим и попакетный вывод

Замечание: Каждый пакет сортируется и ограничивается 4 верхними записями


```python
def sort_batch(df, epoch_id):
    """Sort mini-batch and write to console."""
    df.sort(F.desc("count")) \
        .limit(4) \
        .write \
        .format("console") \
        .save()


def start_query_with_custom_sink(output, mode):
    """Start a query with the foreachBatch sink type."""
    return output \
        .writeStream \
        .foreachBatch(sort_batch) \
        .outputMode(mode) \
        .trigger(processingTime=STREAM_QUERY_TRIGGER) \
        .queryName("wordcount_query") \
        .option("truncate", STREAM_QUERY_TRUNCATE) \
        .start()
```

```
spark-submit --master local[2] complete_update_mode.py -m complete -s foreach
```

```
+----+-----+
|word|count|
+----+-----+
+----+-----+

+----+-----+
|word|count|
+----+-----+
|   b|    2|
|   a|    2|
|   e|    1|
|   d|    1|
+----+-----+

+----+-----+
|word|count|
+----+-----+
|   a|    4|
|   c|    3|
|   b|    3|
|   e|    1|
+----+-----+

```



### Режим обновления и попакетный вывод

```
spark-submit --master local[2] complete_update_mode.py -m update -s foreach
```

```
+----+-----+
|word|count|
+----+-----+
+----+-----+

+----+-----+
|word|count|
+----+-----+
|   b|    2|
|   a|    2|
|   e|    1|
|   d|    1|
+----+-----+

+----+-----+
|word|count|
+----+-----+
|   a|    4|
|   c|    3|
|   b|    3|
+----+-----+

```

## Использованная литература

[Structured Streaming Programming Guide](https://spark.apache.org/docs/2.4.7/structured-streaming-programming-guide.html) (Spark 2.4.7)
