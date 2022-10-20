package rdd_df_ds

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.{col, upper}

object TestDataFrameDataSet extends App {

  val sparkSession = SparkSession.builder()
    .appName("Introduction to RDDs")
    .config("spark.master", "local")
    .getOrCreate()

  case class TaxiZoneDF(
                       LocationID: String,
                       Borough: String,
                       Zone: String,
                       service_zone: String
                     )


  val taxiZoneDF = sparkSession.read
    .option("header", "true")
    .csv("src/main/resources/data/taxi_zones.csv")



  import sparkSession.implicits._

  val taxiZoneDS = taxiZoneDF.as[TaxiZoneDF]

  taxiZoneDS
    .filter(tz => tz.service_zone.toUpperCase == tz.service_zone)
    .filter(upper(col("service_zone")) === col("service_zone"))
    .groupBy(taxiZoneDF("Borough"))
    .count()
    .show()

}
