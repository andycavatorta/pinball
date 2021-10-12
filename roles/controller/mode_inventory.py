"""



"""
import codecs
import os
import queue
import settings
import threading
import time

class Mode_Inventory(threading.Thread):
    """
    When this system boots, there is no way to know how many balls are in the tubes.  
    This module 
        zeroes the motor positions in the matrix
        performs an inventory of the balls
        moves balls to populate tubes for game

    to do:
        write invenory algorithm
    """
    PHASE_ZERO = "phase_zero"
    PHASE_INVENTORY = "phase_inventory"
    PHASE_POPULATE = "phase_populate"
    def __init__(self, tb, hosts, set_current_mode):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.phase = self.PHASE_ZERO
        self.start()
        # self.hosts["pinballmatrix"].request_amt203_zeroed()
        # bypass inventory
        #self.set_current_mode(self.game_mode_names.ATTRACTION)

    def begin(self):
        #self.timer = time.time()
        self.active = True
        #skipping zeroing, inventory, and set_balls_for_game
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",3, 1)
        time.sleep(0.1)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",4, 1)
        time.sleep(0.1)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",5, 1)
        time.sleep(0.1)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",7, 1)
        time.sleep(0.1)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",8, 1)
        time.sleep(0.1)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("set_spoke",9, 1)
        time.sleep(0.1)
        self.set_current_mode(self.game_mode_names.ATTRACTION)
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].disable_gameplay()
        

    def end(self):
        self.active = False

    def set_amt203_zeroed(self,amt203_zeroed):
        if all(amt203_zeroed): # when all report finished.
            self.phase = self.PHASE_INVENTORY
            # start inventory

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

