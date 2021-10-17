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
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.sensors.AMT203_encoder import AMT203_absolute_encoder
import common.deadman as deadman

import roles.carousel.lighting as lighting
from roles.carousel.solenoids import Solenoids as Solenoids

from roles.carousel import fade_led_test

GPIO.setmode(GPIO.BCM)

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
        self.lighting = lighting
        self.tb.subscribe_to_topic("cmd_carousel_all_off")
        self.tb.subscribe_to_topic("cmd_carousel_eject_ball")
        self.tb.subscribe_to_topic("cmd_carousel_lights")
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("request_carousel_detect_ball")
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

    def request_carousel_detect_ball(self):
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
                print(topic, message)
                if topic == b'cmd_carousel_all_off':
                    self.solenoids.add_to_queue('all_off', None) 
                print(2, topic, message)
                if topic == b'cmd_carousel_eject_ball':
                    if destination == self.tb.get_hostname():
                        self.solenoids.add_to_queue('eject', message) # message fruit name
                print(3,topic, message)

                if topic == b'cmd_carousel_lights':
                    print(self.tb.get_hostname())
                    if destination == self.tb.get_hostname():
                        animation_name, group, params = message
                        print(animation_name, group, params)
                        if animation_name == "stroke_ripple":
                            print("---1")
                            self.lighting.stroke_ripple()
                        if animation_name in [b"solid","solid"]:
                            print("---2")
                            self.lighting.solid(group, params)
                print(4 ,topic, message)
                if topic == b'request_carousel_detect_ball':
                    self.tb.publish(
                        topic="response_carousel_ball_detected", 
                        message=self.request_carousel_detect_ball()
                    )
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

