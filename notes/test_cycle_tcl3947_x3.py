import board
import busio
import digitalio
import adafruit_tlc5947
import time
    
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
latch = digitalio.DigitalInOut(board.D26)
number_of_boards = 3
number_of_channels = number_of_boards * 24
tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=number_of_boards)


pins = [0]*(number_of_channels)

for channel in range(len(pins)):
    pins[channel] = tlc5947.create_pwm_out(channel)

while True:
    for channel in range(number_of_channels):
        pins[channel].duty_cycle = 50000
        print("channel=", channel)
        time.sleep(.2)
        pins[channel].duty_cycle = 0

