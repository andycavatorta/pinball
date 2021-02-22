import importlib
import mido
import os
import queue
import sys
import threading
import time

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
print(app_path)
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class States:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
            WAITING_FOR_HOMING = "waiting_for_homing"
            READY = "ready" 
        self.states =States()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.transport_connected = False
        self.horsewheel_connected = False

        self.pitch_slider_home = False
        self.horsewheel_slider_home = False
        self.horsewheel_lifter_home = False
        self.state = self.states.WAITING_FOR_CONNECTIONS

        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("transport_connected")
        self.tb.subscribe_to_topic("horsewheel_connected")
        self.tb.subscribe_to_topic("pitch_slider_home")
        self.tb.subscribe_to_topic("horsewheel_slider_home")
        self.tb.subscribe_to_topic("horsewheel_lifter_home")

        self.start()

    def network_message_handler(self, topic, message):
        self.add_to_queue(topic, message)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
        if status == True: 
            if hostname == "transport":
                self.transport_connected = True
                if self.transport_connected and self.horsewheel_connected:
                    self.state = self.states.WAITING_FOR_HOMING
                    self.tb.publish("pitch_slider_home", False)
                    self.tb.publish("horsewheel_slider_home", False)
                    self.tb.publish("horsewheel_lifter_home", False)
            if hostname == "horsewheel":
                self.horsewheel_connected = True
                if self.transport_connected and self.horsewheel_connected:
                    self.state = self.states.WAITING_FOR_HOMING
                    self.tb.publish("pitch_slider_home", False)
                    self.tb.publish("horsewheel_slider_home", False)
                    self.tb.publish("horsewheel_lifter_home", False)
        else: 
            if hostname == "transport":
                self.transport_connected = True
                self.state = self.states.WAITING_FOR_CONNECTIONS
            if hostname == "horsewheel":
                self.horsewheel_connected = True
                self.state = self.states.WAITING_FOR_CONNECTIONS
        print("self.state=", self.state)

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))
    def run(self):
        #self.state = self.states.READY # just for testing
        while True:
            try:
                #print("--------------",self.tb.check_connections(), self.state)
                topic, message = self.queue.get(True)
                print(">>>",topic, message)
                if self.state == self.states.WAITING_FOR_HOMING:
                    if topic == b'pitch_slider_home':
                        self.pitch_slider_home = True
                        if self.horsewheel_slider_home and self.pitch_slider_home and self.horsewheel_lifter_home:
                            self.state = self.states.READY
                    if topic == b'horsewheel_slider_home':
                        self.horsewheel_slider_home = True
                        if self.horsewheel_slider_home and self.pitch_slider_home and self.horsewheel_lifter_home:
                            self.state = self.states.READY
                    if topic == b'horsewheel_lifter_home':
                        self.horsewheel_lifter_home = True
                        if self.horsewheel_slider_home and self.pitch_slider_home and self.horsewheel_lifter_home:
                            self.state = self.states.READY

                if self.state == self.states.READY:
                    if topic in ["pitch_slider_position","horsewheel_slider_position","horsewheel_speed","horsewheel_lifter_position"]:
                        print(topic, message)
                        self.tb.publish(topic, message)
                print("self.state=", self.state)

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

class MIDI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.last_horsewheel_speed = 0
        self.wheel_lifter_coarse = 0
        self.wheel_lifter_fine = 0
        self.start()
    def run(self):
        time.sleep(1)
        """
        with mido.open_input("Oxygen 88:Oxygen 88 MIDI 1 20:0") as inport:
            for midi_o in inport:
                #print(midi_o)
                if midi_o.type == "note_on":
                    main.add_to_queue("pitch_slider_position", ((midi_o.note-21)*30000)+100000 )
                    continue
                if midi_o.type == "control_change":
                    if midi_o.control == 73: # pitch fine
                        continue
                    if midi_o.control == 74: # wheel lift coarse
                        self.wheel_lifter_coarse = midi_o.value * 5000
                        main.add_to_queue("horsewheel_lifter_position", self.wheel_lifter_coarse + self.wheel_lifter_fine)
                        continue
                    if midi_o.control == 71: # wheel lift fine
                        self.wheel_lifter_fine = midi_o.value * 100
                        main.add_to_queue("horsewheel_lifter_position", self.wheel_lifter_coarse + self.wheel_lifter_fine)
                        continue
                    if midi_o.control == 91: # wheel speed
                        main.add_to_queue("horsewheel_speed", midi_o.value)
                        continue
                    if midi_o.control == 93: # wheel slide
                        main.add_to_queue("horsewheel_slider_position", ((midi_o.value)*10000)+20000)
                        continue
                    if midi_o.control == 5: # vibrato depth
                        pass
                    if midi_o.control == 84: # vibrato speed
                        pass
        """
midi = MIDI()
