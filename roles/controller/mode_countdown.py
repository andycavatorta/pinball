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


    animation counts down from 1000
    animation frame counter decrements to 0
    animation interval is a (base number + animation frame counter/factor) 

    """
    def __init__(self, hosts,set_current_mode):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.button_names = ["izquierda","trueque","comienza","dinero","derecha"]
        self.piano_chimes = ["f_piano", "g_piano","gsharp_piano","asharp_piano","c_piano"]
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.forte_chimes = ["f_forte", "g_forte","gsharp_forte","asharp_forte","c_forte"]
        self.comienza_button_order = [] # added here for thread safety
        self.active = False
        self.set_current_mode = set_current_mode
        self.game_mode_names = settings.Game_Modes
        
        self.animation_countdown_counter = 300.0
        self.animation_interval_base = 0.1
        self.animation_interval_factor = 4000.0

        self.start()
        for pinball_hostname in self.pinball_hostnames:
            if pinball_hostname in self.comienza_button_order: # if button already pushed
                for button_name in self.button_names:
                    self.hosts.hostnames[pinball_hostname].request_button_light_active(button_name, False)


    def _cycle_chimes(self):
        states = [1,-1,2,3,-1,2,-1,1,0,-1,1,-1,4,3,-1,2,-1,1,0,-1]
        while True:
            for state in states:
                yield state


    def begin(self):
        self.cycle_chimes = self._cycle_chimes()
        self.animation_countdown_counter = 1000
        self.active = True

    def end(self):
        self.active = False

    def add_to_queue(self, animation_command): # ["begin"|"end"]
        self.queue.put(animation_command)

    def run(self):
        while True:
            animaition_interval = self.animation_interval_base + (self.animation_countdown_counter / self.animation_interval_factor)
            try:
                animation_command = self.queue.get(True,animaition_interval)
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

                    if self.animation_countdown_counter % 10 == 0:
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(int(self.animation_countdown_counter/10))
                    if self.animation_countdown_counter <=0:
                        self.set_current_mode(self.game_mode_names.BARTER_MODE_INTRO)

                    pitch_numeral = next(self.cycle_chimes)
                    if pitch_numeral != -1:
                        pitch_name = self.piano_chimes[pitch_numeral]
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_score(pitch_name)

                    if self.animation_countdown_counter % 4 == 0:
                        for fruit_id in range(5):
                            self.hosts.carouselcenter.request_eject_ball(fruit_id)



                    """
                    # self.animation_frame_counter goes from 0 to 300 during countdown
                    countdown_seconds = self.countdown_end_seconds - (self.animation_frame_counter / 10.0)
                    for display_hostname in self.display_hostnames:
                        self.hosts.hostnames[display_hostname].request_number(int(countdown_seconds*10))

                    if countdown_seconds <=0:
                        self.set_current_mode(self.game_mode_names.BARTER_MODE_INTRO)
                        self.animation_frame_counter = 0
                    """
                    """
                    if self.animation_frame_counter % 4 == 0:
                        countdown_seconds = self.countdown_end_seconds - self.animation_frame_counter
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(countdown_seconds)
                        if countdown_seconds <= 0:
                            self.set_current_mode(self.game_mode_names.BARTER_MODE_INTRO)
                    if self.animation_frame_counter % 2 == 0:
                        if self.animation_frame_counter % 4 == 0:
                            for display_hostname in self.display_hostnames:
                                self.hosts.hostnames[display_hostname].request_phrase("juega")

                            for pinball_hostname in self.pinball_hostnames:
                                if pinball_hostname not in self.comienza_button_order: # if button already pushed
                                    self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
                                    self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all", "on")
                            for carousel_hostname in self.carousel_hostnames:
                                self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("light_all")

                        else:
                            for display_hostname in self.display_hostnames:
                                self.hosts.hostnames[display_hostname].request_phrase("")
                            if pinball_hostname not in self.comienza_button_order: # if button already pushed
                                self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False)
                                self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all", "off")
                            for carousel_hostname in self.carousel_hostnames:
                                self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("clear_all")
                    """
                    self.animation_countdown_counter -= 1
                else:
                    time.sleep(1)

                



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
        self.animation = Animation(hosts,set_current_mode)
        
        self.start()

    def begin(self):
        self.animation.add_to_queue("begin")
        self.animation.mode_countdown_states = list(self.hosts.mode_countdown_states["comienza_button_order"])

    def end(self):
        self.animation.add_to_queue("end")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
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

