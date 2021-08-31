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

STATUS_PRESENT = "status_present"
STATUS_ABSENT = "status_absent"
STATUS_NOMINAL = "status_nominal"
STATUS_FAULT = "status_fault"


clients = []
class SimpleChat(WebSocket):

    # There may be a more graceful way of doing this
    def setTBRef(self, tb_ref):
        self.tb_ref = tb_ref

    def handleMessage(self):
       print("got ws message", self.data)
       trigger_map = {
           "tb_pull_from_github" : self.tb_ref.tb_pull_from_github,
           "app_pull_from_github" : self.tb_ref.app_pull_from_github,
           "reboot" : self.tb_ref.restart,
           "shutdown" : self.tb_ref.shutdown,
           "run_update_scripts": self.tb_ref.tb_run_update_scripts
       }
       try:
         print(trigger_map[self.data]())
       except Exception as e:
           print("Got Exception", e)

    def handleConnected(self):
    #    print(self.address, 'connected')
       for client in clients:
          client.sendMessage(self.address[0] + u' - connected')
       clients.append(self)

    def handleClose(self):
       clients.remove(self)
    #    print(self.address, 'closed')
       for client in clients:
          client.sendMessage(self.address[0] + u' - disconnected')

    def sendToClients(self, message):
        print("Sending message to client : ", message)
        for client in clients:
            print("client",client)
            client.sendMessage(message)

class Message_Receiver(threading.Thread):
    def __init__(
            self, 
            tb_ref,
            _websocket
            ):
        print("Initialized Dashboard.py")
        self.tb_ref = tb_ref
        self.websocket = _websocket
        self.websocket.setTBRef(self.websocket, tb_ref)
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
                topic, message = self.queue.get(block=True)
                print("topic, message",topic, message)
                message_json = json.dumps([topic, message])
                self.websocket.sendToClients(self.websocket,message_json)

def status_receiver(message):
    message_receiver.add_to_queue("status_event",message)

def exception_receiver(message):
    message_receiver.add_to_queue("exception_event",message)


def init(tb_ref):
    global message_receiver
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    os.chdir(tb_path)  # optional
    #httpd.serve_forever()
    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.start()    

    server = SimpleWebSocketServer('', 8001, SimpleChat)
    server_thread = threading.Thread(target=server.serveforever)
    server_thread.start()
    message_receiver = Message_Receiver(tb_ref, server.websocketclass)
    return message_receiver.add_to_queue


