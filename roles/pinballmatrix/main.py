"""



to-do: add serial safety after creating controllers
fix solenoid cross-wiring between carousel_4 and carouselcenter


"""
import math
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

position_calibration = {
    "carousel_1" : {
        "coco":{"front":3625,"back":1500,"left":3302,"right":3900},
        "naranja":{"front":348,"back":2319,"left":25,"right":623},
        "mango":{"front":1167,"back":3138,"left":844,"right":1442},
        "sandia":{"front":1986,"back":3960,"left":1663,"right":2261},
        "pina":{"front":2805,"back":683,"left":2482,"right":3080},
    },
    "carousel_2" : {
        "coco":{"front":0,"back":2125,"left":3773,"right":275},
        "naranja":{"front":819,"back":2944,"left":496,"right":1094},
        "mango":{"front":1638,"back":3763,"left":1315,"right":1913},
        "sandia":{"front":2460,"back":486,"left":2134,"right":2732},
        "pina":{"front":3279,"back":1305,"left":2953,"right":3551},
    },
    "carousel_3" : {
        "coco":{"front":575,"back":2700,"left":252,"right":850},
        "naranja":{"front":1394,"back":3519,"left":1071,"right":1669},
        "mango":{"front":2213,"back":242,"left":1890,"right":2488},
        "sandia":{"front":3035,"back":1061,"left":2709,"right":3307},
        "pina":{"front":3854,"back":1880,"left":3528,"right":30},
    },
    "carousel_4" : {
        "coco":{"front":2596,"back":625,"left":2273,"right":2871},
        "naranja":{"front":3415,"back":1444,"left":3092,"right":3690},
        "mango":{"front":138,"back":2263,"left":3911,"right":413},
        "sandia":{"front":960,"back":3082,"left":634,"right":1232},
        "pina":{"front":1779,"back":3901,"left":1453,"right":2051},
    },
    "carousel_5" : {
        "coco":{"front":375,"back":2500,"left":52,"right":650},
        "naranja":{"front":1194,"back":3319,"left":871,"right":1469},
        "mango":{"front":2013,"back":42,"left":1690,"right":2288},
        "sandia":{"front":2835,"back":861,"left":2509,"right":3107},
        "pina":{"front":3654,"back":1680,"left":3328,"right":3926},
    },
    "carousel_center" : {
        "coco":{"coco":1250,"naranja":431,"mango":3707,"sandia":2888,"pina":2069},
        "naranja":{"coco":2069,"naranja":1250,"mango":431,"sandia":3707,"pina":2888},
        "mango":{"coco":2888,"naranja":2069,"mango":1250,"sandia":431,"pina":3707},
        "sandia":{"coco":3707,"naranja":2888,"mango":2069,"sandia":1250,"pina":431},
        "pina":{"coco":431,"naranja":3707,"mango":2888,"sandia":2069,"pina":1250},
    }
}

