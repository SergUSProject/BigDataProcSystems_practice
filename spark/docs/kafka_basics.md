# Введение в распределенный брокер сообщений Kafka 
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требования
- Установка Zookeeper
- Установка Kafka
- Конфигурация Kafka
- Запуск Kafka
- Создание topic
- Тестирование при помощи консольных Producer и Consumer
- Быстрые команды для запуска

## Требования

Для запуска необходима установка следующег ПО:

- Установка Ubuntu 14+
- Установка Java 8

## Установка Zookeeper

Загрузите и распакуйте [`Zookeeper 3.5.8`](https://archive.apache.org/dist/zookeeper/zookeeper-3.5.8/apache-zookeeper-3.5.8-bin.tar.gz):

<!-- Install the server:

`apt install zookeeperd` -->

Вы можете запустить/остановить сервер с помощью следующих команд:

`$ZOOKEEPER_HOME/bin/zkServer.sh start | stop`

Показать версию сервера:

`echo stat | nc localhost 2181`

```
Zookeeper version: 3.4.5--1, built on 06/10/2013 17:26 GMT
Clients:
 /127.0.0.1:57312[0](queued=0,recved=1,sent=0)
```

После установки сервер Zookeeper будет запущен автоматически.

## Установка Kafka

Создайте каталог, в котором будет размещена `Kafka`:

`mkdir /opt/kafka`

Скачайте архив `Kafka`:

`wget -P ~/Downloads/ https://archive.apache.org/dist/kafka/2.3.0/kafka_2.11-2.3.0.tgz`

Здесь мы используем `Kafka` со `Scala` `2.11`, что соответствует версии `Scala` нашей установки `Spark`.

Распаковать архив:

`tar -xvzf ~/Downloads/kafka_2.11-2.3.0.tgz --directory /opt/kafka --strip-components 1`

## Конфигурация `Kafka`

#### Директории Kafka:

- `kafka/bin/` - команды kafka
- `kafka/config/` - конфигурация
- `kafka/logs/` - логи kafka

#### Конфигурация

`server.properties`

```bash
# The id of the broker. This must be set to a unique integer for each broker.
broker.id=0

# Zookeeper connection string (see zookeeper docs for details).
# This is a comma separated host:port pairs, each corresponding to a zk
# server. e.g. "127.0.0.1:3000,127.0.0.1:3001,127.0.0.1:3002".
# You can also append an optional chroot string to the urls to specify the
# root directory for all kafka znodes.
zookeeper.connect=localhost:2181

# The default number of log partitions per topic. More partitions allow greater
# parallelism for consumption, but this will also result in more files across
# the brokers.
num.partitions=1

# A comma separated list of directories under which to store log files
log.dirs=/opt/kafka/logs/data
```

## Запуск `Kafka`

Запуск сервера `kafka`:

`$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties`

## Создание topic

`$KAFKA_HOME/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --topic word-count`

```
Created topic word-count.
```

`sudo $ZOOKEEPER_HOME/bin/zkCli.sh`

```
Welcome to ZooKeeper!
JLine support is enabled
[zk: localhost:2181(CONNECTING) 0] 
```

`get /brokers/ids/0`

```
{"listener_security_protocol_map":{"PLAINTEXT":"PLAINTEXT"},"endpoints":["PLAINTEXT://bigdata-VirtualBox:9092"],"jmx_port":-1,"host":"bigdata-VirtualBox","timestamp":"1572980758106","port":9092,"version":4}
cZxid = 0xdd
ctime = Tue Nov 05 22:05:58 MSK 2019
mZxid = 0xdd
mtime = Tue Nov 05 22:05:58 MSK 2019
pZxid = 0xdd
cversion = 0
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x16e3c184ad30001
dataLength = 206
numChildren = 0
```

`quit`


## Тестирование при помощи консольных Producer and Consumer

Откройте новое окно терминала и выполните следующую команду, чтобы запустить консольный `Kafka` Consumer:

`$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic word-count --from-beginning`

В другом окне терминала запустите консольный `Kafka` Producer:

`$KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic word-count`

Введите текст в консоли Producer и примените его. В консоли Consumer вы должны увидеть текст, который вы применили в Producer:

## Быстрые команды для запуска

Запуск сервера `Zookeeper`:

`sudo $ZOOKEEPER_HOME/bin/zkServer.sh start`

Запуск сервера `Kafka`:

`sudo $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties`

В одну строку:
`$ZOOKEEPER_HOME/bin/zkServer.sh start & $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties`