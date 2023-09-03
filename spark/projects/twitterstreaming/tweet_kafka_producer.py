# -*- coding: utf-8 -*-

import tweepy
import json
from kafka import KafkaProducer
import kafka.errors


# Twitter API credentials
CONSUMER_KEY = "YOUR"
CONSUMER_SECRET = "YOUR"
ACCESS_TOKEN = "YOUR"
ACCESS_TOKEN_SECRET = "YOUR"

# Kafka topic name
TOPIC_NAME = "tweets-kafka"

# Kafka server
KAFKA_HOST = "localhost"
KAFKA_PORT = "9092"


class KafkaCommunicator:
    def __init__(self, producer, topic):
        self.producer = producer
        self.topic = topic

    def send(self, message):
        self.producer.send(self.topic, message.encode("utf-8"))

    def close(self):
        self.producer.close()


class StreamListener(tweepy.Stream):
    """Listener to tweet stream from twitter."""
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_token_secret,
                 communicator):
        super().__init__(consumer_key, consumer_secret, access_token, access_token_secret)
        self.communicator = communicator

    def on_data(self, raw_data):
        """Receiving a new data."""
        data = json.loads(raw_data)
        if "extended_tweet" in data:
            text = data["extended_tweet"]["full_text"]
            print(text)
            # put message into Kafka
            # self.communicator.send(text)
        else:
            if "text" in data:
                print(data["text"])
                # put message into Kafka
                # self.communicator.send(data["text"])

    def on_error(self, status):
        print(status)
        return True


def create_communicator():
    """Create Kafka producer."""
    producer = KafkaProducer(bootstrap_servers=KAFKA_HOST + ":" + KAFKA_PORT)
    return KafkaCommunicator(producer, TOPIC_NAME)


def create_stream(communicator):
    """Set stream for twitter api with custom listener."""
    return StreamListener(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        communicator=communicator)


def run_processing(stream):
    # Region that approximately corresponds to Moscow
    region = [34.80, 49.87, 149.41, 74.13]
    # Start filtering messages
    stream.filter(locations=region)


def main():
    communicator = None
    tweet_stream = None
    try:
        # communicator = create_communicator()
        tweet_stream = create_stream(communicator)
        run_processing(tweet_stream)
    except KeyboardInterrupt:
        pass
    except kafka.errors.NoBrokersAvailable:
        print("Kafka broker not found.")
    finally:
        if communicator:
            communicator.close()
        if tweet_stream:
            tweet_stream.disconnect()


if __name__ == "__main__":
    main()