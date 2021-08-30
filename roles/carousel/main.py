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

from roles.carousel.lights import Lights as Lights
from roles.carousel.solenoids import Solenoids as Solenoids

import roles.carousel.fade_led_test

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
        self.solenoids = Solenoids()
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("carousel_all_off")
        self.tb.subscribe_to_topic("carousel_detect_ball")
        self.tb.subscribe_to_topic("carousel_get_amps")
        self.tb.subscribe_to_topic("carousel_lights")
        self.tb.subscribe_to_topic("eject_ball")
        self.tb.subscribe_to_topic("get_system_tests")
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
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'carousel_all_off':
                    self.solenoids.add_to_queue('all_off', None) 
                if topic == b'carousel_detect_ball':
                    pass
                if topic == b'carousel_get_amps':
                    pass
                if topic == b'carousel_lights':
                    pass
                if topic == b'eject_ball':
                    self.solenoids.add_to_queue('eject_ball', message) # message is fruit_id between 0 and 4
                if topic == b'get_system_tests':
                    pass
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()
