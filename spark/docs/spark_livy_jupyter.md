# Spark и Jupyter при помощи Livy в качестве REST-сервера Spark 
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требование
- Сервер Livy
- Отправка заданий при помощи сервера Livy
- Jyputer при помощи Sparkmagic
	- Ядро PySpark	
	- Ядро Scala
- Рекомендации

## Сервер Livy

Согласно [официальному сайту](https://livy.apache.org/):

> Apache Livy — это служба, которая позволяет легко взаимодействовать с кластером Spark через интерфейс REST. Он позволяет легко отправлять задания Spark или фрагменты кода Spark, получать синхронный или асинхронный результат, а также управлять Spark Context  через простой интерфейс REST или клиентскую библиотеку RPC. Apache Livy также упрощает взаимодействие между Spark и серверами приложений, что позволяет использовать Spark для интерактивных веб-приложений и мобильных приложений.

![alt Livy Architecture](https://livy.apache.org/assets/images/livy-architecture.png "Livy Architecture")

#### Установка и запуск Livy

Скачать сервер `Livy` :

`wget -P ~/livy/ http://apache-mirror.rbc.ru/pub/apache/incubator/livy/0.6.0-incubating/apache-livy-0.6.0-incubating-bin.zip`

Распаковать архив:

`sudo unzip ~/livy/apache-livy-0.6.0-incubating-bin.zip -d /opt`

Изменить конфигурационный файл `livy.conf` . Файл располагается в директории `/opt/apache-livy-0.6.0-incubating-bin/conf` . Добавьте следующие строки, которые активируют опцию YARN для сервера:

```
# What spark master Livy sessions should use.
livy.spark.master = yarn

# What spark deploy mode Livy sessions should use.
livy.spark.deploy-mode = cluster
```
Запуск сервера `Livy`:

`/opt/apache-livy-0.6.0-incubating-bin/bin/livy-server`


## Отправка заданий при помощи сервера Livy

Dashboard сервера `Livy` расположен на `port`: `8998`

Отправка на приложение Spark

*Request*

`POST http://localhost:8998/batches`

*Body*
```json
{ 
	"className": "edu.classes.spark.WordCount",
	"args": ["/data/yarn/samples_100.json", "/data/yarn/output"], 
	"file": "/data/jars/word-count-java-app-2.0.jar"
}
```

*Response*

```json
{
    "id": 6,
    "name": null,
    "state": "starting",
    "appId": null,
    "appInfo": {
        "driverLogUrl": null,
        "sparkUiUrl": null
    },
    "log": [
        "stdout: ",
        "\nstderr: ",
        "\nYARN Diagnostics: "
    ]
}
```

Полученик статуса

*Request*

`GET http://localhost:8998/batches/6/state`

*Response*

```json
{
    "id": 6,
    "state": "running"
}
```

Получение логов

*Request*

`GET http://localhost:8998/batches/6/log`

*Response*

```json
{
    "id": 6,
    "from": 0,
    "total": 40,
    "log": [
        "stdout: ",
		...
	]
}

```
Проверка результатов при помощи `WebHDFS` REST API (see [docs](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#Create_and_Write_to_a_File))

*Request*

`GET http://localhost:9870/webhdfs/v1/data/yarn/output/?user.name=bigdata&op=LISTSTATUS`

*Response*

```json
{
    "FileStatuses": {
        "FileStatus": [
            {
                "accessTime": 1573077801331,
                "blockSize": 134217728,
                "childrenNum": 0,
                "fileId": 18713,
                "group": "supergroup",
                "length": 0,
                "modificationTime": 1573077801396,
                "owner": "bigdata",
                "pathSuffix": "_SUCCESS",
                "permission": "644",
                "replication": 1,
                "storagePolicy": 0,
                "type": "FILE"
            },
            {
                "accessTime": 1573077800180,
                "blockSize": 134217728,
                "childrenNum": 0,
                "fileId": 18712,
                "group": "supergroup",
                "length": 12923,
                "modificationTime": 1573077800762,
                "owner": "bigdata",
                "pathSuffix": "part-00000",
                "permission": "644",
                "replication": 1,
                "storagePolicy": 0,
                "type": "FILE"
            },
            {
                "accessTime": 1573077800113,
                "blockSize": 134217728,
                "childrenNum": 0,
                "fileId": 18710,
                "group": "supergroup",
                "length": 12453,
                "modificationTime": 1573077800850,
                "owner": "bigdata",
                "pathSuffix": "part-00001",
                "permission": "644",
                "replication": 1,
                "storagePolicy": 0,
                "type": "FILE"
            }
        ]
    }
}
```
Другие REST API команды можно найти [здесь](http://livy.incubator.apache.org/docs/latest/rest-api.html).

###

## Jyputer при помощи Sparkmagic

Как указано на странице github [`sparkmagic` project](https://github.com/jupyter-incubator/sparkmagic):

> Sparkmagic — это набор инструментов для интерактивной работы с удаленными кластерами Spark через Livy, REST-сервер Spark, в ноутбуках Jupyter. Проект Sparkmagic включает набор инструментов для интерактивного запуска кода Spark на нескольких языках, а также несколько ядер, которые можно использовать для превращения Jupyter в интегрированную среду Spark.

#### Установка Sparkmagic

`pip install sparkmagic` [опционно `--user`]

```
Successfully installed autovizwidget-0.13.1 hdijupyterutils-0.13.1 plotly-4.2.1 pykerberos-1.2.1 requests-kerberos-0.12.0 retrying-1.3.3 sparkmagic-0.13.1
```

`/home/bigdata/.sparkmagic/config.json`

```json
{
	"session_configs": {
	    "driverMemory": "1G",
	    "executorCores": 1,
	    "executorMemory": "512M",
	    "proxyUser": "bigdata",
	    "conf": {
            "spark.master": "yarn-cluster",
            "spark.eventLog.enabled": "true",
            "spark.eventLog.dir": "file:///tmp/spark-events"
	    }
	}
}
```

### Ядро PySpark

`pip show sparkmagic`

```
Name: sparkmagic
Version: 0.13.1
Summary: SparkMagic: Spark execution via Livy
Home-page: https://github.com/jupyter-incubator/sparkmagic
Author: Jupyter Development Team
Author-email: jupyter@googlegroups.org
License: BSD 3-clause
Location: /home/bigdata/.local/lib/python3.7/site-packages
Requires: ipython, notebook, mock, requests-kerberos, hdijupyterutils, ipywidgets, numpy, requests, pandas, ipykernel, tornado, nose, autovizwidget
Required-by:
```

`jupyter-kernelspec install sparkmagic/kernels/pysparkkernel` [опционно `--user`]

```
[InstallKernelSpec] Installed kernelspec pysparkkernel in /home/bigdata/.local/share/jupyter/kernels/pysparkkernel
```

#### Для Python 3

Измените файл ниже, чтобы назначить python 3 вместо 2

`/home/bigdata/.local/share/jupyter/kernels/pysparkkernel/pysparkkernel.py`

```python
language_info = {
    'name': 'pyspark',
    'mimetype': 'text/x-python',
    'codemirror_mode': {'name': 'python', 'version': 3},
    'pygments_lexer': 'python3'
}
```

#### 

## Язык Spark

`jupyter-kernelspec install /home/bigdata/.local/lib/python3.7/site-packages/sparkmagic/kernels/sparkkernel`


#### 

## Рекомендации

[Configure Livy with Spark Modes](https://mapr.com/docs/61/Hue/Configure_Livy_Spark_Modes.html)

[Apache Livy: Getting Started](https://livy.apache.org/get-started/)

[Submitting Spark Applications Through Livy](https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/running-spark-applications/content/submitting_spark_applications_through_livy.html)