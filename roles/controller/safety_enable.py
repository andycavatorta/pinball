import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time

import settings

class Safety_Enable(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(settings.Deadman.GPIO, GPIO.OUT )
        GPIO.output(settings.Deadman.GPIO, GPIO.LOW)
        self.enabled = False # used for detecting when state changes
        self.queue = queue.Queue()
        self.handler = handler
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        self.hosts_alive = set()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            time.sleep(settings.Deadman.DURATION)
            try:
                while True:
                    deadman_message = self.queue.get(False)
                    topic, message, origin, destination = deadman_message
                    self.hosts_alive.add(origin)
            except queue.Empty:
                pass
            missing_hosts = self.required_hosts.difference(self.hosts_alive)
            if len(missing_hosts) > 0:
                print("missing_hosts=",missing_hosts)
            #if len(missing_hosts) > 0:
            #    print("missing hosts:", self.required_hosts.difference(self.hosts_alive))
            if self.required_hosts.issubset(self.hosts_alive):
                if not self.enabled: # if transtioning states
                    self.enabled = True
                    self.handler(self.enabled)
                GPIO.output(settings.Deadman.GPIO, GPIO.HIGH)
                time.sleep(settings.Deadman.DURATION)
                GPIO.output(settings.Deadman.GPIO, GPIO.LOW)
            else:
                if self.enabled: # if transtioning states
                    self.enabled = False
                    self.handler(self.enabled)
            self.hosts_alive = set()
            