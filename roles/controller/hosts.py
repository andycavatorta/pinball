"""
host module functions:
    cache the varied state data of hosts, providing continuity when mode changes
    provide method names for publishing to thirtybirds topics
    provide state data to http_server
    
data flow:
    controller writes state data here
    current mode reads and requests state data here
    http_server reads and requests state data here

verbs:
    request - send request to host for data
    set - store response to request, called by controller.main()
    get - return locally stored data
    cmd - send command that returns nothing

to do:
    ensure thread safety
        what happens when controller writes to self.foo while mode and http_server read self.foo?
        safety could come from the fact that these are only used main.run and never simultaneously
    add vars and methods to store system tests

"""

import codecs
import os
import queue
import sys
import threading
import time

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.sensors.ina260 import ina260 


class Host():
    def __init__(self, hostname):
        self.hostname = hostname
        self.connected = False
        self.ready = False
        self.last_deadman = 0 #unix timestamp
        self.queue = queue.Queue
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
        self.response_current_sensor_present = -1
        self.response_current_sensor_value = -1
        self.response_current_sensor_nominal = -1
    def set_connected(self, connected):
        self.connected = connected
    def get_connected(self):
        return self.connected
    def set_ready(self, ready):
        self.ready = ready
    def get_ready(self, ready):
        return self.ready
    def set_last_deadman(self, last_deadman):
        self.last_deadman = last_deadman
    def get_last_deadman(self, last_deadman):
        return self.last_deadman

    def set_computer_details(self,computer_details):
        self.df = computer_details["df"]
        self.cpu_temp = computer_details["cpu_temp"]
        self.pinball_git_timestamp = computer_details["pinball_git_timestamp"]
        self.tb_git_timestamp = computer_details["tb_git_timestamp"]
    def get_computer_details(self):
        return {
            "df":self.df,
            "cpu_temp":self.cpu_temp,
            "pinball_git_timestamp":self.pinball_git_timestamp,
            "tb_git_timestamp":self.tb_git_timestamp,
        }
    def get_computer_details_received(self):
        if self.df == -1:
            return False
        if self.cpu_temp == -1:
            return False
        if self.pinball_git_timestamp == "":
            return False
        if self.tb_git_timestamp == "":
            return False
        return True
    def get_df(self):
        return self.df
    def get_cpu_temp(self):
        return self.cpu_temp
    def get_pinball_git_timestamp(self):
        return self.pinball_git_timestamp
    def get_tb_git_timestamp(self):
        return self.tb_git_timestamp
    def set_current_sensor_present(self,response_current_sensor_present):
        self.response_current_sensor_present = response_current_sensor_present
    def set_current_sensor_value(self,response_current_sensor_value):
        self.response_current_sensor_value = response_current_sensor_value
    def set_current_sensor_nominal(self,response_current_sensor_nominal):
        self.response_current_sensor_nominal = response_current_sensor_nominal
    def get_current_sensor_present(self):
        return self.response_current_sensor_present
    def get_current_sensor_value(self):
        return self.response_current_sensor_value
    def get_current_sensor_nominal(self):
        return self.response_current_sensor_nominal

