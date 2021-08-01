import adafruit_tlc5947
import board
import busio
import digitalio
import importlib
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
import common.deadman as deadman

GPIO.setmode(GPIO.BCM)


##################################################
# SAFETY SYSTEMS #
##################################################

# DEADMAN SWITCH ( SEND ANY OUT-OF-BOUNDS VALUES FROM OTHER SYSTEMS)

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

###################
# HARDWARE SETUP  #
###################

# set up motor controllers
# set up references to motors
# set up proxies for carousels?

class LED_Group(threading.Thread):
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

    def __init__(self, channels, upstream_queue,):
        threading.Thread.__init__(self)
        self.levels = [0,1024,2048,4096,8192,16384,32768,65535] # just guesses for now
        self.upstream_queue = upstream_queue
        self.channels = channels
        self.local_queue = queue.Queue()
        self.actions = {1
        }
        self.start()
    def off(self):
        self.local_queue.put([self.action_names.OFF, self.channels])
    def on(self):
        self.local_queue.put([self.action_names.ON, self.channels])
    def sparkle(self):
        self.local_queue.put([self.action_names.SPARKLE, self.channels])
    def throb(self):
        self.local_queue.put([self.action_names.THROB, self.channels])
    def energize(self):
        self.local_queue.put([self.action_names.ENERGIZE, self.channels])
    def blink(self):
        self.local_queue.put([self.action_names.BLINK, self.channels])
    def stroke_on(self):
        self.local_queue.put([self.action_names.STROKE_ON, self.channels])
    def stroke_off(self):
        self.local_queue.put([self.action_names.STROKE_OFF, self.channels])
    def back_stroke_on(self):
        self.local_queue.put([self.action_names.BACK_STROKE_ON, self.channels])
    def back_stroke_off(self):
        self.local_queue.put([self.action_names.BACK_STROKE_OFF, self.channels])
    def trace(self):
        self.local_queue.put([self.action_names.TRACE, self.channels])
    def back_trace(self):
        self.local_queue.put([self.action_names.BACK_TRACE, self.channels])
    def run(self):
        while True:
            # new actions in local_queue will override previous actions
            action_name, channel = self.local_queue.get(True)

            if action_name == self.action_names.OFF:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)

            if action_name == self.action_names.ON:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)

            if action_name == self.action_names.SPARKLE: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                        time.sleep(self.action_times.SPARKLE)
                        self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.THROB:
                while True:
                    for level in self.levels:
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.local_queue.empty():
                        break
                    for level in reversed(self.levels): 
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.ENERGIZE: 
                for divisor in [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BLINK: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.BLINK)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.BLINK)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_ON: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    self.upstream_queue.put(self.levels[0], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.TRACE: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_TRACE:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break

class Lights(threading.Thread):
    class group_channels():
        FRUIT_0 = [0,1,2]
        FRUIT_1 = [0,1,2]
        FRUIT_2 = [0,1,2]
        FRUIT_3 = [0,1,2]
        FRUIT_4 =  [0,1,2]
        FRUIT_5 =  [0,1,2]
        ALL_RADIAL = [0,1,2]
        ALL_CLOCKWISE = [0,1,2]

    def __init__(self):
        threading.Thread.__init__(self)
        self.channels = [0]*12
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D5)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=1)
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.tlc5947.create_pwm_out(channel_number)
        self.queue = queue.Queue()
        self.led_groups = {
            "fruit_0": LED_Group(self.group_channels.FRUIT_0, self.queue),
            "fruit_1": LED_Group(self.group_channels.FRUIT_1, self.queue),  
            "fruit_2": LED_Group(self.group_channels.FRUIT_2, self.queue),  
            "fruit_3": LED_Group(self.group_channels.FRUIT_3, self.queue),  
            "fruit_4": LED_Group(self.group_channels.FRUIT_4, self.queue),  
            "dinero": LED_Group(self.group_channels.FRUIT_5, self.queue),  
            "all_radial":LED_Group(self.group_channels.ALL_RADIAL, self.queue),  
            "all_clockwise":LED_Group(self.group_channels.ALL_CLOCKWISE, self.queue),  
        }
    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))
    def run(self):
        while True:
            level, channel_number = self.queue.get(True)
            self.channels[channel_number].duty_cycle = level

class Carousel(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.lights = Lights()
        self.sensor_pins = [0,1,2,3,4,5] # todo: update late
        self.solenoid_pins = [6,7,8,9,10] # todo: update late
        for sensor_pin in self.sensor_pins:
            GPIO.setup(sensor_pin, GPIO.IN)
        for solenoid_pin in self.solenoid_pins:
            GPIO.setup(solenoid_pin, GPIO.OUT)

    def eject_ball(self, fruit_number):
        GPIO.output(self.cs, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.cs, GPIO.LOW)

    def detect_ball(self, fruit_number):
        return GPIO.input(fruit_number)

carousel = Carousel()

################################################
# HARDWARE SEMANTICS (flatter map of callable methods) #
################################################

# carousel class is pretty flat already.  Use as-is.


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

        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.deadman = deadman.Deadman_Switch(self.tb)
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.subscribe_to_topic("connected")
        self.start()

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

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'set_game_mode':
                    self.set_game_mode(message)
                if topic == b'detect_ball':
                    carousel.detect_ball(message)
                if topic == b'eject_ball':
                    carousel.detect_ball(message)
                if topic == b'play_light_animation':
                    carousel.lights.led_groups[message[0]].actions[message[1]]()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()
