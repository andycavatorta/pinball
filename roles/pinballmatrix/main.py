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
from thirtybirds3.adapters.sensors.AMT203_encoder import AMT203_absolute_encoder

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
        self.state = self.states.WAITING_FOR_CONNECTIONS
        self.controller_names = ["carousel1and2", "carousel3and4","carousel5and6"]
        self.motor_names = ["carousel1","carousel2","carousel3","carousel4","carousel5","carousel6"]
        self.chip_select_pins_for_abs_enc = [8,7,18,17,16,5]


        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("home")

        self.create_controllers_and_motors()
        self.set_rel_encoder_position_to_abs_encoder_position()

    def create_controllers_and_motors(self):
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
        for motor_name_ordinal in enumerate(self.motor_names):
            print("xxxxx",motor_name_ordinal[0], motor_name_ordinal[1])
            self.controllers.motors[motor_name_ordinal[1]].absolute_encoder = AMT203_absolute_encoder.AMT203(self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])


    def set_rel_encoder_position_to_abs_encoder_position(self):
        for motor_name in self.motor_names:
            abs_pos = self.controllers.motors[motor_name].absolute_encoder.get_position()
            rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute()
            print(motor_name,abs_pos,rel_pos)
        
        # are all controllers are responding?

        # are all abs encoders responding?

        # homing
        """
        # SET UP BOARDS AND MOTORS
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
        #SET UP ABSOLUTE ENCODERS
        encoders = [
            AMT203_absolute_encoder.AMT203(cs=8),
            AMT203_absolute_encoder.AMT203(cs=7),
            AMT203_absolute_encoder.AMT203(cs=18),
            AMT203_absolute_encoder.AMT203(cs=17),
            AMT203_absolute_encoder.AMT203(cs=16),
            AMT203_absolute_encoder.AMT203(cs=5),
        ]
        for encoder in encoders:
            print(encoder.get_position())
        self.start()
        """


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
            """
            v.motors["carousel_1"].go_to_speed_or_relative_position(0)
            time.sleep(1)
            self.controllers.motors["carousel_2"].go_to_speed_or_relative_position(0)
            time.sleep(1)
            self.controllers.motors["carousel_3"].go_to_speed_or_relative_position(0)
            time.sleep(1)
            self.controllers.motors["carousel_4"].go_to_speed_or_relative_position(0)
            time.sleep(1)
            self.controllers.motors["carousel_5"].go_to_speed_or_relative_position(0)
            time.sleep(1)
            self.controllers.motors["carousel_6"].go_to_speed_or_relative_position(0)
            time.sleep(3)

            self.controllers.motors["carousel_1"].go_to_speed_or_relative_position(2048)
            time.sleep(1)
            self.controllers.motors["carousel_2"].go_to_speed_or_relative_position(2048)
            time.sleep(1)
            self.controllers.motors["carousel_3"].go_to_speed_or_relative_position(2048)
            time.sleep(1)
            self.controllers.motors["carousel_4"].go_to_speed_or_relative_position(2048)
            time.sleep(1)
            self.controllers.motors["carousel_5"].go_to_speed_or_relative_position(2048)
            time.sleep(1)
            self.controllers.motors["carousel_6"].go_to_speed_or_relative_position(2048)
            """
            time.sleep(3)
            """
            try:
                topic, message = self.queue.get(True)
                print(">>>",topic, message)

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
            """
main = Main()

