import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import queue
import time
import threading
import socketserver
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

tb_path = os.path.dirname(os.path.realpath(__file__))
clients = []

class SimpleChat(WebSocket):

    def handleMessage(self):
       #print("got ws message", self.data)
       print("handleMessage",self.data)

    def handleConnected(self):
        #print(self.address, 'connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        #print(self.address, 'closed')
        for client in clients:
            client.sendMessage(self.address[0] + u' - disconnected')

    def sendToClients(self, message):
        #print("Sending message to client : ", message)
        for client in clients:
            #print("client",client)
            client.sendMessage(message)

class Message_Receiver(threading.Thread):
    def __init__(
            self, 
            _websocket
            ):
        self.websocket = _websocket
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, topic, message,origin,destination):
        self.queue.put((topic, message,origin,destination))

    def run(self):
        while True:
            topic, message,origin,destination = self.queue.get(block=True)
            #print("topic, message",topic, message)
            message_json = json.dumps([str(topic), message, str(origin)])
            self.websocket.sendToClients(self.websocket,message_json)
            """
            try:
                topic, message = self.queue.get(block=True, timeout=self.tb_ref.settings.Dashboard.refresh_interval)
                print("topic, message",topic, message)
                message_json = json.dumps([topic, message])
                self.websocket.sendToClients(self.websocket,message_json)
                # self.websocket.sendToClients(message_json)

            except queue.Empty:
                self.generate_system_status()
            """

def status_receiver(message):
    message_receiver.add_to_queue("status_event",message)

def exception_receiver(message):
    message_receiver.add_to_queue("exception_event",message)

def init():
    global message_receiver
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.start()    
    server = SimpleWebSocketServer('', 8081, SimpleChat)
    server_thread = threading.Thread(target=server.serveforever)
    server_thread.start()
    message_receiver = Message_Receiver(server.websocketclass)
    return message_receiver.add_to_queue
