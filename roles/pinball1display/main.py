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
        "beats_per_minute":120,
        "beats":[
            [0],[1],[2],[3],[4],[3],[2],[1],
            [0],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],
            [],[],[],[],[],[],[],[],
        ]
    },
    "countdown_mode" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "barter_mode_intro" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "barter_mode" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "money_mode_intro" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "money_mode" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "score" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "scorex10" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "barter_request" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "fail_theme" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "closing_theme" : {
        "beats_per_minute":120,
        "beats":[
        ]
    },
    "reset" : {
        "beats_per_minute":240,
        "beats":[
            [0],[2],[4],[0],[2],[4],[0],[2],[4]
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
        self.queue.put(beat)

    def run(self):
        while True:
            try:
                notes = self.queue.get(True)
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
        self.queue.put(score)

    def run(self):
        while True:
            try:
                score_name = self.queue.get(True)
                score = scores[score_name]
                delay_between_beats = 60.0 / score["beats_per_minute"]
                for beat in score["beats"]:
                    self.chimes.pulse(beat)
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
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.safety_enable = Safety_Enable(self.tb)
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("sound_event")
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.publish("connected", True)
        self.player = Player()
        self.start()

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

    def test_hardware_ready_state(self): #part of start/reset cycle
        time.sleep(5)
        return True

    def set_game_mode(self, mode):
        if mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            pass # peripheral power should be off during this mode
        if mode == self.game_modes.RESET:
            self.game_mode = self.game_modes.RESET
            self.player.play("reset")
            if self.test_hardware_ready_state() == True:
                self.tb.publish("ready_state",True)

        if mode == self.game_modes.ATTRACTION:
            self.game_mode = self.game_modes.ATTRACTION
            self.player.play("attraction_mode_sparse")
            # waits for press of start button 

        """
        if mode == self.game_modes.COUNTDOWN:
            #self.player.play("countdown_mode")
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
                topic, message = self.queue.get(True)
                print(topic, message)
                if topic == b"sound_event":
                    self.player.play(message)
                if topic == b"set_game_mode":
                    self.set_game_mode(message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()
