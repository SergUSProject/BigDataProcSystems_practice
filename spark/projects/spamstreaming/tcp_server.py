# -*- coding: utf-8 -*-

import json
import socket
from time import sleep
import click


SERVER_HOST = "localhost"
SERVER_PORT = 9999
SERVER_WAIT_FOR_CONNECTION = 10
MESSAGE_DELAY = 4


def get_file_line(file_path):
    """Read a file line by line"""
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()


@click.command()
@click.option("-h", "--host", default=SERVER_HOST, help="Server host.")
@click.option("-p", "--port", default=SERVER_PORT, help="Server port.")
@click.option("-f", "--file", help="File to send.")
@click.option("-d", "--delay", default=MESSAGE_DELAY, help="Delay between messages.")
def main(host, port, file, delay):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        print("Starting the server...")

        server_socket.bind((host, port))
        server_socket.listen()

        print("The server is running on {}:{} and listening to a new connection. "
              "To exit press CTRL+C.".format(host, port))

        while True:
            client_socket = None
            try:
                server_socket.settimeout(SERVER_WAIT_FOR_CONNECTION)
                print("Waiting for client connection...")
                client_socket, client_address = server_socket.accept()
                server_socket.settimeout(None)
                print("Connection established. Client: {}:{}".format(client_address[0], client_address[1]))
                print("Sending data...")
                for indx, review in enumerate(get_file_line(file)):
                    client_socket.send("{}\n".format(review).encode("utf-8"))
                    print("Sent line: {}".format(indx+1))
                    sleep(delay)
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
