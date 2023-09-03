# Конфигурация Spark на YARN
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требования
- Конфигурационные файлы
- Запуск кластера
- Запуск приложения
- Spark и Jupyter

## Требования

Для запуска необходимо установить следующее ПО:

- Ubuntu 14+
- Java 8
- Hadoop 3+
- Spark 2+
- [Optional] Anaconda Python 3.7
- Jupyter (для Scala и Python)
- Toree (для Scala kernel)

## Конфигурационные файлы

#### Директория Spark:

- `spark/bin/` - команды spark (`spark-submit`, `spark-shell`, `pyspark` etc.)
- `spark/sbin/` - скрипты для запуска/остановки Spark демонов
- `spark/conf/` - конфигурация
- `spark/logs/` - spark logs


#### Конфигурация Spark

Специальные файлы конфигурации Spark:

- `spark/conf/spark-env.sh` - файл содержит переменные среды, используемые командами и демонами Spark.
- `spark/conf/spark-defaults.conf` ([default values](https://spark.apache.org/docs/2.3.0/configuration.html)) - файл конфигурации кластера
- `spark/conf/slaves` - список Spark workers

Измените вышеупомянутые файлы конфигурации следующим образом:

`.profile`
```
# Spark configuration
export SPARK_HOME=$HOME/BigData/spark
export SPARK_CONF_DIR=$SPARK_HOME/conf
PATH=$SPARK_HOME/bin:$PATH
```

`spark-env.sh`

```
export SPARK_MASTER_HOST=localhost
export SPARK_EXECUTOR_MEMORY=1G # will be overriden by spark-defaults.conf
export PYSPARK_DRIVER_PYTHON=/home/ubuntu/ML/anaconda3/bin/python
export PYSPARK_PYTHON=/home/ubuntu/ML/anaconda3/bin/python

```

`spark-defaults.conf`

```
spark.master		yarn
spark.driver.cores	2
spark.driver.memory	1g

spark.executor.cores	1
spark.executor.memory	512m

spark.eventLog.enabled	true
spark.eventLog.dir file:///home/ubuntu/BigData/tmp/spark

spark.history.fs.logDirectory file:///home/ubuntu/BigData/tmp/spark
```

`slaves` (для автономного режима)

```
localhost
```

Переменные среды (например, `SPARK_HOME`) можно указать в:

- `$HOME/.profile` or `$HOME/.bashrc`
- `$SPARK_HOME/conf/spark-env.sh`
- `$SPARK_HOME/sbin/spark-config.sh` (для скриптов)

Или загрузить конфигурации динамически:
- Использование флагов командной строки (например, `--master`, `--conf` и т. д.) для `spark-submit`, `spark-shell`, `pyspark`
- Внутри кода приложения путем настройки конфигураций контекста 

## Запуск Spark на YARN кластере

Запустите `HDFS` и `YARN`

`$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh`

Запустите `History Server`

`$SPARK_HOME/sbin/start-history-server.sh`

Проверьте, все ли демоны запущены

`jps`


Веб-интерфейс:
- Порт диспетчера ресурсов YARN: `8088`
- Порт сервера истории Spark: `18080`
- Порт Spark Cluster: `8080` (для автономного режима кластера)

## Запуск простого приложения

#### Запуск приложенния Spark

`spark-submit --master yarn --class org.apache.spark.examples.JavaWordCount /usr/lib/spark/examples/jars/spark-examples_2.11-2.3.3.jar /data/yarn/reviews_Electronics_5_2.json /data/yarn/output`

#### Интерактивный режим Python

Введите в терминал следующую команду:

`pyspark`

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 2.3.3
      /_/

Using Python version 3.7.3 (default, Mar 27 2019 22:11:17)
SparkSession available as 'spark'.
>>> rdd_data = spark.sparkContext.parallelize(range(100))
>>> rdd_data.reduce(lambda x,y: x + y)
4950   
```


#### Интерактивный режим Scala

Введите в терминал следующую команду:

`spark-shell`

```
Spark context Web UI available at http://bigdata-VirtualBox:4040
Spark context available as 'sc' (master = yarn, app id = application_1571764860395_0015).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.3.3
      /_/
         
Using Scala version 2.11.8 (OpenJDK 64-Bit Server VM, Java 1.8.0_222)
Type in expressions to have them evaluated.
Type :help for more information.

scala> val rdd_data = sc.parallelize(0 to 99)
rdd_data: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[1] at parallelize at <console>:24

scala> rdd_data.reduce(_+_)
res1: Int = 4950
```

## Spark и Jupyter

### Python

#### Вариант 1

Создайте новую записную книжку Python и запустите ячейку со следующим кодом:

```python
import os
import sys

os.environ["SPARK_HOME"]="/home/ubuntu/BigData/spark"
os.environ["PYSPARK_PYTHON"]="/home/ubuntu/ML/anaconda3/bin/python"
os.environ["PYSPARK_DRIVER_PYTHON"]="/home/ubuntu/ML/anaconda3/bin/python"

spark_home = os.environ.get("SPARK_HOME")
sys.path.insert(0, os.path.join(spark_home, "python"))
sys.path.insert(0, os.path.join(spark_home, "python/lib/py4j-0.10.7-src.zip"))
```

#### Вариант 2

Создайте файл с содержимым, показанным ниже, чтобы подключить ядро `python` к `Jupyter`.

```json
{
    "display_name": "spark-python",
    "language_info": { "name": "python" },
    "codemirror_mode": "spark-python",
    "argv": ["/home/ubuntu/ML/anaconda3/bin/python", "-m", "ipykernel", "-f", "{connection_file}"],
    "env": {
        "SPARK_HOME": "/home/ubuntu/BigData/spark",
        "PYSPARK_PYTHON": "/home/ubuntu/ML/anaconda3/bin/python",
        "PYSPARK_DRIVER_PYTHON": "/home/ubuntu/ML/anaconda3/bin/python",
        "PYTHONPATH": "/home/ubuntu/BigData/spark/python:/home/ubuntu/BigData/spark/python/lib/py4j-0.10.7-src.zip"
     }
}
```

Каталог, в котором должен находиться файл:

`$HOME/.local/share/jupyter/kernels/spark-python/kernel.json`

Запустите `Jupyter` и выберите ядро `spark-python`

## Рекомендации 

- [Running Spark on YARN](https://spark.apache.org/docs/2.3.0/running-on-yarn.html)
