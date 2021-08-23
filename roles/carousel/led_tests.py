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
    
]

while True:
    for channel in range(number_of_channels):
        pins[channel].duty_cycle = 5000
        print("channel=", channel)
        time.sleep(.2)
        pins[channel].duty_cycle = 0

