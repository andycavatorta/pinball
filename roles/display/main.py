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
import common.deadman as deadman
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.gpio.hc595 import HC595_shift_reg as hc595

from thirtybirds3.adapters.sensors import ina260_current_sensor as ina260
# scores are located outside this script because they're voluminous
import roles.display.score_by_mode.system_test as system_test_scores
import roles.display.score_by_mode.singles as single_notes

scores = {
    "system_test_scores_descending_scale":system_test_scores.descending_scale,
    "c_piano":single_notes.c_piano,
    "c_mezzo":single_notes.c_mezzo,
    "c_forte":single_notes.c_forte,
    "asharp_piano":single_notes.asharp_piano,
    "asharp_mezzo":single_notes.asharp_mezzo,
    "asharp_forte":single_notes.asharp_forte,
    "gsharp_piano":single_notes.gsharp_piano,
    "gsharp_mezzo":single_notes.gsharp_mezzo,
    "gsharp_forte":single_notes.gsharp_forte,
    "g_piano":single_notes.g_piano,
    "g_mezzo":single_notes.g_mezzo,
    "g_forte":single_notes.g_forte,
    "f_piano":single_notes.f_piano,
    "f_mezzo":single_notes.f_mezzo,
    "f_forte":single_notes.f_forte,
}

###########################
# S Y S T E M   T E S T S #
###########################

# machine measurements #
# Check communication with TLC5947
# Check communication with HC595
# [unit 1 only] measure 24V current 
    
# tests for human observation #
# [one station at a time] cycle through all digits and phrases
# [one station at a time] cycle through all 5 pitches

###################
# ACRYLIC DISPLAY #
###################

