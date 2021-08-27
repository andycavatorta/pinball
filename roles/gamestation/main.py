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
import zmq

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
import common.deadman as deadman
from thirtybirds3 import thirtybirds

import roles.gamestation.lighting as lighting

GPIO.setmode(GPIO.BCM)

###########################
# S Y S T E M   T E S T S #
###########################

# Check communication with TLC5947
# Check MPF Bridge
# measure 48V current

#################
# HARDWARE INIT #
#################


"""
launcher GPIOs 
    left: 25
    middle: 7
    right: 8
"""


##################################################
# SAFETY SYSTEMS #
##################################################

# DEADMAN SWITCH ( SEND ANY OUT-OF-BOUNDS VALUES FROM OTHER SYSTEMS)

# COMPUTER STATUS REPORT 

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




##################################################
# HARDWARE SEMANTICS (map of callable methods)#
##################################################

button_lights = {
    "left_flipper":{
        "gpio":None,
        "off":None,
        "on":None,
        "blink":None
    },
    "trade_goods":{
        "gpio":None,
        "off":None,
        "on":None,
        "blink":None
    },
    "start":{
        "gpio":None,
        "off":None,
        "on":None,
        "blink":None
    },
    "trade_money":{
        "gpio":None,
        "off":None,
        "on":None,
        "blink":None
    },
    "right_flipper":{
        "gpio":None,
        "off":None,
        "on":None,
        "blink":None
    },
},
  
launchers = {
    "barter":{
        "launch":None,#(ms)
        "get_count":None,
        "is_count_known":None,
        "is_ball_0_present":None,
        "is_ball_19_present":None,
    },
    "money":{
        "launch":None,#(ms)
        "get_count":None,
        "is_count_known":None,
        "is_ball_0_present":None,
        "is_ball_19_present":None,
    },
    "trough":{
        "launch":None,#(ms)
        "is_ball_present":None,
    },
}

p3roc = {
    "set_log_listener":None,
    "gpios":{
        "trough":None, #local gpio
        "trueque":None, #local gpio
        "dinero":None, #local gpio
    }
    # logging listener?
}



# BUTTONS / BUTTON LIGHTS
    # ADD EVENT LISTENER

# LAUNCHERS



# ROLLOVERS

# SPINNER

# CURRENT SENSOR

# TROUGH BALL SENSOR

# TUBE BALL SENSORS


#############################################
# ROUTINES (time, events, multiple systems) # 
#############################################

class Button_Light():
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    def on(self):
        GPIO.output(pin, GPIO.LOW)
    def off(self):
        GPIO.output(pin, GPIO.HIGH)

#scan all inputs
class Button_Lights():
    def __init__(self):
        self.gpios = [5,6,13,19,26]
        self.izquierda = Button_Light(self.gpios[0])
        self.trueque = Button_Light(self.gpios[1])
        self.comienza = Button_Light(self.gpios[2])
        self.dinero = Button_Light(self.gpios[3])
        self.derecha = Button_Light(self.gpios[4])



class Scan_All_Inputs(threading.Thread):
    def __init__(
            self,
            rollover_handler,
            spinner_handler,
            button_handler,
            trough_sensor_handler,
            pop_bumper_handler,
            slingshot_handler,
        ):
        threading.Thread.__init__()

        GPIO.setup(17, GPIO.IN)
        GPIO.setup(18, GPIO.IN)
        input_value = GPIO.input(17)

        self.inputs = [ # name, gpio, last_state
            ["rollover_outer_left", 0, False],
            ["rollover_inner_left", 0, False],
            ["rollover_inner_right", 0, False],
            ["rollover_outer_right", 0, False],
            ["spinner", 0, False],
            ["trough_Sensor", 0, False],
            ["button_trade_goods", 23, False],
            ["button_start", 18, False],
            ["button_trade_money", 24, False],
        ]
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                for input in self.inputs:
                    time.sleep(1)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))


class MPF_Bridge(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind("tcp://*:5555")

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        print("starting run of mpf bridge")
        while True:
            try:
              message = self.socket.recv()
              print(f"Received msg#: {message}")
              print(type(message))

              self.tb.publish("game_event", message.decode('utf-8'))
              print("Send message")
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("got except90j")
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))



class System_Tests(threading.Thread):
    """
    tests performed:
        read INA260
        write to TLC5947
        read socket messages from P3-ROC
    """
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



class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        #self.safety_enable = Safety_Enable(self.tb)
        self.deadman = deadman.Deadman_Switch(self.tb)
        self.mpf_bridge = MPF_Bridge(self.tb)

        self.button_lights = Button_Lights()

        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("gamestation_all_off")
        self.tb.subscribe_to_topic("gamestation_get_amps")
        self.tb.subscribe_to_topic("get_system_tests")
        self.tb.subscribe_to_topic("button_active_left_flipper")
        self.tb.subscribe_to_topic("button_active_trade_goods")
        self.tb.subscribe_to_topic("button_active_start")
        self.tb.subscribe_to_topic("button_active_trade_money")
        self.tb.subscribe_to_topic("button_active_right_flipper")
        self.tb.subscribe_to_topic("playfield_lights")
        self.tb.subscribe_to_topic("left_stack_launch")
        self.tb.subscribe_to_topic("right_stack_launch")
        self.tb.subscribe_to_topic("left_stack_detect_ball")
        self.tb.subscribe_to_topic("right_stack_detect_ball")
        self.tb.subscribe_to_topic("gutter_detect_ball")
        self.tb.subscribe_to_topic("gutter_launch")
        #self.tb.publish("connected", True)
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
                if topic == b'gamestation_all_off':
                    pass
                if topic == b'gamestation_get_amps':
                    pass
                if topic == b'get_system_tests':
                    pass
                if topic == b'button_active_left_flipper':
                    pass
                if topic == b'button_active_trade_goods':
                    pass
                if topic == b'button_active_start':
                    pass
                if topic == b'button_active_trade_money':
                    pass
                if topic == b'button_active_right_flipper':
                    pass
                if topic == b'playfield_lights':
                    pass
                if topic == b'left_stack_launch':
                    pass
                if topic == b'right_stack_launch':
                    pass
                if topic == b'left_stack_detect_ball':
                    pass
                if topic == b'right_stack_detect_ball':
                    pass
                if topic == b'gutter_detect_ball':
                    pass
                if topic == b'gutter_launch':
                    pass
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

        
        
        
        
        
        
        