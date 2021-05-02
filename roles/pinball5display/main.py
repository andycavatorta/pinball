import importlib
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

print("ggggggggggggggg")

scores ={
    "attraction_mode_dense" : {
        "beats_per_minute":60,
        "beats":[
            [4],[0,1,2,3,4],[0],[0,1,2,3,4],[0],[0,1,2,3,4],[4],[0,1,2,3,4],[0],[0,1,2,3,4],
            [3],[0,1,2,3,4],[0],[0,1,2,3,4],[0],[0,1,2,3,4],[3],[0,1,2,3,4],[0],[0,1,2,3,4],
            [2],[0,1,2,3,4],[0],[0,1,2,3,4],[0],[0,1,2,3,4],[2],[0,1,2,3,4],[0],[],
            [3],[],[1],[],[3],[],[1],[],[3],[],
        ]
    },
    "attraction_mode_sparse" : {
        "beats_per_minute":60,
        "beats":[
            [4],[],[0],[],[0],[],[4],[],[0],[],
            [3],[],[0],[],[0],[],[3],[],[0],[],
            [2],[],[0],[],[0],[],[2],[],[0],[],
            [3],[],[1],[],[3],[],[1],[],[3],[],
        ]
    },
    "countdown_mode" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "barter_mode" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "money_mode" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "score" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "scorex10" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "barter_request" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "fail_theme" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "closing_theme" : {
        "beats_per_minute":4,
        "beats":[
        ]
    },
    "empty" : {
        "beats_per_minute":4,
        "beats":[
        ]
    }
}

class Chimes(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.pitch_to_gpio = [23,24,25,26,27]
        GPIO.setmode(GPIO.BCM)
        for gpio_number in self.pitch_to_gpio:
          GPIO.setup( gpio_number, GPIO.OUT )
        self.all_off()
        self.pulse_duration = 0.011
        self.start()

    def set_pulse_duration(self, pulse_duration):
        self.pulse_duration = pulse_duration

    def all_off(self):
        for gpio_number in self.pitch_to_gpio:
          GPIO.output(gpio_number, GPIO.LOW)

    def pulse(self, beat):
        print("3----")
        self.queue.put(beat)

    def run(self):
        while True:
            try:
                notes = self.queue.get(True)
                print("4----")
                for note in notes:
                    GPIO.output( self.pitch_to_gpio[note], GPIO.HIGH )
                time.sleep(self.pulse_duration)
                self.all_off()
            except Exception as e:
                print(e)
                self.all_off()
            finally:
                self.all_off()

class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.chimes = Chimes()
        self.start()

    def play(self, score):
        print("1----")
        self.queue.put(score)

    def run(self):
        while True:
            try:
                score_name = self.queue.get(True)
                print("2----", score_name)
                score = scores[score_name]
                print("2a----")
                delay_between_beats = 60.0 / score["beats_per_minute"]
                print("2b----")
                for beat in score["beats"]:
                    print("2c----")
                    self.chimes.pulse(beat)
                    print(beat)
                    time.sleep(delay_between_beats)
                self.chimes.all_off() # for safety
            except Exception as e:
                print(e)
                self.chimes.all_off()
            finally:
                self.chimes.all_off()

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()

    def add_to_queue(self, topic, message):
        print("-1 asdf")
        self.queue.put((topic, message))

    def run(self):
        while True:
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
        self.safety_enable = Safety_Enable(self.tb)
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("test_rotation")
        self.tb.subscribe_to_topic("test_lights")
        self.tb.subscribe_to_topic("home")
        self.tb.subscribe_to_topic("pass_ball")
        self.tb.publish("connected", True)
        print("aaaaaaaaaaaaa")
        self.player = Player()
        print("bbbbbbbbbbbbbb")

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self,topic, message):
        print("network_message_handler",topic, message)
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
                print(topic, message)
                if topic == "sound_event":
                    score = message
                    self.player.play(score)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

print("ccccccccccccccc")
main = Main()
print("ddddddddddddddd")
main.start()
print("eeeeeeeeeeeeeee")
time.sleep(10)
print("fffffffffffffffff")
main.add_to_queue("sound_event","attraction_mode_dense")


