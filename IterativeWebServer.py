# coding: utf-8

import socket
import time

__author__ = 'light'

###############################################
# Iterative server version 1.0                #
# A simple web server which sleeps 60 seconds #
# after sending a response to client.         #
###############################################

SERVER_ADDRESS = (HOST, PORT) = "", 8888
REQUEST_QUEUE_SITE = 5


def handle_request(client_connection):
    request = client_connection.recv(1024)
    print(request.decode())
    http_response = b"""
HTTP/1.1 200 OK

<h1>Welcome to use Lightbot's server! </h1>
"""
    client_connection.sendall(http_response)
    time.sleep(10)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SITE)
    print("Serving HTTP on port {port} ...".format(port=PORT))

    while True:
        client_connection, client_address = listen_socket.accept()
        handle_request(client_connection)
        client_connection.close()


if __name__ == '__main__':
    serve_forever()
