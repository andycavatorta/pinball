import codecs
import os
import queue
import random
import settings
import threading
import time

class Animation(threading.Thread):
    def __init__(self, hosts,set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.fruit_names = ["coco", "naranja", "mango", "sandia", "pina"]
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.button_names = ["izquierda","trueque","comienza","dinero","derecha"]
        self.piano_chimes = ["f_piano", "g_piano","gsharp_piano","asharp_piano","c_piano"]
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.forte_chimes = ["f_forte", "g_forte","gsharp_forte","asharp_forte","c_forte"]
        self.carousel_hostname_map = {
            "pinball1game":"carousel1",
            "pinball2game":"carousel2",
            "pinball3game":"carousel3",
            "pinball4game":"carousel4",
            "pinball5game":"carousel5",
        }
        self.active = False
        self.set_current_mode = set_current_mode
        self.comienza_button_order = []
        self.game_mode_names = settings.Game_Modes
        self.animation_frame_counter = 0
        self.animation_interval = 0.075 # seconds
        self.animation_frame_counter_limit = 200
        self.start()

    def _cycle_chimes(self):
        states = [1,-1,2,3,-1,2,-1,1,0,-1,1,-1,4,3,-1,2,-1,1,0,-1]
        while True:
            for state in states:
                yield state

    def begin(self):
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("sign_bottom_left","on")
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", False) 
            self.hosts.hostnames[pinball_hostname].enable_izquierda_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_trueque_coil(False) # also initiate trade
            self.hosts.hostnames[pinball_hostname].enable_dinero_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_kicker_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_derecha_coil(False)

        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("juega")
        self.cycle_chimes = self._cycle_chimes() # start from beginning if interrupted last time
        self.animation_frame_counter = 0
        self.active = True

    def end(self):
        self.active = False

    def add_to_queue(self, animation_command,data): # ["begin"|"end"]
        self.queue.put([animation_command,data])

    def run(self):
        while True:
            try:
                animation_command,data = self.queue.get(True,self.animation_interval)
                if isinstance(animation_command, bytes):
                    animation_command = codecs.decode(animation_command, 'UTF-8')
                if animation_command == "begin":
                    self.begin()
                    continue
                if animation_command == "end":
                    self.end()
                    continue
                if animation_command == "set_comienza_buttons":
                    games_with_players = self.hosts.get_games_with_players()
                    for pinball_hostname in self.pinball_hostnames:
                        if pinball_hostname in games_with_players:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False) 
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","on")
                            self.hosts.hostnames[self.carousel_hostname_map[pinball_hostname]].cmd_carousel_lights("all","on")
                        else:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
                            self.hosts.hostnames[self.carousel_hostname_map[pinball_hostname]].cmd_carousel_lights("all","off")
                    if len(data) == 5:
                        self.set_current_mode(self.game_mode_names.BARTER_MODE_INTRO)
                    self.comienza_button_order = data
                    continue
            except queue.Empty:
                if self.active:
                    for display_hostname in self.display_hostnames:
                        #input 0-200
                        #output 999-888-777-666-555-444-333-222-111-000
                        #ranges 0-19,20-39,40-59,60-79,80-99,100-119,120-139,140-159,160-179,180-200
                        display_number = 000
                        if 0 <= self.animation_frame_counter < 20:
                            display_number = 999
                        if 20<= self.animation_frame_counter < 40:
                            display_number = 888
                        if 40<= self.animation_frame_counter < 60:
                            display_number = 777
                        if 60<= self.animation_frame_counter < 80:
                            display_number = 666
                        if 80<= self.animation_frame_counter < 100:
                            display_number = 555
                        if 100<= self.animation_frame_counter < 120:
                            display_number = 444
                        if 120<= self.animation_frame_counter < 140:
                            display_number = 333
                        if 140<= self.animation_frame_counter < 160:
                            display_number = 222
                        if 160<= self.animation_frame_counter < 180:
                            display_number = 111
                        self.hosts.hostnames[display_hostname].request_number(display_number)
                    if self.animation_frame_counter % 3==0: # 1 second intervals
                        pitch_numeral = next(self.cycle_chimes)
                        if pitch_numeral != -1:
                            pitch_name = self.piano_chimes[pitch_numeral]
                            for display_hostname in self.display_hostnames:
                                self.hosts.hostnames[display_hostname].request_score(pitch_name)
                    if self.animation_frame_counter % 10 ==0: # 1 second intervals
                        get_games_with_players = self.hosts.get_games_with_players()
                        if self.animation_frame_counter % 20 ==0: # alternate seconds A
                            for pinball_hostname in self.pinball_hostnames:
                                self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","on")
                                self.hosts.hostnames[self.carousel_hostname_map[pinball_hostname]].cmd_carousel_lights("all","on")
                                self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("sign_bottom_left","off")
                                if pinball_hostname not in get_games_with_players:
                                    self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False)

                        else: # alternate seconds B
                            for pinball_hostname in self.pinball_hostnames:
                                self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("sign_bottom_left","on")
                                if pinball_hostname not in get_games_with_players:
                                    self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
                                    self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
                                    self.hosts.hostnames[self.carousel_hostname_map[pinball_hostname]].cmd_carousel_lights("all","off")

                    self.animation_frame_counter += 1
                    if self.animation_frame_counter > self.animation_frame_counter_limit:
                        self.set_current_mode(self.game_mode_names.BARTER_MODE_INTRO)
                else:
                    time.sleep(0.5)

class Mode_Countdown(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.choreography = choreography
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.animation = Animation(hosts,set_current_mode,choreography)
        self.start()

    def begin(self):
        print("mode_countdown Mode_Countdown.begin 1")

        self.animation.add_to_queue("set_comienza_buttons",self.hosts.get_games_with_players())

        print("mode_countdown Mode_Countdown.begin 2")
        self.animation.add_to_queue("begin",None)
        print("mode_countdown Mode_Countdown.begin 3")
        self.animation.animation_frame_counter = 0
        print("mode_countdown Mode_Countdown.begin 4")

    def end(self):
        print("mode_countdown.end")
        self.animation.add_to_queue("end",None)

    def respond_host_connected(self, message, origin, destination): 
        # is a host is connected here, that means it was disconnected. must re-run system tests
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def event_button_comienza(self, message, origin, destination): 
        self.hosts.set_games_with_players(origin)



        self.animation.add_to_queue("set_comienza_buttons",self.hosts.get_games_with_players())


    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                # all messages received by controller come here
                topic, message, origin, destination = self.queue.get(True)
                # convert byte strings to strings
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')
                # if topic equals a local method, call it
                getattr(self,topic)(
                        message, 
                        origin, 
                        destination,
                    )
            except AttributeError:
                # if topic does not equal a local method
                pass
