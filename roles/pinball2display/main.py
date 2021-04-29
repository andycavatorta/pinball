import importlib
import os
import queue
import sys
import threading
import time

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

# adafruit libs
import board
import digitalio

# 24-channel LED Driver
import tlc5947_driver as td

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
            time.sleep(1)

class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.safety_enable = Safety_Enable(self.tb)
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("test_rotation")
        self.tb.subscribe_to_topic("test_lights")
        self.tb.subscribe_to_topic("home")
        self.tb.subscribe_to_topic("pass_ball")
        self.tb.subscribe.to_topic("pb2_display")  # pinball2display

        # initialize overhead display
        self.ovdisp = td.tlc_5947(  digitalio.DigitalInOut( board.D5 ), driverCount = 4 )
        
        self.tb.publish("connected", True)
        self.start()
    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self,topic, message):
        print("network_message_handler",topic, message)
        self.add_to_queue(topic, message)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                print(topic, message)

                if topic == "pb2_display":
                    spl = message.split()
                    ledIdx = spl[ 0 ]
                    ledVal = spl[ 1 ]
                    self.ovdisp.write( ledIdx, ledVal )
                
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()

