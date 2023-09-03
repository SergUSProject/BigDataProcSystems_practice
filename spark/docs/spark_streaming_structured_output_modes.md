# Spark Structured Streaming: выполнение и обновление режимов вывода

Усовик С.В. (usovik@bmstu.ru)

## Содержание

- [Требования](#Требования)
- [Исходный код](#Исходный-код)
- [Запуск приложения](#Запуск-приложения)
    - [Полный режим и приемник консоли](#Полный-режим-и-приемник-консоли)
    - [Режим обновления и приемник консоли](#Режим-обновления-и-приемник-консоли)
    - [Полный режим и приемник ForeachBatch](#Полный-режим-и-приемник-ForeachBatch)
    - [Режим обновления и приемник ForeachBatch](#Режим-обновления-и-приемник-ForeachBatch)
- [Рекомендации](#Рекомендации)

## Требования

Для выполнения необходимо установить следующее ПО:

- Ubuntu 14+
- Java 8
- Anaconda (Python 3.7)
- Spark 2.4+
- IntelliJ 2019+ с Python Plugin или PyCharm 2019+


## Исходный код

- Приложение Spark Structured Streaming ([complete_update_streaming.py](../projects/structuredstreaming/complete_update_streaming.py))


## Запуск приложения



### Структура приложения


Главная функция:

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

Преобразование потока:

```python
def transformations(stream):
    """Count words."""
    return stream \
        .select(F.explode(F.split("value", " ")).alias("word")) \
        .groupBy("word") \
        .count()
```

### Полный режим и приемник консоли

Примечание. Вы не можете выполнять несколько запросов к одному источнику потока. Только первый получит данные и будет выполнен.

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

Откройте терминал и начните слушать порт 9999 для подключения нового клиента:

`nc -lk 9999`

Откройте другой терминал, чтобы запустить приложение park streaming. Выполните следующую команду:

```
spark-submit --master local[2] complete_update_mode.py -m complete -s console
```

Примечание. Приложение имеет две опции: mode (`-m`) и sink (`-s`).

В терминале с запущенной утилитой netcat введите следующий текст:

```
a a b c
b d e
```

Через некоторое время (через 10 секунд) введите еще текст:

```
a b c
a c
```

В итоге вы должны получить результат, похожий на этот:

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

Остановите приложение


### Режим обновления и приемник консоли

Повторите те же шаги, что и раньше, но используйте приведенную ниже команду, чтобы запустить приложение spark streaming :

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



### Полный режим и приемник ForeachBatch

Примечание. Каждая партия сортируется и ограничивается 4 лучшими записями.


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



### Режим обновления и приемник ForeachBatch

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

## Рекомендации

[Structured Streaming Programming Guide](https://spark.apache.org/docs/2.4.7/structured-streaming-programming-guide.html) (Spark 2.4.7)