# MapReduce и Scala
Усовик С.В. (usovik@bmstu.ru)

## Разделы:

- Требования
- Конфигурация
- Установка плагина`Scala` для `IntelliJ`
- Создание `Scala`-проекта
- Простой исходный код
- Запуск MapReduce с локальными файлами
- Построение `jar`-файла
- Запуск MapReduce `jar`-файла на кластере YARN
- Рекомендации

## Тпебования

Для запуска необходимо установить следующее ПО:

- Install Ubuntu 14+ (with Python 3.x)
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Scala code)
- (Optional) Install PyCharm 2019+ (for Python code)


## Установка плагина `Scala` для `IntelliJ`

`File` -> `Settings` -> `Plugins` -> Найти плагин `Scala` от `JetBrains` -> Выбрать `Install` -> Перезапустить IDE

## Создание `Scala`-проекта

`File` -> `New` -> `Project...` -> `Scala` with `sbt` -> Next ->  Name: `WordCountApp` - > Finish

Project structure:
```
App --> src --> main --> scala/
    |       |
    |       --> test --> scala/
    |    
    --> build.sbt

```


## Простой `исходный код`

[WordCount.scala](../projects/scala/WordCountApp/src/main/scala/edu/classes/mr/WordCount.scala)

[build.sbt](../projects/scala/WordCountApp/build.sbt)

## Запуск MapReduce с локальными файлами

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` for Application
3) Установите следующую конфигурацию:
- Main class: `edu.classes.mr.WordCount` - (class with the main method)
- Program arguments: `INPUT_LOCAL_FILE OUTPUT_LOCAL_DIR`
- Use classpath of module: `WordCountApp`
- others by default

5) `Apply` -> `OK`
6) `Run` -> `Run...` -> Choose your configuration

## Построение `jar`-файла

1. `File` -> `Project Structure...` -> `Artifacts`
2. `Add` -> `JAR` -> `Empty`
3. Переименуйте artifact в `word-count-scala-app`
4. Измените выходную директорию на `/FULL_PATH/WordCountApp/target`
5. Выберите `root jar` (`word-count-scala-app.jar`) А затем выберите `Create Manifest...`
6. Выберите директорию `/FULL_PATH/WordCountApp/src/main/scala`  -> OK
7. Main class: `edu.classes.mr.WordCount`
8. Добавьте`WordCountApp` в `jar` из `Available Elements`
9. Извлеките `sbt:org.scala-lang:scala-library:2.13.1:jar` в `jar` (необходимо извлеч, а не перемещать `jar` в `root jar`)
10. `Apply` -> `OK`
11. `Build` -> `Build artifacts...` -> `word-count-scala-app` -> build

Если все сделано правильно, вы увидите файл `jar` в целевом каталоге `target `вашего проекта.

## Запуск MapReduce `jar`-файла на кластере YARN

#### Запуск кластера Hadoop

Запуск `HDFS`:

`$HADOOP_HOME/sbin/start-dfs.sh`

Запуск `YARN`:

`$HADOOP_HOME/sbin/start-yarn.sh`

Запуск Job History Server:

`mapred --daemon start historyserver`

Проверьте, все ли демоны запущены:

`jps`

#### Запуск `jar`

Запустите приложение следующей командой:

`yarn jar ./target/word-count-scala-app.jar /data/yarn/reviews_Electronics_5_2.json /data/yarn/output`

Удалите выходной каталог, если это необходимо:

`hdfs dfs -rm -r -f /data/yarn/output`

## Рекомендации