### ДЗ предварительная инструкция

1) Скачать и установить Idea Community - https://www.jetbrains.com/idea/download/#section=windows
2) Установить плагин Скала
3) Скачать и установить Java JDK 11 - https://www.oracle.com/java/technologies/javase-jdk11-downloads.html
4) Скачать и установить git - https://git-scm.com/downloads
5) Скачать и учтановить локально дистрибутив Hadoop (инструкция для Windows - https://www.datasciencecentral.com/profiles/blogs/how-to-install-and-run-hadoop-on-windows-for-beginners )
6) Cкачать стартовый проект с Гитхаб c помощью команды
7) git clone https://github.com/vadopolski/otus-hadoop-homework
8) Запустить Idea и открыть скаченный проект File -> Open -> project folder/build.sbt
9) Открыть в проекте  файл src/main/scala/homework2/DataApiHomeWorkTaxi.scala
10) запустить его, Ctrl + Shift10
11) Скачать и установить docker-compose
12) Из корневой папки проекта запустить сделать запуск - docker-compose up

cd ..
docker-compose exec broker kafka-console-consumer.sh --bootstrap-server localhost:29092 --topic input


docker-compose exec kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic input

docker-compose exec create-topics kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic input


docker-compose exec broker -ti bash

find /  -name 'kafka-console-consumer.*'


find . -type f -name 'kafka-console-consumer.*'


### ДЗ основная инструкция и задания к занятию по Spark Data API:

**Цель:** Выполнив домашнее задание Вы получите опыт работы с RDD API, DataFrame API,Dataset API. Научитесь строить аналитическую витрину на основе сырых данных, используя Spark и различные API.

#### Основная инструкция задание 1:
Загрузить данные в первый DataFrame из файла с фактическими данными поездок в Parquet (src/main/resources/data/yellow_taxi_jan_25_2018).
Загрузить данные во второй DataFrame из файла со справочными данными поездок в csv (src/main/resources/data/taxi_zones.csv)
С помощью DSL построить таблицу, которая покажет какие районы самые популярные для заказов. Результат вывести на экран и записать в файл Паркет.

**Результат:**
В консоли должны появиться данные с результирующей таблицей, в файловой системе должен появиться файл.
Решение оформить в github gist.


#### Основная инструкция задание 2:
Загрузить данные в RDD из файла с фактическими данными поездок в Parquet (src/main/resources/data/yellow_taxi_jan_25_2018).
С помощью lambda построить таблицу, которая покажет В какое время происходит больше всего вызовов. Результат вывести на экран и в txt файл c пробелами.

**Результат:**
В консоли должны появиться данные с результирующей таблицей, в файловой системе должен появиться файл.
Решение оформить в github gist.


#### Основная инструкция задание 3:
Загрузить данные в DataSet из файла с фактическими данными поездок в Parquet (src/main/resources/data/yellow_taxi_jan_25_2018).
С помощью DSL и lambda построить таблицу, которая покажет. Как происходит распределение поездок по дистанции? Результат вывести на экран и записать в бд Постгрес (докер в проекте). Для записи в базу данных необходимо продумать и также приложить инит sql файл со структурой.

_(Пример: можно построить витрину со следующими колонками: общее количество поездок, среднее расстояние, среднеквадратическое отклонение, минимальное и максимальное расстояние)_


**Результат:**
В консоли должны появиться данные с результирующей таблицей, в бд должна появиться таблица.
Решение оформить в github gist.


### ДЗ основная инструкция и задания к занятию по Spark Testing:
!!!!! ВНИМАНИЕ, для корректной работы необходимо сделать reimport dependency 

**Цель:** Выполнив домашнее задание научитесь писать авто тесты для Спарк джобов.

#### Основная инструкция задание 1:
Логически разбить на методы, написанный в домашнем задании к занятию Spark Data API. Пример `src/main/scala/lesson2/OtusFragmentedByMethod.scala` 

**Результат:**
В репозитории должен появиться код с описанием методов.
Решение оформить в github.

#### Основная инструкция задание 2:
Сформировать ожидаемый результат и покрыть простым тестом (с библиотекой AnyFlatSpec) витрину из домашнего задания к занятию Spark Data API, построенную с помощью RDD. 
Пример `src/test/scala/lesson2/SimpleUnitTest.scala`

**Результат:**
В репозитории должен появиться код с тестом. Тест должен успешно выполняться при запуске.
Решение оформить в github.

#### Основная инструкция задание 3:
Сформировать ожидаемый результат и покрыть Spark тестом (с библиотекой SharedSparkSession) витрину из домашнего задания к занятию Spark Data API, построенную с помощью DF и DS. 
Пример `src/test/scala/lesson2/TestSharedSparkSession.scala`  

**Результат:**
В репозитории должен появиться код с тестом. Тест должен успешно выполняться при запуске.
Решение оформить в github.



### ДЗ основная инструкция и задания к занятию по Flink:
!!!!! ВНИМАНИЕ, для корректной работы необходимо сделать reimport dependency 


docker system prune -a --volumes

docker exec -ti 

CASSANDRA

nodetool status

nodetool tpstats

nodetool flush
