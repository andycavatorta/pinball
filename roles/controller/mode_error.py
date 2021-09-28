import codecs
import os
import queue
import settings
import threading
import time

class Mode_Error(threading.Thread):
    """
    These mode modules are classes to help keep the namespace organizes
    These mode modules are threaded because some of them will have time-based tasks.

    inventory carousels
    evacuate center carousel to edge carousels
    evacuate edge carousels into dinero tube
    evacuate fruits carousels into dinero tube via carousel

    """
    def __init__(self, tb, hosts, set_mode):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.set_mode = set_mode
        self.queue = queue.Queue()
        self.motor_names = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6']
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        #self.start()

    def reset(self):
        #retrieve error states from hosts
        #self.timer = time.time()
        errors = self.hosts.errors.get_all()
        print("vvvvvvvvvvvvvvvvvvvvvvv")
        print("vvvvvvvvvvvvvvvvvvvvvvv")
        print(errors)
        print("^^^^^^^^^^^^^^^^^^^^^^^")
        print("^^^^^^^^^^^^^^^^^^^^^^^")

    def respond_host_connected(self, message, origin, destination): 
        if self.hosts.all.get_host_connected() == True:
            self.set_mode(self.game_mode_names.SYSTEM_TESTS)

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

    def request_current_sensor_nominal(self, message, origin, destination):
        # TODO: Make the ACTUAL test here.
        return True

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
            except queue.Empty:
                pass
                #if self.timer + self.timeout_duration < time.time(): # if timeout condition
                #    self.set_mode(self.game_mode_names.ERROR)

            except AttributeError:
                pass
