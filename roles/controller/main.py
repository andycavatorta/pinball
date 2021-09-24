"""
There are three types of host states
    connected [False|True]  part of thirtybirds
    deadman [alive|#error]  deadman switch that cuts higher power >5VDC    
    tests_complete [False|True] performed and passed local tests

    tests_complete and deadman seem redundant.  But deadman must be enabled in order to run some tests
"""
import datetime
import importlib
import json
import math
import os
import queue
import random
import RPi.GPIO as GPIO
import sys
import threading
import time
import traceback

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.sensors import ina260_current_sensor

import roles.controller.tests as tests

import roles.controller.Safety_Enable as Safety_Enable
import roles.controller.Hosts as Hosts

from http_server_root import dashboard

#import roles.pinball.Controller_Tests as Controller_Tests

from roles.controller.Mode_Waiting_For_Connections import Mode_Waiting_For_Connections
from roles.controller.Mode_System_Tests import Mode_System_Tests
from roles.controller.Mode_Error import Mode_Error

#from roles.controller.Mode_Inventory import Mode_Inventory
#import roles.pinball.Mode_Reset as Mode_Reset

##################################################
# LOGGING AND REPORTING #
##################################################

# EXCEPTION

# STATUS MESSAGES

# LOCAL LOGGING / ROTATION

##########
# STATES #
##########

class Game_Mode_Manager():
    """ 
    This may not be the right structure.
    thought: 
    one central system to collect state data from hosts, maybe in Main
    Main modifies host_states becasue the not all events are relevant to the each mode class.
        relevant events are passed to each mode class after Main updates host_states
    each mode class decides when it is time to move to the next class

    One class for each mode.
    each class is passed access to central host states and messages
    how are events routed to these classes?
        are events routed only to class for current mode?
        is there a method add_event_to_queue_for_current_mode?
    """
    def __init__(self):
        self.modes = settings.Game_Modes
        self.game_mode_order = settings.game_mode_order
        self.mode = self.modes.WAITING_FOR_CONNECTIONS #initial mode
        #self.transitional_mode = self.modes.Game_Modes.WAITING_FOR_CONNECTIONS # this is the intened next mode, pending testing
        self.inventory_complete = False
    def set_mode(self,mode_str):
        # test mode_str in values of self.modes
        self.mode = mode_str
        print("new mode:",self.mode)
    def get_mode(self):
        return self.mode
    def get_next_mode(self, mode_str):
        pass
    def transition_to_mode(self, mode_str):
        """ this is largely a set of tests to be initiate and results to be collected """
        self.transitional_mode = mode_str
        if self.transitional_mode == self.modes.SYSTEM_TESTS:
            pass
            # WAITING_FOR_CONNECTIONS when all computers are connected.  where is this data collected?
            # RESET when balls have all been moved back to starting position
        if self.transitional_mode == self.modes.INVENTORY:
            pass
            # SYSTEM_TESTS ends with all computers returning tests_complete as True.   where is this data collected?
        if self.transitional_mode == self.modes.ATTRACTION:
            pass
            # SYSTEM_TESTS ends with all computers returning tests_complete as True.   where is this data collected?
            # INVENTORY runs only once per boot.  It ends when some TBD mathematical inventory process is finished 
        if self.transitional_mode == self.modes.COUNTDOWN:
            pass
            # ATTRACTION ends when 1) one Juega button has been pushed
        if self.transitional_mode == self.modes.BARTER_MODE_INTRO:
            pass
            # COUNTDOWN ends when the countdown timer ends
        if self.transitional_mode == self.modes.BARTER_MODE:
            pass
            # BARTER_MODE_INTRO ends ?????  what is barter mode?
        if self.transitional_mode == self.modes.MONEY_MODE_INTRO:
            pass
            # BARTER_MODE ends when a timer finishes or a maximum of points is reached.
            # Get rid of numerical points entirely and just use balls?
        if self.transitional_mode == self.modes.MONEY_MODE:
            pass
            # MONEY_MODE_INTRO ends ???? what is money mode?
        if self.transitional_mode == self.modes.ENDING:
            pass
            # MONEY_MODE ends when a timer finishes or a maximum of points is reached.
            # Get rid of numerical points entirely and just use balls?
        if self.transitional_mode == self.modes.RESET:
            pass
            # ENDING ends when a timer finishes

