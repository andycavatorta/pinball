#!/usr/bin/env python

import time
import math
import os
import random
import queue
import RPi.GPIO as GPIO
import sys
import threading

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

class Scores():
    attraction_mode = {
        "tempo_multiplier":4,
        "beats":[[1,2],[2,3],[3,4],[4,5],[5,1]]
    }
    countdown_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    barter_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    money_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    score = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    scorex10 = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    barter_request = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    fail_theme = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    closing_theme = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    empty = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }

class Chimes(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.gpio_numbers =  [ 2, 3, 4, 17, 18,   27, 22, 23, 24, 10,   9, 25, 11, 8, 0,   1, 5, 6, 12, 13,   19, 16, 26, 20, 21 ] 
        self.stations = [
            self.gpio_numbers[0:5],
            self.gpio_numbers[5:10],
            self.gpio_numbers[10:15],
            self.gpio_numbers[15:20],
            self.gpio_numbers[20:25],
        ]
        self.duration = 0.010
        GPIO.setmode(GPIO.BCM)
        for gpio_number in self.gpio_numbers:
          GPIO.setup( gpio_number, GPIO.OUT )
        self.all_off()

    def all_off(self):
        for gpio_number in self.gpio_numbers:
          GPIO.output(gpio_number, GPIO.LOW)

    def set_duration(self, duration):
        self.duration = duration

    def pulse(self, target, beat):
        print("5",list_of_station_pitch_pairs)
        self.queue.put((target, beat))

    def run(self):
        while True:
            try:
                target, beat = self.queue.get(True)
                for notes in beat:
                    gpio = self.stations[target][note]
                    GPIO.output( gpio, GPIO.HIGH )
                time.sleep(self.duration)
                self.all_off()
            except Exception as e:
                self.all_off()

class Player(threading.Thread):
    """
    A player receives the name of a score and spools it out to the chimes of its assigned target.
    A target could be a station, a pair of stations, or all stations.
    """
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.target = target
        self.base_tempo = 0.1
        self.chimes = Chimes()
        self.start()

    def play(self, score):
        self.queue.put(score)
        print("3",score)

    def run(self):
        while True:
            try:
                score_name = self.queue.get(True)
                score = Scores[score_name]
                print("4",self.target, score)
                for beat in score.beats:
                    print("5",beat)
                    self.chimes.pulse(self.target, beat)
                time.sleep(self.base_tempo * score.tempo_multiplier)
                self.chimes.all_off() # for safety
            except Exception as e:
                print(e)
                self.chimes.all_off()
            finally:
                self.chimes.all_off()


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
        self.players = [
            Player(0),
            Player(1),
            Player(2),
            Player(3),
            Player(4),
            Player(5)
        ]
        self.tb.subscribe_to_topic("connected")
        self.start()

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self, topic, message):
        self.add_to_queue(topic, message)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))
    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                print("1",topic, message)
                if topic == "sound_event":
                    target, score = message
                    print("2",target, score)
                    self.players[target].play(score)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()



main.add_to_queue("sound_event",(1,"attraction_mode"))








