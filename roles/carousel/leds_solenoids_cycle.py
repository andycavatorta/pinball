import adafruit_tlc5947
import board
import busio
import digitalio
import queue
import RPi.GPIO as GPIO
import threading
import time




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

class Solenoids(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.eject_pulse_time = 0.05
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
                finally:
                    GPIO.output(solenoid_pin, GPIO.LOW)
            if action == "all_off":
                for solenoid_pin in self.solenoid_pins:
                    GPIO.output(solenoid_pin, GPIO.LOW)

solenoids = Solenoids()

led_groups = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]

]

solenoid_map = (
    [1],
    [0,1,2,3,4],
    [2],
    [3],
    [4],
    [0],
)

while True:
    for fruit_id in range(0,6):
        for led in led_groups[fruit_id]:
            pins[led].duty_cycle = 40000
        print("")
        for solenoid_channel in solenoid_map[fruit_id]:
            print(solenoid_channel, fruit_id)
            solenoids.add_to_queue("eject",solenoid_channel)

        time.sleep(.4)
        for led in led_groups[fruit_id]:
            pins[led].duty_cycle = 0
    time.sleep(15)

