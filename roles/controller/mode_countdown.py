"""
countdown mode 
    run animation
        animate gamestations differently after their comienza button is pushed
    
    events:
        countdown ends
        comienza button pushed
        all comienza button pushed

    record which gamestations are active

    when countdown ends or all buttons are pushed
        transition to BARTER_MODE_INTRO

"""
import codecs
import os
import queue
import random
import settings
import threading
import time

class Animation(threading.Thread):
    """
    chimes: descending
    phrase: juega
    numbers: countdown
    carousel lights
        for active: lit up and solid
        for waiting: blinking
    playfield:
        for active: lit up and solid
        for waiting: blinking 
    buttons:
        for active: off
        for waiting: comienza blinking rapidly
    """
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.button_names = ["izquierda","trueque","comienza","dinero","derecha"]
        self.animaition_interval = 0.25
        self.countdown_end_seconds = 30
        self.animation_frame_counter = 0
        self.comienza_button_order = [] # added here for thread safety
        self.active = False
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.start()
        for pinball_hostname in self.pinball_hostnames:
            if pinball_hostname in self.comienza_button_order: # if button already pushed
                for button_name in self.button_names:
                    self.hosts.hostnames[pinball_hostname].request_button_light_active(button_name, False)

    def setup(self):
        self.reset_animation_cycles()

    def reset_animation_cycles(self):
        self.animation_frame_counter = 0

    def begin(self):
        self.reset_animation_cycles()
        self.active = True

    def end(self):
        self.active = False

    def add_to_queue(self, animation_command): # ["begin"|"end"]
        self.queue.put(animation_command)

    def run(self):
        while True:
            try:
                animation_command = self.queue.get(True,self.animaition_interval)
                if isinstance(animation_command, bytes):
                    animation_command = codecs.decode(animation_command, 'UTF-8')
                if animation_command == "begin":
                    self.begin()
                    continue
                if animation_command == "end":
                    self.end()
                    continue
                # the only remaining option would be comienza_button_order
                self.comienza_button_order.append(animation_command)
            except queue.Empty:
                if self.active:
                    if self.animation_frame_counter % 4 == 0:
                        countdown_seconds = self.countdown_end_seconds - self.animation_frame_counter
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(countdown_seconds)
                        if countdown_seconds =< 0:
                            self.set_mode(self.game_mode_names.BARTER_MODE_INTRO)
                    if self.animation_frame_counter % 2 == 0:
                        if self.animation_frame_counter % 4 == 0:
                            for display_hostname in self.display_hostnames:
                                self.hosts.hostnames[display_hostname].request_phrase("juega")
                            if pinball_hostname not in self.comienza_button_order: # if button already pushed
                                self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
                            if pinball_hostname not in self.comienza_button_order: # if button already pushed
                                self.hosts[pinball_hostname].cmd_playfield_lights("all", "on")
                            for carousel_hostname in self.carousel_hostnames:
                                self.hosts[carousel_hostname].cmd_carousel_lights("light_all")

                        else:
                            for display_hostname in self.display_hostnames:
                                self.hosts.hostnames[display_hostname].request_phrase("")
                            if pinball_hostname not in self.comienza_button_order: # if button already pushed
                                self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False)
                                self.hosts[pinball_hostname].cmd_playfield_lights("all", "off")
                            for carousel_hostname in self.carousel_hostnames:
                                self.hosts[carousel_hostname].cmd_carousel_lights("clear_all")

                    self.animation_frame_counter += 1
                else:
                    time.sleep(self.animaition_interval)

                



class Mode_Countdown(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.timeout_duration = 120 #seconds
        self.animation = Animation(hosts)
        
        self.start()

    def begin(self):
        self.animation.add_to_queue("begin")
        self.animation.mode_countdown_states = list(self.hosts.mode_countdown_states["comienza_button_order"])

    def end(self):
        self.animation.add_to_queue("end")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def transition_mode(self):

    def event_button_comienza(self, message, origin, destination): 
        if origin not in self.hosts.mode_countdown_states["comienza_button_order"]:
            self.hosts.mode_countdown_states["comienza_button_order"].append(origin)
            self.animation.add_to_queue(origin)
        if len(self.hosts.mode_countdown_states["comienza_button_order"]) => 5:
            self.set_mode(self.game_mode_names.BARTER_MODE_INTRO)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')
                getattr(self,topic)(
                        message, 
                        origin, 
                        destination,
                    )
            except AttributeError:
                pass

