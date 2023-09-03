# Web-служба при помощи Spark Streaming и Kafka
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- [Требования](#Требования)
- [Конфигурация Spark](#Конфигурация-Spark)
- [Конфигурация Kafka](#Конфигурация-Kafka)
- [Установка и запуск Redis](#Установка-и-запуск-Redis)
- [Web-служба](#Web-служба)
- [Запуск в качестве службы ОС](#Запуск-в-качестве-службы-ОС)
- [Приложение Spark Streaming](#Приложение-Spark-Streaming)
- [Развертывание Web-службы и приложение Spark Streaming](#Развертывание-Web-службы-и-приложение-Spark-Streaming)

## Требование

Общие:

- Ubuntu 14+
- Java 8
- Hadoop 3.2.0
- Spark 2.3
- Kafka 2.3.0
- Redis 5.0.6

Программирование Python (для `Spark Streaming App` и `Tweet Filter App`):
- PyCharm or IntelliJ 2019.2 with Python Plugin
- Python 3.7
- python-kafka (для Kafka)
- tweepy (для Twitter API)

Java coding (для `Web Service`):
- IntelliJ 2019.2
- Spring Boot starters 2.1.8
- Spring for Apache Kafka 2.2.0
- Spring Data Redis 2.1.8
- Jedis 2.9.3


## Конфигурация Spark

В этом руководстве конфигурация по умолчанию включает развертывание Spark в кластере YARN. Итак, вы должны настроить и запустить `HDFS` и `YARN`

Конфигурационные файлы вы можете найти [здесь](spark_basics.md).

## Конфигурация Kafka

В некоторых приведенных ниже примерах сервер Kafka требуется в качестве брокера сообщений, поэтому перейдите по [этой ссылке](kafka_basics.md), чтобы ознакомиться с инструкциями по установке, настройке и запуску Kafka.

## Установка и запуск Redis 

#### При помощи sudo

`apt install redis-server`

#### Без sudo

Загрузите релиз `Redis` :

`wget -P ~/redis/source http://download.redis.io/releases/redis-5.0.6.tar.gz`

Распаковать архив:

`tar -xvzf ~/redis/redis-5.0.6.tar.gz --directory ~/redis --strip-components 1`

Скомпилируйте `Redis`:

`cd ~/redis && make`

#### Запуск Redis-сервера

Запуск `Redis` -сервера:

`$REDIS_HOME/src/redis-server`

Чтобы проверить сервер, запустите CLI `Redis` и введите команду `PING`:

`$REDIS_HOME/src/redis-cli`

```
127.0.0.1:6379> PING
PONG
```

#### Python-клиент Redis


Установить `redis-py`:

`pip install redis --user` (опционно)



## Web-сервер

[Source code](../projects/webservice/service/WordCountService)

![Service Architecture Diagram](img/web_service_diagram.png "Service Architecture")
<center><i>Рисунок 1. Архитектура Web-сервиса</i></center>

```
./src
├── main
│   ├── java
│   │   └── edu
│   │       └── classes
│   │           └── spark
│   │               ├── Application.java
│   │               ├── configurations
│   │               │   ├── KafkaConfiguration.java
│   │               │   └── RedisConfiguration.java
│   │               ├── controllers
│   │               │   ├── WordCountAPIServiceController.java
│   │               │   └── WordCountWebServiceController.java
│   │               ├── models
│   │               │   ├── Message.java
│   │               │   └── WordCountPair.java
│   │               └── services
│   │                   ├── IWordCountService.java
│   │                   └── WordCountService.java
│   └── resources
│       ├── application.yml
│       ├── static
│       └── templates
│           ├── index.html
│           ├── top_words.html
│           └── word_counts.html
└── test
    └── java

```

#### Запуск Service

`mvn spring-boot:run`

Или создайте `jar`-файл и запустите службу следующим образом:

`java -jar ./target/wordcount-service-1.0.jar`

#### Создание jar

Создайте выполняемый `jar`-файл, чтобы запустить службу как отдельное приложение в контейнере Tomcat:

`mvn clean package`


```bash
[INFO] Scanning for projects...
[INFO] 
[INFO] ----------------< edu.classes.spark:wordcount-service >-----------------
[INFO] Building wordcount-service 1.0
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- maven-clean-plugin:3.1.0:clean (default-clean) @ wordcount-service ---
[INFO] 
[INFO] --- maven-resources-plugin:3.1.0:resources (default-resources) @ wordcount-service ---
[INFO] Using 'UTF-8' encoding to copy filtered resources.
[INFO] Copying 1 resource
[INFO] Copying 3 resources
[INFO] 
[INFO] --- maven-compiler-plugin:3.8.1:compile (default-compile) @ wordcount-service ---
[INFO] Changes detected - recompiling the module!
[INFO] Compiling 9 source files to /media/sf_Spark_Streaming/projects/webservice/service/WordCountService/target/classes
[INFO] 
[INFO] --- maven-resources-plugin:3.1.0:testResources (default-testResources) @ wordcount-service ---
[INFO] Using 'UTF-8' encoding to copy filtered resources.
[INFO] skip non existing resourceDirectory /media/sf_Spark_Streaming/projects/webservice/service/WordCountService/src/test/resources
[INFO] 
[INFO] --- maven-compiler-plugin:3.8.1:testCompile (default-testCompile) @ wordcount-service ---
[INFO] Changes detected - recompiling the module!
[INFO] 
[INFO] --- maven-surefire-plugin:2.22.2:test (default-test) @ wordcount-service ---
[INFO] 
[INFO] --- maven-jar-plugin:3.1.2:jar (default-jar) @ wordcount-service ---
[INFO] Building jar: /media/sf_Spark_Streaming/projects/webservice/service/WordCountService/target/wordcount-service-1.0.jar
[INFO] 
[INFO] --- spring-boot-maven-plugin:2.1.8.RELEASE:repackage (repackage) @ wordcount-service ---
[INFO] Replacing main artifact with repackaged archive
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  12.984 s
[INFO] Finished at: 2019-11-19T13:09:51+03:00
[INFO] ------------------------------------------------------------------------

```

Выходной jar-файл (`wordcount-service-1.0.jar`) имеет следующую структуру::

```
.
├── BOOT-INF
│   ├── classes
│   │   ├── application.yml
│   │   ├── edu
│   │   │   └── classes
│   │   │       └── spark
│   │   │           ├── Application.class
│   │   │           ├── configurations
│   │   │           ├── controllers
│   │   │           ├── models
│   │   │           └── services
│   │   └── templates
│   └── lib
├── META-INF
│   ├── MANIFEST.MF
│   └── maven
│       └── edu.classes.spark
│           └── wordcount-service
│               ├── pom.properties
│               └── pom.xml
└── org
    └── springframework
        └── boot
            └── loader
```


Файл `MANIFEST.MF` выглядит как:

```
Manifest-Version: 1.0
Implementation-Title: wordcount-service
Implementation-Version: 1.0
Start-Class: edu.classes.spark.Application
Spring-Boot-Classes: BOOT-INF/classes/
Spring-Boot-Lib: BOOT-INF/lib/
Build-Jdk-Spec: 1.8
Spring-Boot-Version: 2.1.8.RELEASE
Created-By: Maven Archiver 3.4.0
Main-Class: org.springframework.boot.loader.JarLauncher
```

## Запуск в качестве службы ОС


#### Upstart (для Ubuntu 14.04)

Создайте файл конфигурации `/etc/init/wordcount-service.conf` со следующим содержанием:

```bash
description "Word Count Web Service"

# run processes on behalf of the bigdata user 
setuid bigdata

start on runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5 # by default

# command to execute
exec /media/sf_Spark_Streaming/projects/webservice/service/WordCountService/target/wordcount-service-1.0.jar
```

Запустите службу с помощью команды `start`:

`sudo service wordcount-service start | stop | restart`

Показать информацию о состоянии выполнения:

`sudo service wordcount-service status`


Проверьте, запущена ли служба:

`jps`

```
6948 wordcount-service-1.0.jar
7117 Jps
```

Журналы можно найти следующим образом:

`sudo cat /var/log/upstart/wordcount-service.log`

или

`tail -n 100 /var/log/syslog`


#### Systemd (для Ubuntu 16+)

Создайте файл конфигурации `/etc/systemd/system/wordcount-service.service` со следующим содержанием:

```ini
[Unit]
Description=Word Count Web Service
After=syslog.target

[Service]
Type=simple
User=bigdata
ExecStart=/media/sf_Spark_Streaming/projects/webservice/service/WordCountService/target/wordcount-service-1.0.jar
Restart=always
RestartSec=4

[Install]
WantedBy=multi-user.target
```

Запустите службу с помощью команды `start`:

`sudo systemctl start | stop | restart wordcount-service`

Если вы меняете файл конфигурации (`*.service`), вы должны перезагрузить демон:

`sudo systemctl daemon-reload`

Затем перезапустите службу:

`sudo systemctl restart wordcount-service`

Показать информацию о состоянии выполнения:

`sudo systemctl status wordcount-service`

Журналы можно найти следующим образом:

`journalctl --no-pager -u wordcount-service`

или

`tail -n 100 /var/log/syslog`

## Twitter API

![Service Architecture Diagram](img/web_service_twitter_diagram.png "Service Architecture")
<center><i>Рисунок 2. Добавление Kafka producer с помощью Twitter API </i></center>

## Приложение Spark Streaming

#### Kafka consumer

Примените потребителя Kafka в качестве источника ввода. Ниже приведен фрагмент кода, иллюстрирующий использование Kafka внутри приложения Spark Streaming. Полный исходный код доступен [здесь](../projects/webservice/sparkstreaming)

```python
import json

from pyspark.streaming.kafka import KafkaUtils


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "wordcount"

# Create subscriber (consumer) to the Kafka topic
kafka_stream = KafkaUtils.createDirectStream(ssc, 
                                             topics=[KAFKA_TOPIC],
                                             kafkaParams={"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

# Extract a content of messages from Kafka topic stream (per mini-batch)
lines = kafka_stream.map(lambda x: json.loads(x[1])["content"])

```

#### Redis-клиент

```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_CHARSET = "utf-8"
REDIS_DECODE_RESPONSES = True

REDIS_KEY_WORD_COUNT = "count_word"
REDIS_KEY_TOP_10_WORD = "top_10_words"

def save_partition_in_redis(partition):
    """
    Insert/update word count pairs in Redis for each partition

    Note: minus for the count variable in r.zadd() is a workaround to
    guarantee lex ordering when word counts have the same value.
    The sign should be removed when consume this Redis sorted set.
    """
    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset=REDIS_CHARSET, decode_responses=REDIS_DECODE_RESPONSES)
    for row in partition:
        r.zadd(REDIS_KEY_WORD_COUNT, {row[0]: -row[1]})


def save_rdd_in_redis(time, rdd):
    """Insert/update word count pairs in Redis"""
    rdd.foreachPartition(save_partition_in_redis)


def save_top_10_in_redis(time, rdd):
    """
    Insert/update top 10 words

    Note: minus for the count variable in r.zadd() is a workaround to
    guarantee lex ordering when word counts have the same value.
    The sign should be removed when consume this Redis sorted set.
    """
    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset=REDIS_CHARSET, decode_responses=REDIS_DECODE_RESPONSES)
    r.delete(REDIS_KEY_TOP_10_WORD)
    top_10_words = rdd.takeOrdered(10, key=lambda x: -x[1])
    for word, count in top_10_words:
        r.zadd(REDIS_KEY_TOP_10_WORD, {word: -count})


# Save word counts in redis (job 1)
total_counts.foreachRDD(save_rdd_in_redis)

# Save top 10 words in redis (job 2)
total_counts.foreachRDD(save_top_10_in_redis)
```


## Развертывание Web-службы и приложение Spark Streaming

#### Запуск HDFS и Spark на YARN

Запуск `HDFS` и `YARN`

`$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh`

Запуск `History Server`

`$SPARK_HOME/sbin/start-history-server.sh`

Проверьте, все ли демоны запущены

`jps`

Web UI:
- YARN Resource Manager port: `8088`
- Spark History Server port: `18080`
- Spark Cluster port: `8080` (for standalone cluster mode)

#### Запуск Kafka-сервера

Запуск сервера `Zookeeper`:

`$ZOOKEEPER_HOME/bin/zkServer.sh start`

Запуск сервера `Kafka`:

`$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties`

#### Запуск сервера Redis

`$REDIS_HOME/src/redis-server`

#### Отправка приложения Spark Streaming

Ранее мы настроили Spark для запуска на `YARN`. Таким образом, следующая команда по умолчанию запускает приложение потоковой передачи искры на `YARN`:

`spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 wordcount_streaming.py`

Для локального запуска используйте следующую команду:

`spark-submit --master local[2] --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 wordcount_spark_streaming.py`

#### Запуск Web-службы

Запустите/остановите веб-сервис как управляемый процесс командой (см. конфигурацию выше):

`sudo service wordcount-service start | stop | restart` (для Ubuntu 14.04)

или

`sudo systemctl start | stop | restart wordcount-service` (для Ubuntu 16+)

Вы также можете запустить его как неуправляемый процесс следующим образом:

`java -jar ./target/wordcount-service-1.0.jar`


```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.1.8.RELEASE)


......


2019-11-19 13:36:51.407  INFO 9475 --- [           main] edu.classes.spark.Application            : Started Application in 9.698 seconds (JVM running for 10.986)
2019-11-19 13:37:08.348  INFO 9475 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2019-11-19 13:37:08.349  INFO 9475 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2019-11-19 13:37:08.391  INFO 9475 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed initialization in 42 ms
```

Чтобы остановить запущенный сервис, вы можете нажать `CTRL-C` или узнать его `PID` с помощью команды:

`jps`

И убить процесс:

`kill PID`


# Рекомендации

[How To Install and Secure Redis on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04)

[An introduction to Redis data types and abstractions](https://redis.io/topics/data-types-intro)

[Spark Streaming Programming Guide](https://spark.apache.org/docs/2.3.0/streaming-programming-guide.html)

[PySpark Streaming Module API](https://spark.apache.org/docs/2.3.0/api/python/pyspark.streaming.html)

[Jedis](https://github.com/xetorthio/jedis)

[Spring Data Redis](https://docs.spring.io/spring-data/data-redis/docs/current/reference/html/#reference)
