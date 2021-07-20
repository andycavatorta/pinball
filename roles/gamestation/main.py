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
from thirtybirds3 import thirtybirds

GPIO.setmode(GPIO.BCM)


#################
# HARDWARE INIT #
#################

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
        TRAIL_ROLLOVER_RIGHT = [0,1,2]
        TRAIL_ROLLOVER_LEFT = [0,1,2]
        TRAIL_SLING_RIGHT = [0,1,2]
        TRAIL_SLING_LEFT = [0,1,2]
        TRAIL_POP_LEFT =  [0,1,2]
        TRAIL_POP_RIGHT =  [0,1,2]
        TRAIL_POP_CENTER = [0,1,2]
        TRAIL_SPINNER = [0,1,2]
        PIE_ROLLOVER_RIGHT = [0,1,2]
        PIE_ROLLOVER_LEFT = [0,1,2]
        PIE_SLING_RIGHT = [0,1,2]
        PIE_SLING_LEFT = [0,1,2]
        PIE_POP_LEFT =  [0,1,2]
        PIE_POP_RIGHT =  [0,1,2]
        PIE_POP_CENTER = [0,1,2]
        PIE_SPINNER = [0,1,2]
        SIGN_ARROW_LEFT = [0,1,2]
        SIGN_ARROW_RIGHT = [0,1,2]
        SIGN_BOTTOM_LEFT = [0,1,2]
        SIGN_BOTTOM_RIGHT = [0,1,2]
        SIGN_TOP = [0,1,2]
        ALL_RADIAL = [0,1,2]
        ALL_CLOCKWISE = [0,1,2]

    def __init__(self):
        threading.Thread.__init__()
        self.channels = [0]*72
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D5)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=3)
        
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.create_pwm_out(channel_number)

        self.queue = queue.Queue()
        self.trail_rollover_right = Lights_Pattern(self.pattern_channels.TRAIL_ROLLOVER_RIGHT, self.queue)
        self.trail_rollover_left = Lights_Pattern(self.pattern_channels.TRAIL_ROLLOVER_LEFT, self.queue)
        self.trail_sling_right = Lights_Pattern(self.pattern_channels.TRAIL_SLING_RIGHT, self.queue)
        self.trail_sling_left = Lights_Pattern(self.pattern_channels.TRAIL_SLING_LEFT, self.queue)
        self.trail_pop_left = Lights_Pattern(self.pattern_channels.TRAIL_POP_LEFT, self.queue)
        self.trail_pop_right = Lights_Pattern(self.pattern_channels.TRAIL_POP_RIGHT, self.queue)
        self.trail_pop_center = Lights_Pattern(self.pattern_channels.TRAIL_POP_CENTER, self.queue)
        self.trail_spinner = Lights_Pattern(self.pattern_channels.TRAIL_SPINNER, self.queue)
        self.pie_rollover_right = Lights_Pattern(self.pattern_channels.PIE_ROLLOVER_RIGHT, self.queue)
        self.pie_rollover_left = Lights_Pattern(self.pattern_channels.PIE_ROLLOVER_LEFT, self.queue)
        self.pie_sling_right = Lights_Pattern(self.pattern_channels.PIE_SLING_RIGHT, self.queue)
        self.pie_sling_left = Lights_Pattern(self.pattern_channels.PIE_SLING_LEFT, self.queue)
        self.pie_pop_left = Lights_Pattern(self.pattern_channels.PIE_POP_LEFT, self.queue)
        self.pie_pop_right = Lights_Pattern(self.pattern_channels.PIE_POP_RIGHT, self.queue)
        self.pie_pop_center = Lights_Pattern(self.pattern_channels.PIE_POP_CENTER, self.queue)
        self.pie_spinner = Lights_Pattern(self.pattern_channels.PIE_SPINNER, self.queue)
        self.sign_arrow_left = Lights_Pattern(self.pattern_channels.SIGN_ARROW_LEFT, self.queue)
        self.sign_bottom_right = Lights_Pattern(self.pattern_channels.SIGN_BOTTOM_RIGHT, self.queue)
        self.sign_top = Lights_Pattern(self.pattern_channels.SIGN_TOP, self.queue)
        self.all_radial = Lights_Pattern(self.pattern_channels.ALL_RADIAL, self.queue)
        self.all_clockwise = Lights_Pattern(self.pattern_channels.ALL_CLOCKWISE, self.queue)

    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))

    def run(self):
        while True:
            level, channel_number = self.queue.get(True)
            self.channels[channel_number].duty_cycle = level

lights = Lights()


"""
pinball light GPIOs 1, 12, 16, 20, 21
? assume left-to-right?
"""

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

"""
lights.trail_rollover_right.off()
lights.trail_rollover_right.on()
lights.trail_rollover_right.sparkle()
lights.trail_rollover_right.throb()
lights.trail_rollover_right.energize()
lights.trail_rollover_right.blink()
lights.trail_rollover_right.stroke_on()
lights.trail_rollover_right.stroke_off()
lights.trail_rollover_right.back_stroke_on()
lights.trail_rollover_right.back_stroke_off()
lights.trail_rollover_right.trace()
lights.trail_rollover_right.back_trace()

lights.trail_rollover_left  ...
lights.trail_sling_right  ...
lights.trail_sling_left  ...
lights.trail_pop_left  ...
lights.trail_pop_right  ...
lights.trail_pop_center  ...
lights.trail_spinner  ...
lights.pie_rollover_right  ...
lights.pie_rollover_left  ...
lights.pie_sling_right  ...
lights.pie_sling_left  ...
lights.pie_pop_left  ...
lights.pie_pop_right  ...
lights.pie_pop_center  ...
lights.pie_spinner  ...
lights.sign_arrow_left  ...
lights.sign_bottom_right  ...
lights.sign_top  ...
lights.all_radial ...
lights.all_clockwise ...

"""

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

#scan all inputs


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
        GPIO.setup(18, GPIO.OUT)
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

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))


scan_all_inputs = Scan_All_Inputs(
            rollover_handler,
            spinner_handler,
            button_handler,
            trough_sensor_handler,
            pop_bumper_handler,
            slingshot_handler
        )






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
        self.safety_enable = Safety_Enable(self.tb)
        self.mpf_bridge = MPF_Bridge(self.tb)

        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.publish("connected", True)
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
            self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
            pass # peripheral power should be off during this mode
        if mode == self.game_modes.RESET:
            self.game_mode = self.game_modes.RESET
            self.mpf_bridge.set_game_mode = self.game_modes.RESET
            time.sleep(6)
            self.tb.publish("ready_state",True)

        if mode == self.game_modes.ATTRACTION:
            self.game_mode = self.game_modes.ATTRACTION
        # waits for press of start button 

        if mode == self.game_modes.COUNTDOWN:
            #self.player.play("countdown_mode")
            print("In countdown")
        """
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

main = Main()

