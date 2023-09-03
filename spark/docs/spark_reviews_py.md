# Spark и обработка отзывов клиентов
## Часть 2. Самостоятельное приложение (Python)
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требование
- Конфигурация
- Установка плагина `Python` для `IntelliJ`
- Создание проекта `Python`
- Исходный код
- Запуск приложения Spark в IDE
- Запуск приложения Spark при помощи `spark-submit`
- Запуск приложения Spark на YARN
- Рекомендации

## Требования

Для выполнения необходимо установить следующее ПО:

- Установить Ubuntu 14+ (with Python 3.x)
- Установить Java 8
- Установить Hadoop 3+
- Установить Spark 2+
- Установить IntelliJ 2019+
- (Опционально) Установить PyCharm 2019+ (для кода Python)


## Installing `Python` plugin for `IntelliJ`

`File` -> `Settings` -> `Plugins` -> Найти плагин `Python Community Edition` для `JetBrains` -> Выберите `Install` -> Перезапустите IDE

## Создайте проект `Python` 

`File` -> `New` -> `Project...` -> `Python` -> Next ->  Name: `reviewsparkapp` - > Finish

## Набор данных

- [Small subset of reviews](../data/spark-rdd-intro/samples_100.json)
- [Amazon product datasets](http://jmcauley.ucsd.edu/data/amazon/links.html)

## Исходный код

1. [Счетчик слов текста оценок](../code/python/reviewsparkapp/wcount_reviews.py)

Фрагмент кода

```python
...

def extract_words(items):
    """
    Extract words from a review text

    :param items:   records of a partition
    :return:
    """
    import json
    for item in items:
        try:
            for word in json.loads(str(item))["reviewText"].split(" "):
                yield (word, 1)
        except:
            pass


def main(input_file, output_path):
    """
    Entrypoint to the application

    :param input_file: the 1st input argument
    :param output_path: the 2nd input argument
    :return:
    """

    if not input_file or not output_path:
        raise Exception("Wrong input arguments.")

    sc = create_spark_context()

    # Count words
    wcount_rdd = sc.textFile(input_file)\
        .mapPartitions(extract_words)\
        .reduceByKey(lambda v1, v2: v1 + v2)\
        .sortBy(lambda x: -x[1])\
        .map(lambda x: "{}\t{}".format(x[0], x[1]))\
        .coalesce(1)

    # Save the result
    wcount_rdd.saveAsTextFile(output_path)
    sc.stop()

...
```

2. [Средний рейтинг продукта](../code/python/reviewsparkapp/avgratings_reviews.py)

Фрагмент кода

```python
...

def extract_prod_rating_per_partition(items):
    """
    Extract words from a review text

    :param items:   records of a partition
    :return:
    """
    import json
    for item in items:
        try:
            review = json.loads(item)
            yield review["asin"], float(review["overall"])
        except:
            pass


def main(input_file, output_path):
    """
    Entrypoint to the application

    :param input_file: the 1st input argument
    :param output_path: the 2nd input argument
    :return:
    """

    if not input_file or not output_path:
        raise Exception("Wrong input arguments.")

    sc = create_spark_context()

    # Calculate average ratings
    avg_prod_rating_rdd = sc.textFile(input_file)\
        .mapPartitions(extract_prod_rating_per_partition)\
        .aggregateByKey((0,0),
                        lambda x, value: (x[0] + value, x[1] + 1),
                        lambda x, y: (x[0] + y[0], x[1] + y[1]))\
        .map(lambda x: "{}\t{}".format(x[0], x[1][0]/x[1][1]))\
        .coalesce(1)

    # Save the result
    avg_prod_rating_rdd.saveAsTextFile(output_path)
    sc.stop()
...
```

3. Тестовый класс: `TODO`

## Запуск приложения Spark в IDE

Добавить модули Spark:

`File` -> `Project Structure...` -> `Project Settings` -> `Modules` -> `Add Content Root` -> `$SPARK_HOME/python` и `$SPARK_HOME/python/lib/py4j-0.10.7-src.zip` -> `Apply` + `OK`

Создайте конфигурацию для запуска

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` for Application -> Name: `wordcount`
3) Путь к скрипту: `/YOUR_LOCAL_PATH/reviewsparkapp/wcount_reviews.py`
4) Program arguments: `INPUT_LOCAL_FILE OUTPUT_LOCAL_DIR`, e.g. `file:///YOUR_PATH/samples_100.json file:///YOUR_PATH/output` для локальной файловой системы
5) Environment variable: `PYTHONUNBUFFERED=1;PYSPARK_PYTHON=/home/ubuntu/ML/anaconda3/bin/python;PYSPARK_DRIVER_PYTHON=/home/ubuntu/ML/anaconda3/bin/python;SPARK_MASTER=local[2]`
6) Рабочая директория: `/YOUR_LOCAL_PATH/reviewsparkapp`
7) `Apply` -> `OK`
8) `Run` -> `Run...` -> Выберите конфигурацию


