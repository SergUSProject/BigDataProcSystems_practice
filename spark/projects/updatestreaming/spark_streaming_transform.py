# -*- coding: utf-8 -*-

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

import time
import pickle
import click


STREAM_HOST = "localhost"
STREAM_PORT = 9999

SPARK_APP_NAME = "UpdatingModelApp"
SPARK_BATCH_INTERVAL = 10
SPARK_LOG_LEVEL = "OFF"

MODEL_INPUT_PATH = "models/model-current.pickle"

MODEL_RELOAD_INTERVAL = 60


class BroadcastModel:

    def __init__(self, sc, model_path):
        self.sc = sc
        self.model_path = model_path
        self.br_model = self.load()

    def load_model(self, model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)

    def load(self):
        model = self.load_model(self.model_path)
        self.last_update = time.time()
        return self.sc.broadcast(model)

    def get(self):
        """
        Return a model

        If there is more than MODEL_RELOAD_INTERVAL seconds after
        the last update, than reload a model from an external source,
        otherwise return a current model
        """
        current_time = time.time()
        if int(current_time - self.last_update) > MODEL_RELOAD_INTERVAL:
            self.br_model.unpersist()
            self.br_model = self.load()
            self.last_update = current_time
        return self.br_model


def apply_model_wrapper(br_model):

    def apply_model(messages):
        """
        Classify messages in each partition

        Note: Commonly messages are processed on multiple nodes,
        so sklearn must be installed on each of them
        """

        # Load models
        model = br_model.value

        # Predict class of each message
        for message in messages:
            yield model.transform(message)

    return apply_model


def transform_wrapper(broadcast_model):

    def transform(rdd):
        return rdd.mapPartitions(apply_model_wrapper(broadcast_model.get()))

    return transform


@click.command()
@click.option("-h", "--host", default=STREAM_HOST, help="Stream host.")
@click.option("-p", "--port", default=STREAM_PORT, help="Stream port.")
@click.option("-m", "--model", "model_path", default=MODEL_INPUT_PATH,
              help="Path where a model for transformation is placed.")
def main(host, port, model_path):

    # Create Spark Context
    sc = SparkContext(appName=SPARK_APP_NAME)

    # Set log level
    sc.setLogLevel(SPARK_LOG_LEVEL)

    # Create Streaming Context
    ssc = StreamingContext(sc, SPARK_BATCH_INTERVAL)

    # Create an updatable broadcast model
    broadcast_model = BroadcastModel(sc, model_path)

    # Create a stream
    lines = ssc.socketTextStream(host, port)

    # Transform messages
    output = lines.transform(transform_wrapper(broadcast_model))

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