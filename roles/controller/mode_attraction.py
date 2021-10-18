"""
acrylic display
    Juega - solid
Chimes
    intermittent, random motivs
carousel leds
    integrated "wave" animation
carousel motions

carousel solenoid sounds

playfield leds
    integrated "wave" animation
button lights
    integrated "wave" animation
button switches
    comienza triggers countdown

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
    Attraction mode does not beg for attention
    It should be slowly mesmerizing 
    """
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_center",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.animaition_interval = 0.35
        self.animation_frame_counter = 0
        self.active = False
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.digits_1 = [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        self.digits_2 = [
            [0,1,2],
            [1,2,3],
            [2,3,4],
            [3,4,5],
            [4,5,6],
            [5,6,7],
            [6,7,8],
            [7,8,9],
            [8,9,10],
            [9,10,11],
            [10,11,12],
            [11,12,13],
            [12,13,14],
            [13,14,15],
            [14,15,16],
            [15,16,17],
            [16,17,18],
            [17,18,19],
            [18,19,20],
            [19,20,21],
            [20,21,22],
            [21,22,23],
            [22,23,24],
            [23,24,25],
            [24,25,26],
            [25,26,27],
            [26,27,28],
            [27,28,29],
            [28,29,0],
            [29,0,1],
        ]
        self.digits_3 = [
            [0,3,6,9,12],
            [1,4,7,10,13],
            [2,5,8,11,14],
            [3,6,9,12,15],
            [4,7,10,13,16],
            [5,8,11,14,17],
            [6,9,12,15,18],
            [7,10,13,16,19],
            [8,11,14,17,20],
            [9,12,15,18,21],
            [10,13,16,19,22],
            [11,14,17,20,23],
            [12,15,18,21,24],
            [13,16,19,22,25],
            [14,17,20,23,26],
            [15,18,21,24,27],
            [16,19,22,25,28],
            [17,20,23,26,29],
            [18,21,24,27,0],
            [19,22,25,28,1],
            [20,23,26,29,2],
            [21,24,27,0,3],
            [22,25,28,1,4],
            [23,26,29,2,5],
            [24,27,0,3,6],
            [25,28,1,4,7],
            [26,29,2,5,8],
            [27,0,3,6,9],
            [28,1,4,7,10],
            [29,2,5,8,11]
        ]
        self.start()
    def _cycle_attraction_buttons(self):
        states = [
            {"izquierda":True,"trueque":False,"comienza":False,"dinero":False,"derecha":True},
            {"izquierda":True,"trueque":True,"comienza":False,"dinero":True,"derecha":True},
            {"izquierda":False,"trueque":True,"comienza":True,"dinero":True,"derecha":False},
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
        states = ["juega","juega"]
        while True:
            for state in states:
                yield state

    def _cycle_attraction_playfield(self):
        states = [
            [
                ["pie_pop_right","off"],
                ["pie_spinner","on"],
                ["pie_rollover_right","on"],
                ["pie_sling_right","on"],
                ["pie_sling_left","off"],
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
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", False)
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all", "off")
        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("solid","all",0)
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_number(-1)
            self.hosts.hostnames[display_hostname].request_phrase("juega")
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
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].disable_gameplay()
        self.active = True

    def end(self):
        self.active = False

    def add_to_queue(self, animation_command): # ["begin"|"end"]
        self.queue.put(animation_command)

    def run(self):
        carousel_position = "left"
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

                    #if self.animation_frame_counter % 15 == 0:
                    #    if self.animation_frame_counter % 30 == 0:
                    #        for i in range(5):
                    #            self.hosts.hostnames[self.carousel_hostnames[i]].cmd_carousel_lights("stroke_ripple")
                    #            self.hosts.hostnames[self.pinball_hostnames[i]].cmd_playfield_lights("all_radial","single_dot")
                    #    else:
                    #        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("stroke_ripple")

                    frame_3 = self.digits_3[self.animation_frame_counter % 30]
                    a_places = self.digits_2[frame_3[0]]
                    b_places = self.digits_2[frame_3[1]]
                    c_places = self.digits_2[frame_3[2]]
                    d_places = self.digits_2[frame_3[3]]
                    e_places = self.digits_2[frame_3[4]]
                    a_number = (self.digits_1[a_places[0]]*1) + (self.digits_1[a_places[1]]*10) + (self.digits_1[a_places[2]]*100)
                    b_number = (self.digits_1[b_places[0]]*1) + (self.digits_1[b_places[1]]*10) + (self.digits_1[b_places[2]]*100)
                    c_number = (self.digits_1[c_places[0]]*1) + (self.digits_1[c_places[1]]*10) + (self.digits_1[c_places[2]]*100)
                    d_number = (self.digits_1[d_places[0]]*1) + (self.digits_1[d_places[1]]*10) + (self.digits_1[d_places[2]]*100)
                    e_number = (self.digits_1[e_places[0]]*1) + (self.digits_1[e_places[1]]*10) + (self.digits_1[e_places[2]]*100)
                    self.hosts.pinball1display.request_number(a_number)
                    self.hosts.pinball2display.request_number(b_number)
                    self.hosts.pinball3display.request_number(c_number)
                    self.hosts.pinball4display.request_number(d_number)
                    self.hosts.pinball5display.request_number(e_number)
                    for frame_nudge in range(5):
                        if self.animation_frame_counter % 150 == frame_nudge:
                            for hostname in self.display_hostnames:
                                if random.randrange(0,3) == 0:
                                    self.hosts.hostnames[hostname].request_score(self.mezzo_chimes[random.randrange(0,5)])
                    if self.animation_frame_counter % 1550 == 0:                              
                        for motor_name in self.motor_names:
                            print("carousel_position", self.animation_frame_counter, carousel_position)
                            if carousel_position == "left":
                                if motor_name == "carousel_center":
                                    self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","sandia","sandia")
                                else:
                                    self.hosts.pinballmatrix.cmd_rotate_carousel_to_target(motor_name,"pina","left")
                            else:
                                if motor_name == "carousel_center":
                                    self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","sandia","pina")
                                else:
                                    self.hosts.pinballmatrix.cmd_rotate_carousel_to_target(motor_name,"pina","right")
                        if carousel_position == "left":
                            carousel_position = "left"
                        else:
                            carousel_position = "right"


                    self.animation_frame_counter += 1
                else:
                    time.sleep(self.animaition_interval)



class Mode_Attraction(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.choreography = choreography
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.timeout_duration = 120 #seconds
        self.animation = Animation(hosts)
        self.hosts.mode_countdown_states["comienza_button_order"] = []
        self.start()

    def begin(self):
        self.hosts.mode_countdown_states["comienza_button_order"] = []
        self.animation.add_to_queue("begin")

    def end(self):
        self.animation.add_to_queue("end")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def event_button_comienza(self, message, origin, destination): 
        self.hosts.mode_countdown_states["comienza_button_order"].append(origin) 
        self.set_current_mode(self.game_mode_names.COUNTDOWN)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                #print("in attraction:",topic, message, origin, destination)
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

