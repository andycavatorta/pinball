"""
main module functions:
    manage active Mode
    route inbound traffic to active Mode
    manage http interface

data flow:
    outgoing data is mostly sent through methods in hosts
    incoming traffic is received in main
    incoming traffic is routed to http interface
    incoming traffic is routed to hosts, where it is cached
    incoming traffic is routed to current mode module, 
        results in outgoing traffic through hosts
        results in change of current mode

to_do:
    what should safety_enable_handler do?
        Pass events to add_to_queue so changes can be handled by hosts and/or mode?
    parse MPF events into format consistent with tb messages
    create module of chime score names to be used by various Modes
    standardize verbs in topic names
        request_, response_, event_

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

import roles.controller.safety_enable as Safety_Enable
import roles.controller.hosts as Hosts

from http_server_root import dashboard

from roles.controller.mode_error import Mode_Error
from roles.controller.mode_waiting_for_connections import Mode_Waiting_For_Connections
from roles.controller.mode_system_tests import Mode_System_Tests
from roles.controller.mode_inventory import Mode_Inventory
from roles.controller.mode_attraction import Mode_Attraction
#from roles.controller.mode_trueque import Mode_Trueque
#from roles.controller.mode_dinero import Mode_Dinero
#from roles.controller.mode_reset import Mode_Reset
#from roles.controller.mode_ending import Mode_Ending

class Main(threading.Thread):
    class mode_names:
        ERROR = "error"
        WAITING_FOR_CONNECTIONS = "waiting_for_connections"
        SYSTEM_TESTS = "system_tests"
        INVENTORY = "inventory"
        RESET = "reset"
        ATTRACTION = "attraction"
        COUNTDOWN = "countdown"
        BARTER_MODE_INTRO = "barter_mode_intro"
        BARTER_MODE = "barter_mode"
        MONEY_MODE_INTRO = "money_mode_intro"
        MONEY_MODE = "money_mode"
        ENDING = "ending"

    def __init__(self):
        threading.Thread.__init__(self)
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.queue = queue.Queue()
        self.safety_enable = Safety_Enable.Safety_Enable(self.safety_enable_handler)
        self.hosts = Hosts.Hosts(self.tb)

        ##### SUBSCRIPTIONS #####
        # CONNECTIVITY
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")
        #system tests
        self.tb.subscribe_to_topic("response_computer_details")
        self.tb.subscribe_to_topic("response_current_sensor_present")
        self.tb.subscribe_to_topic("response_current_sensor_value")
        self.tb.subscribe_to_topic("response_current_sensor_nominal")
        self.tb.subscribe_to_topic("response_amt203_present")
        self.tb.subscribe_to_topic("response_amt203_zeroed")
        self.tb.subscribe_to_topic("response_amt203_absolute_position")
        self.tb.subscribe_to_topic("response_sdc2160_present")
        self.tb.subscribe_to_topic("response_sdc2160_relative_position")
        self.tb.subscribe_to_topic("response_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("response_sdc2160_controller_faults")
        self.tb.subscribe_to_topic("response_sdc2160_closed_loop_error")
        self.tb.subscribe_to_topic("response_visual_tests")
        self.tb.subscribe_to_topic("request_current_sensor_nominal")
        # pinball events
        self.tb.subscribe_to_topic("event_mpf")
        """
        MPF events will be parsed into tb messages with topics
            event_spinner
            event_pop_left
            event_pop_center
            event_pop_right
            event_sling_left
            event_sling_right
            event_button_izquierda
            event_button_trueque
            event_button_comienza
            event_button_dinero
            event_button_derecho
        """
        self.tb.subscribe_to_topic("event_roll_outer_left")
        self.tb.subscribe_to_topic("event_roll_inner_left")
        self.tb.subscribe_to_topic("event_roll_inner_right")
        self.tb.subscribe_to_topic("event_roll_outer_right")
        self.tb.subscribe_to_topic("event_trough_sensor")
        self.tb.subscribe_to_topic("event_left_stack_ball_present")
        self.tb.subscribe_to_topic("event_right_stack_ball_present")
        self.tb.subscribe_to_topic("event_left_stack_motion_detected")
        self.tb.subscribe_to_topic("event_right_stack_motion_detected")

        # ENCODERS & MOTORS
        self.tb.subscribe_to_topic("response_carousel_absolute")
        self.tb.subscribe_to_topic("response_carousel_relative")
        self.tb.subscribe_to_topic("event_carousel_target_reached")
        self.tb.subscribe_to_topic("event_carousel_error")
        
        # INDUCTIVE SENSORS
        self.tb.subscribe_to_topic("event_carousel_ball_detected")
        self.tb.subscribe_to_topic("response_carousel_ball_detected")

        self.modes = {
            "error":Mode_Error(self.tb, self.hosts, self.set_current_mode),
            "waiting_for_connections":Mode_Waiting_For_Connections(self.tb, self.hosts, self.set_current_mode),
            "system_tests":Mode_System_Tests(self.tb, self.hosts, self.set_current_mode),
            "inventory":Mode_Inventory(self.tb, self.hosts, self.set_current_mode),
            "attraction":Mode_Attraction(self.tb, self.hosts, self.set_current_mode),
            #"reset":Mode_Reset(self.tb, self.hosts, self.set_current_mode),
            #"countdown":Mode_Countdown(self.tb, self.hosts, self.set_current_mode),
            #"barter_intro":Mode_Barter_Intro(self.tb, self.hosts, self.set_current_mode),
            #"barter":Mode_Barter(self.tb, self.hosts, self.set_current_mode),
            #"money_intro":Mode_Money_Intro(self.tb, self.hosts, self.set_current_mode),
            #"money":Mode_mone(self.tb, self.hosts, self.set_current_mode),
            #"ending":Mode_ending(self.tb, self.hosts, self.set_current_mode),
        }
        self.send_to_dashboard = dashboard.init(self.tb)
        self.current_mode_name = self.mode_names.WAITING_FOR_CONNECTIONS
        self.current_mode = self.modes["waiting_for_connections"]
        self.current_mode.begin()
        self.start()
    ##### THIRTYBIRDS CALLBACKS #####
    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        self.add_to_queue(b"respond_host_connected",status,hostname, False)
        # update self.hosts[hostname].set_connected() 
        # self.add_to_queue(topic, message, origin, destination)
    def add_to_queue(self, topic, message, origin, destination):
        # if topic=system_tests, update self.hosts[hostname].set_connected() 
        self.queue.put((topic, message, origin, destination))
    ##### MODE MANAGEMENT #####
    def set_current_mode(self,mode_name):
        print("set_current_mode",mode_name, self.mode_names.SYSTEM_TESTS, mode_name == self.mode_names.SYSTEM_TESTS)
        self.current_mode_name = mode_name
        if mode_name == self.mode_names.ERROR:
            self.current_mode.end()
            self.current_mode = self.mode_error
            self.current_mode.begin()
        if mode_name == self.mode_names.WAITING_FOR_CONNECTIONS:
            self.current_mode.end()
            self.current_mode = self.mode_waiting_for_connections
            self.current_mode.begin()
        if mode_name == self.mode_names.SYSTEM_TESTS:
            print("!!!!!!!!!!!!!!!!!!!")
            self.current_mode.end()
            self.current_mode = self.mode_system_test
            print(self.current_mode)
            print(self.current_mode.begin())
            self.current_mode.begin()
        if mode_name == self.mode_names.INVENTORY:
            self.current_mode.end()
            self.current_mode = self.mode_inventory
            self.current_mode.begin()
        if mode_name == self.mode_names.RESET:
            self.current_mode.end()
            self.current_mode = self.mode_reset
            self.current_mode.begin()
        if mode_name == self.mode_names.ATTRACTION:
            self.current_mode.end()
            self.current_mode = self.mode_attraction
            self.current_mode.begin()
        if mode_name == self.mode_names.COUNTDOWN:
            self.current_mode.end()
            self.current_mode = self.mode_countdown
            self.current_mode.begin()
        if mode_name == self.mode_names.BARTER_MODE_INTRO:
            self.current_mode.end()
            self.current_mode = self.mode_barter_intro
            self.current_mode.begin()
        if mode_name == self.mode_names.BARTER_MODE:
            self.current_mode.end()
            self.current_mode = self.mode_barter
            self.current_mode.begin()
        if mode_name == self.mode_names.MONEY_MODE_INTRO:
            self.current_mode.end()
            self.current_mode = self.mode_money_intro
            self.current_mode.begin()
        if mode_name == self.mode_names.MONEY_MODE:
            self.current_mode.end()
            self.current_mode = self.mode_money
            self.current_mode.begin()
        if mode_name == self.mode_names.ENDING:
            self.current_mode.end()
            self.current_mode = self.mode_ending
            self.current_mode.begin()
    def get_current_mode(self):
        return self.current_mode
    ##### SAFETY ENABLE #####
    def safety_enable_handler(self, state_bool):
        # when all computers are present
        # when power turns on or off
        self.add_to_queue(b"event_safety_enable", state_bool, "", "")

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
                    continue
                print(topic, type(topic), topic.decode('UTF-8'))
                #if "event" not in topic:
                #    print("received:",topic, message, origin, destination)
                if topic==b"event_mpf":
                    if message['component'] == 's_left_flipper':
                        topic = "event_flipper_left"
                    if message['component'] == 's_left_launch':
                        topic = "event_flipper_right"
                    if message['component'] == 's_game_launch':
                        topic = "event_kicker"
                    if message['component'] == 's_right_launch':
                        topic = "event_tube_right"
                    if message['component'] == 's_right_flipper':
                        topic = "event_tube_left"
                    if message['component'] == 's_pop_bumper_1':
                        topic = "event_pop_1"
                    if message['component'] == 's_pop_bumper_2':
                        topic = "event_pop_2"
                    if message['component'] == 's_pop_bumper_3':
                        topic = "event_pop_3"
                    if message['component'] == 's_left_slingshot_main':
                        topic = "event_slingshot_left"
                    if message['component'] == 's_right_slingshot_main':
                        topic = "event_slingshot_right"
                    message = message['new_state']

                self.hosts.dispatch(topic, message, origin, destination)
                self.send_to_dashboard(topic, message, origin, destination)
                self.current_mode.add_to_queue(topic, message, origin, destination)

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()