class Speed_To_Position(threading.Thread):
    """
    to do: 
        add timeout feature
        add error or fault messages
    """
    def __init__(self, motor, absolute_encoder_first_value, callback):
        threading.Thread.__init__(self)
        self.motor = motor
        self.absolute_encoder_first_value = absolute_encoder_first_value
        self.relative_encoder_first_value = self.motor.get_encoder_counter_absolute(True)
        self.abs_offest = self.absolute_encoder_first_value - self.relative_encoder_first_value
        self.callback = callback
        self.encoder_resolution = 4096
        self.queue = queue.Queue()
        self.timeout_timer = time.time()
        self.timeout_timeout = 60 # seconds
        self.discrepancy_threshold = 25
        self.start()

    def get_position_with_offset(self):
        return self.motor.get_encoder_counter_absolute(True) - self.abs_offest

    #def rotate_left_to_position(self, destination, limit_to_less_than_one_rotation=True):
    #    self.add_to_queue("rotate_left_to_position",destination,limit_to_less_than_one_rotation)

    #def rotate_right_to_position(self, destination, limit_to_less_than_one_rotation=True):
    #    self.add_to_queue("rotate_right_to_position",destination,limit_to_less_than_one_rotation)

    def rotate_to_position(self, destination, limit_to_less_than_one_rotation=True):
        self.add_to_queue("rotate_to_position",destination,limit_to_less_than_one_rotation)

    def add_to_queue(self, command, destination, limit_to_less_than_one_rotation):
        self.queue.put((command, destination, limit_to_less_than_one_rotation))

    def run(self):
        while True:
            command, destination, limit_to_less_than_one_rotation = self.queue.get(True)
            retry_stalled_motor = 0
            current_position = self.get_position_with_offset()
            if command == "rotate_to_position":
                self.timeout_timer = time.time() + self.timeout_timeout
                dir = 1 if destination > current_position else -1
                speed = dir * 2
                slop = 0 * -30    # loose attempt to stop before overshooting
                destination_adjusted = destination + slop
                self.motor.set_motor_speed(speed)
                while (current_position < destination_adjusted) if speed > 0 else (current_position > destination_adjusted):
                    current_position = self.get_position_with_offset()
                    runtime_status_flags = self.motor.get_runtime_status_flags()
                    if runtime_status_flags['motor_stalled']:
                        if retry_stalled_motor <= 3:
                            retry_stalled_motor += 1
                            self.motor.set_motor_speed(speed)
                            time.sleep(1)
                        else:
                            self.callback(
                                "event_destination_stalled", 
                                [self.motor.name, True, self.get_position_with_offset(), self.get_position_with_offset()-destination],
                                None,
                                None)
                            self.motor.set_motor_speed(0)
                            break 
                    if time.time() > self.timeout_timer:
                        self.callback(
                            "event_destination_timeout", 
                            [self.motor.name, True, self.get_position_with_offset(), self.get_position_with_offset()-destination],
                            None,
                            None)
                        self.motor.set_motor_speed(0)
                        break 
                self.motor.set_motor_speed(0)
            time.sleep(0.02)
            discrepancy = self.get_position_with_offset()-destination
            self.callback(
                "event_destination_reached", 
                [
                    self.motor.name, 
                    True if discrepancy < self.discrepancy_threshold else False, 
                    self.get_position_with_offset(), 
                    discrepancy
                ],
                None,
                None)

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
        self.tb.subscribe_to_topic("cmd_rotate_carousel_to_target")
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

        self.motor_names = ("carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_center")
        ##### absolute encoder status #####
        self.position_calibration = position_calibration
        #self.absolute_encoders_presences = [False,False,False,False,False,False]
        #self.absolute_encoders_positions = [None,None,None,None,None,None]
        self.absolute_encoders_presences = [True,True,True,True,True,True]
        self.absolute_encoders_positions = [0,0,0,0,0,0]
        self.absolute_encoders_zeroed = [True,True,True,True,True,True]
        self.already_called_once = False
        time.sleep(1) # just being superstitious
        self.start()

    def request_target_position_confirmed(self, message):
        print(">>>>> Main request_target_position_confirmed")
        """
        to do: finish
        """
        return True

    """
    def sync_relative_encoders_to_absolute_encoders(self):
        print(">>>>> Main sync_relative_encoders_to_absolute_encoders")
        if self.high_power_init: # if power is on
            # to do: try/catch blocks and/or general system to track if hi power is on
            for abs_ordinal_position in enumerate(self.absolute_encoders_positions):
                abs_ordinal, abs_position = abs_ordinal_position
                print("sync_relative_encoders_to_absolute_encoders",abs_ordinal, abs_position)
                time.sleep(0.1)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_operating_mode(0)
                time.sleep(0.1)
                self.controllers.motors[self.motor_names[abs_ordinal]].set_encoder_counter(abs_position)
                time.sleep(0.1)
                #self.controllers.motors[self.motor_names[abs_ordinal]].set_operating_mode(6)
                #time.sleep(0.1)
                #self.controllers.motors[self.motor_names[abs_ordinal]].set_motor_speed(0)
    """
    
    def cmd_rotate_carousel_to_target(self, carousel_name, fruit_name, position_name):
        try:
            destination = self.position_calibration[carousel_name][fruit_name][position_name]
            self.controllers.motors[carousel_name].speed_to_position.rotate_to_position(destination)
        except KeyError as e:
            print(e)
            return

    ##### POWER-ON INIT #####
    def get_absolute_positions(self):
        if self.already_called_once:
            return
        print(">>>>> Main get_absolute_positions")
        """
        this must not be called when the motors are not in a PID mode of any kind
        """
        if self.high_power_init == True:
            self.absolute_encoders_presences = [True]*6
            # create SPI interfaces for AMT203
            # time.sleep(3)
            # print(">>>>> Main get_absolute_positions 0")
            # self.absolute_encoders = AMT203(gpios_for_chip_select=[12,13,17,18,5,16])
            # time.sleep(3)
            # # verify that encoders are present
            # print(">>>>> Main get_absolute_positions 1", self.absolute_encoders)
            # self.absolute_encoders_presences = self.absolute_encoders.get_presences()
            # time.sleep(3)
            # # read absolute positions
            # print(">>>>> Main get_absolute_positions 2", self.absolute_encoders_presences)
            # self.absolute_encoders_positions = self.absolute_encoders.get_positions()
            # time.sleep(3)
            # # stop SPI interfaces - spidev.close()
            # print(">>>>> Main get_absolute_positions 3", self.absolute_encoders_positions)
            # self.absolute_encoders.close()
            # print(">>>>> Main get_absolute_positions 4", self.absolute_encoders)
            # self.already_called_once = True
            # time.sleep(1)

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
                "carousel_center":settings.Roboteq.MOTORS["carousel_center"],
            }
        )
        time.sleep(2)

    def response_high_power_enabled(self, message):
        print(">>>>> Main response_high_power_enabled")
        if message: # if power on
            self.high_power_init = True
            self.create_controllers_and_motors()
            self.get_absolute_positions()
            #self.sync_relative_encoders_to_absolute_encoders()
            for motor_ordinal, motor_name in enumerate(self.motor_names):
                self.controllers.motors[motor_name].speed_to_position = Speed_To_Position(self.controllers.motors[motor_name], self.absolute_encoders_positions[motor_ordinal], self.add_to_queue)
            for motor_name in self.motor_names:
                time.sleep(0.1)
                print("SDC values",motor_name,self.controllers.motors[motor_name].get_encoder_counter_absolute(True))
        else: # if power off
            self.high_power_init = False
            self.absolute_encoders_presences = [False,False,False,False,False,False]
            self.absolute_encoders_positions = [None,None,None,None,None,None]
            self.absolute_encoders_zeroed = [False,False,False,False,False,False]

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
                "carousel_center":self.request_sdc2160_channel_faults("carousel_center"),
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
        # engage emergency stop until encoder problem is solved
        # self.controllers.boards["carousel1and2"].emergency_stop()
        # self.controllers.boards["carousel3and4"].emergency_stop()
        # self.controllers.boards["carousel5and6"].emergency_stop()

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
                self.controllers.motors['carousel_center'].get_closed_loop_error(True),
            ]
        else:
            motor_name = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_center'][fruit_id]
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
                self.controllers.motors['carousel_center'].get_encoder_counter_absolute(True),
            ]
        else:
            motor_name = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_center'][fruit_id]
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
            if topic == b'cmd_rotate_carousel_to_target':
                carousel_name, fruit_id, target_name = message
                self.cmd_rotate_carousel_to_target(carousel_name, fruit_id, target_name)

            if topic == b'connected':
                pass               

            if topic == "event_destination_timeout":
                print(topic, message, origin, destination)
                # to do: sent to controller
                self.tb.publish(
                    topic=topic, 
                    message=message
                )

            if topic == "event_destination_stalled":
                print(topic, message, origin, destination)
                # to do: sent to controller
                self.tb.publish(
                    topic=topic, 
                    message=message
                )

            if topic == 'event_destination_reached':
                print(topic, message, origin, destination)
                # to do: sent to controller
                self.tb.publish(
                    topic=topic, 
                    message=message
                )

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
                self.tb.publish(
                    topic="response_computer_details", 
                    message=self.request_computer_details()
                )

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
                        "carousel_center":self.request_sdc2160_channel_faults("carousel_center"),
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
