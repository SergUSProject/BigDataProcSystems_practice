# Расчет среднего рейтинга на основе пользовательских счетчиков
Усовик С.В. (usovik@bmstu.ru)



## Разделы:

- [Требования](#Требования)
- [Конфигурация](#Конфигурация)
- [Поток вычислений](#Поток-вычислений)
- [Создание Java-проекта в IntelliJ](#Создание-Java-проекта-в-IntelliJ)
- [Исходный код на Java](#Исходный-код-на-Java)
- [Запуск MapReduce с локальными файлами](#Запуск-MapReduce-с-локальными-файлами)
- [Построение `jar`-файла с `maven`](#Построение-`jar`-файла-с-`maven`)
- [Запуск MapReduce `jar`-файла на кластере YARN](#Запуск-MapReduce-`jar`-файла-на-кластере-YARN)

## Конфигурация

Для запуска необходимо установить следующее ПО:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)

## Конфигурация

Смотрите [Введение в MapReduce](mapreduce_basics.md)

## Поток вычислений 

<center>

![MapReduce Computation Flow](img/mapreduce_average.jpg "MapReduce Flow")

</center>

## Создание Java-проекта в IntelliJ

1) Open IntelliJ
2) `Create New Project` или `File` -> `Project...`
3) Выберите Maven and project SDK 1.8 -> `Next`
4) GroupId: `edu.classes.mr`; ArtifactId: `average-rating-app` -> `Next`
4) Project name: AverageRatingApp -> `Finish`

## Исходный код на Java

1. [pom.xml](../projects/java/AverageRatingApp/pom.xml)

2. [Review model class](../projects/java//AverageRatingApp/src/main/java/edu/classes/mr/Review.java)

3. [Custom writable class](../projects/java/AverageRatingApp/src/main/java/edu/classes/mr/StatsTupleWritable.java)

4. [Enum for json parsing result](../projects/java/AverageRatingApp/src/main/java/edu/classes/mr/ReviewState.java)

5. [Driver class](../projects/java/AverageRatingApp/src/main/java/edu/classes/mr/AvgRatingDriver.java)

6. [Mapper class](../projects/java/AverageRatingApp/src/main/java/edu/classes/mr/AvgRatingMapper.java)

7. [Reducer class](../projects/java/AverageRatingApp/src/main/java/edu/classes/mr/AvgRatingReducer.java)

   

## Запуск MapReduce с локальными файлами

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` for Application
3) Main class: `edu.classes.mr.AvgRatingDriver` - (class with the main method)
4) Program arguments: `INPUT_LOCAL_FILE OUTPUT_LOCAL_DIR`
5) `Apply` -> `OK`
6) `Run` -> `Run...` -> Choose your configuration

Содержимое выходного файла (`part-r-00000`):

```
0528881469	2.4
0594451647	4.2
0594481813	4.0
0972683275	4.390243902439025
```

## Построение `jar`-файла с `maven`

Перейдите на панель maven, найдите папку `Plugins`  -> `jar` -> `jar:jar`. После завершения, актуальный `jar`-файл будет расположен в целевом каталоге.

Вы можете создать `jar`-файл в качестве артефакта, как описано [здесь](mapreduce_scala.md).


## Запуск MapReduce `jar`-файла на кластере YARN

#### Запустить кластер Hadoop

Запустить `HDFS`:

`$HADOOP_HOME/sbin/start-dfs.sh`

Запустить `YARN`:

`$HADOOP_HOME/sbin/start-yarn.sh`

Запустить Job History Server:

`mapred --daemon start historyserver`

Или все одной командой:

`$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh && mapred --daemon start historyserver`

Проверьте, все ли демоны запущены:

`jps`

#### Запуск приложения

Удалите выходной каталог, если это необходимо:

`hdfs dfs -rm -r -f /data/yarn/output`

Запустить задание:

`yarn jar /PATH/average-rating-app-1.1.jar -D mapreduce.job.reduces=2 /data/yarn/reviews.json /data/yarn/output`

Результат работы:

```
INFO input.FileInputFormat: Total input files to process : 1
INFO mapreduce.JobSubmitter: number of splits:11
INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1572261301516_0001
INFO mapreduce.Job: Running job: job_1572261301516_0001
INFO mapreduce.Job: Job job_1572261301516_0001 running in uber mode : false
INFO mapreduce.Job:  map 0% reduce 0%
INFO mapreduce.Job:  map 13% reduce 0%
INFO mapreduce.Job:  map 22% reduce 0%
INFO mapreduce.Job:  map 55% reduce 9%
INFO mapreduce.Job:  map 73% reduce 12%
INFO mapreduce.Job:  map 86% reduce 14%
INFO mapreduce.Job:  map 91% reduce 15%
INFO mapreduce.Job:  map 100% reduce 33%
INFO mapreduce.Job:  map 100% reduce 50%
INFO mapreduce.Job:  map 100% reduce 100%
INFO mapreduce.Job: Job job_1572261301516_0001 completed successfully
```

Счетчики

```
INFO mapreduce.Job: Counters: 59
        File System Counters
                FILE: Number of bytes read=1575287
                FILE: Number of bytes written=5963087
                ...
                HDFS: Number of bytes read=1479007457
                HDFS: Number of bytes written=1483763
                ....
        Job Counters 
                Killed map tasks=2
                Launched map tasks=11
                Launched reduce tasks=2
                Data-local map tasks=11
                Total time spent by all maps in occupied slots (ms)=264951
                Total time spent by all reduces in occupied slots (ms)=82606
                ...
        Map-Reduce Framework
                Map input records=1689188
                Map output records=1689188
                Map output bytes=38851324
                Map output materialized bytes=1575407
                Input split bytes=1199
                Combine input records=1689188
                Combine output records=63011
                Reduce input groups=63001
                Reduce shuffle bytes=1575407
                Reduce input records=63011
                Reduce output records=63001
                Spilled Records=126022
                Shuffled Maps =22
                Failed Shuffles=0
                Merged Map outputs=22
                GC time elapsed (ms)=4258
                CPU time spent (ms)=85410
                Physical memory (bytes) snapshot=4271931392
                Virtual memory (bytes) snapshot=28059049984
                Total committed heap usage (bytes)=3438804992
                Peak Map Physical memory (bytes)=358109184
                Peak Map Virtual memory (bytes)=2160046080
                Peak Reduce Physical memory (bytes)=200794112
                Peak Reduce Virtual memory (bytes)=2163793920
        RATING INTERVALS
                1=108725
                2=82139
                3=489298
                5=1009026
        Shuffle Errors
                BAD_ID=0
                CONNECTION=0
                IO_ERROR=0
                WRONG_LENGTH=0
                WRONG_MAP=0
                WRONG_REDUCE=0
        edu.classes.mr.ReviewState
                CORRECT=1689188
        File Input Format Counters 
                Bytes Read=1479006258
        File Output Format Counters 
                Bytes Written=1483763

```
Пользовательский счетчик:
- Интервалы

```
RATING INTERVALS
        1=108725
        2=82139
        3=489298
        5=1009026
```

- JSON parser

```
edu.classes.mr.ReviewState
        CORRECT=1689188
```