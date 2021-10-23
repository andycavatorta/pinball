"""

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
        self.animation_frame_counter = 0
        self.animaition_interval = 0.1
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_center",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.mezzo_chimes = ["f_mezzo", "g_mezzo","gsharp_mezzo","asharp_mezzo","c_mezzo"]
        self.active = False
        self.start()

        ### bang ###
        # chime
        # bright fade

        ### wave expansion  ###
        # ----- numerals expand

        # ----- carouselcenter: peso fade in/out
        # ----- carouselcenter: inner_circle fade in/out
        # ----- carouselcenter: outer_circle fade in/out
        # ----- edge carousels:RIPPLE_1
        # ----- edge carousels:RIPPLE_2
        # ----- edge carousels:RIPPLE_3
        # ----- edge carousels:RIPPLE_4
        # ----- edge carousels:RIPPLE_5

        # ----- gamestations: ripple_1 - 47
        # ----- gamestations: ripple_2 - 46
        # ----- gamestations: ripple_3 - 45, 60
        # ----- gamestations: ripple_4 - 44, 61,
        # ----- gamestations: ripple_5 - 43, 38, 67, 62
        # ----- gamestations: ripple_6 - 42, 37, 68, 63
        # ----- gamestations: ripple_7 - 41, 36, 69, 64
        # ----- gamestations: ripple_8 - 40, 35, 50, 65
        # ----- gamestations: ripple_9 - 39, 34, 49, 66
        # ----- gamestations: ripple_10 - 32, 33, 48, 52, 53
        # ----- gamestations: ripple_11 - 31,30,51,
        # ----- gamestations: ripple_12 - 8, 27, 24,57,54,55,3
        # ----- gamestations: ripple_13 - 29, 28, 6, 4, 56
        # ----- gamestations: ripple_14 - 7, 15, 16, 5, 19, 25, 58, 20
        # ----- gamestations: ripple_15 - 12, 13, 14, 25, 58 21, 22, 23
        # ----- gamestations: ripple_16 - 26, 59,
        # ----- gamestations: ripple_17 - 11, 0
        # ----- gamestations: ripple_18 - 9,10, 1, 2

        ### reverse wave ###
        # ---- gamestations: button_percolation
        # ---- carouselcenter: peso energize

    def begin(self):
        print("mode_attraction.begin")
        self.animation_frame_counter = 0
        self.active = True

    def end(self):
        print("mode_attraction.end")
        self.active = False

    def add_to_queue(self, animation_command): # ["begin"|"end"]
        self.queue.put(animation_command)

    def run(self):
        while True:
            try:
                animation_command = self.queue.get(True,self.animaition_interval)
                print("mode_attraction.run 2",animation_command)
                if isinstance(animation_command, bytes):
                    animation_command = codecs.decode(animation_command, 'UTF-8')
                if animation_command == "begin":
                    self.begin()
                if animation_command == "end":
                    self.end()
            except queue.Empty:
                if self.active:
                    print("mode_attraction.run 4",self.animation_frame_counter)
                    if self.animation_frame_counter == 0: # 0 seconds
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("peso","throb")
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(999)
                        for hostname in self.display_hostnames:
                            if random.randrange(0,3) == 0:
                                self.hosts.hostnames[hostname].request_score(self.mezzo_chimes[random.randrange(0,5)])
                    if self.animation_frame_counter == 3:
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("inner_circle","throb")

                    if self.animation_frame_counter == 5: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)

                    if self.animation_frame_counter == 6:
                        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("outer_circle","throb")

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
                        self.hosts.hostnames["carousel1"].cmd_carousel_lights("ripple_1","throb")
                        self.hosts.hostnames["carousel2"].cmd_carousel_lights("ripple_naranja_5","throb")
                        self.hosts.hostnames["carousel3"].cmd_carousel_lights("ripple_mango_5","throb")
                        self.hosts.hostnames["carousel4"].cmd_carousel_lights("ripple_sandia_5","throb")
                        self.hosts.hostnames["carousel5"].cmd_carousel_lights("ripple_pina_5","throb")

                    if self.animation_frame_counter == 25: # 0 seconds                        
                        for pinball_hostname in self.pinball_hostnames:
                             self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 27:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_1","throb")

                    if self.animation_frame_counter == 30: # 3 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(666)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_2","throb")

                    if self.animation_frame_counter == 33:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_3","throb")

                    if self.animation_frame_counter == 35: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 37:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_4","throb")

                    if self.animation_frame_counter == 40: # 4 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(555)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_5","throb")

                    if self.animation_frame_counter == 43:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_6","throb")

                    if self.animation_frame_counter == 45: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 47:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_7","throb")

                    if self.animation_frame_counter == 50: # 5 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(444)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_8","throb")

                    if self.animation_frame_counter == 53:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_9","throb")

                    if self.animation_frame_counter == 55: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 57:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_10","throb")

                    if self.animation_frame_counter == 60: # 6 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(333)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_11","throb")

                    if self.animation_frame_counter == 63:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_12","throb")

                    if self.animation_frame_counter == 65: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        
                    if self.animation_frame_counter == 67:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_13","throb")

                    if self.animation_frame_counter == 70: # 7 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(222)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_14","throb")

                    if self.animation_frame_counter == 73:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_15","throb")

                    if self.animation_frame_counter == 75: # 0 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
                        

                    if self.animation_frame_counter == 77:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_16","throb")

                    if self.animation_frame_counter == 80: # 8 seconds
                        
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_number(111)
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_17","throb")

                    if self.animation_frame_counter == 83:
                        for pinball_hostname in self.pinball_hostnames:
                            self.hosts.hostnames[pinball_hostname].cmd_carousel_lights("ripple_18","throb")

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
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.start()

    def begin(self):
        print("mode_attraction.begin 1")
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all","off")
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("sign_bottom_left","on")
            self.hosts.hostnames[pinball_hostname].disable_gameplay()
        print("mode_attraction.begin 2")
        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
        # phrase: juega
        print("mode_attraction.begin 3")
        #for display_hostname in self.display_hostnames:
        #    self.hosts.hostnames[pinball_hostname].request_phrase("juega")
        # ensure carousels are in correct position
        print("mode_attraction.begin 4")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","sandia","sandia")
        print("mode_attraction.begin 5")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_1","coco","back")        
        print("mode_attraction.begin 6")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_2","naranja","back")        
        print("mode_attraction.begin 7")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_3","mango","back")        
        print("mode_attraction.begin 8")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_4","sandia","back")        
        print("mode_attraction.begin 9")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_5","pina","back")        
        print("mode_attraction.begin 10")
        self.hosts.mode_countdown_states["comienza_button_order"] = []
        print("mode_attraction.begin 11")
        self.animation.add_to_queue("begin")
        print("mode_attraction.begin 12")

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