class Controller(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.safety_enable = False
        self.tb = tb
    def get_safety_enable(self):
        return self.safety_enable
    def set_safety_enable(self,safety_enable):
        self.safety_enable = safety_enable
    def get_computer_details(self):
        return {
            "df":self.tb.get_system_disk(),
            "cpu_temp":self.tb.get_core_temp(),
            "pinball_git_timestamp":self.tb.app_get_git_timestamp(),
            "tb_git_timestamp":self.tb.tb_get_git_timestamp(),
        }

class Carousel(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.carousel_error = {}
        self.solenoids_present = [
            False,
            False,
            False,
            False,
            False
        ]
        self.balls_present = [
            False,
            False,
            False,
            False,
            False
        ]
    def request_solenoids_present(self):
        self.tb.publish(topic="request_solenoids_present",message=True,destination=self.hostname)
    def set_solenoids_present(self, solenoids_present):
        self.solenoids_present = solenoids_present
    def get_solenoids_present(self):
        return self.solenoids_present
    def set_carousel_ball_detected(self, balls_present):
        self.balls_present = balls_present
    def get_carousel_ball_detected(self):
        return self.balls_present
    def request_eject_ball(self, fruit_name):
        self.tb.publish(topic="cmd_carousel_eject_ball",message=fruit_name,destination=self.hostname)
    def request_system_tests(self):
        self.tb.publish(topic="request_system_tests",message=True,destination=self.hostname)
    def cmd_carousel_lights(self, group, animation):
        self.tb.publish(
            topic="cmd_carousel_lights", 
            message=[group, animation],
            destination=self.hostname
        )
    def cmd_carousel_all_off(self):
        self.tb.publish(
            topic="cmd_carousel_all_off", 
            message=True,
            destination=self.hostname
        )
    def set_carousel_error(self,carousel_error):
        self.carousel_error = carousel_error

    def get_carousel_error(self,carousel_error):
        return self.carousel_error

class Matrix(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb        
        self.sdc2160_present = {
            "carousel1and2":False,
            "carousel3and4":False,
            "carousel5and6":False,        
        }
        self.carousel_names = [
            "carousel1",
            "carousel2",
            "carousel3",
            "carousel4",
            "carousel5",
            "carouselcenter",
        ]
        self.sdc2160_controller_faults = [
            None,None,None,
        ]
        self.sdc2160_channel_faults = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.amt203_present = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.amt203_zeroed = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.amt203_absolute_position = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.sdc2160_relative_position = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.sdc2160_closed_loop_error = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.motors = [
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0,
                "target_reached":[False,0],
                "stalled":[False,0],
                "timeout":[False,0],
            },
        ]
        self.motor_by_carousel_name = {
            "carousel_1":self.motors[0],
            "carousel_2":self.motors[0],
            "carousel_3":self.motors[0],
            "carousel_4":self.motors[0],
            "carousel_5":self.motors[0],
            "carousel_center":self.motors[0],
        }
        self.target_position = [
            0,0,0,0,0,0
        ]
        self.target_position_confirmed = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.named_positions = {
            "center_front":0,
            "center_back":0,
            "trueque_tube":0,
            "dinero_tube":0,
            "exchange_left_prep":0,
            "exchange_right_prep":0,
        }
        self.fruit_positions = [0,0,0,0,0,0]

    def cmd_rotate_carousel_to_target(self, carousel_name, fruit_name, position_name):
        self.tb.publish(topic="cmd_rotate_carousel_to_target", message=[carousel_name, fruit_name, position_name])
    def get_amt203_absolute_position(self, fruit_id):
        return self.amt203_absolute_position[fruit_id]
    def get_amt203_absolute_position_populated(self):
        if None in self.amt203_absolute_position:
            return False
        return True
    def get_amt203_present(self):
        return all(self.amt203_present)
    def get_amt203_zeroed(self):
        return False not in self.amt203_zeroed

    def get_destination_reached(self, motor_name):
        motor = self.motor_by_carousel_name[motor_name]
        return motor["target_reached"]
    def get_destination_stalled(self, motor_name):
        motor = self.motor_by_carousel_name[motor_name]
        return motor["stalled"]
    def get_destination_timeout(self, motor_name):
        motor = self.motor_by_carousel_name[motor_name]
        return motor["timeout"]

    def get_motor_details(self, property, fruit_id):
        return self.motors[fruit_id][property]
    def get_sdc2160_channel_faults(self):
        return self.sdc2160_channel_faults
    def get_sdc2160_closed_loop_error(self):
        return self.sdc2160_closed_loop_error
    def get_sdc2160_controller_faults(self):
        return self.sdc2160_controller_faults
    def get_sdc2160_faults(self):
        return self.sdc2160_faults
    def get_sdc2160_present(self):
        return all(self.sdc2160_present.values())
    def get_sdc2160_relative_position(self, fruit_id=-1):
        if fruit_id == -1:
            return self.sdc2160_relative_position
        else:
            return self.sdc2160_relative_position[fruit_id]
    def get_target_position_confirmed(self):
        return self.target_position_confirmed
    def request_amt203_absolute_position(self, fruit_id):
        self.tb.publish(topic="request_amt203_absolute_position", message="")
    def request_amt203_present(self):
        self.tb.publish(topic="request_amt203_present", message="")
    def request_amt203_zeroed(self): # this is a command, not a query
        self.tb.publish(topic="request_amt203_zeroed", message="")
    def request_motor_details(self, property, fruit_id):
        self.tb.publish(topic="request_motor_details", message=[property, fruit_id])
    def request_sdc2160_channel_faults(self): 
        self.tb.publish(topic="request_sdc2160_channel_faults", message="")
    def request_sdc2160_closed_loop_error(self): 
        self.tb.publish(topic="request_sdc2160_closed_loop_error", message="")
    def request_sdc2160_controller_faults(self): 
        self.tb.publish(topic="request_sdc2160_controller_faults", message="")
    def request_sdc2160_faults(self):
        self.tb.publish(topic="request_sdc2160_faults", message="")
    def request_sdc2160_present(self):
        self.tb.publish(topic="request_sdc2160_present", message="")
    def request_sdc2160_relative_position(self, fruit_id):
        self.tb.publish(topic="request_sdc2160_relative_position", message="")
    def request_target_position_confirmed(self): 
        self.tb.publish(topic="request_target_position_confirmed", message="")
    def response_high_power_disabled(self): 
        self.tb.publish(topic="response_high_power_enabled", message=False)
    def response_high_power_enabled(self): 
        self.tb.publish(topic="response_high_power_enabled", message=True)
    def sdc2160_channel_faults_populated(self):
        if None in self.sdc2160_channel_faults:
            return False
        return True
    def sdc2160_closed_loop_error_populated(self):
        if None in self.sdc2160_closed_loop_error:
            return False
        return True
    def sdc2160_controller_faults_populated(self):
        if None in self.sdc2160_controller_faults:
            return False
        return True
    def sdc2160_relative_position_populated(self):
        if None in self.sdc2160_relative_position:
            return False
        return True
    def set_amt203_absolute_position(self, absolute_position, fruit_id=-1):
        if fruit_id == -1 or fruit_id == None:
            self.amt203_absolute_position = absolute_position
        else:
            self.amt203_absolute_position[fruit_id] = absolute_position
    def set_amt203_present(self,amt203_present):
        self.amt203_present = amt203_present
    def set_amt203_zeroed(self,amt203_zeroed):
        self.amt203_zeroed = amt203_zeroed
    def set_destination_reached(self, motor_name, reached, position, position_error):
        motor = self.motor_by_carousel_name[motor_name]
        motor["target"] = position + position_error
        motor["discrepancy"] = position_error
        motor["target_reached"] = [reached, time.time()]
    def set_destination_stalled(self, motor_name, stalled, position, position_error):
        motor = self.motor_by_carousel_name[motor_name]
        motor["target"] = position + position_error
        motor["discrepancy"] = position_error
        motor["stalled"] = [stalled, time.time()]
    def set_destination_timeout(self, motor_name, timeout, position, position_error):
        motor = self.motor_by_carousel_name[motor_name]
        motor["target"] = position + position_error
        motor["discrepancy"] = position_error
        motor["timeout"] = [timeout, time.time()]
    def set_motor_details(self, property, fruit_id, value):
        self.motors[fruit_id][property] = value
    def set_sdc2160_channel_faults(self,sdc2160_channel_faults):
        self.sdc2160_channel_faults = sdc2160_channel_faults
    def set_sdc2160_closed_loop_error(self,sdc2160_closed_loop_error):
        self.sdc2160_closed_loop_error = sdc2160_closed_loop_error
    def set_sdc2160_controller_faults(self,sdc2160_controller_faults):
        self.sdc2160_controller_faults = sdc2160_controller_faults
    def set_sdc2160_faults(self,sdc2160_present):
        self.sdc2160_faults = sdc2160_faults
    def set_sdc2160_present(self,presence):
        self.sdc2160_present = presence
    def set_sdc2160_relative_position(self, relative_position, fruit_id = -1):
        print("set_sdc2160_relative_position",relative_position, fruit_id)
        if fruit_id == -1:
            self.sdc2160_relative_position = relative_position
        else:
            self.sdc2160_relative_position[fruit_id] = relative_position
    def set_target_position_confirmed(self,fruit_id,state_bool):
        self.target_position_confirmed[fruit_id] = state_bool

class Pinball(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self._48v_current = -1
        self.barter_points = -1
        self.current_sensor_present= False
        self.gameplay_enabled = False
        self.gutter_ball_detected = False
        self.left_stack_inventory = -1
        self.money_points = -1
        self.right_stack_inventory = -1
        self.roll_inner_left = False
        self.roll_inner_right = False
        self.roll_outer_left = False
        self.roll_outer_right = False
        self.tb = tb
        self.troughsensor_value = False
        self.playfield_switch_active = {
            "trough_sensor":False,
            "roll_outer_left":False,
            "roll_inner_left":False,
            "roll_outer_right":False,
            "roll_inner_right":False,
        }
        self.button_light_active = {
            "izquierda":False,
            "trueque":False,
            "comienza":False,
            "dinero":False,
            "derecha":False,
        }
        self.button_switch_active = {
            "izquierda":False,
            "trueque":False,
            "comienza":False,
            "dinero":False,
            "derecha":False,
        }
        #is this list useful here?
        self.playfield_animations = {
            "trail_rollover_right":None,
            "trail_rollover_left":None,
            "trail_sling_right":None,
            "trail_sling_left":None,
            "trail_pop_left":None,
            "trail_pop_right":None,
            "trail_pop_center":None,
            "trail_spinner":None,
            "pie_rollover_right":None,
            "pie_rollover_left":None,
            "pie_sling_right":None,
            "pie_sling_left":None,
            "pie_pop_left":None,
            "pie_pop_right":None,
            "pie_pop_center":None,
            "pie_spinner":None,
            "sign_arrow_left":None,
            "sign_bottom_right":None,
            "sign_top":None,
        }

    def enable_gameplay(self):
        self.gameplay_enabled = True
        self.tb.publish(topic="enable_gameplay", message="",destination=self.hostname)

    def disable_gameplay(self):
        self.gameplay_enabled = False
        self.tb.publish(topic="disable_gameplay", message="",destination=self.hostname)

    ### LEFT TUBE ###
    def request_lefttube_present(self):
        self.tb.publish(topic="request_lefttube_present", message="",destination=self.hostname)
    def set_lefttube_present(self,lefttube_present):
        self.lefttube_present = lefttube_present
    def get_lefttube_present(self):
        return self.lefttube_present
    def set_lefttube_value(self,lefttube_value):
        self.lefttube_value = lefttube_value
    def get_lefttube_value(self):
        return self.lefttube_value
    def cmd_lefttube_launch(self):
        self.tb.publish(
            topic="cmd_lefttube_launch", 
            message=True,
            destination=self.hostname
        )
    def set_left_stack_inventory(self,left_stack_inventory):
        self.left_stack_inventory = left_stack_inventory
    def get_left_stack_inventory(self):
        return self.left_stack_inventory
    def set_barter_points(self,barter_points):
        self.barter_points = barter_points
    def get_barter_points(self):
        return self.barter_points
    def request_money_points(self): 
        self.tb.publish(
            topic="request_money_points", 
            message="",
            destination=self.hostname
        )

    ### RIGHT TUBE ###
    def request_righttube_present(self):
        self.tb.publish(topic="request_righttube_present", message="",destination=self.hostname)
    def set_righttube_present(self,righttube_present):
        self.righttube_present = righttube_present
    def get_righttube_present(self):
        return self.righttube_present
    def set_righttube_value(self,righttube_value):
        self.righttube_value = righttube_value
    def get_righttube_value(self):
        return self.righttube_value
    def cmd_righttube_launch(self):
        self.tb.publish(
            topic="cmd_righttube_launch", 
            message=True,
            destination=self.hostname
        )
    def set_right_stack_inventory(self,right_stack_inventory):
        self.right_stack_inventory = right_stack_inventory
    def get_right_stack_inventory(self):
        return self.right_stack_inventory
    def set_money_points(self,money_points):
        self.money_points = money_points

    def request_troughsensor_value(self):
        self.tb.publish(topic="request_troughsensor_value", message="",destination=self.hostname)
    def set_troughsensor_value(self,troughsensor_value):
        self.troughsensor_value = troughsensor_value
    def get_troughsensor_value(self):
        return self.troughsensor_value
    def cmd_kicker_launch(self):
        self.tb.publish(
            topic="cmd_kicker_launch", 
            message=True,
            destination=self.hostname
        )
    def set_roll_outer_left(self,roll_outer_left):
        self.roll_outer_left = roll_outer_left

    def set_roll_outer_right(self,roll_outer_right):
        self.roll_outer_right = roll_outer_right

    def set_roll_inner_right(self,roll_inner_right):
        self.roll_inner_right = roll_inner_right

    def set_roll_inner_left(self,roll_inner_left):
        self.roll_inner_left = roll_inner_left

    def request_button_switch_active(self, button_name, state_bool): 
        self.tb.publish(
            topic="request_button_switch_active", 
            message=[button_name, state_bool],
            destination=self.hostname
        )
    def set_button_switch_active(self,button_name, state_bool):
        self.button_switch_active[button_name] = state_bool
    def get_button_switch_active(self):
        return self.button_switch_active[button_name]

    def request_button_light_active(self, button_name, state_bool): 
        self.tb.publish(
            topic="request_button_light_active", 
            message=[button_name, state_bool],
            destination=self.hostname
        )
    def set_button_light_active(self,button_name, state_bool):
        self.button_light_active[button_name] = state_bool
    def get_button_light_active(self):
        return self.button_light_active[button_name]

    def cmd_gamestation_all_off(self, state_bool):
        self.tb.publish(
            topic="cmd_all_off", 
            message=state_bool,
            destination=self.hostname
        )
    def cmd_playfield_lights(self, group, animation):
        self.tb.publish(
            topic="cmd_playfield_lights", 
            message=[group, animation],
            destination=self.hostname
        )

class Display(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.phrases = ("juega","dinero","trueque","como","fue")
        self.current_number = -1
        self.current_phrase_key = ""
        self.shift_registers_connected = False
        self.current_score_name = ""
        self.solenoids_present = [
            False,
            False,
            False,
            False,
            False,
        ]
        self.leds_present = {
            "A":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "B":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "C":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "words":[
                False,
                False,
                False,
                False,
                False,
            ]
        }
    def request_score(self, score_name):
        self.current_score_name = score_name
        self.tb.publish(topic="cmd_play_score",message=score_name,destination=self.hostname)
        
    def request_phrase(self, phrase_key):
        self.current_phrase_key = phrase_key
        self.tb.publish(topic="cmd_set_phrase",message=phrase_key,destination=self.hostname)
    def set_phrase(self,phrase_key): # in case phrase is set through method othe than self.request_phrase
        self.current_phrase_key = phrase_key
    def get_phrase(self):
        return self.current_phrase_key

    def request_number(self, number):
        self.current_number = number
        self.tb.publish(topic="cmd_set_number",message=number,destination=self.hostname)
    def set_number(self, number):
        self.current_number = number
    def get_number(self):
        return self.current_number

    def request_leds_present(self):
        self.tb.publish(topic="request_display_leds_present", message="",destination="pinball1display")
    def set_leds_present(self,leds_present):
        self.leds_present = leds_present
    def get_leds_present(self):
        return self.leds_present

    def request_solenoids_present(self):
        self.tb.publish(topic="request_display_solenoids_present", message="",destination="pinball1display")
    def set_solenoids_present(self,solenoids_present):
        self.solenoids_present = solenoids_present
    def get_solenoids_present(self):
        return self.solenoids_present

    def cmd_all_off(self):
        self.tb.publish(topic="cmd_all_off",message="")

class Hosts():
    def __init__(self, tb ):
        self.tb = tb
        self.controller = Controller("controller", tb)
        self.carousel1 = Carousel("carousel1", tb)
        self.carousel2 = Carousel("carousel2", tb)
        self.carousel3 = Carousel("carousel3", tb)
        self.carousel4 = Carousel("carousel4", tb)
        self.carousel5 = Carousel("carousel5", tb)
        self.carouselcenter = Carousel("carouselcenter", tb)
        self.pinball1display = Display("pinball1display", tb)
        self.pinball2display = Display("pinball2display", tb)
        self.pinball3display = Display("pinball3display", tb)
        self.pinball4display = Display("pinball4display", tb)
        self.pinball5display = Display("pinball5display", tb)
        self.pinball1game = Pinball("pinball1game", tb)
        self.pinball2game = Pinball("pinball2game", tb)
        self.pinball3game = Pinball("pinball3game", tb)
        self.pinball4game = Pinball("pinball4game", tb)
        self.pinball5game = Pinball("pinball5game", tb)
        self.pinballmatrix = Matrix("pinballmatrix", tb)
        self.hostnames = {
            'controller':self.controller,
            'carousel1':self.carousel1,
            'carousel2':self.carousel2,
            'carousel3':self.carousel3,
            'carousel4':self.carousel4,
            'carousel5':self.carousel5,
            'carouselcenter':self.carouselcenter,
            'pinball1display':self.pinball1display,
            'pinball2display':self.pinball2display,
            'pinball3display':self.pinball3display,
            'pinball4display':self.pinball4display,
            'pinball5display':self.pinball5display,
            'pinball1game':self.pinball1game,
            'pinball2game':self.pinball2game,
            'pinball3game':self.pinball3game,
            'pinball4game':self.pinball4game,
            'pinball5game':self.pinball5game,
            'pinballmatrix':self.pinballmatrix,
        }
        self.dispatch(b"response_computer_details", self.controller.get_computer_details(), "controller", "controller")

        self.mode_countdown_states = {
            "comienza_button_order":[]
        }

    def get_all_host_connected(self):
        for hostname in self.hostnames:
            if hostname != "controller":
                if self.hostnames[hostname].get_connected() == False:
                    return False
        return True

    def request_all_computer_details(self):
        self.tb.publish("request_computer_details",True)

    def get_all_computer_details_received(self):
        absent_list = []
        host_keys  = self.hostnames.keys()
        host_list  = list(host_keys)
        host_list.remove("controller")
        for name in host_list:
            if self.hostnames[name].get_computer_details_received() == False:
                absent_list.append(name)
        print("get_all_computer_details_received.absent_list",absent_list)
        return len(absent_list) == 0

    def get_all_current_sensor_present(self):
       return True
 
    def get_all_current_sensor_populated(self):
        return True

    def get_all_current_sensor_value(self):
        # to do : add controller
        names = ['pinball1display','pinball1game','pinball2game','pinball3game','pinball4game','pinball5game']
        for name in names:
            if self.hostnames[name].get_current_sensor_value() == False:
                return False
        return True

    def get_all_current_sensor_nominal(self):
        # to do : add controller
        names = ['pinball1display','pinball1game','pinball2game','pinball3game','pinball4game','pinball5game']
        for name in names:
            #print("get_all_current_sensor_nominal",name, self.hostnames[name].get_current_sensor_nominal())
            if self.hostnames[name].get_current_sensor_nominal() == False:
                return False
        return True

    def get_all_non_nominal_states(self):
        non_nominal_states = []
        closed_loop_error = self.pinballmatrix.get_sdc2160_closed_loop_error()
        closed_loop_error_list = []
        for channel_value in enumerate(closed_loop_error):
            channel, value = channel_value
            if value > 100:
                closed_loop_error_list.append([channel, value])
                non_nominal_states.append(["pinballmatrix","sdc2160_closed_loop_error",channel, value])
        # sdc: check channel faults
        channel_faults = self.pinballmatrix.get_sdc2160_channel_faults()
        channel_faults_list = []
        for channel_name in channel_faults:
            channel = channel_faults[channel_name]
            if channel["temperature"] > 40:
                channel_faults_list.append(["temperature",channel_name, channel["temperature"]])
                non_nominal_states.append(["pinballmatrix",channel_name,"temperature", channel["temperature"]])
            if channel["closed_loop_error"] > 100:
                channel_faults_list.append("closed_loop_error", channel_name,channel["closed_loop_error"])
                non_nominal_states.append(["pinballmatrix",channel_name,"closed_loop_error", channel["closed_loop_error"]])
            if channel["stall_detection"] != False:
                msg = ["stall_detection", channel_name,channel["stall_detection"]]
                channel_faults_list.append(msg)
                non_nominal_states.append(["pinballmatrix",channel_name,"stall_detection", channel["stall_detection"]])
            if channel["motor_amps"] > 6:
                channel_faults_list.append(["motor_amps",channel_name, channel["motor_amps"]])
                non_nominal_states.append(["pinballmatrix",channel_name,"motor_amps", channel["motor_amps"]])

            runtime_status_flags = channel["runtime_status_flags"]
            for flag_name in runtime_status_flags:
                if runtime_status_flags[flag_name] != 0:
                    channel_faults_list.append(flag_name, channel_name,runtime_status_flags[flag_name])
                    non_nominal_states.append(["pinballmatrix",channel_name,flag_name, runtime_status_flags[flag_name]])
        # sdc: check controller faults
        controller_errors_list = []
        controller_faults_list = self.pinballmatrix.get_sdc2160_controller_faults()
        controller_faults = {
            "carousel1and2":controller_faults_list[0],
            "carousel3and4":controller_faults_list[1],
            "carousel5and6":controller_faults_list[2],
        }
        for controller_name in controller_faults:
            controller = controller_faults[controller_name]
            for fault_name in controller:
                if controller[fault_name] != 0:
                    controller_errors_list.append([fault_name, controller_name,controller[fault_name]])
                    non_nominal_states.append(["pinballmatrix",controller_name,fault_name, controller[fault_name]])
        computer_details_errors = []
        for hostname in self.hostnames:
            deets = self.hostnames[hostname].get_computer_details()
            if deets["cpu_temp"] > 65:
                computer_details_errors.append([hostname,"cpu_temp", deets["cpu_temp"]])
                non_nominal_states.append([hostname,"computer_details","cpu_temp", deets["cpu_temp"]])
            if deets["df"][0] < 500000000:
                computer_details_errors.append([hostname,"df", deets["df"]])
                non_nominal_states.append([hostname,"computer_details","df", deets["df"]])
        # all: check current sensors
        return non_nominal_states

    def dispatch(self, topic, message, origin, destination):
        if isinstance(topic, bytes):
            topic = codecs.decode(topic, 'UTF-8')
        if isinstance(message, bytes):
            message = codecs.decode(message, 'UTF-8')
        if isinstance(origin, bytes):
            origin = codecs.decode(origin, 'UTF-8')
        if isinstance(destination, bytes):
            destination = codecs.decode(destination, 'UTF-8')
        ##### ROUTE MESSAGE TO METHOD #####
        if topic == "connected" or topic == "respond_host_connected":
            self.hostnames[origin].set_connected(message)
        #if topic == "event_button_comienza": # unclear what state data should be stored here
        #    self.hostnames[origin].event_button_comienza(message)
        #if topic == "event_button_derecha": # unclear what state data should be stored here
        #    self.hostnames[origin].event_button_derecha(message)
        #if topic == "event_button_dinero":
        #    self.hostnames[origin].event_button_dinero(message)
        #if topic == "event_button_izquierda": # unclear what state data should be stored here
        #    self.hostnames[origin].event_button_izquierda(message)
        #if topic == "event_button_trueque":
        #    self.hostnames[origin].event_button_trueque(message)
        if topic == "event_carousel_ball_detected":
            self.hostnames[origin].set_carousel_ball_detected(message)
        if topic == "event_carousel_error":
            self.hostnames[origin].set_carousel_error(message)
        if topic == "event_carousel_target_reached":
            self.hostnames[origin].set_target_position_confirmed(message)


        if topic == "event_destination_reached":
            motor_name, reached, position, position_error = message
            self.hostnames[origin].set_destination_reached(motor_name, reached, position, position_error)
        if topic == "event_destination_stalled":
            motor_name, stalled, position, position_error = message
            self.hostnames[origin].set_destination_stalled(motor_name, stalled, position, position_error)
        if topic == "event_destination_timeout":
            motor_name, timeout, position, position_error = message
            self.hostnames[origin].set_destination_timeout(motor_name, timeout, position, position_error)


        #if topic == "event_gamestation_button": # unclear what state data should be stored here
        #    self.hostnames[origin].event_gamestation_button(message)
        if topic == "event_left_stack_ball_present":
            self.hostnames[origin].set_lefttube_value(message)
        #if topic == "event_left_stack_motion_detected": # unclear what state data should be stored here
        #    self.hostnames[origin].set_left_stack_motion_detected(message)
        #if topic == "event_pop_left": # unclear what state data should be stored here
        #    self.hostnames[origin].set_pop_left(message)
        #if topic == "event_pop_middle": # unclear what state data should be stored here
        #    self.hostnames[origin].set_pop_center(message)
        #if topic == "event_pop_right": # unclear what state data should be stored here
        #    self.hostnames[origin].set_pop_right(message)
        if topic == "event_right_stack_ball_present":
            self.hostnames[origin].set_righttube_value(message)
        #if topic == "event_right_stack_motion_detected": # unclear what state data should be stored here
        #    self.hostnames[origin].set_right_stack_motion_detected(message)
        #if topic == "event_roll_inner_left":
        #    self.hostnames[origin].set_roll_inner_left(message)
        #if topic == "event_roll_inner_right":
        #    self.hostnames[origin].set_roll_inner_right(message)
        #if topic == "event_roll_outer_left":
        #    self.hostnames[origin].set_roll_outer_left(message)
        #if topic == "event_roll_outer_right":
        #    self.hostnames[origin].set_roll_outer_right(message
        #if topic == "event_slingshot_left":
        #    self.hostnames[origin].event_slingshot_left(message)
        #if topic == "event_slingshot_right":
        #    self.hostnames[origin].event_slingshot_right(message)
        #if topic == "event_spinner":
        #    self.hostnames[origin].set_spinner(message)
        if topic == "event_trough_sensor":
            self.hostnames[origin].set_troughsensor_value(message)
        if topic == "response_amt203_absolute_position":
            self.hostnames[origin].set_amt203_absolute_position(message)
        if topic == "response_amt203_present":
            self.hostnames[origin].set_amt203_present(message)
        if topic == "response_amt203_zeroed":
            self.hostnames[origin].set_amt203_zeroed(message)
        if topic == "response_carousel_absolute":
            self.hostnames[origin].set_amt203_absolute_position(message)
        if topic == "response_carousel_ball_detected":
            self.hostnames[origin].set_carousel_ball_detected(message)
        if topic == "response_carousel_relative":
            self.hostnames[origin].set_sdc2160_relative_position(message)
        if topic == "response_computer_details":
            self.hostnames[origin].set_computer_details(message)
        if topic == "response_current_sensor_nominal":
            self.hostnames[origin].set_current_sensor_nominal(message)
        if topic == "response_current_sensor_present":
            self.hostnames[origin].set_current_sensor_present(message)
        if topic == "response_current_sensor_value":
            self.hostnames[origin].set_current_sensor_value(message)
        if topic == "response_high_power_enabled":
            self.hostnames[origin].response_high_power_enabled(message)
        if topic == "response_sdc2160_channel_faults":
            self.hostnames[origin].set_sdc2160_channel_faults(message)
        if topic == "response_sdc2160_closed_loop_error":
            self.hostnames[origin].set_sdc2160_closed_loop_error(message)
        if topic == "response_sdc2160_controller_faults":
            self.hostnames[origin].set_sdc2160_controller_faults(message)
        if topic == "response_sdc2160_present":
            self.hostnames[origin].set_sdc2160_present(message)
        if topic == "response_sdc2160_relative_position":
            self.hostnames[origin].set_sdc2160_relative_position(message)
        #if topic == "response_visual_tests":
        #    self.hostnames[origin].set_visual_tests(message)

    ##### AGGREGATED STATES #####

