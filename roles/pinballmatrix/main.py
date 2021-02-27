import importlib
import mido
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
from thirtybirds3.adapters.sensors import AMT203_absolute_encoder

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
        self.controllers = roboteq_command_wrapper.Controllers(
            roboteq_data_receiver.add_to_queue, 
            self.status_receiver, 
            self.network_status_change_handler, 
            {
                "carousel1and2":settings.Roboteq.BOARDS["carousel1and2"],
                "carousel3and4":settings.Roboteq.BOARDS["carousel3and4"],
                "carousel5and6":settings.Roboteq.BOARDS["carousel5and6"],
            },
            {
                "carousel_1":settings.Roboteq.MOTORS["carousel_1"],
                "carousel_2":settings.Roboteq.MOTORS["carousel_2"],
                "carousel_3":settings.Roboteq.MOTORS["carousel_3"],
                "carousel_4":settings.Roboteq.MOTORS["carousel_4"],
                "carousel_5":settings.Roboteq.MOTORS["carousel_5"],
                "carousel_6":settings.Roboteq.MOTORS["carousel_6"],
            }
        )
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("home")
        #self.controllers.macros["carousel_1"].set_speed(0)
        #self.controllers.macros["carousel_2"].set_speed(0)
        #self.controllers.macros["carousel_3"].set_speed(0)
        #self.controllers.macros["carousel_4"].set_speed(0)
        self.controllers.macros["carousel_5"].set_speed(60)
        self.controllers.macros["carousel_6"].set_speed(60)
        self.controllers.macros["carousel_5"].set_speed(60)
        self.controllers.macros["carousel_6"].set_speed(60)
        self.start()

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self, topic, message):
        self.add_to_queue(topic, message)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))
    def run(self):
        while True:
            time.sleep(1)
            """
            print("carousel_1")
            print(self.controllers.motors["carousel_1"].get_encoder_counter_absolute(True))
            print("carousel_2")
            print(self.controllers.motors["carousel_2"].get_encoder_counter_absolute(True))
            print("carousel_3")
            print(self.controllers.motors["carousel_3"].get_encoder_counter_absolute(True))
            print("carousel_4")
            print(self.controllers.motors["carousel_4"].get_encoder_counter_absolute(True))
            print("carousel_5")
            print(self.controllers.motors["carousel_5"].get_encoder_counter_absolute(True))
            print("carousel_6")
            print(self.controllers.motors["carousel_6"].get_encoder_counter_absolute(True))
            """
            """
            try:
                topic, message = self.queue.get(True)
                print(">>>",topic, message)

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
            """
main = Main()

