import adafruit_tlc5947
import board
import busio
import digitalio
import queue
import RPi.GPIO as GPIO
import threading
import time
import random


SCK = board.SCK
MOSI = board.MOSI
LATCH = digitalio.DigitalInOut(board.D26)

number_of_boards = 1
number_of_channels = number_of_boards * 24

spi = busio.SPI(clock=SCK, MOSI=MOSI)

tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH)

pins = [0]*(number_of_channels)

for channel in range(len(pins)):
    pins[channel] = tlc5947.create_pwm_out(channel)


outer_radius = [3, 0, 11, 8, 15, 12, 16, 19, 20, 23]

inner_radius = [2, 1, 10, 9, 14, 13, 17, 18, 21, 22]

center_group = [4,5,6,7]

led_groups = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]

]

duty_cycle_low = 1000
duty_cycle_med = 10000
duty_cycle_hi = 20000
duty_cycle_xhi = 50000

class Solenoids(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.eject_pulse_time = 0.08
        GPIO.setmode(GPIO.BCM)
        self.solenoid_pins = [1,2,3,4,5] # todo: update later
        for solenoid_pin in self.solenoid_pins:
            GPIO.setup(solenoid_pin, GPIO.OUT)
            GPIO.output(solenoid_pin, GPIO.LOW)
        self.start()

    def test_cycle(self, number_of_cycles=1):
        for cycle in range(number_of_cycles):
            for fruit_id in range(0,5):
                self.add_to_queue("eject",fruit_id)
                time.sleep(.5)

    def add_to_queue(self, action, fruit_id = None):
        self.queue.put((action, fruit_id))

    def run(self):
        while True:
            action, fruit_id = self.queue.get(True)
            print(action, fruit_id)
            if action == "eject":
                solenoid_pin = self.solenoid_pins[fruit_id]
                try:
                    GPIO.output(solenoid_pin, GPIO.HIGH)
                    time.sleep(self.eject_pulse_time)
                    GPIO.output(solenoid_pin, GPIO.LOW)
                    time.sleep(self.eject_pulse_time)
                finally:
                    GPIO.output(solenoid_pin, GPIO.LOW)
            if action == "all_off":
                for solenoid_pin in self.solenoid_pins:
                    GPIO.output(solenoid_pin, GPIO.LOW)

solenoids = Solenoids()

def start():
    while True:
        for radial_cycle in range(10):
            for radius in range(10):

                pins[outer_radius[radius-5]].duty_cycle = duty_cycle_low
                pins[inner_radius[radius-5]].duty_cycle = duty_cycle_low

                pins[outer_radius[radius-4]].duty_cycle = duty_cycle_med
                pins[inner_radius[radius-4]].duty_cycle = duty_cycle_med

                pins[outer_radius[radius-3]].duty_cycle = duty_cycle_hi
                pins[inner_radius[radius-3]].duty_cycle = duty_cycle_hi

                pins[outer_radius[radius-2]].duty_cycle = duty_cycle_hi
                pins[inner_radius[radius-2]].duty_cycle = duty_cycle_hi

                pins[outer_radius[radius-1]].duty_cycle = duty_cycle_hi
                pins[inner_radius[radius-1]].duty_cycle = duty_cycle_hi

                pins[outer_radius[radius]].duty_cycle = duty_cycle_med
                pins[inner_radius[radius]].duty_cycle = duty_cycle_med
                time.sleep(0.05)

        random_int = random.randint(0,10)
        for radius in range(10):
            pins[outer_radius[radius]].duty_cycle = 0
            pins[inner_radius[radius]].duty_cycle = 0
            if random_int ==0:
                if radius % 2 == 0:
                    solenoids.add_to_queue("eject",int(radius/2))
                    solenoids.add_to_queue("eject",int(radius/2))
                    solenoids.add_to_queue("eject",int(radius/2))

            time.sleep(0.1)

        for throb_step in [0,duty_cycle_low,duty_cycle_med,duty_cycle_hi,duty_cycle_xhi,duty_cycle_hi,duty_cycle_med,duty_cycle_low,0]:
            for pin in center_group:
                pins[pin].duty_cycle = throb_step
            time.sleep(0.05)
        time.sleep(0.1)
