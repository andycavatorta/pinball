"""
There are three types of host states
    connected [False|True]  part of thirtybirds
    deadman [alive|#error]  deadman switch that cuts higher power >5VDC    
    tests_complete [False|True] performed and passed local tests

    tests_complete and deadman seem redundant.  But deadman must be enabled in order to run some tests
"""

import importlib
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time
import json

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

#import roles.pinball.Mode_Waiting_For_Connections as Mode_Waiting_For_Connections
#import roles.pinball.Mode_System_Tests as Mode_System_Tests
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
        self.mode = self.modes.Game_Modes.WAITING_FOR_CONNECTIONS #initial mode
        self.transitional_mode = self.modes.Game_Modes.WAITING_FOR_CONNECTIONS # this is the intened next mode, pending testing
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
    def __init__(self):
        threading.Thread.__init__(self)
        self.game_modes = settings.Game_Modes
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS

        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        #self.carousel_current_sensor = ina260_current_sensor.INA260()
        self.safety_enable = Safety_Enable.Safety_Enable(self.safety_enable_handler)
        self.game_mode_manager = Game_Mode_Manager()
        self.queue = queue.Queue()
        self.send_to_dashboard = dashboard.init(self.tb)

        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")

        self.tb.subscribe_to_topic("respond_computer_details")
        self.tb.subscribe_to_topic("respond_24v_current")
        self.tb.subscribe_to_topic("respond_amt203_present")
        self.tb.subscribe_to_topic("respond_amt203_zeroed")
        self.tb.subscribe_to_topic("respond_amt203_absolute_position")
        self.tb.subscribe_to_topic("respond_sdc2160_present")
        self.tb.subscribe_to_topic("respond_sdc2160_relative_position")
        self.tb.subscribe_to_topic("respond_sdc2160_channel_faults")
        self.tb.subscribe_to_topic("respond_sdc2160_controller_faults")

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
    """
    def process_computer_details(self, hostname, type, value)


    def (self, state_bool):
        # when all computers are present
        # when power turns on or off
        # self.game_mode_manager.set_mode()
        # self.game_mode_manager.set_mode(modes.SYSTEM_TESTS)
        self.tb.publish("respond_high_power_enabled", state_bool)
        if state_bool:
            self.tb.publish("request_system_tests", True)
    """

    
    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
        # update self.hosts[hostname].set_connected() 
        # self.add_to_queue(topic, message, origin, destination)
    def add_to_queue(self, topic, message, origin, destination):

        # if topic=system_tests, update self.hosts[hostname].set_connected() 
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                if topic!=b"deadman":
                    print(topic, message, origin, destination)
                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
                if topic==b"connected":
                    pass
                if topic==b"respond_computer_details":
                    # update http_server?
                    pass
                if topic==b"respond_24v_current":
                    pass
                if topic==b"respond_amt203_present":
                    pass
                if topic==b"respond_amt203_zeroed":
                    pass
                if topic==b"respond_amt203_absolute_position":
                    pass

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


displays = role_module.tests.Displays(role_module.main.tb)
displays.wave()

