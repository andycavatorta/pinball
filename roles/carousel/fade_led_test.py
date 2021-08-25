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


outer_radius = [3, 0, 11, 8, 15, 12, 19, 16, 23, 20]

inner_radius = [2, 1, 10, 9, 14, 13, 18, 17, 22, 21]

led_groups = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]

]

duty_cycle_low = 5000
duty_cycle_med = 10000
duty_cycle_hi = 50000


while True:
    for radius in range(10):
        pins[outer_radius[radius-3]].duty_cycle = duty_cycle_low
        pins[inner_radius[radius-3]].duty_cycle = duty_cycle_low

        pins[outer_radius[radius-2]].duty_cycle = duty_cycle_med
        pins[inner_radius[radius-2]].duty_cycle = duty_cycle_med

        pins[outer_radius[radius-1]].duty_cycle = duty_cycle_hi
        pins[inner_radius[radius-1]].duty_cycle = duty_cycle_hi

        pins[outer_radius[radius]].duty_cycle = duty_cycle_med
        pins[inner_radius[radius]].duty_cycle = duty_cycle_med
        time.sleep(0.1)
