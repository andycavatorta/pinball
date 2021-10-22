"""
"""

import codecs
import os
import queue
import settings
import threading
import time

class Mode_Waiting_For_Connections(threading.Thread):
    """
    These mode modules are classes to help keep the namespace organizes
    These mode modules are threaded because some of them will have time-based tasks.

    inventory carousels
    evacuate center carousel to edge carousels
    evacuate edge carousels into dinero tube
    evacuate fruits carousels into dinero tube via carousel

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
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.all_hostnames = [
            "controller",
            "pinball1game",
            "pinball2game",
            "pinball3game",
            "pinball4game",
            "pinball5game",
            "pinball1display",
            "pinball2display",
            "pinball3display",
            "pinball4display",
            "pinball5display",
            "pinballmatrix",
            "carousel1",
            "carousel2",
            "carousel3",
            "carousel4",
            "carousel5",
            "carouselcenter"]
        self.connected_hostnames = ["controller"]
        self.start()

    def begin(self):
        self.connected_hostnames = ["controller"]

        self.hosts.hostnames["carousel1"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel2"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel3"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel4"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel5"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("all","off")
        #self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("solid","all",0)
        self.timer = time.time()
        self.active = True
        #for pinball_hostname in self.connected_hostnames:
        #    self.hosts.hostnames[pinball_hostname].disable_gameplay()

    def end(self):
        self.active = False

    def respond_host_connected(self, message, origin, destination): 
        self.connected_hostnames.append(origin)
        for pinball_hostname in self.connected_hostnames: # cycle through all of these on each connection because carousels may connect after other hosts
            if pinball_hostname == "controller":
                self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinball1game":
                self.hosts.hostnames["carousel1"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "pinball2game":
                self.hosts.hostnames["carousel2"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "pinball3game":
                self.hosts.hostnames["carousel3"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "pinball4game":
                self.hosts.hostnames["carousel4"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "pinball5game":
                self.hosts.hostnames["carousel5"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "pinball1display":
                self.hosts.hostnames["carousel1"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinball2display":
                self.hosts.hostnames["carousel2"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinball3display":
                self.hosts.hostnames["carousel3"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinball4display":
                self.hosts.hostnames["carousel4"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinball5display":
                self.hosts.hostnames["carousel5"].cmd_carousel_lights("inner_circle","on")
            if pinball_hostname == "pinballmatrix":
                self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("outer_circle","on")
            if pinball_hostname == "carousel1":
                self.hosts.hostnames["carousel1"].cmd_carousel_lights("peso","on")
            if pinball_hostname == "carousel2":
                self.hosts.hostnames["carousel2"].cmd_carousel_lights("peso","on")
            if pinball_hostname == "carousel3":
                self.hosts.hostnames["carousel3"].cmd_carousel_lights("peso","on")
            if pinball_hostname == "carousel4":
                self.hosts.hostnames["carousel4"].cmd_carousel_lights("peso","on")
            if pinball_hostname == "carousel5":
                self.hosts.hostnames["carousel5"].cmd_carousel_lights("peso","on")
            if pinball_hostname == "carouselcenter":
                self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("peso","on")

        if self.hosts.get_all_host_connected() == True:
            #self.hosts.hostnames["carouselcenter"].cmd_carousel_all_off()
            #self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("solid","spoke_1",8)
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            if self.active:
                try:
                    topic, message, origin, destination = self.queue.get(True,5)
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
                except queue.Empty:
                    if self.timer + self.timeout_duration < time.time(): # if timeout condition
                        self.set_current_mode(self.game_mode_names.ERROR)

                except AttributeError:
                    pass
            else:
                time.sleep(1)
