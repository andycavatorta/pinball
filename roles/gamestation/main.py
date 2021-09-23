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

"""
actions for this module:

WAITING_FOR_CONNECTIONS:
    find controller and connect

SYSTEM_TESTS"
    subscribe to test topics
    perform tests
    playfield light animations
    button animations
    solenoid tests

INVENTORY
    subscribe to inventory topics
    request_fruit_tube_sensor
    cmd_fruit_tube_launch

    respond to topics for tube solenoids and optical sensors

ATTRACTION
    play animations on playfield
    play button animation 
    use solenoids for percussion?

COUNTDOWN
    play animations on playfield
    play button animation 
    use solenoids for percussion?

BARTER_MODE_INTRO


BARTER_MODE
MONEY_MODE_INTRO
MONEY_MODE
ENDING

RESET
    

ERROR = "error"







"""


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
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        #print(self.pin, GPIO.LOW)
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        #print(self.pin, GPIO.HIGH)

#scan all inputs
class Button_Lights():
    def __init__(self):
        self.gpios = [5,6,13,19,26]
        self.izquierda = Button_Light(self.gpios[0])
        self.trueque = Button_Light(self.gpios[1])
        self.comienza = Button_Light(self.gpios[2])
        self.dinero = Button_Light(self.gpios[3])
        self.derecha = Button_Light(self.gpios[4])

def rollover_handler(name, value):
    print("rollover_handler",name, value)
    if name == "rollover_outer_left":
        main.publish_to_controller("event_roll_outer_left", value)
        if value == 1:
            main.gamestation_lights.pie_rollover_left.on()
        else:
            main.gamestation_lights.pie_rollover_left.off()

    if name == "rollover_inner_left":
        main.publish_to_controller("event_roll_inner_left", value)
        if value == 1:
            main.gamestation_lights.pie_rollover_left.on()
        else:
            main.gamestation_lights.pie_rollover_left.off()

    if name == "rollover_inner_right":
        main.publish_to_controller("event_roll_inner_right", value)
        if value == 1:
            main.gamestation_lights.pie_rollover_right.on()
        else:
            main.gamestation_lights.pie_rollover_right.off()

    if name == "rollover_outer_right":
        main.publish_to_controller("event_roll_outer_right", value)
        if value == 1:
            main.gamestation_lights.pie_rollover_right.on()
        else:
            main.gamestation_lights.pie_rollover_right.off()

def spinner_handler(name, value):
    if name == "spinner":
        main.publish_to_controller("event_spinner", value)

def trough_sensor_handler(name, value):
    main.publish_to_controller("event_trough_sensor", value)
    if value == True:
        main.button_lights.comienza.on()
    else:
        main.button_lights.comienza.off()

def button_handler(name, value):
    main.publish_to_controller(self, name, value)





class GPIO_Input():
    def __init__(self, name, pin, callback):
        self.name = name
        self.pin = pin
        self.callback = callback
        self.previous_state = -1 # so first read changes state and reports to callback
        GPIO.setup(self.pin, GPIO.IN)
    def scan(self):
        new_state = GPIO.input(self.pin)
        #if self.name == "rollover_outer_left":
        #    print(new_state) 
        if self.previous_state != new_state:
            print(self.name)
            self.previous_state = new_state
            self.callback(self.name,new_state)

