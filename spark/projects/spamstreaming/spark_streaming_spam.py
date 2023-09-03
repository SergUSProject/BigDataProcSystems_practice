#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

import pickle
import click


STREAM_HOST = "localhost"
STREAM_PORT = 9999

SPARK_APP_NAME = "SpamClassificationApp"
SPARK_BATCH_INTERVAL = 10
SPARK_LOG_LEVEL = "OFF"

MODEL_SPAM_PATH = "models/spammodel.pickle"
MODEL_BINARIZER_PATH = "models/vecmodel.pickle"


def load_spam_model(model_path=MODEL_SPAM_PATH):
    with open(model_path, "rb") as f:
        return pickle.load(f)


def load_binarizer_model(model_path=MODEL_BINARIZER_PATH):
    with open(model_path, "rb") as f:
        return pickle.load(f)


# Option 1

def predict_wrapper(br_bin_model, br_spam_model):

    def predict(messages):
        """
        Classify messages in each partition.

        Note: Commonly messages are processed on multiple nodes,
        so sklearn must be installed on each of them
        """

        # Load models
        bin_model = br_bin_model.value
        spam_model = br_spam_model.value

        # Predict class of each message
        for message in messages:
            message_vector = bin_model.transform([message])
            yield spam_model.predict(message_vector), message

    return predict


# Option 2

# def predict_with_broadcast(messages, br_bin_model, br_spam_model):
#
#     # Load models
#     bin_model = br_bin_model.value
#     spam_model = br_spam_model.value
#
#     # Predict class of each message
#     for message in messages:
#         message_vector = bin_model.transform([message])
#         yield spam_model.predict(message_vector), message


def format_output(record):
    return "spam" if record[0] else "ham", record[1]


@click.command()
@click.option("-s", "--classifier", default=MODEL_SPAM_PATH, help="Model for classification.")
@click.option("-v", "--vectorizer", default=MODEL_BINARIZER_PATH, help="Model for text vectorization.")
def main(vectorizer, classifier):

    # Create Spark Context
    sc = SparkContext(appName=SPARK_APP_NAME)

    # Set log level
    sc.setLogLevel(SPARK_LOG_LEVEL)

    # Load models
    tf_model = load_binarizer_model(model_path=vectorizer)
    spam_model = load_spam_model(model_path=classifier)

    # Transfer model to all executors
    tf_model_broadcast = sc.broadcast(tf_model)
    spam_model_broadcast = sc.broadcast(spam_model)

    # Create Streaming Context
    ssc = StreamingContext(sc, SPARK_BATCH_INTERVAL)

    # Create a stream
    lines = ssc.socketTextStream(STREAM_HOST, STREAM_PORT)

    # Predict class of messages

    # Option 1
    spam_predictions = lines.mapPartitions(predict_wrapper(tf_model_broadcast, spam_model_broadcast))

    # Option 2
    # spam_predictions = lines.mapPartitions(lambda part: predict_with_broadcast(part,
    #                                                                            tf_model_broadcast,
    #                                                                            spam_model_broadcast))

    output = spam_predictions.map(format_output)

    # Print the result (10 records) in terminal
    output.pprint()

    # If you want to save the result in file systems
    # output.transform(lambda rdd: rdd.coalesce(1)).saveAsTextFiles("FILE_PATH")

    # Start Spark Streaming
    ssc.start()

    # Await termination
    ssc.awaitTermination()


if __name__ == "__main__":
    main()
