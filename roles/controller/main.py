"""
There are three types of host states
    connected [False|True]  part of thirtybirds
    deadman [alive|#error]  deadman switch that cuts higher power >5VDC    
    tests_complete [False|True] performed and passed local tests

    tests_complete and deadman seem redundant.  But deadman must be enabled in order to run some tests
"""

import importlib
import mido
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
import roles.controller.tests as tests

###########################
# S Y S T E M   T E S T S #
###########################

# measure 24V current for SDC2160s

##############################
# S A F E T Y  S Y S T E M S #
##############################

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.Deadman.GPIO, GPIO.OUT )
        GPIO.output(settings.Deadman.GPIO, GPIO.LOW)
        self.enabled = False # used for detecting when state changes
        self.queue = queue.Queue()
        self.tb = tb
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        self.hosts_alive = set()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            time.sleep(settings.Deadman.DURATION)
            try:
                while True:
                    deadman_message = self.queue.get(False)
                    topic, message, origin, destination = deadman_message
                    self.hosts_alive.add(origin)
            except queue.Empty:
                pass
            missing_hosts = self.required_hosts.difference(self.hosts_alive)
            print("missing_hosts=",missing_hosts)
            #if len(missing_hosts) > 0:
            #    print("missing hosts:", self.required_hosts.difference(self.hosts_alive))
            if self.required_hosts.issubset(self.hosts_alive):
                if not self.enabled: # if changing state
                    GPIO.output(settings.Deadman.GPIO, GPIO.HIGH)
                    time.sleep(settings.Deadman.DURATION)
                    GPIO.output(settings.Deadman.GPIO, GPIO.LOW)
                    #self.enabled = False
            self.hosts_alive = set()

##################################################
# LOGGING AND REPORTING #
##################################################

# EXCEPTION

# STATUS MESSAGES

# LOCAL LOGGING / ROTATION

##########
# STATES #
##########

class Mode_Waiting_For_Connections(threading.Thread):
    """
    In Waiting_For_Connections mode, the controller is waiting until Thirtybirds 
    establishes connections from all hosts.
    """
    def __init__(self,tb, host_states):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.host_states = host_states
        # self.required_hosts = set(settings.Roles.hosts.keys())
        self.queue = queue.Queue()
        self.start()
    def add_to_queue(self, topic, message, origin, destination):
        """
        receives messages about thirtybirds connections initially received by network_message_handler
        """
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                all_hosts_are_connected, connected_hosts_d = self.tb.check_connections()
                # loop through self.required_hosts
                    # set host_states[hostname].set_connected() to connected_hosts_d[hostname]
                # ^^^ this could all be done in main. gotta do almost everything in main or in mode classes.
                # if all_hosts_are_connected == True
                    # if current mode is settings.Game_Modes.WAITING_FOR_CONNECTIONS
                        # transition to settings.Game_Modes.SYSTEM_TESTS
                # else
                    # if current mode is not settings.Game_Modes.WAITING_FOR_CONNECTIONS
                        # log loss of connection
                        # transition to settings.Game_Modes.WAITING_FOR_CONNECTIONS
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

class Mode_System_Tests(threading.Thread):
    """
    In SYSTEM_TESTS mode, the controller 
        1) checks if System_Enable is on, implying deadman messages from all hosts are present.
        2) sends a get_system_tests request to each host
        3) waits to receive responses from each host
        4) verifies that all tests are passed.
    """
    def __init__(self,tb, host_states):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.host_states = host_states
        self.queue = queue.Queue()
        self.start()
    def add_to_queue(self, topic, message, origin, destination):
        """
        receives messages about host system_tests
        """
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                # if any system tests return False, stop Safety_Enable, cutting higher power, write to log
                # if any tests do not return before timestamp,, stop Safety_Enable, cutting higher power, write to log
                # if all tests return True before timestamp, 
                    # if inventory_complete == True
                        # transition to settings.Game_Modes.RESET
                    # else
                        # transition to settings.Game_Modes.INVENTORY
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

class Mode_Reset(threading.Thread):
    """
    In RESET mode, the controller returns all balls to starting state.
        balls are exchanged via carousels to equalize total number of balls per gamestation
        in final state
            left stack is empty
            right stack has pre-defined max number of balls
            all carousels pockets are filled
        all carousels are in correct positions

    """
    def __init__(self,tb, host_states):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.host_states = host_states
        self.queue = queue.Queue()
        self.start()
    def calculate_steps(self):
        """
        How to represent the steps?
            topic + message would be good because it's not an intermediate system
        Where do movements get verified?  
            Should be in a whole-matrix-exchange system including the matrix, carousels, and stacks.
        Phase 1: 
            fill all carousels 
        Phase 2: 
            fill the right stack until full or until all gamestation balls are used
        Phase 3: 
            move excess balls in left tubes through matrix to unfilled right tubes of other gamestations
            what is the algorithm?
        """
    def add_to_queue(self, topic, message, origin, destination):
        """
        receives messages about stacks, carousels, matrix
        """
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                # if any system tests return False, stop Safety_Enable, cutting higher power, write to log
                # if any tests do not return before timestamp, stop Safety_Enable, cutting higher power, write to log
                # if all tests return True before timestamp, 
                    # if inventory_complete == True
                        # transition to settings.Game_Modes.RESET
                    # else
                        # transition to settings.Game_Modes.INVENTORY
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

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

