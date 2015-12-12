# coding: utf-8

# Because I don't have the Linux environment, I don't test this code.

import os
import signal
import socket
import time

__author__ = 'light'

################################################
# Concurrent web server version 1.0            #
# A multi-process web server which sleeps 10   #
# seconds after sending a response to client.  #
# Using multi-process to handle multi requests #
# at the same time.                            #
################################################

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5


def grim_reaper(signum, frame):
    pid, status = os.wait()
    print(
        'Child {pid} terminated with status {status}'
        '\n'.format(pid=pid, status=status)
    )


def handel_request(client_connection):
    request = client_connection.recv(1024)
    print(request.decode())
    http_response = b"""
HTTP/1.1 200 OK

<p><h1>This is from the concurrent web server</h1></p>
<p><h2>by Lightbot Johnson</h2></p>
"""
    client_connection.sendall(http_response)
    time.sleep(10)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print("Serving HTTP on port {port} ...".format(port=PORT))

    signal.signal(signal.SIGCHLD, grim_reaper())

    while True:
        client_connection, client_address = listen_socket.accept()
        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handel_request(client_connection)
            client_connection.close()
            os._exit(0)
        else:  # parent
            client_connection.close()


if __name__ == '__main__':
    serve_forever()
