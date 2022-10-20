### Демонстрация работы структур данных Apache Spark 

### Необходимые компоненты
1) [Idea Community](https://www.jetbrains.com/idea/download)
2) Плагин Скала
3) [Java JDK 11](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html)

### Основная инструкция:

**Цель:** Выполнив домашнее Вы получите опыт работы с RDD API, DataFrame API,Dataset API. Научитесь строить аналитическую витрину на основе сырых данных, используя Spark и различные API.

#### Для работы необходимо:
1) Загрузить данные из [файла со справочными данными поездок](src/main/resources/data/taxi_zones.csv) в RDD при помощи кода в [файле](src/main/scala/rdd_df_ds/TestRDD.scala).
2) Загрузить данные из [файла со справочными данными поездок](src/main/resources/data/taxi_zones.csv) в DafaFrame и DataSet при помощи кода в [файле](.\Apache Spark RDD_DataFrame_DataSet\src\main\scala\rdd_df_ds\TestDataFrameDataSet.scala).
3) Загрузить данные [файла с фактическими данными поездок в Parquet](src/main/resources/data/yellow_taxi_jan_25_2018)
при помощи кода в [файле](.\Apache Spark RDD_DataFrame_DataSet\src\main\scala\DataApi\DataApi.scala).

**Задание**
С помощью DSL построить таблицу, которая покажет какие районы самые популярные для заказов. Результат вывести на экран и записать в файл Паркет.
