import os
import queue
import settings
import threading
import time

class Mode_System_Tests(threading.Thread):
    """
    These mode modules are classes to help keep the namespace organizes
    These mode modules are threaded because some of them will have time-based tasks.

    evacuate carousels
    """
    def __init__(self, tb, hosts, mode_manager):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.mode_manager = mode_manager
        self.queue = queue.Queue()
        self.motor_names = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6']
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.start()

    def reset(self):
        self.timer = time.time()
        self.tb.publish("request_computer_details",None)

    def respond_host_connected(self, message, origin, destination): 
        if hosts.all.host_connected() == True:
            self.mode_manager.set_mode(self.game_mode_names.System_Tests)

    def respond_computer_details(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_amt203_present(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_sdc2160_present(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_current_sensor_value(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_current_sensor_nominal(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_current_sensor_present(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_amt203_absolute_position(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_sdc2160_relative_position(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_sdc2160_channel_faults(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_sdc2160_controller_faults(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_sdc2160_closed_loop_error(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_amt203_zeroed(self, message, origin, destination):
        # inappropriate response
        pass

    def respond_visual_tests(self, message, origin, destination):
        # inappropriate response
        pass

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True,1)
                getattr(self,topic)(message, origin, destination)
            except queue.Empty:
                if self.timer + self.timeout_duration < time.time(): # if timeout condition
                    self.mode_manager.set_mode(self.game_mode_names.ERROR)

