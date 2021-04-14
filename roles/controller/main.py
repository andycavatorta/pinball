import importlib
import mido
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            #self.queue.get(True)
            self.tb.publish("deadman", "safe")
            time.sleep(2)
            
# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class States:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
        self.states =States()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        """
        self.transport_connected = False
        self.horsewheel_connected = False
        self.pitch_slider_home = False
        self.horsewheel_slider_home = False
        self.horsewheel_lifter_home = False
        """
        self.state = self.states.WAITING_FOR_CONNECTIONS
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")
        self.tb.subscribe_to_topic("home")
        self.start()

    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(">>>",topic, message, origin, destination)
                if topic=="deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()



GPIO.setmode(GPIO.BCM)
GPIO.setup( 26, GPIO.OUT )

while True:
    time.sleep(10)
    GPIO.output(26, GPIO.LOW)
    time.sleep(10)
    GPIO.output(26, GPIO.HIGH)
    print(time.time())
            #try:
            #    polling = self.queue.get(False)
            #except queue.Empty:
            #    pass