class Scan_GPIO_Inputs(threading.Thread):
    def __init__(
            self,
            rollover_handler,
            spinner_handler,
            trough_sensor_handler
        ):
        threading.Thread.__init__(self)

        self.inputs = [ # name, gpio, last_state
            GPIO_Input("rollover_outer_left", 12, rollover_handler),
            GPIO_Input("rollover_inner_left", 16, rollover_handler),
            GPIO_Input("rollover_inner_right", 20, rollover_handler),
            GPIO_Input("rollover_outer_right", 21, rollover_handler),
            GPIO_Input("spinner", 1, spinner_handler),
            GPIO_Input("trough_sensor", 25, trough_sensor_handler),
        ]
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                for input in self.inputs:
                    input.scan()
                time.sleep(0.01)
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
              self.tb.publish("respond_mpf_event", eval(message.decode('utf-8')))
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


        self.gamestation_lights = lighting.Lights()

        self.button_lights = Button_Lights()

        self.queue = queue.Queue()

        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("respond_high_power_enabled")
        self.tb.subscribe_to_topic("request_system_tests")
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("respond_current_sensor_present")
        self.tb.subscribe_to_topic("respond_current_sensor_value")
        self.tb.subscribe_to_topic("request_current_sensor_nominal")
        self.tb.subscribe_to_topic("request_visual_tests")

        # old ones that need to be checked and/or updated
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
    
    def publish_to_controller(self, topic, message):
        self.tb.publish(topic, message)

    def request_computer_details(self):
        return {
            "df":self.tb.get_system_disk(),
            "cpu_temp":self.tb.get_core_temp(),
            "pinball_git_timestamp":self.tb.app_get_git_timestamp(),
            "tb_git_timestamp":self.tb.tb_get_git_timestamp(),
        }
        
    def request_current_sensor_nominal(self):
        #TODO: Do the ACTUAL tests here.
        return True

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
                if topic == b'request_computer_details':
                    self.tb.publish(
                        topic="respond_computer_details", 
                        message=self.request_computer_details()
                    )
                if topic == b'request_current_sensor_nominal':
                    self.tb.publish(
                        topic="respond_current_sensor_nominal",
                        message=self.request_current_sensor_nominal()
                    )
                if topic == b'gamestation_all_off':
                    pass
                if topic == b'gamestation_get_amps':
                    pass
                if topic == b'get_system_tests':
                    pass
                if topic == b'button_active_left_flipper':
                    if destination == self.tb.get_hostname():
                        if message == True:
                            main.button_lights.izquierda.on()
                        else:
                            main.button_lights.izquierda.off()
                if topic == b'button_active_trade_goods':
                    if destination == self.tb.get_hostname():
                        if message == True:
                            main.button_lights.trueque.on()
                        else:
                            main.button_lights.trueque.off()
                if topic == b'button_active_start':
                    if destination == self.tb.get_hostname():
                        if message == True:
                            main.button_lights.comienza.on()
                        else:
                            main.button_lights.comienza.off()
                if topic == b'button_active_trade_money':
                    if destination == self.tb.get_hostname():
                        if message == True:
                            main.button_lights.dinero.on()
                        else:
                            main.button_lights.dinero.off()
                if topic == b'button_active_right_flipper':
                    if destination == self.tb.get_hostname():
                        if message == True:
                            main.button_lights.derecha.on()
                        else:
                            main.button_lights.derecha.off()
                if topic == b'playfield_lights':
                    if destination == self.tb.get_hostname():
                        group_name, animation_name = message
                        group = self.gamestation_lights.sign_top
                        if group_name = "trail_rollover_right":
                            group = self.gamestation_lights.trail_rollover_right
                        if group_name = "trail_rollover_right":
                            group = self.gamestation_lights.trail_rollover_right
                        if group_name = "trail_rollover_left":
                            group = self.gamestation_lights.trail_rollover_left
                        if group_name = "trail_sling_right":
                            group = self.gamestation_lights.trail_sling_right
                        if group_name = "trail_sling_left":
                            group = self.gamestation_lights.trail_sling_left
                        if group_name = "trail_pop_left":
                            group = self.gamestation_lights.trail_pop_left
                        if group_name = "trail_pop_right":
                            group = self.gamestation_lights.trail_pop_right
                        if group_name = "trail_pop_center":
                            group = self.gamestation_lights.trail_pop_center
                        if group_name = "trail_spinner":
                            group = self.gamestation_lights.trail_spinner
                        if group_name = "pie_rollover_right":
                            group = self.gamestation_lights.pie_rollover_right
                        if group_name = "pie_rollover_left":
                            group = self.gamestation_lights.pie_rollover_left
                        if group_name = "pie_sling_right":
                            group = self.gamestation_lights.pie_sling_right
                        if group_name = "pie_sling_left":
                            group = self.gamestation_lights.pie_sling_left
                        if group_name = "pie_pop_left":
                            group = self.gamestation_lights.pie_pop_left
                        if group_name = "pie_pop_right":
                            group = self.gamestation_lights.pie_pop_right
                        if group_name = "pie_pop_center":
                            group = self.gamestation_lights.pie_pop_center
                        if group_name = "pie_spinner":
                            group = self.gamestation_lights.pie_spinner
                        if group_name = "sign_arrow_left":
                            group = self.gamestation_lights.sign_arrow_left
                        if group_name = "sign_bottom_right":
                            group = self.gamestation_lights.sign_bottom_right
                        if group_name = "sign_top":
                            group = self.gamestation_lights.sign_top

                        if animation_name == "off":
                            group.off()
                        if animation_name == "on":
                            group.on()
                        if animation_name == "sparkle":
                            group.sparkle()
                        if animation_name == "throb":
                            group.throb()
                        if animation_name == "energize":
                            group.energize()
                        if animation_name == "blink":
                            group.blink()
                        if animation_name == "stroke_on":
                            group.stroke_on()
                        if animation_name == "stroke_off":
                            group.stroke_off()
                        if animation_name == "back_stroke_on":
                            group.back_stroke_on()
                        if animation_name == "back_stroke_off":
                            group.back_stroke_off()
                        if animation_name == "trace":
                            group.trace()
                        if animation_name == "back_trace":
                            group.back_trace()

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

        
scan_gpio_inputs = Scan_GPIO_Inputs(
    rollover_handler,
    spinner_handler,
    trough_sensor_handler,
)
"""
while True:
    time.sleep(0.2)
    main.button_lights.izquierda.off()
    main.button_lights.trueque.on()
    time.sleep(0.2)
    main.button_lights.trueque.off()
    main.button_lights.comienza.on()
    time.sleep(0.2)
    main.button_lights.comienza.off()
    main.button_lights.dinero.on()
    time.sleep(0.2)
    main.button_lights.dinero.off()
    main.button_lights.derecha.on()
    time.sleep(0.2)
    main.button_lights.derecha.off()
    main.button_lights.dinero.on()
    time.sleep(0.2)
    main.button_lights.dinero.off()
    main.button_lights.comienza.on()
    time.sleep(0.2)
    main.button_lights.comienza.off()
    main.button_lights.trueque.on()
    time.sleep(0.2)
    main.button_lights.trueque.off()
    main.button_lights.izquierda.on()
    time.sleep(0.2)
"""
        
        
        
        
        