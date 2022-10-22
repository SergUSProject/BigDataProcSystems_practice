package rdd_df_ds

import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SparkSession}

object DSLResult {
  def readParquet(path: String)(implicit spark: SparkSession): DataFrame = spark.read.load(path).cache().count()
  def readCSV(path: String)(implicit spark: SparkSession):DataFrame = {
    spark.read
      .option("header", "true")
      .option("inferSchema", "true")
      .csv(path)
      .cashe()
      .count()
  

  def processTaxiData(taxiDF: DataFrame, taxiZonesDF: DataFrame) = {
    taxiDF
      .join(taxiZonesDF, col("PULocationID") === col("LocationID"))
      .groupBy("Borough")
      .agg(
        count("*").as("total trips"),
        min("trip_distance").as("min distance"),
        round(mean("trip_distance"), 2).as("mean distance"),
        max("trip_distance").as("max distance")
      )
      .orderBy(col("total trips").desc)
  }

  def main(args: Array[String]): Unit = {
    implicit val spark = SparkSession.builder()
      .config("spark.master", "local")
      .appName("Taxi Big Data Application")
      .getOrCreate()


    val taxiZonesDF2 = readCSV("src/main/resources/data/taxi_zones.csv")
    val taxiDF2 = readParquet("src/main/resources/data/yellow_taxi_jan_25_2018")
    
    
    val value = processTaxiData(taxiZonesDF2, taxiDF2)
    value.show()

    result.write.save("src/main/resources/DataFrameExmpl.parquet")
  }
}
