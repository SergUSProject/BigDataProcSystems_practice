# Отсортированные рейтинги с Partitioner, SortComparator и GroupingComparator
Усовик С.В. (usovik@bmstu.ru)

## Разделы:

- Требования
- Конфигурация
- Создание Java-проекта в IntelliJ
- Исходный код на Java
- Разделение и сортировка по пользовательскому ключу
- Группировка по пользовательскому ключу

## Требования

Для запуска необходимо установить следующее ПО:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)

## Конфигурация

Смотри [Введение в MapReduce](mapreduce_basics.md)

## Создание Java-проекта в IntelliJ

1) Open IntelliJ
2) `Create New Project` или `File` -> `Project...`
3) Select Maven and project SDK 1.8 -> `Next`
4) GroupId: `edu.classes.mr`; ArtifactId: `sorted-rating-app` -> `Next`
4) Project name: SortedRatingApp -> `Finish`

## Исходный код на Java

1. [pom.xml](../projects/java/SortedRatingApp/pom.xml)

2. [Review model class](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/Review.java)

3. [Custom writable class](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/RatingKeyWritable.java)

4. [Enum for json parsing result](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/ReviewState.java)

5. [Driver class](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/SortedRatingDriver.java)

6. [Mapper class](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/SortedRatingMapper.java)

7. [Reducer class](../projects/java/SortedRatingApp/src/main/java/edu/classes/mr/SortedRatingReducer.java)

   

## Разделение и сортировка по пользовательскому ключу

#### SortComparator

```java
/**
* Define the comparator that controls how the keys are sorted before they
* are passed to the Reducer.
*
* Sorting by product ids and then by ratings
*
*/
public static class SortComparator extends WritableComparator {

    protected SortComparator() {
        super(RatingKeyWritable.class, true);
    }

}
```

#### WritableComparable

```java
public class RatingKeyWritable implements WritableComparable<RatingKeyWritable> {

    // Code before

    @Override
    public int compareTo(RatingKeyWritable ratingKeyWritable) {
        int cmp = productId.compareTo(ratingKeyWritable.productId);
        if (cmp != 0) return cmp;
        return rating.compareTo(ratingKeyWritable.rating);
    }

    // Code after
}

```

#### KeyPartitioner

```java
/**
* The total number of partitions is the same as the number of reduce tasks for the job. Hence this controls
* which of the reduce tasks the intermediate key (and hence the record) is sent for reduction.
*
* In this case the Partitioner class is used to shuffle map outputs to reducers by product ids.
* That means all products with the same id will be passed to an identical reducer
*
* Note: A Partitioner is created only when there are multiple reducers.
*
*/
public static class KeyPartitioner extends Partitioner<RatingKeyWritable, IntWritable> {

    @Override
    public int getPartition(RatingKeyWritable ratingKeyWritable, IntWritable intWritable, int numPartitions) {
        return Math.abs(ratingKeyWritable.getProductId().hashCode() % numPartitions);
    }
}

```

#### Применение SortComparator and KeyPartitioner в драйвере

```java
public class SortedRatingDriver extends Configured implements Tool {

    public int run(String[] args) throws Exception {

        Job job = Job.getInstance(getConf(), "SortedRatingApp");
        
        // Code before

        job.setPartitionerClass(RatingKeyWritable.KeyPartitioner.class);
        job.setSortComparatorClass(RatingKeyWritable.SortComparator.class);

        // Code after
    }
}
```

#### Вывод

Структура вывода:

1. `product id` 
2. `sorted rating` 
3. `count` (общее количество отзывов для данного идентификатора продукта и рейтинга)

```
0528881469	1.0	2
0528881469	2.0	1
0528881469	3.0	1
0528881469	5.0	1
0594451647	2.0	1
0594451647	4.0	1
0594451647	5.0	3
0594481813	3.0	3
0594481813	4.0	2
0594481813	5.0	3
0972683275	1.0	2
0972683275	2.0	1
0972683275	3.0	6
0972683275	4.0	27
0972683275	5.0	46
```


## Группировка по пользовательскому ключу

#### GroupComparator

```java
/**
 * Grouping class defines the comparator that controls which keys are grouped together
 *
 */
public static class GroupComparator extends WritableComparator {

    protected GroupComparator() {
        super(RatingKeyWritable.class, true);
    }

    @Override
    public int compare(WritableComparable a, WritableComparable b) {
        RatingKeyWritable r1 = (RatingKeyWritable) a;
        RatingKeyWritable r2 = (RatingKeyWritable) b;
        return r1.getProductId().compareTo(r2.getProductId());
    }

}
```

#### Применение GroupComparator в драйвере

```java
public class SortedRatingDriver extends Configured implements Tool {

    public int run(String[] args) throws Exception {

        Job job = Job.getInstance(getConf(), "SortedRatingApp");
        
        // Code before

        job.setPartitionerClass(RatingKeyWritable.KeyPartitioner.class);
        job.setSortComparatorClass(RatingKeyWritable.SortComparator.class);
        job.setGroupingComparatorClass(RatingKeyWritable.GroupComparator.class);

        // Code after
    }
}
```

#### Вывод

Структура вывода:

1. `product id` 
2. `max rating` (сгруппированы)
3. `count` (общее количество отзывов для данного идентификатора продукта)


```
0528881469	5.0	5
0594451647	5.0	5
0594481813	5.0	8
0972683275	5.0	82
```