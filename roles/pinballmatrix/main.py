"""
to do:
    event_carousel_error
    event_carousel_target_reached
    response_carousel_absolute
    response_carousel_relative


topics subscribed:
    cmd_rotate_fruit_to_target
    connected
    deadman
    request_amt203_absolute_position
    request_amt203_present
    request_amt203_zeroed
    request_motor_details
    request_sdc2160_channel_faults
    request_sdc2160_closed_loop_error
    request_sdc2160_controller_faults
    request_sdc2160_faults
    request_sdc2160_present
    request_sdc2160_relative_position
    request_target_position_confirmed
    request_computer_details
    request_current_sensor_present
    request_current_sensor_value
    request_current_sensor_nominal
    request_system_tests
    connected




topics published:
    connected
    event_carousel_error
    event_carousel_target_reached
    request_computer_details
    request_current_sensor_nominal
    request_current_sensor_present
    request_current_sensor_value
    request_system_tests
    response_amt203_absolute_position
    response_amt203_present
    response_amt203_zeroed
    response_carousel_absolute
    response_carousel_relative
    response_computer_details
    response_current_sensor_value
    response_sdc2160_channel_faults
    response_sdc2160_closed_loop_error
    response_sdc2160_controller_faults
    response_sdc2160_present
    response_sdc2160_relative_position


"""

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

        self.absolute_encoders_zeroed = False
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("response_high_power_enabled")
        self.tb.subscribe_to_topic("request_system_tests")
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("response_current_sensor_present")
        self.tb.subscribe_to_topic("response_current_sensor_value")
        self.tb.subscribe_to_topic("response_current_sensor_nominal")
        self.tb.subscribe_to_topic("request_sdc2160_present")
        self.tb.subscribe_to_topic("request_sdc2160_faults")
        self.tb.subscribe_to_topic("request_amt203_present")
        self.tb.subscribe_to_topic("request_amt203_zeroed")
        self.tb.subscribe_to_topic("request_amt203_absolute_position")
        self.tb.subscribe_to_topic("request_sdc2160_relative_position")
        self.tb.subscribe_to_topic("request_sdc2160_closed_loop_error")
        self.tb.subscribe_to_topic("request_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("request_sdc2160_controller_faults")
        self.tb.subscribe_to_topic("request_target_position_confirmed")
        #self.tb.subscribe_to_topic("request_visual_tests") # not yet implemented
        self.tb.subscribe_to_topic("cmd_rotate_fruit_to_target")

        self.start()

        time.sleep(1) # just being superstitious

        # check system state
        """
        visual tests are, for x minutes:
           all chimes in order
           all digits in order
           all carousel lights in order
           all playfield lights in order
           all button lights in order
           all carousel solenoids in order, one at a time
           all triggerable playfield solenoids in order
                including trough and short solenoid taps in tubes
        """

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

    def sync_relative_encoders_to_absolute_encoders(self):
        return 
        # temporarily disconnected for safety
        carousel_names =  ("carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6")
        if self.high_power_init: # if power is on
            # add try/catch blocks and/or general system to track if hi power is on
            abs_positions = self.absolute_encoders.get_positions()
            for abs_ordinal_position in enumerate(abs_positions):
                abs_ordinal, abs_position = abs_ordinal_position
                self.controllers.motors[carousel_names[abs_ordinal]].set_operating_mode(0)
                time.sleep(0.5)
                self.controllers.motors[carousel_names[abs_ordinal]].set_encoder_counter(abs_position)
                time.sleep(0.5)
                self.controllers.motors[carousel_names[abs_ordinal]].set_operating_mode(3)





    def request_system_runtime_states(self):
        if self.high_power_init:
            """
            controller_fault_states = self.request_sdc2160_controller_faults()
            collected_faults = [{},{},{}]
            fault_detected = False
            for controller_fault_state in enumerate(controller_fault_states):
                controller_ordinal, faults_d = controller_fault_state
                for fault_type in faults_d:
                    if faults_d[fault_type] > 0:
                        fault_detected = True
                        collected_faults[controller_ordinal][fault_type] = faults_d[fault_type]
            if fault_detected:
                self.tb.publish(
                    topic="response_sdc2160_controller_faults", 
                    message=collected_faults
                )

            all_sdc2160_channel_faults = {}
            for carousel_name in ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]:
                sdc2160_channel_faults = self.request_sdc2160_channel_faults(carousel_name)
                collected_faults = {}
                if sdc2160_channel_faults["temperature"] > 40:
                    collected_faults["temperature"] = sdc2160_channel_faults["temperature"]
                if abs(sdc2160_channel_faults["closed_loop_error"]) > 20:
                    collected_faults["closed_loop_error"] = sdc2160_channel_faults["closed_loop_error"]
                if sdc2160_channel_faults["stall_detection"] > 0:
                    collected_faults["stall_detection"] = sdc2160_channel_faults["stall_detection"]
                if abs(sdc2160_channel_faults["motor_amps"]) > 0:
                    collected_faults["motor_amps"] = sdc2160_channel_faults["motor_amps"]
                if sdc2160_channel_faults["runtime_status_flags"]["amps_limit_activated"] > 0:
                    collected_faults["amps_limit_activated"] = sdc2160_channel_faults["runtime_status_flags"]["amps_limit_activated"]
                if sdc2160_channel_faults["runtime_status_flags"]["motor_stalled"] > 0:
                    collected_faults["motor_stalled"] = sdc2160_channel_faults["runtime_status_flags"]["motor_stalled"]
                if sdc2160_channel_faults["runtime_status_flags"]["loop_error_detected"] > 0:
                    collected_faults["loop_error_detected"] = sdc2160_channel_faults["runtime_status_flags"]["loop_error_detected"]
                if sdc2160_channel_faults["runtime_status_flags"]["safety_stop_active"] > 0:
                    collected_faults["safety_stop_active"] = sdc2160_channel_faults["runtime_status_flags"]["safety_stop_active"]
                if sdc2160_channel_faults["runtime_status_flags"]["forward_limit_triggered"] > 0:
                    collected_faults["forward_limit_triggered"] = sdc2160_channel_faults["runtime_status_flags"]["forward_limit_triggered"]
                if sdc2160_channel_faults["runtime_status_flags"]["reverse_limit_triggered"] > 0:
                    collected_faults["reverse_limit_triggered"] = sdc2160_channel_faults["runtime_status_flags"]["reverse_limit_triggered"]
                if sdc2160_channel_faults["runtime_status_flags"]["amps_trigger_activated"] > 0:
                    collected_faults["amps_trigger_activated"] = sdc2160_channel_faults["runtime_status_flags"]["amps_trigger_activated"]
                #if len(collected_faults.keys()) > 0:
                all_sdc2160_channel_faults[carousel_name] = collected_faults
            if len(all_sdc2160_channel_faults.keys()) > 0:
                self.tb.publish(
                    topic="response_sdc2160_channel_faults", 
                    message=all_sdc2160_channel_faults
                )
            """
            self.tb.publish(
                topic="response_sdc2160_relative_position", 
                message=self.request_sdc2160_relative_position()
            )
            self.tb.publish(
                topic="response_sdc2160_closed_loop_error", 
                message=self.request_sdc2160_closed_loop_error()
            )


    def request_system_faults(self):
        current_sensor_value = self.request_current_sensor_value()
        if current_sensor_value > 0 :
            self.tb.publish(
                topic="response_current_sensor_value", 
                message=current_sensor_value
            )

        computer_details = self.request_computer_details()
        collected_computer_details = {}
        if computer_details["df"][1] <500000:
            collected_computer_details["df"] = computer_details["df"]

        if computer_details["cpu_temp"] > 70:
            collected_computer_details["cpu_temp"] = computer_details["cpu_temp"]

        if len(collected_computer_details.keys()) > 0:
            self.tb.publish(
                topic="response_computer_details", 
                message=collected_computer_details
            )
        if self.high_power_init:

            amt203_present = self.request_amt203_present()
            if not all(amt203_present):
                self.tb.publish(
                    topic="response_amt203_present", 
                    message=amt203_present
                )

            sdc2160_present = self.request_sdc2160_present()
            if not all(sdc2160_present):
                self.tb.publish(
                    topic="response_sdc2160_present", 
                    message=sdc2160_present
                )

            controller_fault_states = self.request_sdc2160_controller_faults()
            collected_faults = [{},{},{}]
            fault_detected = False
            for controller_fault_state in enumerate(controller_fault_states):
                controller_ordinal, faults_d = controller_fault_state
                for fault_type in faults_d:
                    if faults_d[fault_type] > 0:
                        fault_detected = True
                        collected_faults[controller_ordinal][fault_type] = faults_d[fault_type]
            if fault_detected:
                self.tb.publish(
                    topic="response_sdc2160_controller_faults", 
                    message=collected_faults
                )

            all_sdc2160_channel_faults = {}
            for carousel_name in ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]:
                sdc2160_channel_faults = self.request_sdc2160_channel_faults(carousel_name)
                collected_faults = {}
                if sdc2160_channel_faults["temperature"] > 40:
                    collected_faults["temperature"] = sdc2160_channel_faults["temperature"]
                if abs(sdc2160_channel_faults["closed_loop_error"]) > 20:
                    collected_faults["closed_loop_error"] = sdc2160_channel_faults["closed_loop_error"]
                if sdc2160_channel_faults["stall_detection"] > 0:
                    collected_faults["stall_detection"] = sdc2160_channel_faults["stall_detection"]
                if abs(sdc2160_channel_faults["motor_amps"]) > 0:
                    collected_faults["motor_amps"] = sdc2160_channel_faults["motor_amps"]
                if sdc2160_channel_faults["runtime_status_flags"]["amps_limit_activated"] > 0:
                    collected_faults["amps_limit_activated"] = sdc2160_channel_faults["runtime_status_flags"]["amps_limit_activated"]
                if sdc2160_channel_faults["runtime_status_flags"]["motor_stalled"] > 0:
                    collected_faults["motor_stalled"] = sdc2160_channel_faults["runtime_status_flags"]["motor_stalled"]
                if sdc2160_channel_faults["runtime_status_flags"]["loop_error_detected"] > 0:
                    collected_faults["loop_error_detected"] = sdc2160_channel_faults["runtime_status_flags"]["loop_error_detected"]
                if sdc2160_channel_faults["runtime_status_flags"]["safety_stop_active"] > 0:
                    collected_faults["safety_stop_active"] = sdc2160_channel_faults["runtime_status_flags"]["safety_stop_active"]
                if sdc2160_channel_faults["runtime_status_flags"]["forward_limit_triggered"] > 0:
                    collected_faults["forward_limit_triggered"] = sdc2160_channel_faults["runtime_status_flags"]["forward_limit_triggered"]
                if sdc2160_channel_faults["runtime_status_flags"]["reverse_limit_triggered"] > 0:
                    collected_faults["reverse_limit_triggered"] = sdc2160_channel_faults["runtime_status_flags"]["reverse_limit_triggered"]
                if sdc2160_channel_faults["runtime_status_flags"]["amps_trigger_activated"] > 0:
                    collected_faults["amps_trigger_activated"] = sdc2160_channel_faults["runtime_status_flags"]["amps_trigger_activated"]
                #if len(collected_faults.keys()) > 0:
                all_sdc2160_channel_faults[carousel_name] = collected_faults
            if len(all_sdc2160_channel_faults.keys()) > 0:
                self.tb.publish(
                    topic="response_sdc2160_channel_faults", 
                    message=all_sdc2160_channel_faults
                )

            self.tb.publish(
                topic="response_sdc2160_relative_position", 
                message=self.request_sdc2160_relative_position()
            )
            self.tb.publish(
                topic="response_amt203_absolute_position", 
                message=self.request_amt203_absolute_position()
            )

    def request_system_tests(self):
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

    def request_sdc2160_controller_faults(self):
        return [
            self.controllers.boards["carousel1and2"].get_runtime_fault_flags(True),
            self.controllers.boards["carousel3and4"].get_runtime_fault_flags(True),
            self.controllers.boards["carousel5and6"].get_runtime_fault_flags(True),
        ]

    def request_computer_details(self):
        return {
            "df":self.tb.get_system_disk(),
            "cpu_temp":self.tb.get_core_temp(),
            "pinball_git_timestamp":self.tb.app_get_git_timestamp(),
            "tb_git_timestamp":self.tb.tb_get_git_timestamp(),
        }
        
    def request_current_sensor_nominal(self):
        #TODO: Do the ACTUAL tests here.
        return True
        
    def request_current_sensor_present(self):
        #TODO: Do the ACTUAL tests here.
        return True
        
    def request_current_sensor_value(self):
        #TODO: Do the ACTUAL tests here.
        return 0.0
    def request_sdc2160_present(self):
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
        #role_module.main.controller.boards["carousel1and2"].get_mcu_id()
        #


    def request_sdc2160_faults(self):
        pass

    def request_amt203_present(self):
        return self.absolute_encoders.get_presences()

    def request_amt203_zeroed(self):
        return self.absolute_encoders_zeroed

    def request_amt203_absolute_position(self, fruit_id=-1):
        if fruit_id == -1 or fruit_id == None:
            return self.absolute_encoders.get_positions()
        else:
            return self.absolute_encoders.get_position(self.chip_select_pins_for_abs_enc[fruit_id])

    def request_sdc2160_relative_position(self, fruit_id=-1):
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


    def request_sdc2160_closed_loop_error(self, fruit_id=-1):
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

    def request_sdc2160_channel_faults(self, motor_name):
        return {
            "temperature":self.controllers.motors[motor_name].get_temperature(True),
            "runtime_status_flags":self.controllers.motors[motor_name].get_runtime_status_flags(True),
            "closed_loop_error":self.controllers.motors[motor_name].get_closed_loop_error(True),
            "stall_detection":False,   #self.controllers.motors[motor_name].get_stall_detection(True),
            "motor_amps":self.controllers.motors[motor_name].get_motor_amps(True),
        }

    def request_target_position_confirmed(self):
        pass

    def cmd_rotate_fruit_to_target(self, carousel_name, fruit_id, target_name):
        # calculate target position
        target_position = settings.Carousel_Fruit_Offsets[fruit_id] + settings.Carousel_Target_Positions[target_name]
        current_position = self.controllers.motors[carousel_name].get_encoder_counter_absolute(True)
        current_position = current_position % 4096
        self.controllers.motors[carousel_name].go_to_absolute_position(current_position)


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
                topic, message, origin, destination = self.queue.get(True,5)
                print(topic, message)

                if topic == b'cmd_rotate_fruit_to_target':
                    carousel_name, fruit_id, target_name = message
                    self.cmd_rotate_fruit_to_target(carousel_name, fruit_id, target_name)
                if topic == b'connected':
                    pass
                if topic == b'request_amt203_absolute_position':
                    fruit_id = message
                    self.tb.publish(
                        topic="response_amt203_absolute_position", 
                        message=self.request_amt203_absolute_position(fruit_id)
                    )
                if topic == b'request_amt203_present':
                    self.tb.publish(
                        topic="response_amt203_present", 
                        message=self.request_amt203_present()
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
                if topic == b'request_sdc2160_channel_faults':
                    pass
                if topic == b'request_sdc2160_closed_loop_error':
                    pass
                if topic == b'request_sdc2160_controller_faults':
                    pass             
                if topic == b'request_sdc2160_faults':
                    pass                  
                if topic == b'request_sdc2160_present':
                    self.tb.publish(
                        topic="response_sdc2160_present", 
                        message=self.request_sdc2160_present()
                    )    
                if topic == b'request_sdc2160_relative_position':
                    pass
                if topic == b'request_target_position_confirmed':
                    pass

                if topic == b'response_high_power_enabled':
                    print("---------")
                    time.sleep(2)
                    print("---------")
                    if message: #transition for high power
                    print("---------")
                        if not self.high_power_init:# if this is the first transition to high power
                            print("---------")
                            self.create_controllers_and_motors()
                            self.absolute_encoders = AMT203(speed_hz=5000,gpios_for_chip_select=self.chip_select_pins_for_abs_enc)
                            self.high_power_init = True
                            #self.sync_relative_encoders_to_absolute_encoders()
                            time.sleep(5)

                            #self.cmd_rotate_fruit_to_target("carousel_1", 0, "front")
                            #self.cmd_rotate_fruit_to_target("carousel_2", 1, "front")
                            #self.cmd_rotate_fruit_to_target("carousel_3", 2, "front")
                            #self.cmd_rotate_fruit_to_target("carousel_4", 3, "front")
                            #self.cmd_rotate_fruit_to_target("carousel_5", 4, "front")
                            #self.cmd_rotate_fruit_to_target("carousel_6", 5, "front")


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

                if topic == b'request_system_tests':
                    self.request_system_tests()

            except queue.Empty as e:
                #self.request_system_faults()
                self.request_system_runtime_states()

            #except Exception as e:
            #    exc_type, exc_value, exc_traceback = sys.exc_info()
            #    print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()
"""
class Status_Report_Impeller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
    def run(self):
        time.sleep(30) # this is brittle. Fix this later with try/catch blocks
        while
        main.add_to_queue("request_amt203_absolute_position","","controller","pinballmatrix")
        time.sleep(1)
"""