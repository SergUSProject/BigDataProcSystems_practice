## Введение в YARN
Усовик С.В. (usovik@bmstu.ru)

## Разделы:

- [Требования](#Требования)
- [Файлы конфигурации](#Файлы-конфигурации)
- [Планировщик](#Планировщик)
    - [Планировщик ресурсов](#Планировщик-ресурсов)
    - [Иерархия очередей](#Иерархия-очередей)
    - [Обновление конфигурации очереди](#Обновление-конфигурации-очереди)
    - [Прочее](#Прочее)
- [Запуск приложений](#Запуск приложений)

## Требования

Для запуска необходима установка следующего ПО:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)


## Файлы конфигурации

#### Основные файлы для конфигурации

Ранее настроенные конфигурационные файлы HDFS:
- `hadoop/etc/hadoop/hadoop-env.sh`
- `hadoop/etc/hadoop/core-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-common/core-default.xml))
- `hadoop/etc/hadoop/hdfs-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml))


YARN конфигурационные файлы:

- `hadoop/etc/hadoop/yarn-env.sh` - переменные среды, используемые для демонов YARN и выполнения команд YARN
- `hadoop/etc/hadoop/yarn-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-yarn/hadoop-yarn-common/yarn-default.xml)) -  конфигурация параметров
- `hadoop/etc/hadoop/capacity-scheduler.xml` - файл конфигурации для опции `CapacityScheduler` 

Приоритетные правила:

- `yarn-env.sh` > `hadoop-env.sh` > hard-coded defaults
- `YARN_xyz` > `HADOOP_xyz` > hard-coded defaults

Файлы конфигурации можно найти [здесь](../config/yarn).

Или выполните следующие команды, чтобы загрузить и заменить локальные файлы конфигурации:

```bash
# yarn-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/yarn-site.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/yarn/yarn-site.xml
# capacity-scheduler.xml
wget -O ~/BigData/hadoop/etc/hadoop/capacity-scheduler.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/yarn/capacity-scheduler.xml
# mapred-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/mapred-site.xml https://raw.githubusercontent.com/SergUSProject/IntelligentSystemsAndTechnologies/main/Practice/%20ml%20distributed%20environments/hadoop/config/mapreduce/mapred-site.xml
```

### Распределение памяти и vcores

NodeManager memory

Container memory

## Планировщик

### Планировщик ресурсов

Чтобы настроить планировщик ресурсов, отредактируйте файл `capacity-scheduler.xml` в директории конфигурации Hadoop 

### Иерархия очередей

Queue/sub-queue | Capacity | Maximum capacity
--- | --- | ---
mrapp | 90% | 100%
mrapp.dev | 80% | -
mrapp.prod | 20% | -
sparkapp | 5% | 10%
default | 5% | 10%

Чтобы указать параметр очереди для использования, вы можете напрямую написать правило в `capacity-scheduler.xml`.

Синтаксис: [u or g]:[name]:[queue_name][,next_mapping]*. 

Пример,

```xml
<property>
    <name>yarn.scheduler.capacity.queue-mappings</name>
    <value>g:ubuntu:dev</value>
</property>
<property>
    <name>yarn.scheduler.queue-placement-rules.app-name</name>
    <value>wordCountMRApp:prod</value>
</property>
```

### Обновление конфигурации очереди

Для обновления необходимо отредактировать файл `capacity-scheduler.xml` и запустить `yarn rmadmin -refreshQueues`.

`$HADOOP_HOME/bin/yarn rmadmin -refreshQueues`


Удаление очереди:

- Step 1: Остановить очередь
- Step 2: Удалить очередь
- Step 3: Запустить `yarn rmadmin -refreshQueues`

### Прочее

Полные конфигурации находятся в`config/yarn` и в `config/mapreduce`.

Чтобы узнать больше о настройке планировщика ресурсов, перейдите по ссылке: [Hadoop: Capacity Scheduler](https://hadoop.apache.org/docs/r3.1.2/hadoop-yarn/hadoop-yarn-site/CapacityScheduler.html)


## Запуск приложений

Для кластера с одним узлом задачи могут завершаться сбоем из-за нехватки ресурсов. В этом случае необходимо отключить проверку памяти. Измените `yarn-site.xml`, добавив следующие строки:

```xml
<property>
    <name>yarn.nodemanager.pmem-check-enabled</name>
    <value>false</value>
</property>
<property>
    <name>yarn.nodemanager.vmem-check-enabled</name>
    <value>false</value>
</property>
```

### Изменение `mapred-site.xml` для выполнения MapReduce в режиме YARN

Путь к конфигурационному файлу с правильными настройками: `config/mapreduce/mapred-site.xml`

### Запуск HDFS и YARN

`$HADOOP_HOME/sbin/start-dfs.sh`

`$HADOOP_HOME/sbin/start-yarn.sh`

`$HADOOP_HOME/bin/mapred --daemon start historyserver`

`jps`

### Загрузка и распаковка набора данных

Создайте новую директорию для набора данных:

`mkdir -p ~/datasets/reviews`

Скачайте архив отзывов клиентов:

`wget -P ~/datasets/reviews/ http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Electronics_5.json.gz`

Распакуйте архив:

`gzip -dk ~/datasets/reviews/reviews_Electronics_5.json.gz`

Создайте директорию в HDFS

`hdfs dfs -mkdir -p /data/yarn`

Скопируйте файл с локальной директории в HDFS

`hdfs dfs -copyFromLocal ~/datasets/reviews/reviews_Electronics_5.json /data/yarn/`

### Запуск MapReduce-приложения

Удалите выходной каталог, если он существует:

`hdfs dfs -rm -r -f /data/yarn/output`

Запустите MapReduce по следующему примеру:

`yarn jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.2.jar wordcount -D mapreduce.job.reduces=2 /data/yarn/reviews_Electronics_5.json /data/yarn/output`

Проверьте выходной каталог. Должно быть два файла, имена которых начинаются с `part-r-0000x`. Это файлы, в которых хранится результат.

Вы можете использовать следующую опцию, чтобы указать очередь:

`-D mapred.job.queue.name=dev`

### YARN dashboard

`http://localhost:8088`
