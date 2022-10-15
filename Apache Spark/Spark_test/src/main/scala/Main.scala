import org.apache.spark.sql.SparkSession


object Main {
  def main(args: Array[String]) = {

    val sparkSession = SparkSession
      .builder
      .appName("Otus")
      .config("spark.master", "local")
      .getOrCreate()

//    import org.apache.spark.sql.functions.col
//    var df = sparkSession.read.option("multiline","true").json("src/main/data/temp.json")
//    df = df.withColumnRenamed("id", "myId")
//    df = df.withColumnRenamed("name", "my name")
//    df = df.withColumn("location", col("location").cast("string"))
//    df.show()
//    df.printSchema()
//
    val sc = sparkSession.sparkContext

    val firstRDD = sc.parallelize(Array(1,4,5,6,7,10,15))

    firstRDD.collect().foreach(println)

    firstRDD.collect().filter(i => (i % 2 == 0)).map(i => i + 1).foreach(println)

    val secondRDD = sc.parallelize(Seq((1, 2, 3), (4, 5, 6)))

    secondRDD.collect().foreach(println)

    import sparkSession.implicits._

    val firstDF = secondRDD.toDF("one", "two", "three")

    firstDF.show(5)

    val crimeDF = sparkSession.read
      .option("header", "true")
      .option("delimiter", ",")
      .csv("src/main/data/Crime_Data_from_2010_to_2019.csv")

    crimeDF.printSchema()

    crimeDF.show(5)

    import org.apache.spark.sql.functions.mean
    import org.apache.spark.sql.functions.col

    crimeDF
      .withColumn("vAge", col("Vict Age").cast("int"))
      .withColumnRenamed("Vict Sex", "vSex")
      .groupBy("vSex")
      .agg(mean("vAge"))
      .show()

    crimeDF
      .withColumn("vAge", col("Vict Age").cast("int"))
      .withColumnRenamed("Vict Sex", "vSex")
      .select("vSex", "vAge")
      .where(col("vSex") === "F" || col("vSex") === "M")
      .groupBy("vSex")
      .agg(mean("vAge"))
      .show()

    val filteredDF = crimeDF
      .withColumn("vAge", col("Vict Age").cast("int"))
      .withColumnRenamed("AREA NAME", "areaName")
      .withColumnRenamed("Vict Sex", "vSex")
      .select("vSex", "vAge", "areaName")
      .where(col("vSex") === "F" || col("vSex") === "M")
      .groupBy("vSex", "areaName")
      .agg(mean("vAge").alias("meanAge"))

    filteredDF
      .write
      .partitionBy("areaName", "vSex")
      .parquet("src/main/data/victims")

    sparkSession.read
      .parquet("src/main/data/victims").show()

  }
}
