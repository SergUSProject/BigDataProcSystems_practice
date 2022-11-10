import pyspark
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StringType, IntegerType, DateType

import click


STREAM_HOST = "localhost"
STREAM_PORT = 9999

STREAM_TIMESTAMP_MODE = "include"


# Note: Only for the Spark local mode
APP_CHECKPOINT_DIR = "file:///home/ubuntu/BigData/tmp/update_timestamp_streaming/checkpoints"


def start_spark():

    # Note: spark.executor.* options are not the case in the local mode
    #  as all computation happens in the driver.
    conf = pyspark.SparkConf()\
        .set("spark.executor.memory", "1g")\
        .set("spark.executor.core", "2")\
        .set("spark.driver.memory", "2g")

    spark = SparkSession\
        .builder\
        .appName("appendTimestampApp")\
        .config(conf=conf)\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Logging
    # log4j = spark._jvm.org.apache.log4j
    # logger = log4j.LogManager.getLogger(__name__)
    # logger.info("=================================")
    # logger.info("LOGGER")
    # logger.info("=================================")

    return spark


def load_input_stream(spark, include_timestamp=True):
    """Load stream."""
    return spark\
        .readStream\
        .format("socket")\
        .option("host", STREAM_HOST)\
        .option("port", STREAM_PORT)\
        .option("includeTimestamp", include_timestamp)\
        .load()


# INCLUDE ITEM TIMESTAMP

def transformation_include_item(stream):
    """Raw input data with timestamp when an item arrived."""
    return stream\
        .withColumnRenamed("value", "number")


# INCLUDE BATCH TIMESTAMP

def transformation_include_batch(stream):
    """Raw input data with timestamp when processing is started."""
    return stream\
        .withColumn("timestamp", F.current_timestamp())\
        .withColumnRenamed("value", "number")


# EMBEDDED TIMESTAMP

def transformations_embedded_steps(stream):
    """Transformation steps."""

    schema = StructType()
    schema.add("number", StringType())
    schema.add("timestamp", StringType())

    return stream\
        .select("*", F.from_json("value", schema).alias("data"))\
        .select("*", "data.*")\
        .select("*", F.to_timestamp("timestamp").alias("datetime"))


def transformations_embedded(stream):
    """Transformation steps."""

    schema = StructType()
    schema.add("number", StringType())
    schema.add("timestamp", StringType())

    return stream\
        .select(F.from_json("value", schema).alias("data"))\
        .select("data.number", F.to_timestamp("data.timestamp").alias("timestamp"))


def start_query(output):

    return output\
        .writeStream\
        .outputMode("append")\
        .format("console")\
        .trigger(processingTime="10 seconds")\
        .option("checkpointLocation", APP_CHECKPOINT_DIR)\
        .queryName("query")\
        .option("truncate", "false")\
        .start()


def cleanup():
    """
    Remove all previous checkpoints.

    Note: Remove only local files
    """
    rmdir(APP_CHECKPOINT_DIR)


def rmdir(path_dir):
    """Remove a directory recursively."""
    import shutil
    local_pattern = "file://"
    if path_dir.find(local_pattern) != 0:
        return
    path_dir = path_dir[len(local_pattern):]
    try:
        shutil.rmtree(path_dir)
    except OSError as e:
        print("Error: {} : {}".format(path_dir, e.strerror))


def main_include_timestamp(spark_session):
    lines = load_input_stream(spark_session, True)
    output = transformation_include_item(lines)
    return start_query(output)


def main_include_batch_timestamp(spark_session):
    lines = load_input_stream(spark_session, False)
    output = transformation_include_batch(lines)
    return start_query(output)


def main_embedded_timestamp(spark_session):
    lines = load_input_stream(spark_session, False)
    output = transformations_embedded_steps(lines)
    return start_query(output)


@click.command()
@click.option("-m", "--timestamp_mode", default=STREAM_TIMESTAMP_MODE, help="Timestamp mode.")
def main(timestamp_mode):

    cleanup()
    spark_session = start_spark()

    if timestamp_mode == "include":
        query = main_include_timestamp(spark_session)
    elif timestamp_mode == "include_batch":
        query = main_include_batch_timestamp(spark_session)
    elif timestamp_mode == "embedded":
        query = main_embedded_timestamp(spark_session)
    else:
        raise Exception("Unsupported timestamp mode.")

    query.awaitTermination()


if __name__ == "__main__":
    main()
