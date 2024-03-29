"""

"""
import codecs
import os
import queue
import random
import settings
import threading
import time


FRUITS = ["coco", "laranja", "mango", "sandia", "pina"]
STATION_NAMES = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]


class Animation(threading.Thread):
    """
    Attraction mode does not beg for attention
    It should be slowly mesmerizing 
    """
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = hosts
        self.animation_frame_counter = 0
        self.animaition_interval = 0.1
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_center",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.piano_chimes = ["f_piano", "g_piano","gsharp_piano","asharp_piano","c_piano"]
        self.active = False
        self.start()

    def begin(self):
        print("mode_attraction Animation.begin")
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].barter_mode_score = 0
            self.hosts.hostnames[pinball_hostname].money_mode_score = 0
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[pinball_hostname].enable_izquierda_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_trueque_coil(False) # also initiate trade
            self.hosts.hostnames[pinball_hostname].enable_dinero_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_kicker_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_derecha_coil(False)   
        self.animation_frame_counter = 0
        self.active = True

    def end(self):
        print("mode_attraction Animation.end")
        self.active = False

    def add_to_queue(self, animation_command): # ["begin"|"end"]
        self.queue.put(animation_command)

    def run(self):
        print("mode_attraction Animation.run 0")
        while True:
            try:
                animation_command = self.queue.get(True,self.animaition_interval)
                print("animation_command", animation_command)
                if isinstance(animation_command, bytes):
                    animation_command = codecs.decode(animation_command, 'UTF-8')
                if animation_command == "begin":
                    self.begin()
                if animation_command == "end":
                    self.end()
            except queue.Empty:
                if self.active:
                    play_chimes = True if random.randrange(0,5) == 0 else False
                    if self.animation_frame_counter == 0: # 0 seconds
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("peso","throb")
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(999)
                        for hostname in self.display_hostnames:
                            if random.randrange(0,2) == 0 and play_chimes:
                                self.hosts.hostnames[hostname].request_score(self.piano_chimes[random.randrange(0,5)])

                    if self.animation_frame_counter == 2 and play_chimes:
                        for hostname in self.display_hostnames:
                            if random.randrange(0,3) == 0:
                                self.hosts.hostnames[hostname].request_score(self.piano_chimes[random.randrange(0,5)])

                    if self.animation_frame_counter == 3 and play_chimes:
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("inner_circle","throb")

                    if self.animation_frame_counter == 4 and play_chimes: # 0 seconds
                        for hostname in self.display_hostnames:
                            if random.randrange(0,4) == 0:
                                self.hosts.hostnames[hostname].request_score(self.piano_chimes[random.randrange(0,5)])

                    if self.animation_frame_counter == 5 and play_chimes: # 0 seconds
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 6 and play_chimes:
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("outer_circle","throb")
                        for hostname in self.display_hostnames:
                            if random.randrange(0,3) == 0:
                                self.hosts.hostnames[hostname].request_score(self.piano_chimes[random.randrange(0,5)])                        

                    if self.animation_frame_counter == 8 and play_chimes:
                        for hostname in self.display_hostnames:
                            if random.randrange(0,2) == 0:
                                self.hosts.hostnames[hostname].request_score(self.piano_chimes[random.randrange(0,5)])

                    if self.animation_frame_counter == 10: # 1 second
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(888)
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_coco_1","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_1","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_1","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_1","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_1","throb")

                    if self.animation_frame_counter == 13:
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_coco_2","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_2","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_2","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_2","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_2","throb")

                    if self.animation_frame_counter == 15: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 17:
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_coco_3","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_3","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_3","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_3","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_3","throb")

                    if self.animation_frame_counter == 20: # 2 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(777)
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_coco_4","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_4","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_4","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_4","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_4","throb")

                    if self.animation_frame_counter == 23:
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_coco_5","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_5","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_5","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_5","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_5","throb")

                    if self.animation_frame_counter == 25: # 0 seconds  
                        for pinball_hostname in self.pinball_hostnames:
                             self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 27:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_1","throb")

                    if self.animation_frame_counter == 30: # 3 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(666)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_2","throb")

                    if self.animation_frame_counter == 33:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_3","throb")

                    if self.animation_frame_counter == 35: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 37:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_4","throb")

                    if self.animation_frame_counter == 40: # 4 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(555)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_5","throb")

                    if self.animation_frame_counter == 43:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_6","throb")

                    if self.animation_frame_counter == 45: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 47:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_7","throb")

                    if self.animation_frame_counter == 50: # 5 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(444)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_8","throb")

                    if self.animation_frame_counter == 53:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_9","throb")

                    if self.animation_frame_counter == 55: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 57:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_10","throb")

                    if self.animation_frame_counter == 60: # 6 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(333)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_11","throb")

                    if self.animation_frame_counter == 63:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_12","throb")

                    if self.animation_frame_counter == 65: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 67:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_13","throb")

                    if self.animation_frame_counter == 70: # 7 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(222)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_14","throb")

                    if self.animation_frame_counter == 73:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_15","throb")

                    if self.animation_frame_counter == 75: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        

                    if self.animation_frame_counter == 77:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_16","throb")

                    if self.animation_frame_counter == 80: # 8 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(111)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_17","throb")

                    if self.animation_frame_counter == 83:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("ripple_18","throb")

                    if self.animation_frame_counter == 85: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 90: # 9 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(000)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 91:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 92:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 93:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 94:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 95:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 96:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 97:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 98:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 99:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True if random.randrange(0,3) == 0 else False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True if random.randrange(0,3) == 0 else False)

                    if self.animation_frame_counter == 100: # 10 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",False)
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",False)

                    if self.animation_frame_counter == 105: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 110: # 11 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(111)

                    if self.animation_frame_counter == 115: 
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(222)
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 120: # 12 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(333)

                    if self.animation_frame_counter == 125: 
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(444)
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 130: # 13 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(555)

                    if self.animation_frame_counter == 135: 
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(666)
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 139: 
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(777)

                    if self.animation_frame_counter == 140: # 14 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("peso","energize")

                    if self.animation_frame_counter == 143: 
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(888)

                    if self.animation_frame_counter == 145: 
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 147:
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(999)

                    self.animation_frame_counter += 1
                    if self.animation_frame_counter >= 150: # 15 seconds
                        self.animation_frame_counter = 0
                else:
                    time.sleep(self.animaition_interval)

