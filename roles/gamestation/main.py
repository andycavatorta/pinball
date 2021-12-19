"""
===== H A R D W A R E =====

    x playfield sensors
        tube_sensor_left
        tube_sensor_right
        trough_sensor
        spinner
        rollover_outer_left
        rollover_inner_left
        rollover_inner_right
        rollover_outer_right

    x playfield switches
        izquierda
        trueque
        comienza
        dinero
        derecha

        pop_left
        pop_middle
        pop_right
        slingshot_left
        slingshot_right

    # playfield_button_lights

    # playfield LEDs

    Multimorphic / pinball

    current_sensor

===== TOPICS =====

to do:
    response_current_sensor_nominal 
    response_current_sensor_present 
    response_current_sensor_value 
    event_left_stack_ball_present
    event_left_stack_motion_detected
    event_right_stack_ball_present
    event_right_stack_motion_detected
    response_lefttube_present
    response_rightttube_present

topics subscribed:
    cmd_all_off
    cmd_kicker_launch
    cmd_lefttube_launch
    cmd_playfield_lights
    cmd_righttube_launch
    request_button_light_active
    request_button_switch_active
    request_computer_details
    request_current_sensor_nominal
    request_current_sensor_present
    request_current_sensor_value
    request_gutter_ball_detected
    request_lefttube_present
    request_rightttube_present
    request_system_tests
    request_troughsensor_value


topics published:
    connected
    event_gamestation_button
    event_left_stack_ball_present
    event_left_stack_motion_detected
    event_mpf
    event_right_stack_ball_present
    event_right_stack_motion_detected
    event_roll_inner_left
    event_roll_inner_right
    event_roll_outer_left
    event_roll_outer_right
    event_spinner
    event_trough_sensor
    response_computer_details
    response_current_sensor_nominal 
    response_current_sensor_present 
    response_current_sensor_value 
    response_lefttube_present
    response_rightttube_present
    response_troughsensor_value
    response_visual_tests

===== ACTIONS =====

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

    response to topics for tube solenoids and optical sensors

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
request_button_light_active
MONEY_MODE

ENDING

RESET

===== TO DO =====


"""

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
import roles.gamestation.multimorphic as multimorphic
from thirtybirds3 import thirtybirds

import roles.gamestation.lighting as lighting

GPIO.setmode(GPIO.BCM)

###################################
#### B U T T O N  L I G H T S #####
###################################

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
        self.names = {
            "izquierda":self.izquierda,
            "trueque":self.trueque,
            "comienza":self.comienza,
            "dinero":self.dinero,
            "derecha":self.derecha
        }

###########################################
#### P L A Y F I E L D  S E N S O R S #####
###########################################

class GPIO_Input():
    def __init__(self, name, pin, pullupdn, callback):
        self.name = name
        self.pin = pin
        self.callback = callback
        self.previous_state = -1 # so first read changes state and reports to callback
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=pullupdn)
    def detect_change(self):
        new_state = GPIO.input(self.pin)
        if self.previous_state != new_state:
            print(self.name)
            self.previous_state = new_state
            self.callback("event_{}".format(self.name),new_state, self.name, None)
    def get_state(self):
        return [self.name, GPIO.input(self.pin)]

