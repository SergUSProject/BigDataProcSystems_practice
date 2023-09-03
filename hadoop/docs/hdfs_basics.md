# Введение в HDFS
Усовик С.В. (usovik@bmstu.ru)



## Разделы:

- [Требования](#Требования)
- [Задачи](#Задачи)
- [Конфигурация](#конфигурация)
- [HDFS Shell Команды](#HDFS-Shell-Команды)
- [HDFS Java API](#HDFS-Java-API)
- [Запуск на Docker кластере](#Запуск-на-Docker-кластере)

## Требования

Для начала следует установить следующее программное обеспечение:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)

Образ виртуальной машины с предустановленным ПО для VirtualBox можно найти [здесь](https://disk.yandex.ru/d/0Hd92rzNB0_IHg).

## Задачи

В ходе практики необходимо выполнить следующие задачи:
- научиться управлять HDFS daemons
- изменить конфигуациюHDFS
- использовать HDFS CLI
- запустить JAVA-проект для работы с файлами HDFS


## Конфигурация

#### Hadoop директории:

- `hadoop/bin` - папка с hadoop командами
- `hadoop/sbin` - скрипты
- `hadoop/etc/hadoop` - конфигурации
- `hadoop/logs` - hadoop log-файлы

#### Основные конфигурируемые файлы:

- `hadoop/etc/hadoop/hadoop-env.sh`
- `hadoop/etc/hadoop/core-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-common/core-default.xml))
- `hadoop/etc/hadoop/hdfs-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml))

Вы можете найти все файлы конфигурации, которые должны быть изменены, ссылке: [configuration files](../config/hdfs).


Или выполните следующие команды для загрузки:

```bash
# .profile
wget -O ~/.profile https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/hdfs/.profile
# hadoop-env.sh
wget -O ~/BigData/hadoop/etc/hadoop/hadoop-env.sh https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/hdfs/hadoop-env.sh
# core-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/core-site.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/hdfs/core-site.xml
# hdfs-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/hdfs-site.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/hdfs/hdfs-site.xml
```


#### Запуск HDFS

Подготовка:

1) Создайте ключи доступа и добавьте общий ключ `authorized_keys` чтобы включить беспарольную связь между `namenode` и `datanode`:

`ssh-keygen -t rsa -P '' -f $HOME/.ssh/id_rsa && cat $HOME/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys`

2) Создайте директорию namenode:

`mkdir -p $HOME/BigData/tmp/hadoop/namenode`

3) Перед запуском отформатируйте HDFS:

`hdfs namenode -format -force`

Для запуска/остановки HDFS демонов по отдельности используйте следующие команды:

`hdfs --daemon start|stop namenode`

`hdfs --daemon start|stop datanode`

`hdfs --daemon start|stop secondarynamenode`

Или можно запустить скрипт для одновременного запуска/остановки всех демонов:

`$HADOOP_HOME/sbin/start-dfs.sh`

`$HADOOP_HOME/sbin/stop-dfs.sh`

Запустите `jps` команду, чтобы проверить, какие демоны запущены:

```
7792 Jps
7220 NameNode
7389 DataNode
7663 SecondaryNameNode
```

Если что-то пошло не так, посмотрите `hadoop/logs` для получения дополнительной информации.

#### HDFS dashboard

`http://localhost:9870`

## HDFS Shell Команды

- [HDFS Commands Guide](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html)

- [File System Shell Guide](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html)

Отобразить основную информацию о файловой системе и статистику:

`hdfs dfsadmin -report`

Показать HDFS топологию:

`hdfs dfsadmin -printTopology`

Создать директорию:

`hdfs dfs -mkdir /data`

Скопировать локальный файл в HDFS

`hdfs dfs -copyFromLocal LOCAL_FILE /data`

Изменить права доступа к файлам

`hdfs dfs -chmod 600 /data/file`

Распечатать местоположение для каждого блока

`hdfs fsck /myfile.txt -files -blocks -locations`

Рекурсивно удалять каталоги:

`hdfs dfs -rm -R /data`

Чтение и редактирование logs:

`hdfs oev -i $EDIT_LOG_FILE -o $EDIT_LOG_FILE.xml`

`cat $EDIT_LOG_FILE.xml`

## HDFS Java API

### Создание Java-проекта в IntelliJ (v2019.2+)

1) Откройте IntelliJ (Сначала запустите скрипт: `/home/ubuntu/ML/ideaic/bin/idea.sh`)
2) `Create New Project` призапуске или `File` -> `Project...`

