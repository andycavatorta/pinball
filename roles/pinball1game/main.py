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
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
"""
class Roboteq_Data_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("data",message)
            #if "internal_event" in message:
            #    pass

roboteq_data_receiver = Roboteq_Data_Receiver()
"""

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
        """
        self.controllers = roboteq_command_wrapper.Controllers(
            roboteq_data_receiver.add_to_queue, 
            self.status_receiver, 
            self.network_status_change_handler, 
            {"sliders":settings.Roboteq.BOARDS["sliders"]},
            {
                "pitch_slider":settings.Roboteq.MOTORS["pitch_slider"],
                "bow_position_slider":settings.Roboteq.MOTORS["bow_position_slider"],
            }
        )
        """
        self.tb.subscribe_to_topic("test_rotation")
        self.tb.subscribe_to_topic("test_lights")
        self.tb.subscribe_to_topic("home")
        self.tb.subscribe_to_topic("pass_ball")

        self.tb.publish("connected", True)
        self.start()
    """
    def macro_callback(self, motor_name, action, status):
        print("macro_callback",motor_name, action, status)
        if motor_name == "pitch_slider":
            if action == 'go_to_limit_switch':
                self.tb.publish("pitch_slider_home", False)

        if motor_name == "bow_position_slider":
            if action == 'go_to_limit_switch':
                self.tb.publish("horsewheel_slider_home", False)
    """
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
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()

