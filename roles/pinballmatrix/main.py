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
from thirtybirds3.adapters.sensors.AMT203_encoder.AMT203_absolute_encoders import AMT203
from thirtybirds3.adapters.sensors import ina260_current_sensor

GPIO.setmode(GPIO.BCM)


###########################
# S Y S T E M   T E S T S #
###########################

#[13,12,18,17,16,5]

# test ability to read encoders via SPI
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

        self.encoders = AMT203(speed_hz=5000,gpios_for_chip_select=self.chip_select_pins_for_abs_enc)

        self.hostname = self.tb.get_hostname()
        self.deadman = deadman.Deadman_Switch(self.tb)


        time.sleep(5)
        print("encoders", self.encoders.get_positions())

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
        pass

    def request_sdc2160_faults(self):
        pass

    def request_amt203_present(self):
        amt203_present = [False,False,False,False,False,False,]
        for position_and_absolute_encoder in enumerate(self.absolute_encoders):
            position, absolute_encoder = position_and_absolute_encoder
            try:
                absolute_encoder.get_position()
                amt203_present[position] = True
            except Exception: # todo: specify exceptions
                pass # todo: hande exceptions
        return amt203_present

    def request_amt203_zeroed(self):
        return self.absolute_encoders_zeroed

    def request_amt203_absolute_position(self, fruit_id=-1):
        if fruit_id > -1:
            return self.absolute_encoders[fruit_id].get_position()
        else:
            return [
                self.absolute_encoders[0].get_position(),
                self.absolute_encoders[1].get_position(),
                self.absolute_encoders[2].get_position(),
                self.absolute_encoders[3].get_position(),
                self.absolute_encoders[4].get_position(),
                self.absolute_encoders[5].get_position()
            ]

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
                    fruit_id = message
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
