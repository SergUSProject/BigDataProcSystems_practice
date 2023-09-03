#!/usr/bin/python3
# -*- coding: utf-8 -*-


def create_spark_context():

    import os
    from pyspark import SparkContext, SparkConf

    SPARK_MASTER = os.environ.get("SPARK_MASTER")

    conf = SparkConf().setAppName("WordCountPySparkApp")

    # Enable an external master parameter. So if this parameter is specified,
    # we set its value as a master to Spark, otherwise the parameter that
    # is specified in configuration as default or in the spark-submit command
    # will be used.
    if SPARK_MASTER:
        conf.setMaster(SPARK_MASTER)
    sc = SparkContext(conf=conf)
    return sc


def extract_prod_rating_per_partition(items):
    """
    Extract words from a review text

    :param items:   records of a partition
    :return:
    """
    import json
    for item in items:
        try:
            review = json.loads(item)
            yield review["asin"], float(review["overall"])
        except:
            pass


def main(input_file, output_path):
    """
    Entrypoint to the application

    :param input_file: the 1st input argument
    :param output_path: the 2nd input argument
    :return:
    """

    if not input_file or not output_path:
        raise Exception("Wrong input arguments.")

    sc = create_spark_context()

    # Calculate average ratings
    avg_prod_rating_rdd = sc.textFile(input_file)\
        .mapPartitions(extract_prod_rating_per_partition)\
        .aggregateByKey((0,0),
                        lambda x, value: (x[0] + value, x[1] + 1),
                        lambda x, y: (x[0] + y[0], x[1] + y[1]))\
        .map(lambda x: "{}\t{}".format(x[0], x[1][0]/x[1][1]))\
        .coalesce(1)

    # Save the result
    avg_prod_rating_rdd.saveAsTextFile(output_path)
    sc.stop()


if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])