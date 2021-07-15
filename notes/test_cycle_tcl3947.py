import board
import busio
import digitalio
import adafruit_tlc5947
import time

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
latch = digitalio.DigitalInOut(board.D5)
tlc5947 = adafruit_tlc5947.TLC5947(spi, latch)

pins = []
for channel in range(23):
    pin[channel] = tlc5947.create_pwm_out(channel)


while True:
    for pwm in range(0, 30000, 10):
        for channel in range(23):
            pins[channel].duty_cycle = pwm
"""
while True:
    for channel in range(23):
        print(channel, "on")
        tlc5947[channel] = 1023
    time.sleep(0.5)
    for channel in range(23):
        print(channel, "off")
        tlc5947[channel] = 0
    time.sleep(0.5)




import board
import busio
import digitalio

import adafruit_tlc5947

SCK = board.SCK
MOSI = board.MOSI
LATCH = digitalio.DigitalInOut(board.D5)

spi = busio.SPI(clock=SCK, MOSI=MOSI)

tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH)

red = tlc5947.create_pwm_out(0)
green = tlc5947.create_pwm_out(1)
blue = tlc5947.create_pwm_out(2)

step = 10
start_pwm = 0
end_pwm = 32767  # 50% (32767, or half of the maximum 65535):

while True:
    for pin in (red, green, blue):
        # Brighten:
        print("Brightening LED")
        for pwm in range(start_pwm, end_pwm, step):
            pin.duty_cycle = pwm

        # Dim:
        print("Dimming LED")
        for pwm in range(end_pwm, start_pwm, 0 - step):
            pin.duty_cycle = pwm

"""