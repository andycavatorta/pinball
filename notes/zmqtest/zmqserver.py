#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")

count = 0
while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received msg#{count}: {message}")
    count = count +1

    #  Do some 'work'
    #time.sleep(1)

    #  Send reply back to client
    #socket.send(b"World")
