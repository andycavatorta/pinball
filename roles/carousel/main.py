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


import roles.carousel.lights.Lights as Lights
import roles.carousel.solenoids.Solenoids as Solenoids


GPIO.setmode(GPIO.BCM)


###########################
# S Y S T E M   T E S T S #
###########################

# Check communication with TLC5947

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
