import queue
import RPi.GPIO as GPIO
import threading
import time
import traceback


GPIO.setmode( GPIO.BCM )


class GPIO_Switch():
    def __init__(self, gpio_pin):
        self.gpio_pin = gpio_pin
        self.last_value = 0
        GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP )
    def read(self):
        value = GPIO.input(self.gpio_pin)
        if self.last_value == value:
            return -1
        self.last_value = value
        return value

class Scanner(threading.Thread):
    def __init__(self, switch_event_receiver):
        threading.Thread.__init__(self)
        self.switch_event_receiver = switch_event_receiver
        self.switches = {
            "derecho" : GPIO_Switch(24),
            "trueque" : GPIO_Switch(15),
            "comienza" : GPIO_Switch(18),
            "dinero" : GPIO_Switch(23),
            "izquierda" : GPIO_Switch(14),
            "spinner" : GPIO_Switch(1),
            "roll_outer_left" : GPIO_Switch(12),
            "roll_outer_right" : GPIO_Switch(21),
            "roll_inner_left" : GPIO_Switch(16),
            "roll_inner_right" : GPIO_Switch(20),
            "trough" : GPIO_Switch(25),
            "beam_left" : GPIO_Switch(17),
            "beam_right" : GPIO_Switch(27),
        }
        self.start()

    def run(self):
        while True:
            for switch_name in self.switches:
                switch_value = self.switches[switch_name].read()
                if switch_value != -1: # if the value has changed
                    self.switch_event_receiver(switch_name,switch_value)
                    time.sleep(0.05)

def receiver(switch_name,switch_value):
    print(switch_name,switch_value)


scanner = Scanner(receiver)
