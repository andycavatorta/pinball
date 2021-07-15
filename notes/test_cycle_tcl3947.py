import board
import busio
import digitalio
import adafruit_tlc5947
import time
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
latch = digitalio.DigitalInOut(board.D5)
tlc5947 = adafruit_tlc5947.TLC5947(spi, latch)

while True:
    for channel in range(23):
        print(channel, "on")
        tlc5947[channel] = 1023
    time.sleep(0.5)
    for channel in range(23):
        print(channel, "off")
        tlc5947[channel] = 0
    time.sleep(0.5)
