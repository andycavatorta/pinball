import importlib
import mido
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time
import traceback

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
import common.deadman as deadman
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.sensors.AMT203_encoder.AMT203_absolute_encoders import AMT203
from thirtybirds3.adapters.sensors import ina260_current_sensor

GPIO.setmode(GPIO.BCM)


###########################
# S Y S T E M   T E S T S #
###########################

# + test ability to read encoders via SPI
# test ability to communicate with SDC2160
# check SDC2160 for fault flags or error states
# check SDC2160 for current consumption
# check SDC2160 for temperature
# if not yet zeroed:
    # rotate carousel to abs zero position
    # check abs position
    # set relative encoder to zero
# rotate carousel to center self-fruit
# check agreement between absolute and relative encoders

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
        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.chip_select_pins_for_abs_enc = [12,13,17,18,5,16]

        self.hostname = self.tb.get_hostname()
        self.deadman = deadman.Deadman_Switch(self.tb)

        self.high_power_init = False

        

        #self.current_sensor = ina260_current_sensor.INA260()
        """
        self.absolute_encoders = [
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=8),
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=7),
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=18),
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=17),
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=16),
            AMT203_absolute_encoder.AMT203(speed_hz=5000, cs=5),
        ]
        """        
        self.absolute_encoders_zeroed = False
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("high_power_enabled")
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("request_24v_current")
        self.tb.subscribe_to_topic("request_sdc2160_present")
        self.tb.subscribe_to_topic("request_sdc2160_faults")
        self.tb.subscribe_to_topic("request_amt203_present")
        self.tb.subscribe_to_topic("request_amt203_zeroed")
        self.tb.subscribe_to_topic("request_amt203_absolute_position")
        self.tb.subscribe_to_topic("request_amt203_relative_position")
        self.tb.subscribe_to_topic("request_sdc2160_details")
        self.tb.subscribe_to_topic("request_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("request_sdc2160_controller_faults")
        self.tb.subscribe_to_topic("request_target_position_confirmed")
        self.tb.subscribe_to_topic("cmd_rotate_fruit_to_target")

        self.start()


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

    def request_computer_details(self):
        return {
            "df":self.tb.get_system_disk,
            "cpu_temp":self.tb.get_core_temp,
            "pinball_git_timestamp":self.tb.app_get_git_timestamp,
            "tb_git_timestamp":self.tb.tb_get_git_timestamp,
        }

    def request_24v_current(self):
        return self.current_sensor.get_current()

    def request_sdc2160_present(self):
        present = {
            "carousel1and2":"",
            "carousel3and4":"",
            "carousel5and6":""
        }
        for controller_name in present:
            try:     
                mcu_id = self.controller.boards[controller_name].get_mcu_id()
                present[controller_name] = mcu_id
            except:
                present[controller_name] = ""
        return present


    def request_sdc2160_faults(self):
        pass

    def request_amt203_present(self):
        return self.absolute_encoders.get_presences()

    def request_amt203_zeroed(self):
        return self.absolute_encoders_zeroed

    def request_amt203_absolute_position(self, fruit_id=-1):
        if fruit_id == -1:
            return self.absolute_encoders.get_positions()
        else:
            return self.absolute_encoders.get_position(self.chip_select_pins_for_abs_enc[fruit_id])

    def request_amt203_relative_position(self):
        pass

    def request_sdc2160_details(self):
        pass

    def request_sdc2160_channel_faults(self):
        pass

    def request_sdc2160_controller_faults(self):
        pass

    def request_target_position_confirmed(self):
        pass

    def cmd_rotate_fruit_to_target(self, fruit_id, target_name):
        pass


    #####
    def status_receiver(self, msg):
        print("status_receiver", msg)
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
                print(topic, message)
                if topic == b'connected':
                    pass
                if topic == b'high_power_enabled':
                    time.sleep(2)
                    if message; #transition for high power
                        if not self.high_power_init:# if this is the first transition to high power
                            self.high_power_init = True
                            self.create_controllers_and_motors()
                            self.absolute_encoders = AMT203(speed_hz=5000,gpios_for_chip_select=self.chip_select_pins_for_abs_enc)

                if topic == b'request_computer_details':
                    self.tb.publish(
                        topic="respond_computer_details", 
                        message=self.request_computer_details()
                    )
                if topic == b'request_24v_current':
                    self.tb.publish(
                        topic="respond_24v_current", 
                        message=self.request_24v_current()
                    )                    
                if topic == b'request_sdc2160_present':
                    pass
                if topic == b'request_sdc2160_faults':
                    pass
                if topic == b'request_amt203_present':
                    self.tb.publish(
                        topic="respond_amt203_present", 
                        message=self.request_amt203_present()
                    )                    
                if topic == b'request_amt203_zeroed':
                    self.tb.publish(
                        topic="respond_amt203_zeroed", 
                        message=self.request_amt203_zeroed()
                    )                    
                if topic == b'request_amt203_absolute_position':
                    fruit_id = mess
                    age
                    self.tb.publish(
                        topic="respond_amt203_absolute_position", 
                        message=self.request_amt203_absolute_position(fruit_id)
                    )                    
                if topic == b'request_amt203_relative_position':
                    pass
                if topic == b'request_sdc2160_details':
                    pass
                if topic == b'request_sdc2160_channel_faults':
                    pass
                if topic == b'request_sdc2160_controller_faults':
                    pass
                if topic == b'request_target_position_confirmed':
                    pass
                if topic == b'cmd_rotate_fruit_to_target':
                    pass

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()
