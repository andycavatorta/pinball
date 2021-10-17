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

groups = {
    "all":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
    "peso":[4,5,6,7],
    "coco":[16,17,18,19],
    "naranja":[12,13,14,15],
    "mango":[8,9,10,11],
    "sandia":[0,1,2,3],
    "pina":[20,21,22,23],
    "spoke_1":[2,3],
    "spoke_2":[0,1],
    "spoke_3":[10,11],
    "spoke_4":[8,9],
    "spoke_5":[12,13],
    "spoke_6":[14,15],
    "spoke_7":[16,17],
    "spoke_8":[18,19],
    "spoke_9":[20,21],
    "spoke_10":[22,23],
    "inner_circle":[2, 1, 10, 9, 14, 13, 17, 18, 21, 22],
    "outer_circle":[3, 0, 11, 8, 15, 12, 16, 19, 20, 23],   
}
sequences = {
    "spokes":["spoke_1","spoke_2","spoke_3","spoke_4","spoke_5","spoke_6","spoke_7","spoke_8","spoke_9","spoke_10"],
    "radial":["peso","inner_circle","outer_circle"],
}
levels = [
    0,
    50,
    100,
    1000,
    5000,
    10000,
    20000,
    30000,
    50000,
    65535,
]

def solid(group, level):
    pin_numbers = groups[group]
    duty_cycle = levels[level]
    for pin_number in pin_numbers:
        pins[pin_number].duty_cycle = duty_cycle

def fade_group(pin_numbers, start_level, end_level, fade_period = 0.1):
    start_duty_cycle = levels[start_level]
    end_duty_cycle = levels[end_level]
    animation_frame_period = 0.01
    increment_count = int(fade_period / animation_frame_period)
    increment_size = int(float(end_duty_cycle-start_duty_cycle)/float(increment_count))
    for increment_ordinal in range(increment_count):
        current_level = start_duty_cycle + (increment_ordinal * increment_size)
        for pin_number in pin_numbers:
            pins[pin_number].duty_cycle = int(current_level)
        time.sleep(animation_frame_period/2)
    for pin_number in pin_numbers:
        pins[pin_number].duty_cycle = int(end_duty_cycle)

def stroke_ripple():
    solid("all", 0)
    for group in sequences["radial"]:
        fade_group(group, 0, levels[8],0.05)
    for group in sequences["radial"]:
        fade_group(group, levels[8],0.05)
    solid("all", 0)

#############################################
"""
outer_radius = [3, 0, 11, 8, 15, 12, 16, 19, 20, 23]

inner_radius = [2, 1, 10, 9, 14, 13, 17, 18, 21, 22]

center_group = 

led_groups = [
    [0,1,2,3],
    [4,5,6,7],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]
]
radial_groups = [
    [0,1,2,3],
    [8,9,10,11],
    [12,13,14,15],
    [16,17,18,19],
    [20,21,22,23]
]

radial_spokes = [
    [2,3],
    [0,1],
    [10,11],
    [8,9],
    [12,13],
    [14,15],
    [16,17],
    [18,19],
    [20,21],
    [22,23],
]

radial_ripple = [
    [4,5,6,7],
    [2, 1, 10, 9, 14, 13, 17, 18, 21, 22],
    [3, 0, 11, 8, 15, 12, 16, 19, 20, 23]
]

duty_cycle_low = 1000
duty_cycle_med = 10000
duty_cycle_hi = 20000
duty_cycle_xhi = 50000


def set_group(id, level):
    led_group = radial_groups[id]
    for led in led_group:
        pins[led].duty_cycle = level

def set_spoke(id, level):
    print("lighting.set_spoke",id, level,int(level*65536))
    radial_spoke = radial_spokes[id]
    for led in radial_spoke:
        pins[led].duty_cycle = int(level*65535)

def fade_spoke(id, start_level, end_level, fade_period = 0.1):
    animation_frame_period = 0.01
    increment_count = int(fade_period / animation_frame_period)
    increment_size = int(float(end_level-start_level)/float(increment_count))
    radial_spoke = radial_spokes[id]
    for increment_ordinal in range(increment_count):
        current_level = start_level + (increment_ordinal * increment_size)
        for led in radial_spoke:
            pins[led].duty_cycle = current_level
        time.sleep(animation_frame_period/2)

def stroke_arc(id1, id2):
    if id1 == id2:
        return
    if id2 > id1:
        steps = range(id1, id2)
    else:
        steps = range(id1, id2, -1)
    for step in steps:
        group = radial_spokes[step]
        fade_group(group, 0, duty_cycle_med, 0.05)
    for step in steps:
        group = radial_spokes[step]
        fade_group(group, duty_cycle_med, 0, 0.05)

def pulse_fruit(fruit_id):
    group = radial_groups[fruit_id]
    fade_group(group, 0, duty_cycle_hi,0.05)
    fade_group(group, duty_cycle_hi,0, 0.05)
    fade_group(group, 0, duty_cycle_hi,0.05)
    fade_group(group, duty_cycle_hi,0, 0.05)

def play_ball_motion(fruit_is_start, fruit_id_end):
    stroke_ripple()
    stroke_ripple()
    stroke_ripple()
    pulse_fruit(fruit_is_start)
    stroke_arc(fruit_is_start*2,fruit_id_end*2)
    pulse_fruit(fruit_id_end)
"""