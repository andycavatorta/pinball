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
    def __init__(self, tb, hosts, mode_manager):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.hosts = hosts
        self.mode_manager = mode_manager
        self.queue = queue.Queue()
        self.motor_names = ['carousel_1','carousel_2','carousel_3','carousel_4','carousel_5','carousel_6']
        self.phase = self.PHASE_COMPUTER_DETAILS
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 20 #seconds
        self.start()

    def reset(self):
        self.timer = time.time()
        self.phase = self.PHASE_COMPUTER_DETAILS
        self.hosts.all.request_computer_details()
        #self.tb.publish("request_computer_details",None)

    def respond_host_connected(self, message, origin, destination):
        # inappropriate response
        # if message is False, change mode back to Wait_For_Connections
        if message == False:
            self.mode_manager.set_mode(self.game_mode_names.WAITING_FOR_CONNECTIONS)

    def respond_computer_details(self, message, origin, destination):
        # if self.hosts responds that all self.hosts have reported details
        #     send request for hardware presence
        if self.phase == self.PHASE_COMPUTER_DETAILS:
            if self.hosts.all.get_computer_details_received() == True:
                self.phase = self.PHASE_DEVICE_PRESENCE
                self.tb.publish("request_amt203_present",None)
                self.tb.publish("request_sdc2160_present",None)
                self.tb.publish("request_current_sensor_present",None)
                self.timer = time.time()

    # presence
    def _check_presence_(self):
        if self.phase == self.PHASE_DEVICE_PRESENCE:
            if self.hosts.all.amt203_present() == True:
                if self.hosts.all.sdc2160_present() == True:
                    if self.hosts.all.current_sensor_present() == True:
                        self.phase = self.PHASE_DEVICE_STATES
                        self.tb.publish("respond_current_sensor_value",None)
                        self.tb.publish("respond_current_sensor_nominal",None)
                        self.tb.publish("respond_current_sensor_present",None)
                        self.tb.publish("request_amt203_absolute_position",None)
                        self.tb.publish("request_sdc2160_relative_position",None)
                        self.tb.publish("request_sdc2160_closed_loop_error",None)
                        self.tb.publish("request_sdc2160_channel_faults",None)
                        self.tb.publish("request_sdc2160_controller_faults",None)
                        self.tb.publish("request_amt203_zeroed",None)
                        self.timer = time.time()

    def respond_amt203_present(self, message, origin, destination):
        self._check_presence_()

    def respond_sdc2160_present(self, message, origin, destination):
        self._check_presence_()

    def respond_current_sensor_present(self, message, origin, destination):
        self._check_presence_()

    # device states
    def _check_all_device_states_(self):
        if self.phase == self.PHASE_DEVICE_STATES:
            if self.hosts.all.current_sensor_value() == True:
                if self.hosts.all.amt203_absolute_position() == True:
                    if self.hosts.all.sdc2160_relative_position() == True:
                        if self.hosts.all.sdc2160_channel_faults() == True:
                            if self.hosts.all.sdc2160_controller_faults() == True:
                                if self.hosts.all.sdc2160_closed_loop_error() == True:
                                    if self.hosts.all.amt203_zeroed() == True:
                                        self.phase = self.PHASE_CHECK_CURRENT_LEAK
                                        self.tb.publish("request_current_sensor_nominal",None)
                                        self.timer = time.time()


    def respond_current_sensor_nominal(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        if self.hosts.all.current_sensor_value() == True:
            self.timer = time.time()
            self.phase = self.PHASE_VISUAL_TESTS
            self.tb.publish("request_visual_tests",None)

    def respond_current_sensor_value(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_amt203_absolute_position(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_sdc2160_relative_position(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_sdc2160_channel_faults(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_sdc2160_controller_faults(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_sdc2160_closed_loop_error(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_amt203_zeroed(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self._check_all_device_states_()

    def respond_visual_tests(self, message, origin, destination):
        # No need to pass params.  Hosts handles this.
        # This is just responding to the events
        self.mode_manager.set_mode(self.game_mode_names.INVENTORY)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True,1)
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')
                getattr(self,topic)(message, origin, destination)
            except queue.Empty:
                if self.phase != self.PHASE_VISUAL_TESTS:
                    if self.timer + self.timeout_duration < time.time(): # if timeout condition
                        self.mode_manager.set_mode(self.game_mode_names.ERROR)