Выходной каталог выглядит следующим образом:

```shell
output
├── part-00000
├── .part-00000.crc
├── _SUCCESS
└── ._SUCCESS.crc
```

Первые несколько строк из `part-00000`:
```
the	460
to	304
a	265
I	253
and	210
	192
it	187
is	130
of	127
for	113
```

Проделайте те же действия для приложения со средним рейтингом, и вы получите следующий результат:

```shell
output
├── part-00000
├── .part-00000.crc
├── _SUCCESS
└── ._SUCCESS.crc
```

Первые несколько строк из `part-00000`:
```
0972683275	4.390243902439025
0528881469	2.4
0594451647	4.2
0594481813	4.0
```

## Запустить приложение Spark используя `spark-submit`

Примечание. Вы также можете использовать HDFS.

Запустите приложение spark:

```
spark-submit --master local[2] \
    wcount_reviews.py \
    file:///YOUR_LOCAL_PATH/samples_100.json \
    file:///YOUR_LOCAL_PATH/output
```

Первые несколько строк из `part-00000`:

```
the	460
to	304
a	265
I	253
and	210
	192
it	187
is	130
of	127
for	113
```

## Запуск приложения Spark на YARN

#### Запуск Hadoop кластера

Запуск `HDFS`:

`$HADOOP_HOME/sbin/start-dfs.sh`

Запуск `YARN`:

`$HADOOP_HOME/sbin/start-yarn.sh`

Запуск `History Server`:

`$SPARK_HOME/sbin/start-history-server.sh`

Или все одной командой:

`$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh && $SPARK_HOME/sbin/start-history-server.sh`

Проверьте, все ли демоны запущены

`jps`


#### Запуск приложения

При необходимости создайте каталог в HDFS для входных данных:

`hdfs dfs -mkdir -p /data/reviews`

При необходимости добавьте отзывы в HDFS:

`hdfs dfs -copyFromLocal YOUR_LOCAL_FILE /data/reviews`

При необходимости удалите выходной каталог:

`hdfs dfs -rm -r -f /data/reviews/output`

Запуск job:

```
spark-submit --master yarn --deploy-mode cluster --name ReviewPySparkClusterApp \
    wcount_reviews.py \
    /data/reviews/samples_100.json \
    /data/reviews/output
```


Job вывод:

`hdfs dfs -head /data/yarn/output/part-00000`

```
the     460
to      304
a       265
I       253
and     210
        192
it      187
is      130
of      127
for     113
...
```

Запуск второго задания:

```
spark-submit --master yarn --deploy-mode cluster --name ReviewPySparkClusterApp \
    avgratings_reviews.py \
    /data/yarn/samples_100.json \
    /data/yarn/output
```

Параметры:
- `--executor-memory 1g`
- `--executor-cores 2`
- `--num-executors 4`


Job вывод:

`hdfs dfs -head /data/yarn/output/part-00000`

```
0972683275      4.390243902439025
0528881469      2.4
0594451647      4.2
0594481813      4.0
```
