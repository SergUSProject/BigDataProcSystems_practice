import pyspark
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

import click


STREAM_HOST = "localhost"
STREAM_PORT = 9999

STREAM_QUERY_SINK = "console"
STREAM_QUERY_MODE = "complete"
STREAM_QUERY_TRIGGER = "10 seconds"
STREAM_QUERY_TRUNCATE = False

APP_CHECKPOINT_DIR = "file:///home/ubuntu/BigData/tmp/structured_streaming/complete_update_streaming/checkpoints"


def start_spark():

    # Note: spark.executor.* options are not the case in the local mode
    #  as all computation happens in the driver.
    conf = pyspark.SparkConf()\
        .set("spark.executor.memory", "1g")\
        .set("spark.executor.core", "2")\
        .set("spark.driver.memory", "2g")

    spark = SparkSession\
        .builder\
        .config(conf=conf)\
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    return spark


def load_input_stream(spark):
    """Load stream."""
    return spark\
        .readStream\
        .format("socket")\
        .option("host", STREAM_HOST)\
        .option("port", STREAM_PORT)\
        .load()


def transform(stream):
    """Count words."""
    return stream\
        .select(F.explode(F.split("value", " ")).alias("word"))\
        .groupBy("word")\
        .count()


def start_query(output, mode):

    return output\
        .writeStream\
        .outputMode(mode)\
        .option("checkpointLocation", APP_CHECKPOINT_DIR)\
        .format(STREAM_QUERY_SINK)\
        .trigger(processingTime=STREAM_QUERY_TRIGGER)\
        .queryName("wordcount_query")\
        .start()


def sort_batch(df, epoch_id):
    """Sort mini-batch and write to console."""
    df.sort(F.desc("count"))\
        .limit(4)\
        .write\
        .format("console")\
        .save()


def start_query_with_custom_sink(output, mode):
    """Start a query with the foreachBatch sink type."""
    return output\
        .writeStream\
        .foreachBatch(sort_batch)\
        .outputMode(mode)\
        .option("checkpointLocation", APP_CHECKPOINT_DIR)\
        .trigger(processingTime=STREAM_QUERY_TRIGGER)\
        .queryName("wordcount_query")\
        .option("truncate", STREAM_QUERY_TRUNCATE)\
        .start()


@click.command()
@click.option("-m", "--mode", default=STREAM_QUERY_MODE, help="Output mode.")
@click.option("-s", "--sink", default=STREAM_QUERY_SINK, help="Output sink.")
def main(mode, sink):

    spark_session = start_spark()
    lines = load_input_stream(spark_session)
    output = transform(lines)

    if sink == "foreach":
        query = start_query_with_custom_sink(output, mode)
    elif sink == "console":
        # Note: sorting is available only in the complete mode.
        output = output.sort(F.desc("count")) if mode == "complete" else output
        query = start_query(output, mode)
    else:
        raise Exception("Unsupported sink.")

    query.awaitTermination()


if __name__ == "__main__":
    main()