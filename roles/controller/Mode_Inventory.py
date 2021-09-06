"""
There are three types of host states
    connected [False|True]  part of thirtybirds
    deadman [alive|#error]  deadman switch that cuts higher power >5VDC    
    tests_complete [False|True] performed and passed local tests

    tests_complete and deadman seem redundant.  But deadman must be enabled in order to run some tests
"""
import datetime
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

from roles.controller.Mode_Waiting_For_Connections import Mode_Waiting_For_Connections
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
    def __init__(self, tb, hosts, mode_manager):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.mode_manager = mode_manager
        self.game_mode_names = settings.Game_Modes
        self.game_mode_name = self.game_mode_names.WAITING_FOR_CONNECTIONS

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
        self.hosts = Hosts.Hosts(self.tb)

        #self.mode_waiting_for_connections = Mode_Waiting_For_Connections(self.tb,self.hosts)
        #self.mode_system_tests = Mode_System_Tests(self.tb,self.hosts)
        #self.mode_inventory = Mode_Inventory(self.tb,self.hosts)
        #self.mode_attraction = Mode_Attraction(self.tb,self.hosts)
        #self.mode_countdown = Mode_Countdown(self.tb,self.hosts)
        #self.mode_barter_mode_intro = Mode_Barter_Mode_Intro(self.tb,self.hosts)
        #self.mode_barter_mode = Mode_Barter_Mode(self.tb,self.hosts)
        #self.mode_money_mode_intro = Mode_Money_Mode_Intro(self.tb,self.hosts)
        #self.mode_money_mode = Mode_Money_Mode(self.tb,self.hosts)
        #self.mode_ending = Mode_Ending(self.tb,self.hosts)
        #self.mode_reset = Mode_Reset(self.tb,self.hosts)

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
       

