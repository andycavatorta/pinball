"""
mode_money_intro
    button lights:
        izquierda: False 
        trueque: False
        comienza: False
        dinero: False
        derecho: False
    button actions:
        izquierda: None
        trueque: None
        comienza: None
        dinero: None
        derecho: None
    playfield light animation:
        signs: off
        all off
    carousel light animation:
        all off
        inner_circle energize
        outer_circle energize
    chimes:
        ding ding ding
    phrase:
        dinero, blink
    numbers:
        000
    timeout: transition to mode_money

"""
import codecs
import os
import queue
import random
import settings
import threading
import time

class Mode_Money_Intro(threading.Thread):
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
        self.start()

    def begin(self):
        self.active = True
        for pinball_hostname in self.pinball_hostnames:
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
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("peso","energize")
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_number(0)
        for i in range(5):
            for display_hostname in self.display_hostnames:
                self.hosts.hostnames[display_hostname].request_score("f_piano")
                self.hosts.hostnames[display_hostname].request_score("asharp_mezzo")
                self.hosts.hostnames[display_hostname].request_phrase("")
            time.sleep(0.5)
            for display_hostname in self.display_hostnames:
                self.hosts.hostnames[display_hostname].request_score("f_piano")
                self.hosts.hostnames[display_hostname].request_score("g_piano")
                self.hosts.hostnames[display_hostname].request_phrase("dinero")
            time.sleep(0.5)
        time.sleep(3)
        self.set_current_mode(self.game_mode_names.MONEY_MODE)
        
    def end(self):
        self.active = False

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
