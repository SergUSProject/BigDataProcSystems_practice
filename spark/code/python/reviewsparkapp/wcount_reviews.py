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


def extract_words(items):
    """
    Extract words from a review text

    :param items:   records of a partition
    :return:
    """
    import json
    for item in items:
        try:
            for word in json.loads(str(item))["reviewText"].split(" "):
                yield (word, 1)
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

    # Count words
    wcount_rdd = sc.textFile(input_file)\
        .mapPartitions(extract_words)\
        .reduceByKey(lambda v1, v2: v1 + v2)\
        .sortBy(lambda x: -x[1])\
        .map(lambda x: "{}\t{}".format(x[0], x[1]))\
        .coalesce(1)

    # Save the result
    wcount_rdd.saveAsTextFile(output_path)
    sc.stop()


if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])