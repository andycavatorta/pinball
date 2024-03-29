import queue
import RPi.GPIO as GPIO
import time
import threading

class Solenoids(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.eject_pulse_time = 0.03
        GPIO.setmode(GPIO.BCM)
        self.solenoid_pins = [1,2,3,4,5] # todo: update later
        self.fruit_names = {
            "coco":1,
            "naranja":2,
            "mango":3,
            "sandia":4,
            "pina":5,
        }
        for solenoid_pin in self.solenoid_pins:
            GPIO.setup(solenoid_pin, GPIO.OUT)
            GPIO.output(solenoid_pin, GPIO.LOW)
        self.start()

    def test_cycle(self, number_of_cycles=1):
        for cycle in range(number_of_cycles):
            for fruit_id in range(0,5):
                self.add_to_queue("eject",fruit_id)
                time.sleep(.5)

    def add_to_queue(self, action, fruit_name):
        self.queue.put((action, fruit_name))

    def run(self):
        while True:
            action, fruit_name = self.queue.get(True)
            print(action, fruit_name)
            if action == "eject":
                solenoid_pin = self.fruit_names[fruit_name]
                #solenoid_pin = self.solenoid_pins[fruit_id]
                try:
                    GPIO.output(solenoid_pin, GPIO.HIGH)
                    time.sleep(self.eject_pulse_time)
                    GPIO.output(solenoid_pin, GPIO.LOW)
                finally:
                    GPIO.output(solenoid_pin, GPIO.LOW)
            if action == "all_off":
                for solenoid_pin in self.solenoid_pins:
                    GPIO.output(solenoid_pin, GPIO.LOW)