class Host:
    def __init__(self, hostname):
        self.hostname = hostname
        self.connected = False
        self.ready = False
        self.last_deadman = 0 #unix timestamp
    def set_connected(self, connected):
        self.connected = connected
    def get_connected(self, connected):
        return self.connected
    def set_ready(self, ready):
        self.ready = ready
    def get_ready(self, ready):
        return self.ready
    def set_last_deadman(self, last_deadman):
        self.last_deadman = last_deadman
    def get_connected(self, last_deadman):
        return self.last_deadman

class Hosts:
    def __init__(self):
        self.controller = Host("controller")
        self.pinball1game = Host("pinball1game")
        self.pinball2game = Host("pinball2game")
        self.pinball3game = Host("pinball3game")
        self.pinball4game = Host("pinball4game")
        self.pinball5game = Host("pinball5game")
        self.pinball1display = Host("pinball1display")
        self.pinball2display = Host("pinball2display")
        self.pinball3display = Host("pinball3display")
        self.pinball4display = Host("pinball4display")
        self.pinball5display = Host("pinball5display")
        self.pinballmatrix = Host("pinballmatrix")
        self.carousel1 = Host("carousel1")
        self.carousel2 = Host("carousel2")
        self.carousel3 = Host("carousel3")
        self.carousel4 = Host("carousel4")
        self.carousel5 = Host("carousel5")
        self.carouselcenter = Host("carouselcenter")

class Display():
    def __init__(self, tb, fruit_id):
        self.td = td
        self.fruit_id = fruit_id
    def play_score(self):
        pass
    def set_phrase(self):
        pass
    def set_number(self):
        pass
    def display_all_off(self):
        pass
    def display_get_amps(self):
        pass

class Carousel():
    def __init__(self, tb, fruit_id):
        self.td = td
        self.fruit_id = fruit_id
        self.carousel_measured_position = 0
        self.carousel_target_position = 0
        self.carousel_target_reached = False
        self.carousel_ball_1 = False
        self.carousel_ball_2 = False
        self.carousel_ball_3 = False
        self.carousel_ball_4 = False
        self.carousel_ball_5 = False
    def get_carousel_measured_position(self, carousel_measured_position):
        return self.carousel_measured_position    
    def set_carousel_measured_position(self, carousel_measured_position):
        self.carousel_measured_position = carousel_measured_position
    def get_carousel_target_position(self, carousel_target_position):
        return self.carousel_target_position    
    def set_carousel_target_position(self, carousel_target_position):
        self.carousel_target_position = carousel_target_position
    def get_carousel_target_reached(self, carousel_target_reached):
        return self.carousel_target_reached    
    def set_carousel_target_reached(self, carousel_target_reached):
        self.carousel_target_reached = carousel_target_reached
    def get_carousel_ball_1(self, carousel_ball_1):
        return self.carousel_ball_1    
    def set_carousel_ball_1(self, carousel_ball_1):
        self.carousel_ball_1 = carousel_ball_1
    def get_carousel_ball_2(self, carousel_ball_2):
        return self.carousel_ball_2    
    def set_carousel_ball_2(self, carousel_ball_2):
        self.carousel_ball_2 = carousel_ball_2
    def get_carousel_ball_3(self, carousel_ball_3):
        return self.carousel_ball_2    
    def set_carousel_ball_3(self, carousel_ball_3):
        self.carousel_ball_3 = carousel_ball_3
    def get_carousel_ball_4(self, carousel_ball_4):
        return self.carousel_ball_3    
    def set_carousel_ball_4(self, carousel_ball_4):
        self.carousel_ball_4 = carousel_ball_4
    def get_carousel_ball_5(self, carousel_ball_5):
        return self.carousel_ball_5    
    def set_carousel_ball_5(self, carousel_ball_5):
        self.carousel_ball_5 = carousel_ball_5

