# Введение в распределенный брокер сообщений Apache Kafka



## Содержание

- [Требования к установленному ПО](Требования-к-установленному-ПО)
- [Установка и запуск Kafka](#Установка-и-запуск-Kafka)
- [Конфигурация Kafka](#Конфигурация-Kafka)
- [Тестирование Kafka Producer и Consumer в консольном режиме](#Тестирование-Kafka-Producer-и-Consumer-в-консольном-режиме)
- [Ссылки](#Ссылки)

## 

## Требования к установленному ПО

Для успешного запуска необходима установка следующего программного обеспечения:

- ОС Linux
- Java 8+
- Опционно Docker

## 

## Установка и запуск Kafka

Скачать дистрибутив Apache Kafka можно [отсюда](https://kafka.apache.org/downloads).

Создайте каталог для установки`Kafka` :

```
mkdir /opt/kafka
```

Скачайте архив `Kafka` (например):

```bash
wget -P ~/Downloads/ https://archive.apache.org/dist/kafka/3.3.1/kafka_2.12-3.3.1.tgz
```

Здесь используется `Kafka` с `Scala` `2.12` (версия `Scala` должна совпадать с версией установленного `Spark`).

Распакуйте архив:

```bash
tar -xvzf ~/Downloads/kafka_2.12-3.3.1.tgz --directory /opt/kafka --strip-components 1
```

Инструкция по установке и запуску находится [здесь](https://kafka.apache.org/quickstart). 

Другим распространенным способом установки и запуска является развертывание Kafka через docker-compose командой `docker-compose up -d` в каталоге с файлом [docker-compose.yml](./docker-compose.yml).

Запуск сервиса Kafka необходимо производить в строго определенной последовательности. В одном терминале выполнить команду:   

```bash
# Start the ZooKeeper service
$KAFKA_HOME/bin/zookeeper-server-start.sh config/zookeeper.properties
```

В другом запустить:        

```bash
# Start the Kafka broker service
$KAFKA_HOME/kafka-server-start.sh config/server.properties
```

После успешного запуска всех служб базовая среда Kafka будет запущена и готова к использованию.        



## Конфигурация Kafka

#### Kafka дирректории:

- `kafka/bin/` - команды kafka
- `kafka/config/` - конфигурация
- `kafka/logs/` - логи kafka

#### Пример конфигурации

```
server.properties
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



#### Создание топика

Для создания топика на запущенном брокере Kafka откройте новый терминал и выполните следующую команду:

`$KAFKA_HOME/bin/kafka-topics.sh --create  --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1  --topic <topic_name>`

Запуск Kafka producer:

`$KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic <topic_name>`

Запуск Kafka consumer:

`$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <topic_name>`

Для просмотра всей информации о топиках необходимо использовать команду:

`$KAFKA_HOME/bin/kafka-topics.sh --describe --bootstrap-server localhost:9092`

Для просмотра всей информации о топиках необходимо использовать команду:

`$KAFKA_HOME/bin/kafka-topics.sh --list --bootstrap-server localhost:9092` 



## Тестирование Kafka Producer и Consumer в консольном режиме

Откройте окно нового терминала и выполните команду по запуску консольного producer Kafka:

`$KAFKA_HOME/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic <topic_name>`

В результате выполнения команды должно появиться приглашение для ввода символов с клавиатуры в консоль. 

Откройте окно нового терминала и выполните команду по запуску консольного consumer Kafka:

`$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <topic_name>`

Введите текст в консоли Producer. В консоли Consumer вы должны увидеть текст, который вы ввели в Producer.

Для просмотра всех данных, поступивших в топик необходимо выполнить команду:

`$KAFKA_HOME/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <topic_name> --from-beginning`

