import importlib
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time
import traceback

scores = {
    "descending_scale":{
        "default_beat_period":0.5,
        "beats":[ # beats
            [#beat
                [#notes in beat
                    {"pitch":0,"period":0.006},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":0,"period":0.008},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":0,"period":0.01},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":0,"period":0.012},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":0,"period":0.014},
                ]
            ],

            [#beat
                [#notes in beat
                    {"pitch":1,"period":0.006},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":1,"period":0.008},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":1,"period":0.01},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":1,"period":0.012},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":1,"period":0.014},
                ]
            ],

            [#beat
                [#notes in beat
                    {"pitch":2,"period":0.006},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":2,"period":0.008},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":2,"period":0.01},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":2,"period":0.012},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":2,"period":0.014},
                ]
            ],

            [#beat
                [#notes in beat
                    {"pitch":3,"period":0.006},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":3,"period":0.008},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":3,"period":0.01},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":3,"period":0.012},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":3,"period":0.014},
                ]
            ],

            [#beat
                [#notes in beat
                    {"pitch":4,"period":0.006},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":4,"period":0.008},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":4,"period":0.01},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":4,"period":0.012},
                ]
            ],
            [#beat
                [#notes in beat
                    {"pitch":4,"period":0.014},
                ]
            ],
        ]
    }
}


class Chime(threading.Thread):
    def __init__(self, gpio_number):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.gpio_number = gpio_number
        GPIO.setup(gpio_number, GPIO.OUT)
        self.stop_power()
        self.start()

    def stop_power(self):
        print("stop_power", self.gpio_number)
        GPIO.output(self.gpio_number, GPIO.LOW)

    def start_power(self):
        print("start_power", self.gpio_number)
        GPIO.output(self.gpio_number, GPIO.HIGH)

    def add_pulse_to_queue(self, pulse_duration):
        self.queue.put(pulse_duration)

    def run(self):
        while True:
            try:
                pulse_duration = self.queue.get(True)
                if pulse_duration < 0.1: # saftey check
                    self.start_power()
                    time.sleep(pulse_duration)
                    self.stop_power()
            except Exception as e:
                print(e)
                self.stop_power()
            finally:
                self.stop_power()

class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.current_score = queue.Queue() # queue can act as interrupt or stop message
        GPIO.setmode(GPIO.BCM)
        self.gpios = [6,16,5,17,22]
        self.chimes = []
        for gpio in self.gpios: # how can this be a comprehension
            self.chimes.append(Chime(gpio))
        self.start()

    def stop_all_chime_power(self):
        for chime in self.chimes:
            chime.stop_power()

    def play_score(self,score_name):
        self.current_score.put(score_name)

    def run(self):
        while True:
            try:
                score_name = self.current_score.get(True)
                score = scores[score_name]
                default_beat_period = score["default_beat_period"]
                beats = score["beats"]
                for beat in beats:
                    print("beat",beat)
                    for notes in beat:
                        print("notes",notes)
                        for note in notes:
                            print("note",note) 
                            self.chimes[note["pitch"]].add_pulse_to_queue(note["period"])
                    time.sleep(default_beat_period)
            except Exception as e:
                print(e)
                self.stop_all_chime_power()

player = Player()

def repeat_score(score_name):
    while True:
        player.play_score(score_name)
        time.sleep(10)