############
# ROUTINES #
############

##################################################
# MAIN, TB, STATES, AND TOPICS #
##################################################

# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    """
    incoming messages are sorted and routed to the Hosts module, the dashboard, and the game mode manager
    """
    def __init__(self):
        threading.Thread.__init__(self)

        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        #self.carousel_current_sensor = ina260_current_sensor.INA260()
        self.safety_enable = Safety_Enable.Safety_Enable(self.safety_enable_handler)
        #self.game_mode_manager = Game_Mode_Manager()
        self.queue = queue.Queue()
        self.hosts = Hosts.Hosts(self.tb)

        self.game_modes = {
            "waiting_for_connections" : Mode_Waiting_For_Connections(self.tb,self.hosts,self.set_mode),
            "system_test" : Mode_System_Tests(self.tb,self.hosts,self.set_mode),
            "error" : Mode_Error(self.tb,self.hosts,self.set_mode),

            #"inventory" : Mode_Inventory(self.tb,self.hosts)
            #"attraction" : Mode_Attraction(self.tb,self.hosts)
            #"countdown" : Mode_Countdown(self.tb,self.hosts)
            #"barter_mode_intro" : Mode_Barter_Mode_Intro(self.tb,self.hosts)
            #"barter_mode" : Mode_Barter_Mode(self.tb,self.hosts)
            #"money_mode"_intro : Mode_Money_Mode_Intro(self.tb,self.hosts)
            #"money_mode" : Mode_Money_Mode(self.tb,self.hosts)
            #"ending" : Mode_Ending(self.tb,self.hosts)
            #"reset" : Mode_Reset(self.tb,self.hosts)
        }
        self.game_mode_names = settings.Game_Modes
        self.game_mode_name = self.game_mode_names.WAITING_FOR_CONNECTIONS


        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")

        self.tb.subscribe_to_topic("respond_computer_details")
        self.tb.subscribe_to_topic("respond_current_sensor_present")
        self.tb.subscribe_to_topic("respond_current_sensor_value")
        self.tb.subscribe_to_topic("respond_current_sensor_nominal")
        self.tb.subscribe_to_topic("respond_amt203_present")
        self.tb.subscribe_to_topic("respond_amt203_zeroed")
        self.tb.subscribe_to_topic("respond_amt203_absolute_position")
        self.tb.subscribe_to_topic("respond_sdc2160_present")
        self.tb.subscribe_to_topic("respond_sdc2160_relative_position")
        self.tb.subscribe_to_topic("respond_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("respond_sdc2160_controller_faults")
        self.tb.subscribe_to_topic("respond_sdc2160_closed_loop_error")
        self.tb.subscribe_to_topic("respond_visual_tests")
        #self.tb.subscribe_to_topic("respond_mpf_event")
        self.tb.subscribe_to_topic("request_current_sensor_nominal")

        self.tb.subscribe_to_topic("event_spinner")
        self.tb.subscribe_to_topic("event_pop_left")
        self.tb.subscribe_to_topic("event_pop_center")
        self.tb.subscribe_to_topic("event_pop_right")
        self.tb.subscribe_to_topic("event_sling_left")
        self.tb.subscribe_to_topic("event_sling_right")
        self.tb.subscribe_to_topic("event_roll_outer_left")
        self.tb.subscribe_to_topic("event_roll_inner_left")
        self.tb.subscribe_to_topic("event_roll_inner_right")
        self.tb.subscribe_to_topic("event_roll_outer_right")
        self.tb.subscribe_to_topic("event_trough_sensor")

        """
        # SYSTEM READINESS
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")
        self.tb.subscribe_to_topic("measured_amps") # might be subsumed by system_tests
        self.tb.subscribe_to_topic("system_tests")

        # BUTTONS
        self.tb.subscribe_to_topic("button_press_left_flipper")
        self.tb.subscribe_to_topic("button_press_trade_goods")
        self.tb.subscribe_to_topic("button_press_start")
        self.tb.subscribe_to_topic("button_press_trade_money")
        self.tb.subscribe_to_topic("button_press_right_flipper")

        # STACKS
        self.tb.subscribe_to_topic("left_stack_ball_present")
        self.tb.subscribe_to_topic("right_stack_ball_present")
        self.tb.subscribe_to_topic("left_stack_motion_detected")
        self.tb.subscribe_to_topic("right_stack_motion_detected")

        # GUTTER
        self.tb.subscribe_to_topic("gutter_ball_detected")

        # PLAYFIELD
        self.tb.subscribe_to_topic("spinner")
        self.tb.subscribe_to_topic("pop_left")
        self.tb.subscribe_to_topic("pop_center")
        self.tb.subscribe_to_topic("pop_right")
        self.tb.subscribe_to_topic("sling_left")
        self.tb.subscribe_to_topic("sling_right")
        self.tb.subscribe_to_topic("roll_outer_left")
        self.tb.subscribe_to_topic("roll_inner_left")
        self.tb.subscribe_to_topic("roll_inner_right")
        self.tb.subscribe_to_topic("roll_outer_right")

        # ENCODERS
        self.tb.subscribe_to_topic("absolute_position")
        self.tb.subscribe_to_topic("relative_position")

        # MOTORS
        self.tb.subscribe_to_topic("confirm_position")
        
        # INDUCTIVE SENSORS
        self.tb.subscribe_to_topic("carousel_ball_detected")
        """
        self.start()
        self.send_to_dashboard = dashboard.init(self.tb)
        self.set_mode(self.game_mode_names.WAITING_FOR_CONNECTIONS)
        
    """
    def process_computer_details(self, hostname, type, value)

    """

    def set_mode(self, mode_name):
        self.game_mode_name = mode_name
        self.game_mode = self.game_modes[mode_name]
        self.game_mode.reset()


    def convert_git_timestamp_to_epoch(self, git_timestamp):
        weekdayname_str, monthname_str, day_str, time_str, year_str, timezone_str =  git_timestamp.split(" ")
        hour_str, minute_str, second_str = time_str.split(":")
        month_int = datetime.datetime.strptime(monthname_str, "%b").month
        return datetime.datetime(int(year_str),month_int,int(day_str),int(hour_str),int(minute_str),int(second_str)).timestamp()

    def safety_enable_handler(self, state_bool):
        # when all computers are present
        # when power turns on or off
        # self.game_mode_manager.set_mode()
        # self.game_mode_manager.set_mode(modes.SYSTEM_TESTS)
        self.tb.publish("respond_high_power_enabled", state_bool)
        if state_bool:
            self.tb.publish("request_system_tests", True)

    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        self.add_to_queue("respond_host_connected",status,hostname, False)

        # update self.hosts[hostname].set_connected() 
        # self.add_to_queue(topic, message, origin, destination)
    def add_to_queue(self, topic, message, origin, destination):

        # if topic=system_tests, update self.hosts[hostname].set_connected() 
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                """
                much of this switchboard below can be moved into Hosts
                and Hosts will manage and call methods within each Mode class
                """
                topic, message, origin, destination = self.queue.get(True)
                #if topic!=b"deadman":
                #    print(topic, message, origin, destination)

                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)

                if topic!=b"deadman":
                    self.hosts.dispatch(topic, message, origin, destination)
                    self.send_to_dashboard(topic, message)
                    self.game_mode.add_to_queue(topic, message, origin, destination)


                ### temporarily parsing here for demo

                if topic==b"respond_mpf_event":
                    print("respond_mpf_event", message, origin)

                # ERROR

                # WAITING_FOR_CONNECTIONS
                #if self.game_mode_name == self.game_mode_names.WAITING_FOR_CONNECTIONS:
                #    if topic!=b"deadman":
                #            self.mode_waiting_for_connections.add_to_queue(topic, message, origin, destination)

                # SYSTEM_TESTS
                #if self.game_mode_name == self.game_mode_names.SYSTEM_TESTS:
                #    if topic!=b"deadman":
                #            self.mode_system_tests.add_to_queue(topic, message, origin, destination)

                # INVENTORY

                # RESET

                # ATTRACTION

                # COUNTDOWN

                # BARTER_MODE_INTRO

                # BARTER_MODE

                # MONEY_MODE_INTRO

                # MONEY_MODE

                # ENDING


                #if topic==b"connected": # is this useful when we have the network_status_change_handler?
                #    print("----------connected----------", topic, message, origin, destination)
                #if topic==b"respond_computer_details":
                #    cpu_temp = message["cpu_temp"]
                #    df = message["df"][0]
                #    pinball_git_timestamp = self.convert_git_timestamp_to_epoch(message["pinball_git_timestamp"])
                #    tb_git_timestamp = self.convert_git_timestamp_to_epoch(message["tb_git_timestamp"])

                    #send to game mode
                    #send to hosts object
                    #send to dashboard
                    """
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "rpi", # device
                            "temp",#data_name
                            cpu_temp
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "rpi", # device
                            "df",#data_name
                            round(df/1073741824,2)
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "rpi", # device
                            "pin git",#data_name
                            pinball_git_timestamp
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "rpi", # device
                            "tb git",#data_name
                            tb_git_timestamp
                        ]
                    )

                if topic==b"respond_current_sensor_value":
                    pass
                if topic==b"respond_current_sensor_nominal":
                    pass
                if topic==b"respond_current_sensor_present":
                    pass
                if topic==b"respond_amt203_present":
                    #send to game mode
                    #send to hosts object
                    #send to dashboard
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_1", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[0] else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_2", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[1] else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_3", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[2] else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_4", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[3] else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_5", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[4] else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "amt_6", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if message[5] else dashboard.STATUS_ABSENT
                        ]
                    )
                    
                if topic==b"respond_amt203_zeroed":
                    pass
                if topic==b"respond_amt203_absolute_position":
                    #send to game mode
                    #send to hosts object
                    #send to dashboard
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_1", # device
                            "θ absolute",#data_name
                            message[0]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_2", # device
                            "θ absolute",#data_name
                            message[1]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_3", # device
                            "θ absolute",#data_name
                            message[2]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_4", # device
                            "θ absolute",#data_name
                            message[3]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_5", # device
                            "θ absolute",#data_name
                            message[4]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_6", # device
                            "θ absolute",#data_name
                            message[5]
                        ]
                    )
                if topic==b"respond_sdc2160_present":
                    #send to game mode
                    #send to hosts object
                    #send to dashboard
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "sdc_1_2", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel1and2'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_1", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel1and2'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_2", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel1and2'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "sdc_3_4", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel3and4'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_3", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel1and2'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_4", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel1and2'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "sdc_5_6", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel5and6'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_5", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel5and6'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )
                    self.send_to_dashboard(
                        "update_status",
                        [
                            origin, #hostname
                            "carousel_6", # device
                            "",#data_name
                            dashboard.STATUS_PRESENT if len(message['carousel5and6'])>0 else dashboard.STATUS_ABSENT
                        ]
                    )

                if topic==b"respond_sdc2160_controller_faults":
                    device_names = ['sdc_1_2','sdc_3_4','sdc_5_6']
                    for controller_ordinal_name in enumerate(device_names):
                        controller_ordinal, controller_name = controller_ordinal_name
                        controller = message[controller_ordinal]
                        for fault_type in controller:
                            if controller[fault_type] > 0:
                                self.send_to_dashboard(
                                    "update_value",
                                    [
                                        origin, #hostname
                                        controller_name, # device
                                        "faults",#data_name
                                        fault_type
                                    ]
                                )

                if topic==b"respond_sdc2160_channel_faults":
                    device_names = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6']
                    for motor_ordinal_name in enumerate(device_names):
                        motor_ordinal, motor_name = motor_ordinal_name
                        motor = message[motor_name]
                        for fault_type in motor:
                            if fault_type == 'runtime_status_flags':
                                # add interface affordance for runtime_status_flags
                                    'runtime_status_flags': {
                                        'amps_limit_activated': 0, 
                                        'motor_stalled': 0, 
                                        'loop_error_detected': 0, 
                                        'safety_stop_active': 0, 
                                        'forward_limit_triggered': 0, 
                                        'reverse_limit_triggered': 0, 
                                        'amps_trigger_activated': 0
                                    }, 
                                pass
                            else:

                                fault_type_client_names = {
                                    "closed_loop_error":"pid error",
                                    "motor_amps":"amps" ,
                                    "temperature":"temp",
                                    "stall_detection":"stall",
                                    "status":"status",
                                    "θ target":"θ target",
                                }
                                try:
                                    self.send_to_dashboard(
                                        "update_value",
                                        [
                                            origin, #hostname
                                            motor_name, # device
                                            fault_type_client_names[fault_type],#data_name
                                            motor[fault_type]
                                        ]
                                    )
                                except KeyError:
                                    print("key error in respond_sdc2160_channel_faults", fault_type)

                if topic==b"respond_sdc2160_relative_position":
                    #send to game mode
                    #send to hosts object
                    #send to dashboard

                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_1", # device
                            "θ relative",#data_name
                            message[0]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_2", # device
                            "θ relative",#data_name
                            message[1]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_3", # device
                            "θ relative",#data_name
                            message[2]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_4", # device
                            "θ relative",#data_name
                            message[3]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_5", # device
                            "θ relative",#data_name
                            message[4]
                        ]
                    )
                    self.send_to_dashboard(
                        "update_value",
                        [
                            origin, #hostname
                            "amt_6", # device
                            "θ relative",#data_name
                            message[5]
                        ]
                    )

                    """

                    """
                if topic==b"system_tests":
                    pass
                if topic==b"button_press_left_flipper":
                    pass
                if topic==b"button_press_trade_goods":
                    pass
                if topic==b"button_press_start":
                    pass
                if topic==b"button_press_trade_money":
                    pass
                if topic==b"button_press_right_flipper":
                    pass
                if topic==b"left_stack_ball_present":
                    pass
                if topic==b"right_stack_ball_present":
                    pass
                if topic==b"left_stack_motion_detected":
                    pass
                if topic==b"right_stack_motion_detected":
                    pass
                if topic==b"gutter_ball_detected":
                    pass
                if topic==b"spinner":
                    pass
                if topic==b"pop_left":
                    pass
                if topic==b"pop_center":
                    pass
                if topic==b"pop_right":
                    pass
                if topic==b"sling_left":
                    pass
                if topic==b"sling_right":
                    pass
                if topic==b"roll_outer_left":
                    pass
                if topic==b"roll_inner_left":
                    pass
                if topic==b"roll_inner_right":
                    pass
                if topic==b"roll_outer_right":
                    pass
                if topic==b"absolute_position":
                    pass
                if topic==b"relative_position":
                    pass
                if topic==b"confirm_position":
                    pass
                if topic==b"carousel_ball_detected":
                    pass
                    """
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()




#displays = tests.Displays(main.tb)
#displays.wave()

class Fake_Attraction_Mode(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tb = main.tb # real dirty
        self.carousel_names = [
            "carousel1",
            "carousel2",
            "carousel3",
            "carousel4",
            "carousel5",
            "carouselcenter"
        ]
        self.display_names = [
            "pinball1display",
            "pinball2display",
            "pinball3display",
            "pinball4display",
            "pinball5display",
            "" # hack for indexes  probably can't hurt for demo
        ]
        self.gamestation_names = [
            "pinball1game",
            "pinball2game",
            "pinball3game",
            "pinball4game",
            "pinball5game",
            "" # hack for indexes  probably can't hurt for demo
        ]
        self.carousel_fruit_index_offsets = [
            3,
            2,
            1,
            0,
            4,
        ]
        self.carouselcenter_fruit_led_map = [
            6,
            4,
            2,
            0,
            -2,
        ]

        self.carousel_start_end = [
            [8,1,7,1],
            [5,-1,4,-1],
            [3,-3,4,-3],
            [1,-5,2,-5],
            [9,3,8,3],
        ]
        self.start()
    def run_ball_motion_sim(self, start_carousel_ord, end_carousel_ord):
        start_pocket = self.carousel_start_end[start_carousel_ord][2]
        end_pocket = self.carousel_start_end[start_carousel_ord][3]
        carousel_name = self.carousel_names[start_carousel_ord]
        self.tb.publish("request_led_animations",["stroke_arc",[start_pocket,end_pocket]], carousel_name)
        time.sleep(0.5)

        start_pocket = self.carouselcenter_fruit_led_map[start_carousel_ord]
        end_pocket =  self.carouselcenter_fruit_led_map[end_carousel_ord]
        carousel_name = self.carousel_names[5]
        self.tb.publish("request_led_animations",["stroke_arc",[start_pocket,end_pocket]], carousel_name)
        time.sleep(0.5)


        end_pocket = self.carousel_start_end[end_carousel_ord][0]
        start_pocket = self.carousel_start_end[end_carousel_ord][1]
        carousel_name = self.carousel_names[end_carousel_ord]
        self.tb.publish("request_led_animations",["stroke_arc",[start_pocket,end_pocket]], carousel_name)

    def normalize_to_range(self, num, max):
        if num > max-1:
            return num - max
        if num < 0:
            return num + max
        return num

    def run(self):
        while True:
            ball_origin_carousel_ord = random.randrange(0,5)
            while True:
                ball_destination_carousel_ord = random.randrange(0,5)
                if ball_destination_carousel_ord != ball_origin_carousel_ord:
                    break
            for station_ordinal in range(6):
                self.tb.publish(topic="set_phrase",message="",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="all_off",message="",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="set_number",message=-1,destination=self.display_names[station_ordinal])



                time.sleep(3)
                self.tb.publish("playfield_lights",["trail_rollover_right","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_rollover_right","off"], self.gamestation_names[station_ordinal])
                time.sleep(2)
                self.tb.publish("playfield_lights",["trail_rollover_left","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_rollover_left","off"], self.gamestation_names[station_ordinal])
                time.sleep(1.8)
                self.tb.publish("playfield_lights",["trail_sling_right","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_right","off"], self.gamestation_names[station_ordinal])
                time.sleep(1.6)
                self.tb.publish("playfield_lights",["trail_sling_left","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_left","off"], self.gamestation_names[station_ordinal])
                time.sleep(1.4)
                self.tb.publish("playfield_lights",["trail_pop_left","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_left","off"], self.gamestation_names[station_ordinal])
                time.sleep(1.2)
                self.tb.publish("playfield_lights",["trail_pop_right","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_right","off"], self.gamestation_names[station_ordinal])
                time.sleep(1)
                self.tb.publish("playfield_lights",["trail_pop_center","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_center","off"], self.gamestation_names[station_ordinal])
                time.sleep(0.8)
                self.tb.publish("playfield_lights",["trail_spinner","stroke_on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_spinner","off"], self.gamestation_names[station_ordinal])
                time.sleep(0.6)

                self.tb.publish("playfield_lights",["trail_rollover_right","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_rollover_left","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_sling_right","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_sling_left","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_pop_left","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_pop_right","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_pop_center","on"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["trail_spinner","on"], self.gamestation_names[station_ordinal])

                self.tb.publish("playfield_lights",["pie_rollover_right","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_rollover_left","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_right","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_left","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_left","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_right","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_center","off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_spinner","off"], self.gamestation_names[station_ordinal])

            for station_ordinal in range(6):
                time.sleep(3)
                self.tb.publish("playfield_lights",["trail_rollover_right","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_rollover_right","on"], self.gamestation_names[station_ordinal])
                time.sleep(2)
                self.tb.publish("playfield_lights",["trail_rollover_left","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_rollover_left","on"], self.gamestation_names[station_ordinal])
                time.sleep(1.8)
                self.tb.publish("playfield_lights",["trail_sling_right","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_right","on"], self.gamestation_names[station_ordinal])
                time.sleep(1.6)
                self.tb.publish("playfield_lights",["trail_sling_left","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_sling_left","on"], self.gamestation_names[station_ordinal])
                time.sleep(1.4)
                self.tb.publish("playfield_lights",["trail_pop_left","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_left","on"], self.gamestation_names[station_ordinal])
                time.sleep(1.2)
                self.tb.publish("playfield_lights",["trail_pop_right","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_right","on"], self.gamestation_names[station_ordinal])
                time.sleep(1)
                self.tb.publish("playfield_lights",["trail_pop_center","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_pop_center","on"], self.gamestation_names[station_ordinal])
                time.sleep(0.8)
                self.tb.publish("playfield_lights",["trail_spinner","back_stroke_off"], self.gamestation_names[station_ordinal])
                self.tb.publish("playfield_lights",["pie_spinner","on"], self.gamestation_names[station_ordinal])
                time.sleep(0.6)



            self.tb.publish("button_active_trade_goods",True, self.gamestation_names[ball_origin_carousel_ord])
            self.tb.publish("button_active_trade_goods",True, self.gamestation_names[ball_destination_carousel_ord])
            for station_ordinal in range(6):
                self.tb.publish(topic="set_phrase",message="",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="all_off",message="",destination=self.display_names[station_ordinal])
            self.tb.publish(topic="set_phrase",message="trueque",destination=self.display_names[ball_origin_carousel_ord])
            self.tb.publish(topic="set_phrase",message="trueque",destination=self.display_names[ball_destination_carousel_ord])
            for i in range(3):
                self.tb.publish("request_led_animations",["stroke_ripple",[]], self.carousel_names[ball_origin_carousel_ord])
                self.tb.publish(topic="play_score",message="gsharp_mezzo",destination=self.display_names[ball_origin_carousel_ord])
                time.sleep(0.1)
                self.tb.publish(topic="play_score",message="f_mezzo",destination=self.display_names[ball_origin_carousel_ord])
                time.sleep(1)
                self.tb.publish("request_led_animations",["stroke_ripple",[]], self.carousel_names[ball_destination_carousel_ord])
                self.tb.publish(topic="play_score",message="f_mezzo",destination=self.display_names[ball_destination_carousel_ord])
                time.sleep(0.1)
                self.tb.publish(topic="play_score",message="gsharp_mezzo",destination=self.display_names[ball_destination_carousel_ord])
                time.sleep(1)
            self.tb.publish("button_active_trade_goods",False, self.gamestation_names[ball_origin_carousel_ord])
            self.tb.publish("button_active_trade_goods",False, self.gamestation_names[ball_destination_carousel_ord])
            self.tb.publish(topic="set_phrase",message="",destination=self.display_names[ball_origin_carousel_ord])
            self.tb.publish(topic="set_phrase",message="",destination=self.display_names[ball_destination_carousel_ord])
            self.tb.publish(topic="all_off",message="",destination=self.display_names[ball_origin_carousel_ord])
            self.tb.publish(topic="all_off",message="",destination=self.display_names[ball_destination_carousel_ord])
            self.run_ball_motion_sim(ball_origin_carousel_ord,ball_destination_carousel_ord)





            """
            for station_ordinal in range(6):
                self.tb.publish("request_led_animations",["stroke_ripple",[]], self.carousel_names[station_ordinal])
                print(self.display_names[station_ordinal])
                self.tb.publish(topic="play_score",message="f_mezzo",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="set_phrase",message="trueque",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="set_number",message=random.randrange(0,999),destination=self.display_names[station_ordinal])
                time.sleep(0.1)
            for i in range(10):
                for station_ordinal in range(6):
                    self.tb.publish(topic="set_number",message=random.randrange(0,999),destination=self.display_names[station_ordinal])
                    time.sleep(0.05)

            for station_ordinal in range(6):
                self.tb.publish(topic="set_phrase",message="",destination=self.display_names[station_ordinal])
                self.tb.publish(topic="all_off",message="",destination=self.display_names[station_ordinal])
            time.sleep(3)
            self.run_ball_motion_sim(4,2)
            """
            time.sleep(30)
fake_attraction_mode = Fake_Attraction_Mode()


#role_module.main.tb.publish("request_led_animations",["stroke_ripple",[]], "carouselcenter")
#role_module.main.tb.publish("request_led_animations",["pulse_fruit",[0]], "carouselcenter")
#role_module.main.tb.publish("request_led_animations",["stroke_arc",[0,8]], "carouselcenter")
