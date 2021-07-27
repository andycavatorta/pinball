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
from thirtybirds3.adapters.gpio.hc595 import HC595_shift_reg as hc595

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
            [0],[],[],[],[],[],[],[]
        ]
    },
    "attraction_mode_test" : {
        "beats_per_minute":120,
        "beats":[
            [0,0],[2,3],[4]
        ]
    },
    "countdown_mode" : {
        "beats_per_minute":120,
        "beats":[
            [0,0],[2,3],[4]
        ]
    },
    "barter_mode_intro" : {
        "beats_per_minute":120,
        "beats":[
            [0],[0],[0],[0]
        ]
    },
    "barter_mode" : {
        "beats_per_minute":120,
        "beats":[
            [1],[1],[1],[1]

        ]
    },
    "money_mode_intro" : {
        "beats_per_minute":120,
        "beats":[
            [2],[2],[2],[2]

        ]
    },
    "money_mode" : {
        "beats_per_minute":120,
        "beats":[
            [3],[3],[3],[3]

        ]
    },
    "score" : {
        "beats_per_minute":120,
        "beats":[
            [3,1]
        ]
    },
    "scorex10" : {
        "beats_per_minute":120,
        "beats":[
            [0,2]
        ]
    },
    "note1" : {
        "beats_per_minute":120,
        "beats":[
            [0,4]
        ]
    },
    "note2" : {
        "beats_per_minute":120,
        "beats":[
            [1,4]
        ]
    },
    "note3" : {
        "beats_per_minute":120,
        "beats":[
            [2,4]
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
            [4],[4],[4],[4]

        ]
    },
    "reset" : {
        "beats_per_minute":240,
        "beats":[
            [0],[2],[4],[0],[2],[4],[0],[2],[4]
        ]
    },
     "reset_sparse" : {
        "beats_per_minute":240,
        "beats":[
            [0],[2],[4]
        ]
    }
}

class Acrylic_Display():
    def __init__(self):
        self.current_words = 0
        self.current_number = 0
        self.game_mode = "countdown"
        self.shift_register_state = [0, 0, 0, 0, 0]
        self.shift_register = hc595.HC595()

    def format_number(self, num):
        num = str(num)
        # Make sure 7 goes to 007 and 37 goes to 037
        num = ("0" + num) if len(num) == 1 else num
        num = ("0" + num) if len(num) == 2 else num
        return num

    def set_number(self, num):
        self.current_number = self.format_number(num)
        print("setting num to ", self.current_number)
        self._update_display_()

    def generate_number_bytes(self):
        # For each number of 007 look up the correct shift reg and bit to flip
        for index, number in enumerate(self.current_number):

            # Casting Int to Number right now because not sure if we are getting int or str input
            # Will Standardize Format Later 
            shift_register_index = self.Display_LED_Mapping.shift_reg_mapping[
                "display_number"][index][int(number)]["shift_register_index"]

            bit = self.Display_LED_Mapping.shift_reg_mapping["display_number"][index][int(
                number)]["bit"]
            print("Shift Reg {} Writing {} at index {}".format(
                self.shift_register_state, bit, shift_register_index))
            self.shift_register_state[shift_register_index] = self.shift_register_state[shift_register_index] + (
                1 << bit)

    def set_words(self):
        self.current_words = self.game_mode
        self._update_display_()

    def generate_word_bytes(self):
        shift_register_index = self.Display_LED_Mapping.shift_reg_mapping[
            "display_sentence"][self.game_mode]["shift_register_index"]
        bit = self.Display_LED_Mapping["display_sentence"][self.game_mode]["bit"]

        # Turn on state for word
        self.shift_register_state[shift_register_index] = self.shift_register_state[shift_register_index] + (
            1 << bit)

    def turn_off_lights(self):
        # Set every value in byte array to 0 
        for index, val in enumerate(self.shift_register_state):
            self.shift_register_state[index] = 0x00
        self.shift_register.write(self.shift_register_state)

    def _update_display_(self):
        self.turn_off_lights()
        self.generate_number_bytes()
        # self.generate_word_bytes()
        self.shift_register.write(self.shift_register_state)
        print("updating display to Current Word {} Number {}".format(
            self.current_words, self.current_number))




class Chimes(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.pitch_to_gpio = [23,24,25,26,27]
        GPIO.setmode(GPIO.BCM)
        for gpio_number in self.pitch_to_gpio:
          GPIO.setup( gpio_number, GPIO.OUT )
        self.all_off()
        self.pulse_duration = 0.008
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
        self.hostname = self.tb.self.get_hostname()
        self.display_subscription_topic = "set_display_number" + self.hostname
        self.sound_event_subscription_topic = "sound_event_" + self.hostname

        self.tb.subscribe_to_topic("sound_event")
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.subscribe_to_topic("set_display_number")

        self.tb.subscribe_to_topic(self.display_subscription_topic)
        self.tb.subscribe_to_topic(self.sound_event_subscription_topic)

        self.tb.publish("connected", True)
        self.player = Player()
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

        # Set game mode words here on change 
        # self.acrylic_display.set_words(0)
        self.player.play("attraction_mode_sparse")

    def handle_countdown(self):
        self.game_mode = self.game_modes.COUNTDOWN
        print("In countdown, playing countdown motif")
        self.player.play("countdown_mode")
        # Set game mode words here on change 
        # self.acrylic_display.set_words(0)
        
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
        self.acrylic_display.set_words()
        time.sleep(5)
        self.tb.publish("confirm_barter_mode_intro",True)

    def handle_barter_mode(self):
        self.game_mode = self.game_modes.BARTER_MODE
        self.player.play("barter_mode")
        self.acrylic_display.set_words()
        time.sleep(5)
        self.tb.publish("confirm_barter_mode",True)

    def handle_money_mode_intro(self):
        self.game_mode = self.game_modes.MONEY_MODE_INTRO
        self.player.play("money_mode_intro")
        self.acrylic_display.set_words()
        time.sleep(5)
        self.tb.publish("confirm_money_mode_intro",True)

    def handle_money_mode(self):
        self.game_mode = self.game_modes.MONEY_MODE
        self.player.play("money_mode")
        self.acrylic_display.set_words()
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
