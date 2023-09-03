# Введение в MapReduce
Усовик С.В. (usovik@bmstu.ru)

#### 

## Разделы:

- [Требования](#Требования)
- [Конфигурация](#Конфигурация)
- [Конфигурация MapReduce](#Конфигурация-MapReduce)
- [Запуск Hadoop кластера](#Запуск-Hadoop-кластера)
- [Создание Java-проекта](#Создание-Java-проекта)
- [Пример исходного кода Java WordCount](#Пример-исходного-кода-Java-WordCount)
- [Запуск MapReduce с локальными файлами](#Запуск-MapReduce-с-локальными-файлами)
- [Построение `jar`-файла при помощи `maven`](#Построение-`jar`-файла-при-помощи-`maven`)
- [Запуск MapReduce `jar`-файла на YARN кластере](#Запуск-MapReduce-`jar`-файла-на-YARN-кластере)
- [Применение параметров конфигурации](#Применение-параметров-конфигурации)
- [Рекомендации](#Рекомендации)

## Требования

Для запуска необходима установка следующего ПО:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)

## Конфигурация

#### Hadoop директории:

- `hadoop/bin` - hadoop-команды
- `hadoop/sbin/` - скрипты
- `hadoop/etc/hadoop` - конфигурация
- `hadoop/logs` - hadoop log-файлы

Ранее сконфигурирванные файлы HDFS и YARN:
- `hadoop/etc/hadoop/hadoop-env.sh`
- `hadoop/etc/hadoop/core-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-common/core-default.xml))
- `hadoop/etc/hadoop/hdfs-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml))
- `hadoop/etc/hadoop/yarn-env.sh`
- `hadoop/etc/hadoop/yarn-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-yarn/hadoop-yarn-common/yarn-default.xml)) -  параметры конфигурации
- `hadoop/etc/hadoop/capacity-scheduler.xml`

Файлы конфигурации можно найти [здесь](../config/) 

## Конфигурация MapReduce

MapReduce конфигурационные файлы:

- `hadoop/etc/hadoop/mapred-env.sh` - переопределить  `hadoop-env.sh` для всей работы, выполняемой `mapred` и связанных команд
- `hadoop/etc/hadoop/mapred-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml)) -  конфигурационные параметры

Приоритетные правила:

- `mapred-env.sh` > `hadoop-env.sh` > hard-coded defaults
- `MAPRED_xyz` > `HADOOP_xyz` > hard-coded defaults

Установите`YARN` как основной для MapReduce-приложений

```xml
<property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
    <description>The runtime framework for executing MapReduce jobs.
    Can be one of local, classic or yarn.
    </description>
</property>
```

Команда для загрузки конфигурационного файла:

```
wget -O ~/BigData/hadoop/etc/hadoop/mapred-site.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/mapreduce/mapred-site.xml
```

## Запуск Hadoop кластера

Запустить `HDFS`:

`$HADOOP_HOME/sbin/start-dfs.sh`

Запустить `YARN`:

`$HADOOP_HOME/sbin/start-yarn.sh`

Запустить Job History Server:

`mapred --daemon start historyserver`

Проверьте, все ли демоны запущены:

`jps`

## Создание Java-проекта

1) Открыть IntelliJ (v2019.2)
2) Выбрать `Create New Project` или `File` -> `Project...`
3) Выбрать Maven и project SDK 1.8 -> `Next`
4) GroupId: `edu.classes.mr`; ArtifactId: `word-count-app` -> `Next`
4) Project name: WordCountApp -> `Finish`

## Пример исходного кода Java WordCount

1. [Main class](../projects/java/WordCountApp/src/main/java/edu/classes/mr/WordCount.java)

2. [Test class](../projects/java//WordCountApp/src/test/java/edu/classes/mr/WordCountTest.java)

3. [pom.xml](../projects/java/WordCountApp/pom.xml)

## Запуск MapReduce с локальными файлами

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` для приложения
3) Main class: `edu.classes.mr.WordCount` - (class with the main method)
4) Program arguments: `INPUT_LOCAL_FILE OUTPUT_LOCAL_DIR`
5) `Apply` -> `OK`
6) `Run` -> `Run...` -> Choose your configuration

## Построение `jar`-файла при помощи `maven`

1. Изменить `pom.xml`, добавив следующий плагин maven в `pom.xml`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-jar-plugin</artifactId>
    <version>3.1.2</version>
    <configuration>
        <archive>
            <addMavenDescriptor>false</addMavenDescriptor>
            <manifest>
                <mainClass>edu.classes.mr.WordCount</mainClass>
            </manifest>
        </archive>
    </configuration>
</plugin>
```

Параметр `mainClass` необходим для определения точки входа для приложения map-reduce, когда вы запускаете его с помощью команды `yarn jar` , в противном случае вам нужно добавить полный путь к классу (с пакетом) непосредственно в командной строке.

2. Постройте `jar`-файл. Перейдите на панель maven, найдите папку `Plugins`  -> `jar` -> `jar:jar`. После завершения актуальный файл `jar` будет расположен в целевом каталоге.

`jar`-файл содержит `MANIFEST.MF`, где определен основной класс.

```
Manifest-Version: 1.0
Build-Jdk-Spec: 1.8
Created-By: Maven Archiver 3.4.0
Main-Class: edu.classes.mr.WordCount

```

## Запуск MapReduce `jar`-файла на YARN кластере


Команда для запуска `jar`-файла:

`yarn jar <jar> [mainClass] args... `

Для word count приложения команда будет следующей:

`yarn jar ./target/word-count-app-1.0.jar -D mapreduce.job.reduces=2 /data/yarn/reviews_Electronics_5_2.json /data/yarn/output`

Удалите выходной каталог, если это необходимо:

`hdfs dfs -rm -r -f /data/yarn/output`


## Применение параметров конфигурации

### Приоритет

1. В настройках Java-code: 

```java
job.setNumReduceTasks(2);
```

2. `yarn jar` настройки командной строки: 

```cmd
-D mapreduce.job.reduces=2
```


3. `yarn-site.xml` и `mapred-site.xml`: 

```xml
<property>
  <name>mapreduce.job.reduces</name>
  <value>1</value>
  <description>The default number of reduce tasks per job. Typically set to 99%
  of the cluster's reduce capacity, so that if a node fails the reduces can
  still be executed in a single wave.
  Ignored when mapreduce.framework.name is "local".
  </description>
</property>
```

## Рекомендации

