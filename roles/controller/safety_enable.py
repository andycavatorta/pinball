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
        GPIO.output(settings.Deadman.GPIO, GPIO.HIGH)
        self.enabled = False # used for detecting when state changes
        self.active = True # used for setting the general state to on or off
        self.queue = queue.Queue()
        self.handler = handler
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        self.hosts_alive = set()
        self.start()

    def set_active(self, active):
        self.queue.put((b"set_active", active, "", ""))

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        last_missing_hosts = {}
        while True:
            time.sleep(settings.Deadman.DURATION)
            try:
                while True:
                    deadman_message = self.queue.get(False)
                    topic, message, origin, destination = deadman_message
                    if topic==b"deadman":
                        self.hosts_alive.add(origin)
                    if topic==b"set_active":
                        self.active = message

            except queue.Empty:
                pass
            missing_hosts = self.required_hosts.difference(self.hosts_alive)
            if missing_hosts != last_missing_hosts:
                if len(missing_hosts) > 0:
                    print("missing_hosts=",missing_hosts)
                    last_missing_hosts = missing_hosts
            #if len(missing_hosts) > 0:
            #    print("missing hosts:", self.required_hosts.difference(self.hosts_alive))
            if self.required_hosts.issubset(self.hosts_alive):
                if not self.enabled: # if transtioning states
                    self.enabled = True
                    self.handler(self.enabled)
                if self.active:
                    GPIO.output(settings.Deadman.GPIO, GPIO.HIGH)
                    time.sleep(settings.Deadman.DURATION)
                    GPIO.output(settings.Deadman.GPIO, GPIO.LOW)
                else:
                    time.sleep(settings.Deadman.DURATION)
            else:
                if self.enabled: # if transtioning states
                    self.enabled = False
                    self.handler(self.enabled)
            self.hosts_alive = set()
            