import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
import pyspark.sql.functions as F

import click


STREAM_HOST = "localhost"
STREAM_PORT = 9999


APP_OUTPUT_SINK = "console"

# Note: Only for the Spark local mode
APP_CHECKPOINT_DIR = "file:///home/ubuntu/BigData/tmp/structured_streaming/window_append_streaming/checkpoints"
APP_DATA_OUTPUT_DIR = "file:///home/ubuntu/BigData/tmp/structured_streaming/window_append_streaming/output"


def start_spark():

    # Note: spark.executor.* options are not the case in the local mode
    #  as all computation happens in the driver.
    conf = pyspark.SparkConf()\
        .set("spark.executor.memory", "1g")\
        .set("spark.executor.core", "2")\
        .set("spark.driver.memory", "2g")

    spark = SparkSession\
        .builder\
        .appName("windowAppendApp")\
        .config(conf=conf)\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    return spark


def load_input_stream(spark):
    return spark\
        .readStream\
        .format("socket")\
        .option("host", STREAM_HOST)\
        .option("port", STREAM_PORT)\
        .option("includeTimestamp", "true")\
        .load()


@F.udf(returnType=StringType())
def stringify_window(s):
    """Convert the window type to string"""
    return "{}-{}".format(s["start"].strftime("%H%M%S"), s["end"].strftime("%H%M%S"))


def transformations(stream):
    """Group by value and window."""
    return stream.withWatermark("timestamp", "15 seconds")\
        .groupBy("value", F.window("timestamp", "30 seconds", "15 seconds"))\
        .count()\
        .select(stringify_window("window").alias("window"), "value", "count")\
        .coalesce(1)


def start_query_console(output):
    """Start a query with the console sink type."""
    return output.writeStream\
        .option("checkpointLocation", APP_CHECKPOINT_DIR)\
        .outputMode("append")\
        .format("console")\
        .queryName("wordcount_query")\
        .option("truncate", False)\
        .trigger(processingTime="15 seconds")\
        .start()


def start_query_csv(output):
    """Start a query with the console sink type."""
    return output.writeStream\
        .format("csv")\
        .partitionBy("window")\
        .option("checkpointLocation", APP_CHECKPOINT_DIR)\
        .option("path", APP_DATA_OUTPUT_DIR)\
        .trigger(processingTime="10 seconds")\
        .outputMode("append")\
        .start()


def cleanup():
    """
    Remove all previous checkpoints and output results.

    Note: Remove only local files
    """

    rmdir(APP_DATA_OUTPUT_DIR)
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


@click.command()
@click.option("-s", "--sink", default=APP_OUTPUT_SINK, help="Output sink.")
def main(sink):

    # Cleaning up all previous data (for the local mode only)
    cleanup()

    # Creating a Spark session
    spark_session = start_spark()

    # Loading input stream
    lines = load_input_stream(spark_session)

    # Transformations
    output = transformations(lines)

    # Writing to output sink
    if sink == "console":
        query = start_query_console(output)
    elif sink == "file":
        query = start_query_csv(output)
    else:
        raise Exception("Provided output sink type is not supported.")

    # Waiting for termination
    query.awaitTermination()


if __name__ == "__main__":
    main()