#### Основной метод 
Maven-проект

3) Выберите Maven и проект SDK 1.8 -> `Next`
4) GroupId: `edu.classes.hdfs`; ArtifactId: `basic-hdfs-app` -> `Next`
5) Project name: BasicHDFSApp -> `Finish`

Project structure:

```
BasicHDFSApp
├── out
│   └── artifacts
│       └── ReadFileApp
│           └── ReadFileApp.jar
├── pom.xml
├── readwrite.log
├── src
│   ├── main
│   │   ├── java
│   │   │   ├── edu
│   │   │   │   └── classes
│   │   │   │       └── hdfs
│   │   │   │           ├── BasicReadFile.java
│   │   │   │           ├── BasicWriteFile.java
│   │   │   │           ├── ReadWriteDriver.java
│   │   │   │           └── ReadWriteFile.java
│   │   │   └── META-INF
│   │   │       └── MANIFEST.MF
│   │   └── resources
│   └── test
│       └── java
│           └── edu
│               └── classes
│                   └── hdfs
│                       ├── BasicReadFileTest.java
│                       └── BasicWriteFileTest.java

```

Исходный код находится [здесь](../projects/java/BasicHDFSApp).

#### Альтернативный метод
Общий Java-проект

3) Выберите Java и project SDK 1.8 -> `Next` -> `Next`
4) Project name: `BasicHDFSApp` -> `Finish`
5) Нажмите правой кнопкой мыши на `BasicHDFSApp` в панели структуры проекта и выберите `Add framework support...`
6) Выберите `Maven` -> `OK` 
7) В появившемся окне сообщения нажмите `Import changes`

### Добавьте зависимости в `pom.xml`
```xml
    <dependencies>
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-client</artifactId>
            <version>3.1.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-common</artifactId>
            <version>3.1.0</version>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>RELEASE</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
```

### Прикрепите HDFS исходный код

1) Загрузите исходный код Hadoop ([here Hadoop 3.1.0](https://archive.apache.org/dist/hadoop/core/hadoop-3.1.0/))
2) Распакуйте архив
3) `File` -> `Project structure` -> Выберите `Libraries`
4) Найдите`org.apache.hadoop:hadoop-common:3.1.0` -> Удалите `Source` -> Добавьте `Source`: `HADOOP_SOURCE_DIR/hadoop-common-project/hadoop-common` -> `OK` -> Прикрепите `src/main/java` -> `OK` -> `Apply` и `OK`

### Запуск и отладка

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` for Application
3) Main class: `edu.classes.hdfs.BasicWriteFile` - (class with the main method)
4) Program arguments: `INPUT_LOCAL_FILE OUTPUT_HDFS_FILE`
5) `Apply` -> `OK`
6) `Run` -> `Run...` -> Выберите свою конфигурацию


### Create `jar`

1) `File` -> `Project Structure` -> Выберите `Artifacts` -> `Add` -> Выберите `Jar`
2) `Apply` -> `OK`
3) `Build` -> `Build Artifacts...`


### Запустите `jar`

`
hadoop jar ReadFileApp.jar edu.classes.hdfs.BasicReadFile hdfs://localhost:9000/FULL_FILE_PATH_TO_READ
`

## Запуск на Docker кластере

Смотрите

- [Развертывание на docker](../docs/hadoop_docker_part_1.md)