class Pinball():
    def __init__(self, tb, fruit_id, hosts):
        self.td = td
        self.fruit_id = fruit_id
        self.hosts = hosts
        self.measured_amps = -1
        self.left_stack_inventory = -1
        self.right_stack_inventory = -1
        self.gutter_ball_detected = False
        self.barter_points = -1
        self.money_points = -1
    def get_measured_amps(self, measured_amps):
        return self.measured_amps    
    def set_measured_amps(self, measured_amps):
        self.measured_amps = measured_amps        
    def get_left_stack_inventory(self, left_stack_inventory):
        return self.left_stack_inventory    
    def set_left_stack_inventory(self, left_stack_inventory):
        self.left_stack_inventory = left_stack_inventory
    def get_right_stack_inventory(self, right_stack_inventory):
        return self.right_stack_inventory    
    def set_right_stack_inventory(self, right_stack_inventory):
        self.right_stack_inventory = right_stack_inventory
    def get_gutter_ball_detected(self, gutter_ball_detected):
        return self.gutter_ball_detected    
    def set_gutter_ball_detected(self, gutter_ball_detected):
        self.gutter_ball_detected = gutter_ball_detected
    def get_barter_points(self, barter_points):
        return self.barter_points   
    def set_barter_points(self, barter_points):
        self.barter_points = barter_points
    def get_money_points(self, money_points):
        return self.money_points    
    def set_money_points(self, money_points):
        self.money_points = money_points
    def gamestation_all_off(self, bool):
        pass
    def gamestation_get_amps(self):
        pass
    def button_active_left_flipper(self):
        pass
    def button_active_trade_goods(self):
        pass
    def button_active_start(self):
        pass
    def button_active_trade_money(self):
        pass
    def button_active_right_flipper(self):
        pass
    def playfield_lights(self, group, animation):
        pass
    def left_stack_launch(self):
        pass
    def right_stack_launch(self):
        pass
    def left_stack_detect_ball(self):
        pass
    def stack_detect_ball(self):
        pass
    def gutter_detect_ball(self):
        pass
    def gutter_launch(self):
        pass

"""
class Gamestations():
    def __init__(self):
        self.gamestation_1 = Gamestation(1,["pinball1game","pinball1display","carousel1"]),
        self.gamestation_2 = Gamestation(2,["pinball2game","pinball2display","carousel2"]),
        self.gamestation_3 = Gamestation(3,["pinball3game","pinball3display","carousel3"]),
        self.gamestation_4 = Gamestation(4,["pinball4game","pinball4display","carousel4"]),
        self.gamestation_5 = Gamestation(5,["pinball5game","pinball5display","carousel5"])
"""

class Matrix():
    def __init__(self, tb, fruit_id, hosts):
        """
        This class choreographs the passing of balls through stacks, carousels, and the pinball matrix.
        actions:
        expire ball to right stack
            0:
            lights for fruit x: energize animation
            1:
            lights for fruit x: blink animation
            sounds: something in sync with blink.  how to do that?
            command motor to rotate so fruit x aligns with right stack
            2: 
            confirm motor position
                if not?
            3: 
            turn on solenoid x for n ms
            sound: loss sound
            4: 
            confirm sensor x reads negative
            rotate carousel so fruit x faces player
            confirm motor position
                if not?

        expire ball to left stack
            0:
            lights for fruit x: energize animation
            1:
            lights for fruit x: blink animation
            sounds: something in sync with blink.  how to do that?
            command motor to rotate so fruit x aligns with left stack
            2: 
            confirm motor position
                if not?
            3: 
            turn on solenoid x for n ms
            sound: loss sound
            4: 
            confirm sensor x reads negative
            rotate carousel so fruit x faces player
            confirm motor position
                if not?

        add money point (transfer ball from left stack to right stack in same game)
            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?
            
        add money point (transfer ball from right stack to left stack in same game)
            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?
            
        trade goods (transfer ball from left stack to self fruit in other game)
            0: 
            player A lights: instructions for trading
            player A lights: trade goods button: blink animation
            player A sound: single-pitch alarm

            player B ball expires when their playfield ball is in the gutter?

            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?

        
        trade money
        trade goods

        inventory and reset routines

        transfer ball from left stack to right stack in different game
        transfer ball from right stack to left stack in different game
        transfer ball from left stack to left stack in different game
        transfer ball from right stack to right stack in different game

        lights?
        sensors?
        """
        pass
        #"controller"
        #"pinballmatrix"
        #"carouselcenter"


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
        self.safety_enable = Safety_Enable(self.tb)
        self.queue = queue.Queue()

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
        self.tb.subscribe_to_topic("right stack_ball_present")
        self.tb.subscribe_to_topic("left_stack_motion_detected")
        self.tb.subscribe_to_topic("right stack_motion_detected")

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
        self.start()
    
    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
        # update self.hosts[hostname].set_connected() 
        self.add_to_queue(topic, message, origin, destination)
    def add_to_queue(self, topic, message, origin, destination):

        # if topic=system_tests, update self.hosts[hostname].set_connected() 
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

