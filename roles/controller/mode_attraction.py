import codecs
import os
import queue
import random
import settings
import threading
import time

class Animation(threading.Thread):
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.animaition_interval = 0.2
        self.animation_frame_counter = 0
        self.active = False
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.start()

        


    def _cycle_attraction_buttons(self):
        states = [
            {"izquierda":True,"trueque":False,"comienza":False,"dinero":False,"derecha":True},
            {"izquierda":False,"trueque":True,"comienza":False,"dinero":True,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":False,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
            {"izquierda":False,"trueque":False,"comienza":True,"dinero":False,"derecha":False},
        ]
        while True:
            for state in states:
                yield state

    def _cycle_attraction_numbers(self):
        return [
            random.randrange(0,999),
            random.randrange(0,999),
            random.randrange(0,999),
            random.randrange(0,999),
            random.randrange(0,999),
        ]

    def _cycle_attraction_phrase(self):
        states = ["","juega"]
        while True:
            for state in states:
                yield state

    def _cycle_attraction_playfield(self):
        states = [
            [
                ["pie_pop_right","off"],
                ["pie_spinner","on"],
                ["pie_rollover_right","on"],
                ["pie_sling_right","off"],
                ["pie_sling_left","on"],
                ["pie_rollover_left","on"],
                ["pie_pop_left","on"],
                ["pie_pop_center","on"],
            ],
            [
                ["pie_pop_right","on"],
                ["pie_spinner","off"],
                ["pie_rollover_right","on"],
                ["pie_sling_right","on"],
                ["pie_sling_left","on"],
                ["pie_rollover_left","off"],
                ["pie_pop_left","on"],
                ["pie_pop_center","on"],
            ],
            [
                ["pie_pop_right","on"],
                ["pie_spinner","on"],
                ["pie_rollover_right","off"],
                ["pie_sling_right","on"],
                ["pie_sling_left","on"],
                ["pie_rollover_left","on"],
                ["pie_pop_left","off"],
                ["pie_pop_center","on"],
            ],
            [
                ["pie_pop_right","on"],
                ["pie_spinner","on"],
                ["pie_rollover_right","on"],
                ["pie_sling_right","off"],
                ["pie_sling_left","on"],
                ["pie_rollover_left","on"],
                ["pie_pop_left","on"],
                ["pie_pop_center","off"],
            ],
        ]
        while True:
            for state in states:
                yield state

    def _cycle_attraction_chimes(self):
        states = [
            "c_piano",
            "asharp_piano",
            "g_piano",
            "gsharp_piano",
            "f_piano",
            "g_piano",
            "gsharp_piano",
            "asharp_piano"
        ]
        while True:
            for state in states:
                yield state

    def setup(self):
        for pinball_hostname in self.pinball_hostnames:
            self.hosts[pinball_hostname].request_button_light_active("izquierda", False)
            self.hosts[pinball_hostname].request_button_light_active("trueque", False)
            self.hosts[pinball_hostname].request_button_light_active("comienza", False)
            self.hosts[pinball_hostname].request_button_light_active("dinero", False)
            self.hosts[pinball_hostname].request_button_light_active("derecha", False)
            self.hosts[pinball_hostname].cmd_playfield_lights("all", "off")
        for carousel_hostname in self.carousel_hostnames:
            self.hosts[carousel_hostname].cmd_carousel_lights("clear_all")
        for display_hostname in self.display_hostnames:
            self.hosts[display_hostname].request_phrase("")
            self.hosts[display_hostname].request_number(-1)
        self.reset_animation_cycles()

    def reset_animation_cycles(self):
        self.animation_frame_counter = 0
        self.cycle_attraction_buttons = self._cycle_attraction_buttons()
        self.cycle_attraction_numbers = self._cycle_attraction_numbers()
        self.cycle_attraction_phrase = self._cycle_attraction_phrase()
        self.cycle_attraction_playfield = self._cycle_attraction_playfield()
        self.cycle_attraction_chimes = self._cycle_attraction_chimes()

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
                print("self.animation_frame_counter",self.animation_frame_counter)
                if isinstance(animation_command, bytes):
                    animation_command = codecs.decode(animation_command, 'UTF-8')
                if animation_command == "begin":
                    self.begin()
                if animation_command == "end":
                    self.end()
            except queue.Empty:
                
                if self.active:
                    button_cycle = next(self.cycle_attraction_buttons)
                    for name_val in button_cycle.items():
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active(name_val[0], name_val[1])
                    if self.animation_frame_counter % 25 == 0:
                        print(self.animation_frame_counter)
                        score_name = next(self.cycle_attraction_chimes)
                        print(score_name)
                        self.hosts.pinball1display.request_score(score_name)
                        self.hosts.pinball2display.request_score(score_name)
                        self.hosts.pinball3display.request_score(score_name)
                        self.hosts.pinball4display.request_score(score_name)
                        self.hosts.pinball5display.request_score(score_name)

                    if self.animation_frame_counter % 4 == 0:
                        for hostname in self.pinball_hostnames:
                            light_states = next(self.cycle_attraction_playfield)
                            for light_state in light_states:
                                self.hosts.hostnames[hostname].cmd_playfield_lights(light_state[0],light_state[1])

                        if self.animation_frame_counter % 8 == 0:
                            for hostname in self.display_hostnames:
                                self.hosts.hostnames[hostname].request_phrase("")
                                self.hosts.hostnames[hostname].request_number(random.randrange(0,1000))
                            for i in range(5):
                                self.hosts.hostnames[self.carousel_hostnames[i]].cmd_carousel_lights("stroke_ripple")
                        else:
                            for hostname in self.display_hostnames:
                                self.hosts.hostnames[hostname].request_phrase("juega")
                            self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("stroke_ripple")

                    for frame_nudge in range(5):
                        if self.animation_frame_counter % 250 == frame_nudge:
                            for hostname in self.display_hostnames:
                                if random.randrange(0,3) == 0:
                                    self.hosts.hostnames[hostname].request_score(self.mezzo_chimes[random.randrange(0,5)])




                    self.animation_frame_counter += 1
                else:
                    time.sleep(self.animaition_interval)










class Mode_Attraction(threading.Thread):
    """
    just a single mode animation, waiting for comienza button
    button_lights
    playfield_lights
    carousel_lights
    acrylic_display
    chimes
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
        self.hosts.mode_countdown_states["comienza_button_order"] = []
        self.start()

    def begin(self):
        self.animation.add_to_queue("begin")

    def end(self):
        self.animation.add_to_queue("end")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def event_button_comienza(self, message, origin, destination): 
        self.hosts.mode_countdown_states["comienza_button_order"] = [origin]
        self.set_mode(self.game_mode_names.COUNTDOWN)

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

