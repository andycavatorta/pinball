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
    def __init__(self, tb, hosts, mode_names, set_current_mode):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.mode_names = mode_names
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.start()

    def reset(self):
        self.timer = time.time()

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.get_all_host_connected() == True:
            self.set_current_mode(self.game_mode_names.SYSTEM_TESTS)
    
    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
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

