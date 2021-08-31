import os
import queue
import threading
import time

class Mode_Waiting_For_Connections(threading.Thread):
    """
    In Waiting_For_Connections mode, the controller is waiting until Thirtybirds 
    establishes connections from all hosts.
    """
    def __init__(self,tb, host_states):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.host_states = host_states
        # self.required_hosts = set(settings.Roles.hosts.keys())
        self.queue = queue.Queue()
        self.start()
    def add_to_queue(self, topic, message, origin, destination):
        """
        receives messages about thirtybirds connections initially received by network_message_handler
        """
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                all_hosts_are_connected, connected_hosts_d = self.tb.check_connections()
                # loop through self.required_hosts
                    # set host_states[hostname].set_connected() to connected_hosts_d[hostname]
                # ^^^ this could all be done in main. gotta do almost everything in main or in mode classes.
                # if all_hosts_are_connected == True
                    # if current mode is settings.Game_Modes.WAITING_FOR_CONNECTIONS
                        # transition to settings.Game_Modes.SYSTEM_TESTS
                # else
                    # if current mode is not settings.Game_Modes.WAITING_FOR_CONNECTIONS
                        # log loss of connection
                        # transition to settings.Game_Modes.WAITING_FOR_CONNECTIONS
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

