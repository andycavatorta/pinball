"""
topics subscribed:
    request_carousel_detect_ball
    request_solenoids_present
    cmd_carousel_eject_ball
    cmd_carousel_lights
    request_carousel_all_off

    request_computer_details
    request_system_tests
    connected

topics published:
    event_carousel_ball_detected
    response_carousel_ball_detected

    connected
    deadman
    response_computer_details
    response_visual_tests

to do: 
    add callback to Solenoids for change in ball detection
    request_solenoids_present
    request_carousel_detect_ball

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

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds
#from thirtybirds3.adapters.actuators import roboteq_command_wrapper
#from thirtybirds3.adapters.sensors.AMT203_encoder import AMT203_absolute_encoder
import common.deadman as deadman

# CENTER CAROUSEL HACK BEGIN ---
# Get my hostname
import socket
MY_HOSTNAME = socket.gethostname()
# Import special module if I am the central carousel, or normal module if not
if MY_HOSTNAME == "carouselcenter":
    import roles.carousel.lighting_center as lighting
else:
    import roles.carousel.lighting as lighting
# --- CENTER CAROUSEL HACK END

from roles.carousel.solenoids import Solenoids as Solenoids

GPIO.setmode(GPIO.BCM)

###########################################
#### P L A Y F I E L D  S E N S O R S #####
###########################################

class GPIO_Input():
    def __init__(self, name, pin, tb):
        self.name = name
        self.pin = pin
        self.tb = tb
        self.previous_state = -1 # so first read changes state and reports to tb
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    def detect_change(self):
        new_state = GPIO.input(self.pin)
        if self.previous_state != new_state:
            self.previous_state = new_state
            self.tb.publish("event_carousel_ball_detected",{self.name:new_state})
    def get_state(self):
        return [self.name, GPIO.input(self.pin)]

class Inductive_Sensors(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.tb = tb
        self.sensors = [ # name, gpio, last_state
            GPIO_Input("coco", 14, tb),
            GPIO_Input("naranja", 15, tb),
            GPIO_Input("mango", 18, tb),
            GPIO_Input("sandia", 23, tb),
            GPIO_Input("pina", 24, tb),
        ]
        self.queue = queue.Queue()
        self.start()
    def response_carousel_detect_balls(self):
        self.queue.put(True)
    def run(self):
        while True:
            try:
                self.queue.get(True,0.1)
                states = {}
                for sensor in self.sensors:
                    states[sensor.name] = sensor.get_state()
                self.tb.publish("response_carousel_detect_balls",states)
            except queue.Empty:
                for sensor in self.sensors:
                    sensor.detect_change()
                time.sleep(0.1)

##################
#### M A I N #####
##################

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
        self.lighting = lighting.Lights()
        self.inductive_sensors = Inductive_Sensors(self.tb)
        self.tb.subscribe_to_topic("cmd_carousel_all_off")
        self.tb.subscribe_to_topic("cmd_carousel_eject_ball")
        self.tb.subscribe_to_topic("cmd_carousel_lights")
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("request_carousel_detect_balls")
        self.tb.subscribe_to_topic("request_computer_details")
        self.tb.subscribe_to_topic("request_solenoids_present")
        self.tb.subscribe_to_topic("request_system_tests")
        self.start()

    def request_system_tests(self):
        # computer details
        self.tb.publish(
            topic="response_computer_details", 
            message=self.request_computer_details()
        )

    def request_computer_details(self):
        return {
            "df":self.tb.get_system_disk(),
            "cpu_temp":self.tb.get_core_temp(),
            "pinball_git_timestamp":self.tb.app_get_git_timestamp(),
            "tb_git_timestamp":self.tb.tb_get_git_timestamp(),
        }

    def request_solenoids_present(self):
            # to do: finish
            return [True,True,True,True,True]

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
                if topic == b'cmd_carousel_all_off':
                    self.solenoids.add_to_queue('all_off', None) 
                if topic == b'cmd_carousel_eject_ball':
                    if destination == self.tb.get_hostname():
                        self.solenoids.add_to_queue('eject', message) # message fruit name

                if topic == b'cmd_carousel_lights':
                    if destination == self.tb.get_hostname():
                        print("topic, message, origin, destination",topic, message, origin, destination)
                        group_name, animation_name = message
                        if group_name == "all":
                            group = self.lighting.all
                        if group_name == "peso":
                            group = self.lighting.peso
                        if group_name == "coco":
                            group = self.lighting.coco
                        if group_name == "naranja":
                            group = self.lighting.naranja
                        if group_name == "mango":
                            group = self.lighting.mango
                        if group_name == "sandia":
                            group = self.lighting.sandia
                        if group_name == "pina":
                            group = self.lighting.pina
                        if group_name == "spoke_1":
                            group = self.lighting.spoke_1
                        if group_name == "spoke_2":
                            group = self.lighting.spoke_2
                        if group_name == "spoke_3":
                            group = self.lighting.spoke_3
                        if group_name == "spoke_4":
                            group = self.lighting.spoke_4
                        if group_name == "spoke_5":
                            group = self.lighting.spoke_5
                        if group_name == "spoke_6":
                            group = self.lighting.spoke_6
                        if group_name == "spoke_7":
                            group = self.lighting.spoke_7
                        if group_name == "spoke_8":
                            group = self.lighting.spoke_8
                        if group_name == "spoke_9":
                            group = self.lighting.spoke_9
                        if group_name == "spoke_10":
                            group = self.lighting.spoke_10
                        if group_name == "inner_circle":
                            group = self.lighting.inner_circle
                        if group_name == "outer_circle":
                            group = self.lighting.outer_circle
                        if group_name == "ripple_coco_1":
                            group = self.lighting.ripple_coco_1
                        if group_name == "ripple_naranja_1":
                            group = self.lighting.ripple_naranja_1
                        if group_name == "ripple_mango_1":
                            group = self.lighting.ripple_mango_1
                        if group_name == "ripple_sandia_1":
                            group = self.lighting.ripple_sandia_1
                        if group_name == "ripple_pina_1":
                            group = self.lighting.ripple_pina_1
                        if group_name == "ripple_coco_2":
                            group = self.lighting.ripple_coco_2
                        if group_name == "ripple_naranja_2":
                            group = self.lighting.ripple_naranja_2
                        if group_name == "ripple_mango_2":
                            group = self.lighting.ripple_mango_2
                        if group_name == "ripple_sandia_2":
                            group = self.lighting.ripple_sandia_2
                        if group_name == "ripple_pina_2":
                            group = self.lighting.ripple_pina_2
                        if group_name == "ripple_coco_3":
                            group = self.lighting.ripple_coco_3
                        if group_name == "ripple_naranja_3":
                            group = self.lighting.ripple_naranja_3
                        if group_name == "ripple_mango_3":
                            group = self.lighting.ripple_mango_3
                        if group_name == "ripple_sandia_3":
                            group = self.lighting.ripple_sandia_3
                        if group_name == "ripple_pina_3":
                            group = self.lighting.ripple_pina_3
                        if group_name == "ripple_coco_4":
                            group = self.lighting.ripple_coco_4
                        if group_name == "ripple_naranja_4":
                            group = self.lighting.ripple_naranja_4
                        if group_name == "ripple_mango_4":
                            group = self.lighting.ripple_mango_4
                        if group_name == "ripple_sandia_4":
                            group = self.lighting.ripple_sandia_4
                        if group_name == "ripple_pina_4":
                            group = self.lighting.ripple_pina_4
                        if group_name == "ripple_coco_5":
                            group = self.lighting.ripple_coco_5
                        if group_name == "ripple_naranja_5":
                            group = self.lighting.ripple_naranja_5
                        if group_name == "ripple_mango_5":
                            group = self.lighting.ripple_mango_5
                        if group_name == "ripple_sandia_5":
                            group = self.lighting.ripple_sandia_5
                        if group_name == "ripple_pina_5":
                            group = self.lighting.ripple_pina_5

                        if group_name == "serpentine_edge_coco":
                            group = self.lighting.serpentine_edge_coco
                        if group_name == "serpentine_edge_naranja":
                            group = self.lighting.serpentine_edge_naranja
                        if group_name == "serpentine_edge_mango":
                            group = self.lighting.serpentine_edge_mango
                        if group_name == "serpentine_edge_sandia":
                            group = self.lighting.serpentine_edge_sandia
                        if group_name == "serpentine_edge_pina":
                            group = self.lighting.serpentine_edge_pina

                        if group_name == "serpentine_center_coco":
                            group = self.lighting.serpentine_center_coco
                        if group_name == "serpentine_center_naranja":
                            group = self.lighting.serpentine_center_naranja
                        if group_name == "serpentine_center_mango":
                            group = self.lighting.serpentine_center_mango
                        if group_name == "serpentine_center_sandia":
                            group = self.lighting.serpentine_center_sandia
                        if group_name == "serpentine_center_pina":
                            group = self.lighting.serpentine_center_pina

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

                        if animation_name == "serpentine_edge":
                            group.serpentine_edge()
                        if animation_name == "serpentine_center":
                            group.serpentine_center()

                if topic == b'request_carousel_detect_balls':
                    self.inductive_sensors.response_carousel_detect_balls()
                if topic == b'request_computer_details':
                    self.tb.publish(
                        topic="response_computer_details", 
                        message=self.request_computer_details()
                    )
                if topic == b'request_solenoids_present':
                    self.tb.publish(
                        topic="response_solenoids_present", 
                        message=self.request_solenoids_present()
                    )
                if topic == b'request_system_tests':
                    self.request_system_tests()

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

