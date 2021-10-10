"""




"""

import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time
import traceback

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.sensors import ina260_current_sensor
from thirtybirds3.adapters.sensors.AMT203_encoder.AMT203_absolute_encoders import AMT203
import common.deadman as deadman
import settings

 

GPIO.setmode(GPIO.BCM)

class Rotate_to_Position(threading.Thread):
    """
    to do: 
        add timeout feature
        add error or fault messages
    """
    def __init__(self, motor, callback):
        print(">>>>> Rotate_to_Position __init__")
        threading.Thread.__init__(self)
        self.motor = motor
        self.callback = callback
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, destination, speed=70, precision=100):
        print(">>>>> Rotate_to_Position add_to_queue")
        self.queue.put((destination, speed, precision))

    def run(self):
        print(">>>>> Rotate_to_Position run")
        while True:
            destination, speed, precision = self.queue.get(True)
            # get current position
            current_position = self.motor.get_encoder_counter_absolute(True)
            # calculate direction
            speed = -abs(speed) if current_position >= destination else abs(speed)
            # change mode to speed position
            #self.motor.set_operating_mode(6)
            # set speed
            # self.motor.set_speed(speed)
            if speed > 0:
                while current_position < destination - precision:
                    current_position = self.motor.get_encoder_counter_absolute(True)
                    print(destination, current_position, speed)
                    time.sleep(0.01)
            if speed < 0:
                while current_position > destination + precision:
                    current_position = self.motor.get_encoder_counter_absolute(True)
                    print(destination, current_position, speed)
                    time.sleep(0.01)
            print("event_destination_reached")
            self.callback("event_destination_reached", self.motor.get_encoder_counter_absolute(True), self.motor.name, None)
            
class Roboteq_Data_Receiver(threading.Thread):
    def __init__(self):
        print(">>>>> Roboteq_Data_Receiver __init__")
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, message):
        print(">>>>> Roboteq_Data_Receiver add_to_queue")
        self.queue.put(message)

    def run(self):
        print(">>>>> Roboteq_Data_Receiver run")
        while True:
            message = self.queue.get(True)
            print("data",message)
            # to do : what should happen with this data?
            #if "internal_event" in message:
            #    pass

roboteq_data_receiver = Roboteq_Data_Receiver()

