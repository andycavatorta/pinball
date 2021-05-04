import importlib
import os
import queue
import sys
import threading
import time
import traceback
import zmq

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

class MPF_Bridge(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind("tcp://*:5555")

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        print("starting run of mpf bridge")
        while True:
            try:
              message = self.socket.recv()
              print(f"Received msg#: {message}")
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

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
            #self.queue.get(True)
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
        self.mpf_bridge = MPF_Bridge(self.tb)

        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.publish("connected", True)
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

    def set_game_mode(self, mode):
        if mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
            pass # peripheral power should be off during this mode
        if mode == self.game_modes.RESET:
            self.game_mode = self.game_modes.RESET
            time.sleep(6)
            self.tb.publish("ready_state",True)

        if mode == self.game_modes.ATTRACTION:
            self.game_mode = self.game_modes.ATTRACTION
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
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'set_game_mode':
                    self.set_game_mode(message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()

