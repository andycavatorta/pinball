import adafruit_tlc5947
import board
import busio
import digitalio
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

led_groups = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]

]

while True:
    for led_group in led_groups:
        for led in led_group:
            pins[led].duty_cycle = 40000
        time.sleep(.8)
        for led in led_group:
            pins[led].duty_cycle = 0
        time.sleep(.8)

    for channel in range(number_of_channels):
        pins[channel].duty_cycle = 4000
        print("channel=", channel)
        time.sleep(.25)
        pins[channel].duty_cycle = 0

