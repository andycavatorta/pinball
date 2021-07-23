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
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.sensors.AMT203_encoder import AMT203_absolute_encoder

GPIO.setmode(GPIO.BCM)


##################################################
# SAFETY SYSTEMS #
##################################################

# DEADMAN SWITCH ( SEND ANY OUT-OF-BOUNDS VALUES FROM OTHER SYSTEMS)

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            #self.queue.get(True)
            self.tb.publish("deadman", "safe")
            time.sleep(1)

# COMPUTER STATUS CHECK
    # runs on slower rhythm than deadman
    # only log report if there is a problem

# 48V CURRENT METER current_sensor_handler

##################################################
# LOGGING AND REPORTING #
##################################################

# EXCEPTION

# STATUS MESSAGES

# LOCAL LOGGING / ROTATION

##################################################
# MAIN, TB, STATES, AND TOPICS #
##################################################


##########
# STATES #
##########

class Game_Mode():
    def __init__(self):
        self.modes = settings.Game_Modes
        self.mode = self.game_modes.WAITING_FOR_CONNECTIONS
    def get_mode(self):
        return self.mode
    def set_mode(self, mode_ref):
        self.mode = mode_ref

class Matrix_Mode():
    UNHOMED = "unhomed"
    HOMED = "homed"
    START_POSITIONS_FOR_BARTER = "start positions for barter"
    START_POSITIONS_FOR_MONEY = "start positions for money"
    BALL_TRANSFER_MODE = "ball transfer mode" # same for game and inventory?

    def __init__(self):
        self.mode = self.UNHOMED


###################
# HARDWARE SETUP  #
###################

# set up motor controllers
# set up references to motors
# set up proxies for carousels?

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



class Motor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, chip_select_pin)
        self.chip_select_pin = chip_select_pin
        self.encoder = AMT203_absolute_encoder.AMT203(cs=chip_select_pin)
        self.queue = queue.Queue()
        self.lights = Lights()
        self.sensors = Sensors()

        # ?? sensors? 
    def home(self):
        # on completion, publish confirmation
        pass

    def rotate_to_position_in_degrees(self):
        # on completion, publish confirmation
        pass

    def rotate_to_position_in_pulses(self):
        # on completion, publish confirmation
        pass

    def rotate_fruitpocket_to_barter_tube_position(self):
        # on completion, publish confirmation
        pass

    def rotate_fruitpocket_to_money_tube_position(self):
        # on completion, publish confirmation
        pass

    def rotate_fruitpocket_to_center(self):
        # on completion, publish confirmation
        pass
        
    def eject_ball(self):
        pass

    def detect_ball(self):
        pass

