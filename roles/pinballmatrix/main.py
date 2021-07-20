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



class Lights_Pattern(threading.Thread):
    class action_times():
        SPARKLE = 0.025
        THROB = 0.025
        ENERGIZE = 0.25
        BLINK = 0.25
        STROKE = 0.125
        BACK_TRACE = 0.125
        TRACE = 0.125

    class action_names():
        ON = "on"
        OFF = "off"
        SPARKLE = "sparkle"
        THROB = "throb"
        ENERGIZE = "energize"
        BLINK = "blink"
        STROKE_ON = "stroke_on"
        STROKE_OFF = "stroke_off"
        BACK_STROKE_ON = "back_stroke_on"
        BACK_STROKE_OFF = "back_stroke_off"
        TRACE = "trace"
        BACK_TRACE = "back_trace"

    def __init__(self):
        threading.Thread.__init__(
            self, 
            channels, 
            upstream_queue, 
        )
        self.levels = [0,1024,2048,4096,8192,16384,32768,65535] # just guesses for now
        self.upstream_queue = upstream_queue
        self.channels = channels
        self.queue = queue.Queue()
        self.start()
    def off(self):
        self.action_queue.put([self.action_names.OFF, self.channels])
    def on(self):
        self.action_queue.put([self.action_names.ON, self.channels])
    def sparkle(self):
        self.action_queue.put([self.action_names.SPARKLE, self.channels])
    def throb(self):
        self.action_queue.put([self.action_names.THROB, self.channels])
    def energize(self):
        self.action_queue.put([self.action_names.ENERGIZE, self.channels])
    def blink(self):
        self.action_queue.put([self.action_names.BLINK, self.channels])
    def stroke_on(self):
        self.action_queue.put([self.action_names.STROKE_ON, self.channels])
    def stroke_off(self):
        self.action_queue.put([self.action_names.STROKE_OFF, self.channels])
    def back_stroke_on(self):
        self.action_queue.put([self.action_names.BACK_STROKE_ON, self.channels])
    def back_stroke_off(self):
        self.action_queue.put([self.action_names.BACK_STROKE_OFF, self.channels])
    def trace(self):
        self.action_queue.put([self.action_names.TRACE, self.channels])
    def back_trace(self):
        self.action_queue.put([self.action_names.BACK_TRACE, self.channels])
    def run(self):
        while True:
            # new actions in action_queue will override previous actions
            action_name, channel = self.action_queue.get(True)
            if action_name in [self.action_names.OFF, self.action_names.ON]: 
                self.upstream_queue.put([action_name, channel])
            if action_name == self.action_names.SPARKLE: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                        time.sleep(self.action_times.SPARKLE)
                        self.upstream_queue.put(self.levels[-1], channel)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.THROB:
                while True:
                    for level in self.levels:
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.action_queue.empty():
                        break
                    for level in reversed(self.levels): 
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.ENERGIZE: 
                for divisor in [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BLINK: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.BLINK)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.BLINK)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_ON: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    self.upstream_queue.put(self.levels[0], channel)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.TRACE: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_TRACE:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.action_queue.empty():
                        break

class Lights(threading.Thread):
    class pattern_channels():
        FRUIT_0 = [0,1,2]
        FRUIT_1 = [0,1,2]
        FRUIT_2 = [0,1,2]
        FRUIT_3 = [0,1,2]
        FRUIT_4 =  [0,1,2]
        FRUIT_5 =  [0,1,2]
        ALL_RADIAL = [0,1,2]
        ALL_CLOCKWISE = [0,1,2]

    def __init__(self):
        threading.Thread.__init__()
        self.channels = [0]*12
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D5)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=1)
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.create_pwm_out(channel_number)
        self.queue = queue.Queue()
        self.fruit_0 = Lights_Pattern(self.pattern_channels.FRUIT_0, self.queue)
        self.fruit_1 = Lights_Pattern(self.pattern_channels.FRUIT_1, self.queue)
        self.fruit_2 = Lights_Pattern(self.pattern_channels.FRUIT_2, self.queue)
        self.fruit_3 = Lights_Pattern(self.pattern_channels.FRUIT_3, self.queue)
        self.fruit_4 = Lights_Pattern(self.pattern_channels.FRUIT_4, self.queue)
        self.fruit_5 = Lights_Pattern(self.pattern_channels.FRUIT_5, self.queue)
        self.all_radial = Lights_Pattern(self.pattern_channels.ALL_RADIAL, self.queue)
        self.all_clockwise = Lights_Pattern(self.pattern_channels.ALL_CLOCKWISE, self.queue)
        self.start()
        
    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))
    def run(self):
        while True:
            level, channel_number = self.queue.get(True)
            self.channels[channel_number].duty_cycle = level

class Sensors():
    def __init__(self):
        self.pins [0,1,2,3,4,5] # todo: update late
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN)
    def detect_ball(self, fruit_number):
            return GPIO.input(fruit_number)

class Carousel(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, chip_select_pin)
        self.chip_select_pin = chip_select_pin
        self.encoder = AMT203_absolute_encoder.AMT203(cs=chip_select_pin)
        self.queue = queue.Queue()
        self.lights = Lights()
        self.sensors = Sensors()

        # ?? sensors? 
    def home(self):
        pass

    def rotate_to_position_in_degrees(self):
        pass

    def rotate_to_position_in_pulses(self):
        pass

    def rotate_to_barter_tube_position(self):
        pass

    def rotate_to_money_tube_position(self):
        pass

    def rotate_to_center(self):
        pass

    def eject_ball(self):
        pass

    def detect_ball(self):
        pass

        
        



class Carousels(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
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

motor_controllers = Motor_Controllers()


################################################
# HARDWARE SEMANTICS (map of callable methods) #
################################################

motor_controller = {
    "carousel1and2":motor_controllers.controllers.boards["carousel1and2"],
    "carousel3and4":motor_controllers.controllers.boards["carousel3and4"],
    "carousel5and6":motor_controllers.controllers.boards["carousel5and6"],
}

motor = {
    "carousel_1":{
        "set_rel_encoder_position":motor_controllers.controllers.motors["carousel_1"].set_encoder_counter,#(relative position in encoder pulses)
        "get_rel_encoder_position":motor_controllers.controllers.motors["carousel_1"].get_encoder_counter_absolute,
        "get_abs_encoder_position":motor_controllers.controllers.motors["carousel_1"].absolute_encoder.get_position,
        "get_abs_encoder_position_to_zero":motor_controllers.controllers.motors["carousel_1"].absolute_encoder.set_zero,
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_2":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_3":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_4":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_5":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_6":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruit_number_to_gamestation_number":None,#(fruit_number,gamestation_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
}

#############################################
# ROUTINES (time, events, multiple systems) # 
#############################################



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
