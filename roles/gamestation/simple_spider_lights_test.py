import adafruit_tlc5947
import board
import busio
import digitalio
import time

SCK = board.SCK
MOSI = board.MOSI
LATCH = digitalio.DigitalInOut(board.D26)

number_of_boards = 3
number_of_channels = number_of_boards * 24

spi = busio.SPI(clock=SCK, MOSI=MOSI)

tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH,num_drivers=number_of_boards)

pins = [0]*(number_of_channels)

print("number of pins=", len(pins))

for channel in range(len(pins)):
    print(channel)
    pins[channel] = tlc5947.create_pwm_out(channel)

groups = {
    "TRAIL_ROLLOVER_RIGHT" : [16,15,14,13,12],
    "TRAIL_ROLLOVER_LEFT" : [19,20,21,22,23],
    "TRAIL_SLING_RIGHT" : [11,10,9],
    "TRAIL_SLING_LEFT" : [0,1,2],
    "TRAIL_POP_LEFT" :  [66,65,64,63,62,61,60],
    "TRAIL_POP_CENTER" : [69,68,67],
    "TRAIL_POP_RIGHT" :  [36,37,38],
    "TRAIL_SPINNER" : [39,40,41,42,43,44,45,46,47],
    "PIE_ROLLOVER_RIGHT" : [27,28,29],
    "PIE_ROLLOVER_LEFT" : [54,55,56],
    "PIE_SLING_RIGHT" : [24,25,26],
    "PIE_SLING_LEFT" : [57,58,59],
    "PIE_POP_LEFT" :  [51,52,52],
    "PIE_POP_CENTER" : [48,49,50],
    "PIE_POP_RIGHT" :  [33,34,35],
    "PIE_SPINNER" : [30,31,32],
    "SIGN_ARROW_LEFT" : [5,4,3],
    "SIGN_ARROW_RIGHT" : [6,7,8],
    "SIGN_BOTTOM_LEFT" : [17],
    "SIGN_BOTTOM_RIGHT" : [18],
    "SIGN_TOP" : [70,71],
}

group_names = [
    "PIE_ROLLOVER_RIGHT",
    "PIE_ROLLOVER_LEFT",
    "PIE_SLING_RIGHT",
    "PIE_SLING_LEFT",
    "PIE_SPINNER",
    "PIE_POP_RIGHT",
    "PIE_POP_CENTER",
    "PIE_POP_LEFT",
    "SIGN_ARROW_RIGHT",
    "SIGN_ARROW_LEFT",
    "SIGN_BOTTOM_RIGHT",
    "SIGN_BOTTOM_LEFT",
    "SIGN_TOP",
    "TRAIL_ROLLOVER_RIGHT",
    "TRAIL_ROLLOVER_LEFT",
    "TRAIL_SLING_RIGHT",
    "TRAIL_SLING_LEFT",
    "TRAIL_SPINNER",
    "TRAIL_POP_RIGHT",
    "TRAIL_POP_CENTER",
    "TRAIL_POP_LEFT",
    "TRAIL_SLING_LEFT"
]

while True:
    for group_name in group_names:
        led_group = groups[group_name]
        for led in led_group:
            pins[led].duty_cycle = 40000
        time.sleep(2)
        for led in led_group:
            pins[led].duty_cycle = 0
        #time.sleep(1)
