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
import common.deadman
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.gpio.hc595 import HC595_shift_reg as hc595
# scores are located outside this script because they're voluminous
import roles.display.score_by_mode.system_test as system_test_scores

###################
# ACRYLIC DISPLAY #
###################

class Acrylic_Display():
    """ This class is the hardware init and control for the acrylic displays and 
    their shift registers. It also acts as simple receiver of commands.  
    All animations and sophisticated behaviors reside elsewhere.
    """
    def __init__(self):
        self.current_phrase = 0
        self.current_number = 0
        self.shift_register_states = [0x00,0x00,0x00,0x00,0x00]
        self.shift_register_chain = shifter.HC595(bus=0,deviceId=0)
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
                "juega":  {"bit": 2, "shift_register_index": 4},
                "trueque":{"bit": 3, "shift_register_index": 4},
                "dinero": {"bit": 4, "shift_register_index": 4},
                "como":   {"bit": 5, "shift_register_index": 4},
                "que":    {"bit": 6, "shift_register_index": 4}
            }
        }

    def set_phrase(self, phrase): # [ juega | trueque | dinero | como | que ]
        self.current_phrase = phrase
        self._update_display_()
    
    def generate_phrase_bytes(self):
        shift_register_index = self.Display_LED_Mapping["display_phrase"][self.current_phrase]["shift_register_index"]
        bit = self.Display_LED_Mapping["display_phrase"][self.current_phrase]["bit"]
        self.shift_register_state[shift_register_index] = self.shift_register_state[shift_register_index] + (1 << bit)

    def set_number(self, number):
        if number > 999:
            number = number % 1000
        self.current_number = number
        self.update_display()

    def generate_number_bytes(self):
        a,b,c = '{:>03d}'.format(self.current_number)

        shift_register_index = self.Display_LED_Mapping["digit"]["a"][int(a)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["a"][int(a)]["bit"]
        self.shift_register_state[shift_register_index] += (1 << bit)

        shift_register_index = self.Display_LED_Mapping["digit"]["b"][int(b)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["b"][int(b)]["bit"]
        self.shift_register_state[shift_register_index] += (1 << bit)

        shift_register_index = self.Display_LED_Mapping["digit"]["c"][int(c)]["shift_register_index"]
        bit = self.Display_LED_Mapping["digit"]["c"][int(c)]["bit"]
        self.shift_register_state[shift_register_index] += (1 << bit)

    def set_all_off(self):
        self.shift_register_states = [0x00] * len(self.shift_register_states)
        self.shift_register_chain.write(self.shift_register_state)

    def update_display_(self):
        self.set_all_off()
        self.generate_number_bytes()
        self.generate_phrase_bytes()
        self.shift_register_chain.write(self.shift_register_state)

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
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.deadman = deadman.Deadman_Switch(self.tb)
        self.queue = queue.Queue()
        self.hostname = self.tb.self.get_hostname()

        self.display_subscription_topic = "display_number_" + self.hostname
        self.sound_event_subscription_topic = "play_score_" + self.hostname

        self.tb.subscribe_to_topic("sound_event")
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.subscribe_to_topic("set_display_number")

        self.tb.subscribe_to_topic(self.display_subscription_topic)
        self.tb.subscribe_to_topic(self.sound_event_subscription_topic)

        self.tb.publish("connected", True)
        self.player = Chime_Player()
        self.start()
        self.acrylic_display = Acrylic_Display()

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



    def handle_attraction(self):
        print("Starting attraction mode")
        self.game_mode = self.game_modes.ATTRACTION

        # Set game mode phrase here on change 
        # self.acrylic_display.set_phrase(0)
        self.player.play("attraction_mode_sparse")

    def handle_countdown(self):
        self.game_mode = self.game_modes.COUNTDOWN
        print("In countdown, playing countdown motif")
        self.player.play("countdown_mode")
        # Set game mode phrase here on change 
        # self.acrylic_display.set_phrase(0)
        
        # Comment this block out if you want to stay in countdown for testing
        time.sleep(5)
        self.tb.publish("confirm_countdown",True)
        
    def handle_reset(self):
        self.game_mode = self.game_modes.RESET
        self.player.play("reset_sparse")
        time.sleep(5)
        self.tb.publish("ready_state",True)

    def handle_barter_mode_intro(self):
        self.game_mode = self.game_modes.BARTER_MODE_INTRO
        self.player.play("barter_mode_intro")
        self.acrylic_display.set_phrase()
        time.sleep(5)
        self.tb.publish("confirm_barter_mode_intro",True)

    def handle_barter_mode(self):
        self.game_mode = self.game_modes.BARTER_MODE
        self.player.play("barter_mode")
        self.acrylic_display.set_phrase()
        time.sleep(5)
        self.tb.publish("confirm_barter_mode",True)

    def handle_money_mode_intro(self):
        self.game_mode = self.game_modes.MONEY_MODE_INTRO
        self.player.play("money_mode_intro")
        self.acrylic_display.set_phrase()
        time.sleep(5)
        self.tb.publish("confirm_money_mode_intro",True)

    def handle_money_mode(self):
        self.game_mode = self.game_modes.MONEY_MODE
        self.player.play("money_mode")
        self.acrylic_display.set_phrase()
        time.sleep(5)
        self.tb.publish("confirm_money_mode",True)

    def handle_ending(self):
        self.game_mode = self.game_modes.ENDING

        self.player.play("closing_theme")
        time.sleep(5)
        self.tb.publish("confirm_ending",True)

    def set_game_mode(self, mode):
        if mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            pass # peripheral power should be off during this mode

        if mode == self.game_modes.RESET:
            self.handle_reset()

        if mode == self.game_modes.ATTRACTION:
            self.handle_attraction()

        # waits for press of start button 
        if mode == self.game_modes.COUNTDOWN:
            self.handle_countdown()

        if mode == self.game_modes.BARTER_MODE_INTRO:
            self.handle_barter_mode_intro()


        if mode == self.game_modes.BARTER_MODE:
            self.handle_barter_mode()


        if mode == self.game_modes.MONEY_MODE_INTRO:
            self.handle_money_mode_intro()
 
        if mode == self.game_modes.MONEY_MODE:
            self.handle_money_mode()


        if mode == self.game_modes.ENDING:
            self.handle_ending()

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'sound_event':
                    self.player.play(message)
                if topic == b'set_game_mode':
                    print("setting game mode ", message)
                    self.set_game_mode(message)
                if topic == b'set_display_number':
                    self.acrylic_display.set_display_number(message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()