class Main(threading.Thread):
    def __init__(self):
        print(">>>>> Main __init__")
        threading.Thread.__init__(self)
        ###### NETWORK #####
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.hostname = self.tb.get_hostname()
        self.deadman = deadman.Deadman_Switch(self.tb)

        self.chip_select_pins_for_abs_enc = [12,13,17,18,5,16]
        ##### SUBSCRIPTIONS #####
        self.tb.subscribe_to_topic("cmd_rotate_fruit_to_target")
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("request_amt203_absolute_position")
        self.tb.subscribe_to_topic("request_amt203_present")
        self.tb.subscribe_to_topic("request_amt203_zeroed")
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("request_current_sensor_nominal")
        self.tb.subscribe_to_topic("request_current_sensor_present")
        self.tb.subscribe_to_topic("request_current_sensor_value")
        self.tb.subscribe_to_topic("request_motor_details")
        self.tb.subscribe_to_topic("request_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("request_sdc2160_closed_loop_error")
        self.tb.subscribe_to_topic("request_sdc2160_controller_faults")
        self.tb.subscribe_to_topic("request_sdc2160_faults")
        self.tb.subscribe_to_topic("request_sdc2160_present")
        self.tb.subscribe_to_topic("request_sdc2160_relative_position")
        self.tb.subscribe_to_topic("request_system_tests")
        self.tb.subscribe_to_topic("request_target_position_confirmed")
        self.tb.subscribe_to_topic("response_high_power_enabled")


        self.motor_names = ("carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6")
        ##### absolute encoder status #####
        self.absolute_encoders_presences = [False,False,False,False,False,False]
        self.absolute_encoders_positions = [None,None,None,None,None,None]
        self.absolute_encoders_zeroed = [True,True,True,True,True,True]
        time.sleep(1) # just being superstitious
        self.start()

    def request_target_position_confirmed(self, message):
        print(">>>>> Main request_target_position_confirmed")
        """
        to do: finish
        """
        return True

    def sync_relative_encoders_to_absolute_encoders(self):
        print(">>>>> Main sync_relative_encoders_to_absolute_encoders")
        if self.high_power_init: # if power is on
            # to do: try/catch blocks and/or general system to track if hi power is on
            for abs_ordinal_position in enumerate(self.absolute_encoders_positions):
                abs_ordinal, abs_position = abs_ordinal_position
                time.sleep(0.1)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_operating_mode(0)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_encoder_counter(abs_position)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_operating_mode(1)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_motor_speed(0)

    
    def cmd_rotate_fruit_to_target(self, carousel_name, fruit_id, target_name):
        print(">>>>> Main cmd_rotate_fruit_to_target")
        # calculate target position
        pass
        """
        target_position = settings.Carousel_Fruit_Offsets[fruit_id] + settings.Carousel_Target_Positions[target_name]
        current_position = self.controllers.motors[carousel_name].get_encoder_counter_absolute(True)
        current_position = current_position % 4096
        self.controllers.motors[carousel_name].go_to_absolute_position(current_position)
        """

    ##### POWER-ON INIT #####
    def get_absolute_positions(self):
        print(">>>>> Main get_absolute_positions")
        """
        this must not be called when the motors are in a PID mode of any kind
        """
        if self.high_power_init == True:
            # create SPI interfaces for AMT203
            time.sleep(3)
            self.absolute_encoders = AMT203(gpios_for_chip_select=[12,13,17,18,5,16], speed_hz = 5859375)
            time.sleep(3)
            # verify that encoders are present
            self.absolute_encoders_presences = self.absolute_encoders.get_presences()
            time.sleep(3)
            # read absolute positions
            self.absolute_encoders_positions = self.absolute_encoders.get_positions()
            time.sleep(3)
            # stop SPI interfaces - spidev.close()
            self.absolute_encoders.close()
            time.sleep(1)

    def create_controllers_and_motors(self):
        print(">>>>> Main create_controllers_and_motors")
        """
        this code assumes this method can be run safely more than once, 
            as high power turns off and on
        """
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
        time.sleep(2)

    def response_high_power_enabled(self, message):
        print(">>>>> Main response_high_power_enabled")
        if message: # if power on
            self.high_power_init = True
            self.create_controllers_and_motors()
            self.get_absolute_positions()
            self.sync_relative_encoders_to_absolute_encoders()
            for motor_name in self.motor_names:
                self.controllers.motors[motor_name].rotate_to_position = Rotate_to_Position(self.controllers.motors[motor_name], self.add_to_queue)
            print("AMT values:",self.absolute_encoders_positions)
            for motor_name in self.motor_names:
                time.sleep(0.1)
                print("sDC values",motor_name,self.controllers.motors[motor_name].get_encoder_counter_absolute(True))
            #self.absolute_encoders_presences = [True,True,True,True,True,True]
            #self.absolute_encoders_positions = [0,0,0,0,0,0]
            #self.absolute_encoders_zeroed = [True,True,True,True,True,True]
        else: # if power off
            self.high_power_init = False
            self.absolute_encoders_presences = [False,False,False,False,False,False]
            self.absolute_encoders_positions = [None,None,None,None,None,None]

    def request_amt203_zeroed(self):
        print(">>>>> Main request_amt203_zeroed")
        """
        to do: what does this mean now?
        """
        return self.absolute_encoders_zeroed


    ##### SETUP METHODS #####

    def request_system_tests(self):
        print(">>>>> Main request_system_tests")
        # INA260 current
        self.tb.publish(
            topic="response_current_sensor_value", 
            message=self.request_current_sensor_value()
        )
        # computer details
        self.tb.publish(
            topic="response_computer_details", 
            message=self.request_computer_details()
        )
        # motor controllers present
        self.tb.publish(
            topic="response_sdc2160_present", 
            message=self.request_sdc2160_present()
        )
        # motor controllers faults

        self.tb.publish(
            topic="response_sdc2160_controller_faults",
            message=self.request_sdc2160_controller_faults()
        )
        #board "get_runtime_fault_flags" True
        self.tb.publish(
           topic="response_sdc2160_channel_faults", 
            message={
                "carousel_1":self.request_sdc2160_channel_faults("carousel_1"),
                "carousel_2":self.request_sdc2160_channel_faults("carousel_2"),
                "carousel_3":self.request_sdc2160_channel_faults("carousel_3"),
                "carousel_4":self.request_sdc2160_channel_faults("carousel_4"),
                "carousel_5":self.request_sdc2160_channel_faults("carousel_5"),
                "carousel_6":self.request_sdc2160_channel_faults("carousel_6"),
            }
        )

        self.tb.publish(
           topic="response_amt203_present", 
            message=self.request_amt203_present()
        )               
        # absolute encoder value
        self.tb.publish(
            topic="response_amt203_absolute_position", 
            message=self.request_amt203_absolute_position()
        )
        # relative encoder value
        self.tb.publish(
            topic="response_sdc2160_relative_position", 
            message=self.request_sdc2160_relative_position()
        )





    ##### SYSTEM TESTS #####

    def request_computer_details(self):
        print(">>>>> Main request_computer_details")
        return {
            "df":self.tb.get_system_disk(),
            "cpu_temp":self.tb.get_core_temp(),
            "pinball_git_timestamp":self.tb.app_get_git_timestamp(),
            "tb_git_timestamp":self.tb.tb_get_git_timestamp(),
        }

    def request_current_sensor_nominal(self):
        print(">>>>> Main request_current_sensor_nominal")
        #TODO: Do the ACTUAL tests here.
        return True
        
    def request_current_sensor_present(self):
        print(">>>>> Main request_current_sensor_present")
        #TODO: Do the ACTUAL tests here.
        return True
        
    def request_current_sensor_value(self):
        print(">>>>> Main request_current_sensor_value")
        #TODO: Do the ACTUAL tests here.
        return 0.0

    def request_sdc2160_channel_faults(self, motor_name):
        print(">>>>> Main request_sdc2160_channel_faults")
        return {
            "temperature":self.controllers.motors[motor_name].get_temperature(True),
            "runtime_status_flags":self.controllers.motors[motor_name].get_runtime_status_flags(True),
            "closed_loop_error":self.controllers.motors[motor_name].get_closed_loop_error(True),
            "stall_detection":False,   #self.controllers.motors[motor_name].get_stall_detection(True),
            "motor_amps":self.controllers.motors[motor_name].get_motor_amps(True),
        }

    def request_sdc2160_closed_loop_error(self, fruit_id=-1):
        print(">>>>> Main request_sdc2160_closed_loop_error")
        if fruit_id == -1:
            return [
                self.controllers.motors['carousel_1'].get_closed_loop_error(True),
                self.controllers.motors['carousel_2'].get_closed_loop_error(True),
                self.controllers.motors['carousel_3'].get_closed_loop_error(True),
                self.controllers.motors['carousel_4'].get_closed_loop_error(True),
                self.controllers.motors['carousel_5'].get_closed_loop_error(True),
                self.controllers.motors['carousel_6'].get_closed_loop_error(True),
            ]
        else:
            motor_name = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6'][fruit_id]
            return self.controllers.motors[motor_name].get_closed_loop_error()

    def request_sdc2160_controller_faults(self):
        print(">>>>> Main request_sdc2160_controller_faults")
        return [
            self.controllers.boards["carousel1and2"].get_runtime_fault_flags(True),
            self.controllers.boards["carousel3and4"].get_runtime_fault_flags(True),
            self.controllers.boards["carousel5and6"].get_runtime_fault_flags(True),
        ]

    def request_sdc2160_faults(self):
        print(">>>>> Main request_sdc2160_faults")
        pass

    def request_sdc2160_present(self):
        print(">>>>> Main request_sdc2160_present")
        present = {
            "carousel1and2":"",
            "carousel3and4":"",
            "carousel5and6":""
        }
        for controller_name in present:
            try:     
                mcu_id = self.controllers.boards[controller_name].get_mcu_id()
                present[controller_name] = mcu_id
            except:
                present[controller_name] = ""
        return present

    def request_sdc2160_relative_position(self, fruit_id=-1):
        print(">>>>> Main request_sdc2160_relative_position")
        if fruit_id == -1:
            return [
                self.controllers.motors['carousel_1'].get_encoder_counter_absolute(True),
                self.controllers.motors['carousel_2'].get_encoder_counter_absolute(True),
                self.controllers.motors['carousel_3'].get_encoder_counter_absolute(True),
                self.controllers.motors['carousel_4'].get_encoder_counter_absolute(True),
                self.controllers.motors['carousel_5'].get_encoder_counter_absolute(True),
                self.controllers.motors['carousel_6'].get_encoder_counter_absolute(True),
            ]
        else:
            motor_name = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6'][fruit_id]
            return self.controllers.motors[motor_name].get_encoder_counter_absolute()



    def status_receiver(self, msg):
        print(">>>>> Main status_receiver")
        print("status_receiver", msg)
    def network_message_handler(self, topic, message, origin, destination):
        print(">>>>> Main network_message_handler")
        print(topic, message, origin, destination)
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print(">>>>> Main exception_handler")
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print(">>>>> Main network_status_change_handler")
        print("network_status_change_handler", status, hostname)
    def add_to_queue(self, topic, message, origin, destination):
        print(">>>>> Main add_to_queue")
        self.queue.put((topic, message, origin, destination))
    def run(self):
        print(">>>>> Main run")
        while True:
            topic, message, origin, destination = self.queue.get(True)
            if topic == b'cmd_rotate_fruit_to_target':
                carousel_name, fruit_id, target_name = message
                self.cmd_rotate_fruit_to_target(carousel_name, fruit_id, target_name)

            if topic == b'connected':
                pass               


            if topic == b'event_destination_reached':
                print(topic, message, origin, destination)
                # to do: sent to controller

            if topic == b'request_amt203_absolute_position':
                self.tb.publish(
                    topic="response_amt203_absolute_position", 
                    message=self.absolute_encoders_positions
                )

            if topic == b'request_amt203_present':
                self.tb.publish(
                    topic="response_amt203_present", 
                    message=self.absolute_encoders_presences
                )               
            if topic == b'request_amt203_zeroed':
                self.tb.publish(
                    topic="response_amt203_zeroed", 
                    message=self.request_amt203_zeroed()
                )     

            if topic == b'request_computer_details':
                print("!!!!!! 0")
                self.tb.publish(
                    topic="response_computer_details", 
                    message=self.request_computer_details()
                )
                print("!!!!!! 2")

            if topic == b'request_current_sensor_nominal':
                self.tb.publish(
                    topic="response_current_sensor_nominal",
                    message=self.request_current_sensor_nominal()
                )
            if topic == b'request_current_sensor_present':
                self.tb.publish(
                    topic="response_current_sensor_present",
                    message=self.request_current_sensor_present()
                )
            if topic == b'request_current_sensor_value':
                self.tb.publish(
                    topic="response_current_sensor_value",
                    message=self.request_current_sensor_value()
                )

            if topic == b'request_motor_details':
                """
                to do : is this implemented?
                """

            if topic == b'request_sdc2160_channel_faults':
                self.tb.publish(
                   topic="response_sdc2160_channel_faults", 
                    message={
                        "carousel_1":self.request_sdc2160_channel_faults("carousel_1"),
                        "carousel_2":self.request_sdc2160_channel_faults("carousel_2"),
                        "carousel_3":self.request_sdc2160_channel_faults("carousel_3"),
                        "carousel_4":self.request_sdc2160_channel_faults("carousel_4"),
                        "carousel_5":self.request_sdc2160_channel_faults("carousel_5"),
                        "carousel_6":self.request_sdc2160_channel_faults("carousel_6"),
                    }
                )

            if topic == b'request_sdc2160_closed_loop_error':
                self.tb.publish(
                    topic="response_sdc2160_closed_loop_error", 
                    message=self.request_sdc2160_closed_loop_error()
                )    

            if topic == b'request_sdc2160_controller_faults':
                self.tb.publish(
                    topic="response_sdc2160_controller_faults",
                    message=self.request_sdc2160_controller_faults()
                )

            if topic == b'request_sdc2160_faults':
                pass

            if topic == b'request_sdc2160_present':
                self.tb.publish(
                    topic="response_sdc2160_present", 
                    message=self.request_sdc2160_present()
                )

            if topic == b'request_sdc2160_relative_position':
                self.tb.publish(
                    topic="response_sdc2160_relative_position", 
                    message=self.request_sdc2160_relative_position()
                )    

            if topic == b'request_system_tests':
                self.request_system_tests()

            if topic == b'request_target_position_confirmed':
                self.tb.publish(
                    topic="response_target_position_confirmed",
                    message=self.request_target_position_confirmed()
                )

            if topic == b'response_high_power_enabled': 
                self.response_high_power_enabled(message)


main = Main()
