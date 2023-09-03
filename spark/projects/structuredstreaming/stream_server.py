# -*- coding: utf-8 -*-

import socket
from time import sleep
import click


SERVER_HOST = "localhost"
SERVER_PORT = 9999
SERVER_WAIT_FOR_CONNECTION = 30
MESSAGE_DELAY = 2
MESSAGE_REPEATS = 10
MESSAGE_OUTPUT_TYPE = "random"


def send_messages(message_gen, send_func):
    for message in message_gen:
        send_func("{}\n".format(message).encode("utf-8"))
        print("Sent value: {}".format(message))


def random_output(delay):
    import random
    for i in range(1000):
        yield random.randint(0, 10)
        sleep(delay)


def sequence_output(delay):
    for i in range(1000):
        yield i
        sleep(delay)


def text_file_output(file_path, delay):
    """Read a file line by line"""
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()
            sleep(delay)


def random_json_with_timestamp(delay, random_timestamp=False, timestamp_delay=60):
    import random
    import datetime
    import json
    for i in range(1000):
        timestamp = datetime.datetime.today() if not random_timestamp \
            else datetime.datetime.today() - datetime.timedelta(seconds=random.randint(0, timestamp_delay))
        yield json.dumps({
            "number": random.randint(0, 10),
            "timestamp": timestamp.isoformat()
        })
        sleep(delay)


def init_iterator(output, delay, file):

    if output == "random":
        return random_output(delay)
    elif output == "sequence":
        return sequence_output(delay)
    elif output == "file":
        if file:
            return text_file_output(file, delay)
        else:
            raise Exception("File path was not provided.")
    elif output == "json_random_timestamp":
        return random_json_with_timestamp(delay, random_timestamp=True)
    else:
        raise Exception("Unsupported output type.")


@click.command()
@click.option("-h", "--host", default=SERVER_HOST, help="Server host.")
@click.option("-p", "--port", default=SERVER_PORT, help="Server port.")
@click.option("-o", "--output", default=MESSAGE_OUTPUT_TYPE, help="Output data type.")
@click.option("-d", "--delay", default=MESSAGE_DELAY, help="Delay between messages.")
@click.option("-r", "--repeat", default=MESSAGE_REPEATS, help="The number of cycles.")
@click.option("-f", "--file", help="File to send.")
def main(host, port, output, delay, repeat, file):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        print("Starting the server...")

        server_socket.bind((host, port))
        server_socket.listen()

        print("The server is running on {}:{} and listening to a new connection. "
              "To exit press CTRL+C.".format(host, port))

        while True:

            # TODO: Implement multithreading to support connections of multiple clients

            client_socket = None
            try:
                server_socket.settimeout(SERVER_WAIT_FOR_CONNECTION)
                print("Waiting for client connection...")
                client_socket, client_address = server_socket.accept()
                server_socket.settimeout(None)
                print("Connection established. Client: {}:{}".format(client_address[0], client_address[1]))
                print("Sending data...")

                for i in range(repeat):
                    send_messages(init_iterator(output, delay, file), client_socket.send)

                print("Closing connection...")
                client_socket.close()

            except socket.timeout:
                print("No clients to connect.")
                break

            except KeyboardInterrupt:
                print("Interrupt")
                if client_socket:
                    client_socket.close()
                break

        print("Stopping the server...")


if __name__ == "__main__":
    main()