class Motors(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.tb = tb
        self.controller_names = ["carousel1and2", "carousel3and4","carousel5and6"]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]
        self.chip_select_pins_for_abs_enc = [13,12,18,17,16,5]
        self.encoder_value_offset = [0,0,0,0,0,0]
        self.ppr = 4096
        self.queue = queue.Queue()
        self.create_controllers_and_motors()
        time.sleep(1)
        #self.set_rel_encoder_position_to_abs_encoder_position()
        #self.home()
        self.start()

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
        for motor_name_ordinal in enumerate(self.motor_names):
            print("creating AMT203_absolute_encoder", motor_name_ordinal[0], self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])
            self.controllers.motors[motor_name_ordinal[1]].absolute_encoder = AMT203_absolute_encoder.AMT203(cs=self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    """
    def set_rel_encoder_position_to_abs_encoder_position(self):
        for motor_name in self.motor_names:
            abs_pos = self.controllers.motors[motor_name].absolute_encoder.get_position()
            self.controllers.motors[motor_name].set_encoder_counter(abs_pos)

    def ppr_to_mils(self, ppr):
        return int(((ppr-2048)/2048*1000))

    def mils_to_ppr(self, mils):
        return int(((float(mils)/1000.0)*2048.0)+2048.0)

    def home(self):
        for motor_name in self.motor_names:
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()
            rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            self.controllers.motors[motor_name].go_to_speed_or_relative_position(self.ppr_to_mils(0))
            time.sleep(2)
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()

    def ball_transfer(self, gamestation_a, gamestation_b):
        # start timer_a and timer_b
        # confirm bridges a and b are down
        # turn gamestation_a carousel to receive ball
        # turn gamestation_b carousel to receive ball
        # if gamestation_a and gamestation_b receive balls before time runs out:
            # rotate carousels to bridges
            # confirm carousel positions
            # lift bridges
            # confirm balls are received in central carousel
            # rotate 
        time.sleep(1)
    """

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

motors = Motors() 


################################################
# HARDWARE SEMANTICS (map of callable methods) #
################################################

motor_controller = {
    "carousel1and2":motors.controllers.boards["carousel1and2"],
    "carousel3and4":motors.controllers.boards["carousel3and4"],
    "carousel5and6":motors.controllers.boards["carousel5and6"],
}

motor = {
    "carousel_1":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_1"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_1"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_1"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_1"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_1",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_1",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_1",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_1",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_1",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_1",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_1",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_1",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_1",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_1",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_1", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_1", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_1", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_1", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_1", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_1", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_1", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_1", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_1", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_1", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_1", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_1", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_1", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_1", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_1", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_1", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_1", ["lights", "dinero", "back_trace"]),
            },
        },
    },
    "carousel_2":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_2"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_2"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_2"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_2"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_2",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_2",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_2",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_2",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_2",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_2",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_2",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_2",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_2",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_2",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_2", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_2", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_2", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_2", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_2", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_2", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_2", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_2", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_2", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_2", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_2", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_2", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_2", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_2", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_2", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_2", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_2", ["lights", "dinero", "back_trace"]),
            },
        },
    },
    "carousel_3":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_3"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_3"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_3"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_3"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_3",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_3",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_3",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_3",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_3",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_3",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_3",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_3",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_3",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_3",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_3", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_3", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_3", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_3", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_3", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_3", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_3", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_3", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_3", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_3", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_3", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_3", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_3", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_3", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_3", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_3", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_3", ["lights", "dinero", "back_trace"]),
            },
        },
    },
    "carousel_4":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_4"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_4"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_4"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_4"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_4",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_4",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_4",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_4",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_4",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_4",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_4",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_4",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_4",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_4",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_4", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_4", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_4", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_4", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_4", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_4", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_4", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_4", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_4", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_4", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_4", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_4", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_4", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_4", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_4", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_4", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_4", ["lights", "dinero", "back_trace"]),
            },
        },
    },
    "carousel_5":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_5"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_5"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_5"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_5"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_5",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_5",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_5",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_5",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_5",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_5",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_5",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_5",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_5",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_5",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_5", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_5", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_5", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_5", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_5", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_5", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_5", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_5", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_5", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_5", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_5", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_5", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_5", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_5", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_5", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_5", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_5", ["lights", "dinero", "back_trace"]),
            },
        },
    },
    "carousel_center":{
        "set_rel_encoder_position":motors.controllers.motors["carousel_center"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motors.controllers.motors["carousel_center"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motors.controllers.motors["carousel_center"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motors.controllers.motors["carousel_center"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruitpocket_to_barter_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_money_tube_position":None,#(fruit_number)
        "rotate_fruitpocket_to_center":None,#(fruit_number)
        "eject_ball": {
            "fruit_0":motors.tb.publish("carousel_center",["eject_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_center",["eject_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_center",["eject_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_center",["eject_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_center",["eject_ball","fruit_4"]),
        }
        "detect_ball": {
            "fruit_0":motors.tb.publish("carousel_center",["detect_ball","fruit_0"]),
            "fruit_1":motors.tb.publish("carousel_center",["detect_ball","fruit_1"]),
            "fruit_2":motors.tb.publish("carousel_center",["detect_ball","fruit_2"]),
            "fruit_3":motors.tb.publish("carousel_center",["detect_ball","fruit_3"]),
            "fruit_4":motors.tb.publish("carousel_center",["detect_ball","fruit_4"]),
        }
        "lights":{
            "fruit_0":{
                "off":motors.tb.publish("carousel_center", ["lights", "fruit_0", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "fruit_0", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "fruit_0", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "fruit_0", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "fruit_0", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "fruit_0", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_0", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_0", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_0", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_0", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "fruit_0", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "fruit_0", "back_trace"]),
            },
            "fruit_1":{
                "off":motors.tb.publish("carousel_center", ["lights", "fruit_1", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "fruit_1", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "fruit_1", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "fruit_1", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "fruit_1", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "fruit_1", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_1", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_1", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_1", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_1", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "fruit_1", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "fruit_1", "back_trace"]),
            },
            "fruit_2":{
                "off":motors.tb.publish("carousel_center", ["lights", "fruit_2", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "fruit_2", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "fruit_2", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "fruit_2", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "fruit_2", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "fruit_2", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_2", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_2", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_2", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_2", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "fruit_2", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "fruit_2", "back_trace"]),
            },
            "fruit_3":{
                "off":motors.tb.publish("carousel_center", ["lights", "fruit_3", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "fruit_3", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "fruit_3", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "fruit_3", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "fruit_3", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "fruit_3", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_3", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_3", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_3", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_3", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "fruit_3", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "fruit_3", "back_trace"]),
            },
            "fruit_4":{
                "off":motors.tb.publish("carousel_center", ["lights", "fruit_4", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "fruit_4", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "fruit_4", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "fruit_4", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "fruit_4", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "fruit_4", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_4", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_4", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "fruit_4", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "fruit_4", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "fruit_4", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "fruit_4", "back_trace"]),
            },
            "dinero":{
                "off":motors.tb.publish("carousel_center", ["lights", "dinero", "off"]),
                "on":motors.tb.publish("carousel_center", ["lights", "dinero", "on"]),
                "sparkle":motors.tb.publish("carousel_center", ["lights", "dinero", "sparkle"]),
                "throb":motors.tb.publish("carousel_center", ["lights", "dinero", "throb"]),
                "energize":motors.tb.publish("carousel_center", ["lights", "dinero", "energize"]),
                "blink":motors.tb.publish("carousel_center", ["lights", "dinero", "blink"]),
                "stroke_on":motors.tb.publish("carousel_center", ["lights", "dinero", "stroke_on"]),
                "stroke_off":motors.tb.publish("carousel_center", ["lights", "dinero", ""stroke_off]),
                "back_stroke_on":motors.tb.publish("carousel_center", ["lights", "dinero", "back_stroke_on"]),
                "back_stroke_off":motors.tb.publish("carousel_center", ["lights", "dinero", "back_stroke_off"]),
                "trace":motors.tb.publish("carousel_center", ["lights", "dinero", "trace"]),
                "back_trace":motors.tb.publish("carousel_center", ["lights", "dinero", "back_trace"]),
            },
        },
    },
}




#############################################
# ROUTINES (time, events, multiple systems) # 
#############################################

# trade_goods

# trade_money


#############################################

# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class States:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
        self.states =States()
        self.state = self.states.WAITING_FOR_CONNECTIONS
        self.controller_names = ["carousel1and2", "carousel3and4","carousel5and6"]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]
        self.chip_select_pins_for_abs_enc = [8,7,18,17,16,5]
        self.ppr = 4096

        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.safety_enable = Safety_Enable(self.tb)
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.subscribe_to_topic("connected")

        #self.create_controllers_and_motors()
        #time.sleep(3)
        #self.set_rel_encoder_position_to_abs_encoder_position()
        #time.sleep(1)
        #self.home()
        self.start()

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
        for motor_name_ordinal in enumerate(self.motor_names):
            self.controllers.motors[motor_name_ordinal[1]].absolute_encoder = AMT203_absolute_encoder.AMT203(cs=self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])

    def set_rel_encoder_position_to_abs_encoder_position(self):
        for motor_name in self.motor_names:
            abs_pos = self.controllers.motors[motor_name].absolute_encoder.get_position()
            #rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            #print(motor_name,abs_pos,rel_pos)
            self.controllers.motors[motor_name].set_encoder_counter(abs_pos)
            #rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            #print(motor_name,abs_pos,rel_pos)

    def ppr_to_mils(self, ppr):
        return int(((ppr-2048)/2048*1000))

    def mils_to_ppr(self, mils):
        return int(((float(mils)/1000.0)*2048.0)+2048.0)

    def home(self):
        for motor_name in self.motor_names:
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()
            rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            self.controllers.motors[motor_name].go_to_speed_or_relative_position(self.ppr_to_mils(0))
            time.sleep(2)
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()

    def ball_transfer(self, gamestation_a, gamestation_b):
        # start timer_a and timer_b
        # confirm bridges a and b are down
        # turn gamestation_a carousel to receive ball
        # turn gamestation_b carousel to receive ball
        # if gamestation_a and gamestation_b receive balls before time runs out:
            # rotate carousels to bridges
            # confirm carousel positions
            # lift bridges
            # confirm balls are received in central carousel
            # rotate 
        time.sleep(1)

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
    def set_game_mode(self, mode):
        if mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            print("Mode Attraction")
            self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
            pass # peripheral power should be off during this mode
        if mode == self.game_modes.RESET:
            print("Mode : Reset ")
            
            self.game_mode = self.game_modes.RESET
            time.sleep(6)
            self.tb.publish("ready_state",True)
            print("Done with reset, initiating attraction")

        if mode == self.game_modes.ATTRACTION:
            print("Mode Attraction")

            self.game_mode = self.game_modes.ATTRACTION
        # waits for press of start button 
        """
        if mode == self.game_modes.COUNTDOWN:
            #self.player.play("countdown_mode")
        if mode == self.game_modes.BARTER_MODE_INTRO:
            self.player.play("barter_mode_intro")
        if mode == self.game_modes.BARTER_MODE:
            self.player.play("barter_mode")
        if mode == self.game_modes.MONEY_MODE_INTRO:
            self.player.play("money_mode_intro")
        if mode == self.game_modes.MONEY_MODE:
            self.player.play("money_mode")
        if mode == self.game_modes.ENDING:
            self.player.play("closing_theme")
        if mode == self.game_modes.RESET:
            self.player.play("reset")
        if mode == self.game_modes.ERROR:
            pass
        """

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'set_game_mode':
                    self.set_game_mode(message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
#main = Main()
