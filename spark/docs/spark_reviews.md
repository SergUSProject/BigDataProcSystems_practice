# Spark и обработка пользовательских отзывов
## Часть 2. Самостоятельное приложение (Java)
Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Требования
- Конфигурация
- Создание Java-проекта в IntelliJ
- Исходный код
- Запуск приложения Spark в IDE
- Построение `jar`-файла при помощи `maven`
- Запуск приложения Spark при помощи `spark-submit`
- Запуск приложения Spark на YARN
- Рекомендации


## Создание Java-проекта на IntelliJ (v2019.2+)

1) Открыть IntelliJ
2) `Create New Project` или `File` -> `Project...`
3) Выбрать Maven и project SDK 1.8 -> `Next`
4) GroupId: `edu.classes.spark`; ArtifactId: `wordcount-review-app` -> `Next`
4) Project name: WordCountReviewSparkApp -> `Finish`


## Набор данных

- [Small subset of reviews](../data/spark-rdd-intro/samples_100.json)
- [Amazon product datasets](http://jmcauley.ucsd.edu/data/amazon/links.html)


## Исходный код

1. [pom.xml](../code/java/WordCountReviewApp/pom.xml)
2. [Review model class](../code/java/WordCountReviewApp/src/main/java/edu/classes/spark/Review.java)
3. [Driver class](../code/java/WordCountReviewApp/src/main/java/edu/classes/spark/WordCountReviewDriver.java)
4. Test class: `TODO`


### Создание Spark Context


Для операций над RDD, необходимо получить или создать Spark Context.

#### Вариант 1

```java
// Configuration for a Spark application
SparkConf conf = new SparkConf()
        .setMaster(sparkMaster)
        .setAppName(APP_NAME);

// Create a JavaSparkContext that loads settings from system properties
JavaSparkContext sc = new JavaSparkContext(conf);
```

#### Вариант 2

```java
// Spark Session is provided by a spark-sql package
SparkSession spark = SparkSession
                .builder()
                .master(sparkMaster)
                .appName(APP_NAME)
                .getOrCreate();

JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
```

### Разбор JSON отзывов


#### Вариан 1. Анонимная функция

```java
JavaRDD<Review> reviewsRDD = textFileRDD.mapPartitions(records -> {

    Gson gson = new Gson();
    List<Review> reviews = new ArrayList<>();

    // Iterate over records of a RDD partition
    while (records.hasNext()) {
        String item = records.next();
        Review review = gson.fromJson(item, Review.class);
        reviews.add(review);
    }

    return reviews.iterator();
});
```

#### Вариант 2. Реализация интерфейса FlatMapFunction

```java
/**
 * Implementation of the FlatMapFunction interface for the mapPartitions() methods
 * to deserialize json records.
 *
 */
public static final class ReviewConverterPartitionFunction implements FlatMapFunction<Iterator<String>, Review> {

    /**
     * Convert records of a partition to the Review class
     *
     * @param records   records of a partition
     * @return          records of the Review class
     * @throws Exception
     */
    @Override
    public Iterator<Review> call(Iterator<String> records) throws Exception {

        Gson gson = new Gson();
        List<Review> reviews = new ArrayList<>();

        // Iterate over records of a RDD partition
        while (records.hasNext()) {
            String record = records.next();
            Review review = gson.fromJson(record, Review.class);
            reviews.add(review);
        }

        return reviews.iterator();
    }
}
```

И применение **ReviewConverterPartitionFunction**:

```java
JavaRDD<Review> reviewsRDD = textFileRDD.mapPartitions(new ReviewConverterPartitionFunction());
```


#### Вариант 3. Пользовательский сериализуемый class

```java
/**
 * Custom serializable class for json deserialization
 *
 * Inspired by https://stackoverflow.com/a/56626264
 */
public static final class ReviewConverterRDD implements Serializable {

    private transient Gson gson;

    /**
     * Get/create a Gson instance
     *
     * Note: If the variable is not initialized on an executor, the instance will be created.
     * Otherwise the method returns the existing Gson instance.
     *
     * @return  a Gson instance
     */
    private Gson getGsonInstance() {
        if (gson == null) gson = new Gson();
        return gson;
    }

    /**
     * Transform RDD from RDD<String> to RDD<Review>
     *
     * @param rdd   an input rdd with records of the String type
     * @return      a rdd of the Review type
     */
    public JavaRDD<Review> fromJson(JavaRDD<String> rdd) {
        return rdd.map(record -> getGsonInstance().fromJson(record, Review.class));
    }
}
```

Код ниже показывает, как использовать этот класс:

```java
ReviewConverterRDD converter = new ReviewConverterRDD();
JavaRDD<Review> reviewsRDD = converter.fromJson(textFileRDD);
```

### Word Count

```java
sc.textFile(args[0])
    .mapPartitions(new ReviewConverterPartitionFunction())
    .flatMap(review -> Arrays.asList(review.getReview().split(SEPARATOR)).iterator())
    .mapToPair(word -> new Tuple2<>(word, 1))
    .reduceByKey((x, y) -> x + y)
    .saveAsTextFile(args[1])
```

## Запуск приложения Spark в IDE

1) `Run` -> `Edit Configurations...`
2) `Add new configuration...` for Application -> Name: `wordcount`
3) Main class: `edu.classes.spark.WordCountReviewDriver` - (класс, содержащий метод main)
4) Program arguments: `INPUT_LOCAL_FILE OUTPUT_LOCAL_DIR`, e.g. `data/samples_100.json output` для локальной файловой системы
5) Рабочая директория: `/YOUR_LOCAL_PATH/WordCountReviewApp`
6) Environment variable: `SPARK_MASTER=local[2]`
7) `Apply` -> `OK`
8) Закомментируйте **предоставленную** область в файле pom для `spark-core_2.11`, если вы еще этого не сделали.
9) `Run` -> `Run...` -> Выберите Вашу конфигурацию