class Mode_Development(threading.Thread):
    """
    This class watches for incoming messages
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
        self.hosts.clear_games_with_players()
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.start()

    def begin(self):
        for pinball_hostname in self.pinball_hostnames:
            pinball = self.hosts.hostnames[pinball_hostname] 
            pinball.cmd_playfield_lights("all_radial","off")
            pinball.cmd_playfield_lights("sign_bottom_right","off")
            pinball.cmd_playfield_lights("sign_bottom_left","off")
            pinball.enable_izquierda_coil(False)
            pinball.enable_trueque_coil(False) # also initiate trade
            pinball.enable_dinero_coil(False)
            pinball.enable_kicker_coil(False)
            pinball.enable_derecha_coil(False)

        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
        # phrase: juega
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("juega")
        # ensure carousels are in correct position
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","sandia","sandia")
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_1","coco","back")        
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_2","naranja","back")        
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_3","mango","back")        
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_4","sandia","back")        
        #self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_5","pina","back")        
        self.hosts.clear_games_with_players()
        # self.animation.add_to_queue("begin")

    def end(self):
        self.animation.add_to_queue("end")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def event_button_comienza(self, message, origin, destination): 
        choreo = self.choreography
        sender = choero.carousels["coco"]
        receiver = choero.carousels["mango"]
        path = choreo.generate_path(sender, receiver)
        print(path)

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

