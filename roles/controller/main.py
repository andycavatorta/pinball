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

setting_safety_enable_duration = 3
setting_safety_enable_gpio = 26

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup( setting_safety_enable_gpio, GPIO.OUT )
        self.queue = queue.Queue()
        self.tb = tb
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        """
        self.required_hosts = {
            "pinballmatrix",
            "pinball1game",
            "pinball2game",
            "pinball3game",
            "pinball4game",
            "pinball5game",
            "pinball1display",
            "pinball2display",
            "pinball3display",
            "pinball4display",
            "pinball5display"
        }
        """
        self.hosts_alive = set()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            time.sleep(setting_safety_enable_duration)
            try:
                while True:
                    deadman_message = self.queue.get(False)
                    topic, message, origin, destination = deadman_message
                    self.hosts_alive.add(origin)
            except queue.Empty:
                pass
            mission_hosts = self.required_hosts.difference(self.hosts_alive)
            if len(mission_hosts) > 0:
                print("missing hosts:", self.required_hosts.difference(self.hosts_alive))
            GPIO.output(setting_safety_enable_gpio, GPIO.HIGH if self.required_hosts.issubset(self.hosts_alive) else GPIO.LOW)
            self.hosts_alive = set()
            
# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class Modes:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
            ERROR = "error"
            ATTRACTION = "attraction"
            BARTER_MODE_INTRO = "barter_mode_intro"
            BARTER_MODE = "barter_mode"
            MONEY_MODE_INTRO = "money_mode_intro"
            MONEY_MODE = "money_mode"
            ENDING = "ending"
            RESET = "reset"
        self.modes =Modes()
        self.mode = self.modes.WAITING_FOR_CONNECTIONS

        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.safety_enable = Safety_Enable(self.tb)
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
                #print(">>>",topic, message, origin, destination)
                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