class Acrylic_Display():
    """ This class is the hardware init and control for the acrylic displays and 
    their shift registers. It also acts as simple receiver of commands.  
    All animations and sophisticated behaviors reside elsewhere and call this over thirtybirds
    """
    def __init__(self):
        self.current_phrase = "juega"
        self.current_number = 0
        self.shift_register_states = [0x00,0x00,0x00,0x00,0x00]
        self.shift_register_chain = hc595.HC595(bus=0,deviceId=0)
        self.Display_LED_Mapping = {
            "digit":  {
                "a": {
                    0: {"bit": 0, "shift_register_index": 0},
                    1: {"bit": 1, "shift_register_index": 0},
                    2: {"bit": 2, "shift_register_index": 0},
                    3: {"bit": 3, "shift_register_index": 0},
                    4: {"bit": 4, "shift_register_index": 0},
                    5: {"bit": 5, "shift_register_index": 0},
                    6: {"bit": 6, "shift_register_index": 0},
                    7: {"bit": 7, "shift_register_index": 0},
                    8: {"bit": 0, "shift_register_index": 1},
                    9: {"bit": 1, "shift_register_index": 1}
                },
                "b": {
                    0: {"bit": 2, "shift_register_index": 1},
                    1: {"bit": 3, "shift_register_index": 1},
                    2: {"bit": 4, "shift_register_index": 1},
                    3: {"bit": 5, "shift_register_index": 1},
                    4: {"bit": 6, "shift_register_index": 1},
                    5: {"bit": 7, "shift_register_index": 1},
                    6: {"bit": 0, "shift_register_index": 2},
                    7: {"bit": 1, "shift_register_index": 2},
                    8: {"bit": 2, "shift_register_index": 2},
                    9: {"bit": 3, "shift_register_index": 2}
                },
                "c": {
                    0: {"bit": 0, "shift_register_index": 3},
                    1: {"bit": 1, "shift_register_index": 3},
                    2: {"bit": 2, "shift_register_index": 3},
                    3: {"bit": 3, "shift_register_index": 3},
                    4: {"bit": 4, "shift_register_index": 3},
                    5: {"bit": 5, "shift_register_index": 3},
                    6: {"bit": 6, "shift_register_index": 3},
                    7: {"bit": 7, "shift_register_index": 3},
                    8: {"bit": 0, "shift_register_index": 4},
                    9: {"bit": 1, "shift_register_index": 4}
                }
            },
            "display_phrase": {
                "como":  {"bit": 2, "shift_register_index": 4},
                "fue":{"bit": 3, "shift_register_index": 4},
                "dinero": {"bit": 4, "shift_register_index": 4},
                "trueque":   {"bit": 5, "shift_register_index": 4},
                "juega":    {"bit": 6, "shift_register_index": 4}
            }
        }

    def set_phrase(self, phrase): # [ juega | trueque | dinero | como | que ]
        self.current_phrase = phrase
        self.update_display()
    
    def generate_phrase_bytes(self):
        shift_register_index = self.Display_LED_Mapping["display_phrase"][self.current_phrase]["shift_register_index"]
        bit = self.Display_LED_Mapping["display_phrase"][self.current_phrase]["bit"]
        self.shift_register_states[shift_register_index] = self.shift_register_states[shift_register_index] + (1 << bit)

    def set_number(self, number):
        if number > 999:
            number = number % 1000
        self.current_number = number
        self.update_display()

    def generate_number_bytes(self):
        a,b,c = '{:>03d}'.format(self.current_number)

        shift_register_index = self.Display_LED_Mapping["digit"]["a"][int(a)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["a"][int(a)]["bit"]
        self.shift_register_states[shift_register_index] += (1 << bit)

        shift_register_index = self.Display_LED_Mapping["digit"]["b"][int(b)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["b"][int(b)]["bit"]
        self.shift_register_states[shift_register_index] += (1 << bit)

        shift_register_index = self.Display_LED_Mapping["digit"]["c"][int(c)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["c"][int(c)]["bit"]
        self.shift_register_states[shift_register_index] += (1 << bit)

    def set_all_off(self):
        self.shift_register_states = [0x00] * len(self.shift_register_states)
        self.shift_register_chain.write(self.shift_register_states)

    def update_display(self):
        self.set_all_off()
        self.generate_number_bytes()
        self.generate_phrase_bytes()
        self.shift_register_chain.write(self.shift_register_states)

###############
# C H I M E S #
###############

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

class Chime_Player(threading.Thread):
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
        self.play_score("blank")
        for chime in self.chimes:
            chime.stop_power()

    def play_score(self,score_name):
        print("score_name=",score_name)
        self.current_score.put(score_name)

    def run(self):
        while True:
            try:
                #score_name = self.current_score.get(True)
                #score = scores[score_name]
                print("a")
                score = self.current_score.get(True)
                print("b")
                score = scores[score]
                print("c")                
                default_beat_period = score["default_beat_period"]
                print("d")
                beats = score["beats"]
                interrupt = False
                for beat in beats:
                    print("beat=", beat)
                    if interrupt:
                        break
                    #print("beat",beat)
                    for notes in beat:
                        #print("notes",notes)
                        if interrupt:
                            break
                        for note in notes:
                            #print("note",note) 
                            self.chimes[note["pitch"]].add_pulse_to_queue(note["period"])
                            if not self.current_score.empty():
                                interrupt = True
                                break
                    time.sleep(default_beat_period)
            except Exception as e:
                print(e)
                #self.stop_all_chime_power()

###########
# M A I N #
###########

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
        self.deadman = deadman.Deadman_Switch(self.tb)
        self.queue = queue.Queue()
        self.hostname = self.tb.get_hostname()

        self.tb.subscribe_to_topic("play_score")
        self.tb.subscribe_to_topic("set_phrase")
        self.tb.subscribe_to_topic("set_number")
        self.tb.subscribe_to_topic("all_off")

        self.tb.publish("connected", True)
        self.chime_player = Chime_Player()
        self.acrylic_display = Acrylic_Display()
        if self.tb.get_hostname() == 'pinball1game':
            self.power_sensor = ina260.INA260()
            self.tb.subscribe_to_topic("get_amps")
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
                if topic == b'play_score':
                    if destination == self.tb.get_hostname():
                        self.chime_player.play_score(message)

                if topic == b'set_phrase':
                    if destination == self.tb.get_hostname():
                        self.acrylic_display.set_phrase(message)

                if topic == b'set_number':
                    if destination == self.tb.get_hostname():
                        self.acrylic_display.set_number(message)
                        
                if topic == b'get_amps':
                    tb.publish('measured_amps', self.power_sensor.get_current())

                if topic == b'all_off':
                    self.acrylic_display.set_all_off()
                    self.chime_player.stop_all_chime_power()
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()