class Playfield_Sensors(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.sensors = [ # name, gpio, last_state
            GPIO_Input("rollover_inner_left", 16, GPIO.PUD_DOWN, callback),
            GPIO_Input("rollover_inner_right", 20, GPIO.PUD_DOWN, callback),
            GPIO_Input("rollover_outer_left", 12, GPIO.PUD_DOWN, callback),
            GPIO_Input("rollover_outer_right", 21, GPIO.PUD_DOWN, callback),
            GPIO_Input("spinner", 1, GPIO.PUD_DOWN, callback),
            GPIO_Input("trough_sensor", 25, GPIO.PUD_DOWN, callback),
            GPIO_Input("tube_sensor_left", 17, GPIO.PUD_UP, callback),
            GPIO_Input("tube_sensor_right", 27, GPIO.PUD_UP, callback),
        ]
        self.queue = queue.Queue()
        self.start()

    def request_lefttube_full(self): 
        self.queue.put("request_lefttube_full")

    def request_righttube_full(self): 
        self.queue.put("request_righttube_full")

    def request_playfield_states(self):
        self.queue.put("request_playfield_states")

    def run(self):
        while True:
            try:
                topic = self.queue.get(True,0.01)
                if topic == "request_lefttube_full":
                    for i in range(4):
                        if self.sensors[6].get_state() == 1:
                            self.callback("response_lefttube_full",False, None, None)
                                continue
                        time.sleep(0.05)
                    self.callback("response_lefttube_full",True, None, None)

                if topic == "request_righttube_full":
                    for i in range(4):
                        if self.sensors[7].get_state() == 1:
                            self.callback("response_righttube_full",False, None, None)
                            continue
                        time.sleep(0.05)
                    self.callback("response_righttube_full",True, None, None)


                if topic == "request_playfield_states":
                    states = []
                    self.sensors
                    for sensor in self.sensors: 
                        states.append(sensor.get_state())
                    self.callback("response_playfield_states",states, None, None)
            except queue.Empty:
                for sensor in self.sensors:
                    sensor.detect_change()
                # time.sleep(0.02)

##################
#### M A I N #####
##################

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
        self.deadman = deadman.Deadman_Switch(self.tb)
        self.gamestation_lights = lighting.Lights()
        self.button_lights = Button_Lights()
        self.multimorphic = multimorphic.Multimorphic(self.add_to_queue)
        self.playfiels_sensors = Playfield_Sensors(self.add_to_queue)
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("cmd_all_off") # to do: finish code
        self.tb.subscribe_to_topic("cmd_enable_derecha_coil")
        self.tb.subscribe_to_topic("cmd_enable_dinero_coil")
        self.tb.subscribe_to_topic("cmd_enable_izquierda_coil")
        self.tb.subscribe_to_topic("cmd_enable_kicker_coil")
        self.tb.subscribe_to_topic("cmd_enable_trueque_coil")
        self.tb.subscribe_to_topic("cmd_kicker_launch") # to do: finish code -  might not be used
        self.tb.subscribe_to_topic("cmd_lefttube_launch")# to do: finish code -  might not be used
        self.tb.subscribe_to_topic("cmd_playfield_lights")
        self.tb.subscribe_to_topic("cmd_set_mode")
        self.tb.subscribe_to_topic("cmd_righttube_launch")# to do: finish code -  might not be used
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("disable_gameplay")
        self.tb.subscribe_to_topic("enable_gameplay")
        self.tb.subscribe_to_topic("event_button_comienza")
        self.tb.subscribe_to_topic("event_button_derecha")
        self.tb.subscribe_to_topic("event_button_dinero")
        self.tb.subscribe_to_topic("event_button_izquierda")
        self.tb.subscribe_to_topic("event_button_trueque")
        self.tb.subscribe_to_topic("event_pop_left")
        self.tb.subscribe_to_topic("event_pop_middle")
        self.tb.subscribe_to_topic("event_pop_right")
        self.tb.subscribe_to_topic("event_roll_inner_left")
        self.tb.subscribe_to_topic("event_roll_inner_right")
        self.tb.subscribe_to_topic("event_roll_outer_left")
        self.tb.subscribe_to_topic("event_roll_outer_right")
        self.tb.subscribe_to_topic("event_slingshot_left")
        self.tb.subscribe_to_topic("event_slingshot_right")
        self.tb.subscribe_to_topic("event_spinner")
        self.tb.subscribe_to_topic("event_trough_sensor")
        self.tb.subscribe_to_topic("event_tube_sensor_left")
        self.tb.subscribe_to_topic("event_tube_sensor_right")
        self.tb.subscribe_to_topic("request_button_light_active")
        self.tb.subscribe_to_topic("request_button_switch_active") # to do: finish code -  this de/activates reactions to buttons
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("request_current_sensor_nominal")
        self.tb.subscribe_to_topic("request_current_sensor_present")
        self.tb.subscribe_to_topic("request_current_sensor_value")
        self.tb.subscribe_to_topic("request_lefttube_full")
        self.tb.subscribe_to_topic("request_righttube_full")
        self.tb.subscribe_to_topic("request_lefttube_present")
        self.tb.subscribe_to_topic("request_rightttube_present")
        self.tb.subscribe_to_topic("request_system_tests")
        self.tb.subscribe_to_topic("request_troughsensor_value")
        self.tb.subscribe_to_topic("request_visual_tests") # not implemented yet
        self.tb.subscribe_to_topic("request_playfield_states")
        self.tb.publish("connected", True)
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
        
    def request_current_sensor_present(self):
        #TODO: Do the ACTUAL tests here.
        return True
        
    def request_current_sensor_value(self):
        #TODO: Do the ACTUAL tests here.
        return 0.0

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
                #print(topic, message, origin, destination)

                try: 
                    topic = topic.decode('UTF-8')
                except AttributeError:
                    pass

                #if topic == 'cmd_all_off':
                #        self.multimorphic.disable_gameplay()

                if topic == 'cmd_enable_derecha_coil':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.enable_derecha(message[0],message[1])

                if topic == 'cmd_enable_dinero_coil':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.enable_dinero(message[0],message[1])

                if topic == 'cmd_enable_izquierda_coil':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.enable_izquierda(message[0],message[1])

                if topic == 'cmd_enable_kicker_coil':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.enable_kicker(message[0],message[1])

                if topic == 'cmd_enable_trueque_coil':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.enable_trueque(message[0],message[1])

                if topic == 'cmd_kicker_launch':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.pulse_coil("kicker",25)
                if topic == 'cmd_lefttube_launch':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.pulse_coil("trueque",25)
                if topic == 'cmd_playfield_lights':
                    if destination == self.tb.get_hostname():
                        group_name, animation_name = message
                        group = self.gamestation_lights.sign_top
                        if group_name == "trail_rollover_right":
                            group = self.gamestation_lights.trail_rollover_right
                        if group_name == "trail_rollover_left":
                            group = self.gamestation_lights.trail_rollover_left
                        if group_name == "trail_sling_right":
                            group = self.gamestation_lights.trail_sling_right
                        if group_name == "trail_sling_left":
                            group = self.gamestation_lights.trail_sling_left
                        if group_name == "trail_pop_left":
                            group = self.gamestation_lights.trail_pop_left
                        if group_name == "trail_pop_right":
                            group = self.gamestation_lights.trail_pop_right
                        if group_name == "trail_pop_middle":
                            group = self.gamestation_lights.trail_pop_middle
                        if group_name == "trail_spinner":
                            group = self.gamestation_lights.trail_spinner
                        if group_name == "pie":
                            group = self.gamestation_lights.pie
                        if group_name == "pie_rollover_right":
                            group = self.gamestation_lights.pie_rollover_right
                        if group_name == "pie_rollover_left":
                            group = self.gamestation_lights.pie_rollover_left
                        if group_name == "pie_sling_right":
                            group = self.gamestation_lights.pie_sling_right
                        if group_name == "pie_sling_left":
                            group = self.gamestation_lights.pie_sling_left
                        if group_name == "pie_pop_left":
                            group = self.gamestation_lights.pie_pop_left
                        if group_name == "pie_pop_right":
                            group = self.gamestation_lights.pie_pop_right
                        if group_name == "pie_pop_middle":
                            group = self.gamestation_lights.pie_pop_middle
                        if group_name == "pie_spinner":
                            group = self.gamestation_lights.pie_spinner
                        if group_name == "sign_arrow_left":
                            group = self.gamestation_lights.sign_arrow_left
                        if group_name == "sign_bottom_right":
                            group = self.gamestation_lights.sign_bottom_right
                        if group_name == "sign_bottom_left":
                            group = self.gamestation_lights.sign_bottom_left
                        if group_name == "sign_top":
                            group = self.gamestation_lights.sign_top
                        if group_name == "all_radial":
                            group = self.gamestation_lights.all_radial

                        if group_name == "ripple_1":
                            group = self.gamestation_lights.ripple_1
                        if group_name == "ripple_2":
                            group = self.gamestation_lights.ripple_2
                        if group_name == "ripple_3":
                            group = self.gamestation_lights.ripple_3
                        if group_name == "ripple_4":
                            group = self.gamestation_lights.ripple_4
                        if group_name == "ripple_5":
                            group = self.gamestation_lights.ripple_5
                        if group_name == "ripple_6":
                            group = self.gamestation_lights.ripple_6
                        if group_name == "ripple_7":
                            group = self.gamestation_lights.ripple_7
                        if group_name == "ripple_8":
                            group = self.gamestation_lights.ripple_8
                        if group_name == "ripple_9":
                            group = self.gamestation_lights.ripple_9
                        if group_name == "ripple_10":
                            group = self.gamestation_lights.ripple_10
                        if group_name == "ripple_11":
                            group = self.gamestation_lights.ripple_11
                        if group_name == "ripple_12":
                            group = self.gamestation_lights.ripple_12
                        if group_name == "ripple_13":
                            group = self.gamestation_lights.ripple_13
                        if group_name == "ripple_14":
                            group = self.gamestation_lights.ripple_14
                        if group_name == "ripple_15":
                            group = self.gamestation_lights.ripple_15
                        if group_name == "ripple_16":
                            group = self.gamestation_lights.ripple_16
                        if group_name == "ripple_17":
                            group = self.gamestation_lights.ripple_17
                        if group_name == "ripple_18":
                            group = self.gamestation_lights.ripple_18

                        if animation_name == "off":
                            group.off()
                        if animation_name == "on":
                            group.on()
                        if animation_name == "low":
                            group.low()
                        if animation_name == "med":
                            group.med()
                        if animation_name == "high":
                            group.high()
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
                        if animation_name == "single_dot":
                            group.single_dot()
                        if animation_name == "wink":
                            group.wink()

                if topic == 'cmd_set_mode': # this might not get used
                    pass
                if topic == 'cmd_righttube_launch':
                    if destination == self.tb.get_hostname():
                        self.multimorphic.pulse_coil("dinero",25)
                if topic == 'connected':
                    pass
                #if topic == 'disable_gameplay':
                #    if destination == self.tb.get_hostname():
                #        self.multimorphic.disable_gameplay()
                #if topic == 'enable_gameplay':
                #    if destination == self.tb.get_hostname():
                #        self.multimorphic.enable_gameplay()
                if topic == 'event_button_comienza':
                    self.tb.publish(
                        topic="event_button_comienza",
                        message=True if message=="closed" else False
                    )
                if topic == 'event_button_derecha':
                    self.tb.publish(
                        topic="event_button_derecha",
                        message=True if message=="closed" else False
                    )
                if topic == 'event_button_dinero':
                    self.tb.publish(
                        topic="event_button_dinero",
                        message=True if message=="closed" else False
                    )
                if topic == 'event_button_izquierda':
                    self.tb.publish(
                        topic="event_button_izquierda",
                        message=True if message=="closed" else False
                    )
                if topic == 'event_button_trueque':
                    self.tb.publish(
                        topic="event_button_trueque",
                        message=True if message=="closed" else False
                    )
                if topic == 'event_pop_left':
                    self.tb.publish(
                        topic="event_pop_left",
                        message=True
                    )
                if topic == 'event_pop_middle':
                    self.tb.publish(
                        topic="event_pop_middle",
                        message=True
                    )
                if topic == 'event_pop_right':
                    self.tb.publish(
                        topic="event_pop_right",
                        message=True
                    )
                if topic == 'event_rollover_inner_left':
                    self.tb.publish(
                        topic="event_roll_inner_left",
                        message=True
                    )
                if topic == 'event_rollover_inner_right':
                    self.tb.publish(
                        topic="event_roll_inner_right",
                        message=True
                    )
                if topic == 'event_rollover_outer_left':
                    self.tb.publish(
                        topic="event_roll_outer_left",
                        message=True
                    )
                if topic == 'event_rollover_outer_right':
                    self.tb.publish(
                        topic="event_roll_outer_right",
                        message=True
                    )
                if topic == 'event_slingshot_left':
                    self.tb.publish(
                        topic="event_slingshot_left",
                        message=True
                    )
                if topic == 'event_slingshot_right':
                    self.tb.publish(
                        topic="event_slingshot_right",
                        message=True
                    )
                if topic == 'event_spinner':
                    self.tb.publish(
                        topic="event_spinner",
                        message=True
                    )
                if topic == 'event_trough_sensor':
                    self.tb.publish(
                        topic="event_trough_sensor",
                        message=True
                    )
                if topic == 'event_tube_sensor_left':
                    self.tb.publish(
                        topic="event_tube_sensor_left",
                        message=message
                    )
                if topic == 'event_tube_sensor_right':
                    self.tb.publish(
                        topic="event_tube_sensor_right",
                        message=message
                    )
                if topic == 'request_button_light_active':
                    if destination == self.tb.get_hostname():
                        button_name, button_state = message
                        if button_state:
                            #print("if topic == 'request_button_light_active'",button_state)
                            self.button_lights.names[button_name].on()
                        else:
                            self.button_lights.names[button_name].off()
                    
                if topic == 'request_button_switch_active': # this might be subsumed by en/disable_gameplay
                    pass
                if topic == 'request_computer_details':
                    self.tb.publish(
                        topic="response_computer_details", 
                        message=self.request_computer_details()
                    )
                if topic == 'request_current_sensor_nominal':
                    self.tb.publish(
                        topic="response_current_sensor_nominal",
                        message=self.request_current_sensor_nominal()
                    )
                if topic == 'request_current_sensor_present':
                    self.tb.publish(
                        topic="response_current_sensor_present",
                        message=self.request_current_sensor_present()
                    )
                if topic == 'request_current_sensor_value':
                    self.tb.publish(
                        topic="response_current_sensor_value",
                        message=self.request_current_sensor_value()
                    )


                if topic == 'request_lefttube_full':
                    self.playfiels_sensors.request_lefttube_full()
                if topic == 'request_righttube_full':
                    self.playfiels_sensors.request_righttube_full()



                if topic == 'request_lefttube_present':
                    if destination == self.tb.get_hostname():
                        self.tb.publish(
                            topic="response_lefttube_present",
                            message=True
                        )
                if topic == 'request_rightttube_present':
                    if destination == self.tb.get_hostname():
                        self.tb.publish(
                            topic="response_rightttube_present",
                            message=True
                        )
                if topic == 'request_system_tests':
                    if destination == self.tb.get_hostname():
                        self.tb.publish(
                            topic="response_system_tests",
                            message=True
                        )
                if topic == 'request_troughsensor_value':
                    pass
                if topic == 'request_visual_tests':
                    pass
                if topic == 'request_playfield_states':
                    self.playfiels_sensors.request_playfield_states()
                if topic == 'response_playfield_states':
                    self.tb.publish(
                        topic="response_playfield_states",
                        message=message
                    )

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()