Выходной каталог выглядит следующим образом:

```shell
output
├── part-00000
├── .part-00000.crc
├── part-00001
├── .part-00001.crc
├── _SUCCESS
└── ._SUCCESS.crc
```

Первые несколько строк из `part-00000`:
```
(better.,1)
(bone,1)
(charm!,1)
(chair).,1)
(GPS,7)
(price!,1)
(pickup.,2)
(heat,1)
(problem--u,1)
```

## Построение `jar`-файла при помощи `maven`

Добавьте **provided** область в pom-файл для `spark-core_2.11` (или раскомментируйте ее) чтобы исключить spark-зависимости из jar-файла. 

Перейдите на панель maven, перезагрузите проект maven (при необходимости), найдите папку `Lifecycle` -> `package`. После завершения сгенерированный файл `jar` будет расположен в целевом каталоге.

```
target
└── wordcount-review-app-1.0-SNAPSHOT.jar
```

Вы можете создать файл `jar` как артефакт, как описано [здесь](mapreduce_scala.md).

## Запуск приложения Spark при помощи `spark-submit`

Изменить рабочий каталог:
```
cd target
```

Запустите приложение spark:
```
SPARK_MASTER=local[2] spark-submit \
    wordcount-review-app-1.0-SNAPSHOT.jar \
    file:///YOUR_LOCAL_PATH/samples_100.json \
    file:///YOUR_LOCAL_PATH/output
```

Выходной каталог имеет следующую структуру:

```
/YOUR_LOCAL_PATH/output
├── part-00000
├── .part-00000.crc
├── part-00001
├── .part-00001.crc
├── _SUCCESS
└── ._SUCCESS.crc
```


## Запуск приложения Spark на YARN

#### Запустить Hadoop кластер

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

При необходимости удалите выходной каталог:

`hdfs dfs -rm -r -f /data/yarn/output`

Запустите job:

```
SPARK_MASTER=yarn spark-submit \
    wordcount-review-app-1.0-SNAPSHOT.jar \
    /data/yarn/samples_100.json \
    /data/yarn/output
```

Примечание. Приложение по умолчанию запускается в YARN в клиентском режиме.

Результат:

`hdfs dfs -head /data/yarn/output/part-00000`

```
(better.,1)
(charm!,1)
(chair).,1)
(bone,1)
(price!,1)
(GPS,7)
(pickup.,2)
...
```

