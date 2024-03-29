"""
All displays off
All carousel LEDs off
All playfield LEDs off

turn on all $ in carousels



"""

import codecs
import os
import queue
import settings
import threading
import time

class Mode_System_Tests(threading.Thread):
    """
    These mode modules are classes to help keep the namespace organizes
    These mode modules are threaded because some of them will have time-based tasks.
    """
    PHASE_COMPUTER_DETAILS = "phase_computer_details"
    PHASE_DEVICE_PRESENCE = "phase_device_presence"
    PHASE_DEVICE_STATES = "phase_device_states"
    PHASE_CHECK_CURRENT_LEAK = "phase_check_current_leak"
    PHASE_VISUAL_TESTS = "phase_visual_tests"
    def __init__(self, tb, hosts, set_current_mode):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb
        self.hosts = hosts
        self.set_mode = set_current_mode
        self.queue = queue.Queue()
        self.motor_names = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_center']
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.phase = self.PHASE_COMPUTER_DETAILS
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 20 #seconds
        self.start()

    def begin(self):
        self.active = True
        self.timer = time.time()

        self.hosts.hostnames["carousel1"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel2"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel3"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel4"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carousel5"].cmd_carousel_lights("all","off")
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("all","off")

        self.phase = self.PHASE_COMPUTER_DETAILS
        #self.hosts.pinballmatrix.response_high_power_enabled()
        time.sleep(10)
        self.hosts.request_all_computer_details()

    def end(self):
        self.active = False


    def reset(self):
        self.timer = time.time()
        self.phase = self.PHASE_COMPUTER_DETAILS
        self.hosts.request_all_computer_details()
        print("")
        print("===========PHASE_COMPUTER_DETAILS============")
        print("")
        #self.tb.publish("request_computer_details",None)


    def response_host_connected(self, message, origin, destination):
        # inappropriate response
        # if message is False, change mode back to Wait_For_Connections
        if message == False:
            self.set_mode(self.game_mode_names.WAITING_FOR_CONNECTIONS)


    def response_computer_details(self, message, origin, destination):
        if self.phase == self.PHASE_COMPUTER_DETAILS:
            if self.hosts.get_all_computer_details_received() == True:
                self.phase = self.PHASE_DEVICE_STATES
                # when all computers details have responded
                self._check_all_device_states_()


    # device states
    def _check_all_device_states_(self):
        if self.phase == self.PHASE_DEVICE_STATES:
            if len(self.hosts.get_all_non_nominal_states()) == 0:

                self.set_mode(self.game_mode_names.INVENTORY)
                #print("")
                #print("===========PHASE_CHECK_CURRENT_LEAK============")
                #print("")
                #self.tb.publish("request_current_sensor_nominal",None)
                #self.timer = time.time()
            else:
                print("")
                print("non-nominal states reported")
                print(self.hosts.get_all_non_nominal_states())
                print("")
                self.set_mode(self.game_mode_names.ERROR)

    """
    def response_current_sensor_nominal(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        if self.hosts.get_all_current_sensor_nominal() == True:
            self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("all","off")
            if self.active:
                print("+++++++++++++++")
                self.set_mode(self.game_mode_names.INVENTORY)
                print("-----------------")
            #print("")
            #print("===========PHASE_VISUAL_TESTS============")
            #print("")
            #self.timer = time.time()
            #self.phase = self.PHASE_VISUAL_TESTS
            #self.tb.publish("request_visual_tests",None)
    """
    """
    def response_current_sensor_value(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()
    """

    def response_visual_tests(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self.set_mode(self.game_mode_names.INVENTORY)

    """
    def request_current_sensor_nominal(self, message, origin, destination):
        # TODO: Make the ACTUAL test here.
        return True
    """

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))


    def run(self):
        while True:
            if self.active:
                try:
                    topic, message, origin, destination = self.queue.get(True,1)
                    #print("in Mode_System_Tests",topic, message, origin, destination)
                    if isinstance(topic, bytes):
                        topic = codecs.decode(topic, 'UTF-8')
                    if isinstance(message, bytes):
                        message = codecs.decode(message, 'UTF-8')
                    if isinstance(origin, bytes):
                        origin = codecs.decode(origin, 'UTF-8')
                    if isinstance(destination, bytes):
                        destination = codecs.decode(destination, 'UTF-8')
                    #print("topic",topic)
                    #print("getattr(self,topic)",getattr(self,topic))
                    getattr(self,topic)(
                            message, 
                            origin, 
                            destination,
                        )
                    #getattr(self,topic)(message, origin, destination)
                    
                except queue.Empty:
                    pass
                    """
                    if self.phase != self.PHASE_VISUAL_TESTS:
                        if self.timer + self.timeout_duration < time.time(): # if timeout condition
                            self.hosts.errors.set_timeout = [self.phase]
                            self.set_mode(self.game_mode_names.ERROR)
                    """
                except AttributeError:
                    pass
            else:
                time.sleep(1)
