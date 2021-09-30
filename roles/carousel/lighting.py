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
        pins[led].duty_cycle = int(level*65536)

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

def fade_group(led_pins, start_level, end_level, fade_period = 0.1):
    animation_frame_period = 0.01
    increment_count = int(fade_period / animation_frame_period)
    increment_size = int(float(end_level-start_level)/float(increment_count))
    for increment_ordinal in range(increment_count):
        current_level = start_level + (increment_ordinal * increment_size)
        for led in led_pins:
            pins[led].duty_cycle = int(current_level)
        time.sleep(animation_frame_period/2)
    for led in led_pins:
        pins[led].duty_cycle = int(end_level)

def clear_all():
    for led_group in led_groups:
        for led in led_group:
            pins[led].duty_cycle = 0

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

def stroke_ripple():
    clear_all()
    for group in radial_ripple:
        fade_group(group, 0, duty_cycle_hi,0.05)
    for group in radial_ripple:
        fade_group(group, duty_cycle_hi,0.05)
    clear_all()

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
