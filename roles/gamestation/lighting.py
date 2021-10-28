import adafruit_tlc5947
import board
import busio
import digitalio
import queue
import threading
import time
import traceback

class Lights_Pattern(threading.Thread):
    class action_times():
        BACK_TRACE = 0.125
        BLINK = 0.25
        ENERGIZE = 0.25
        SINGLE_DOT = 0.125
        SPARKLE = 0.025
        STROKE = 0.125
        THROB = 0.025
        TRACE = 0.125
        WINK = 0.5

    class action_names():
        BACK_STROKE_OFF = "back_stroke_off"
        BACK_STROKE_ON = "back_stroke_on"
        BACK_TRACE = "back_trace"
        BLINK = "blink"
        ENERGIZE = "energize"
        OFF = "off"
        LOW = "low"
        MED = "med"
        HIGH = "high"
        ON = "on"
        SINGLE_DOT = "single_dot"
        SPARKLE = "sparkle"
        STROKE_OFF = "stroke_off"
        STROKE_ON = "stroke_on"
        THROB = "throb"
        TRACE = "trace"
        WINK = "wink"

    def __init__(self, channels, upstream_queue,):
        threading.Thread.__init__(self )
        self.levels = [0,1024,2048,4096,8192,16384,32768,65535] # just guesses for now
        self.upstream_queue = upstream_queue
        self.channels = channels
        self.action_queue = queue.Queue()
        self.start()
    def back_stroke_off(self):
        self.action_queue.put([self.action_names.BACK_STROKE_OFF, self.channels])
    def back_stroke_on(self):
        self.action_queue.put([self.action_names.BACK_STROKE_ON, self.channels])
    def back_trace(self):
        self.action_queue.put([self.action_names.BACK_TRACE, self.channels])
    def blink(self):
        self.action_queue.put([self.action_names.BLINK, self.channels])
    def energize(self):
        self.action_queue.put([self.action_names.ENERGIZE, self.channels])
    def off(self):
        self.action_queue.put([self.action_names.OFF, self.channels])
    def low(self):
        self.action_queue.put([self.action_names.LOW, self.channels])
    def med(self):
        self.action_queue.put([self.action_names.MED, self.channels])
    def high(self):
        self.action_queue.put([self.action_names.HIGH, self.channels])
    def on(self):
        self.action_queue.put([self.action_names.ON, self.channels])
    def single_dot(self):
        self.action_queue.put([self.action_names.SINGLE_DOT, self.channels])
    def sparkle(self):
        self.action_queue.put([self.action_names.SPARKLE, self.channels])
    def stroke_off(self):
        self.action_queue.put([self.action_names.STROKE_OFF, self.channels])
    def stroke_on(self):
        self.action_queue.put([self.action_names.STROKE_ON, self.channels])
    def throb(self):
        self.action_queue.put([self.action_names.THROB, self.channels])
    def trace(self):
        self.action_queue.put([self.action_names.TRACE, self.channels])
    def wink(self):
        self.action_queue.put([self.action_names.WINK, self.channels])

    def run(self):
        while True:
            # new actions in action_queue will override previous actions
            action_name, channel = self.action_queue.get(True)
            #print("action_name, channel", action_name, channel)
            if action_name == self.action_names.BACK_STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_ON: 
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.STROKE)
                    self.upstream_queue.put([self.levels[0], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_TRACE:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BLINK: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.BLINK)
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.BLINK)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.ENERGIZE: 
                for divisor in [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]:
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[7], [channel]])
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.OFF: 
                self.upstream_queue.put([self.levels[0], channel])
            if action_name == self.action_names.ON: 
                self.upstream_queue.put([self.levels[-1], channel])

            if action_name == self.action_names.LOW: 
                self.upstream_queue.put([self.levels[3], channel])
            if action_name == self.action_names.MED: 
                self.upstream_queue.put([self.levels[5], channel])
            if action_name == self.action_names.HIGH: 
                self.upstream_queue.put([self.levels[7], channel])

            if action_name == self.action_names.SINGLE_DOT: 
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[6], [channel]])
                    time.sleep(self.action_times.SINGLE_DOT)
                    self.upstream_queue.put([self.levels[0], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.SPARKLE: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[0], [channel]])
                        time.sleep(self.action_times.SPARKLE)
                        self.upstream_queue.put([self.levels[-1], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.STROKE)
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.THROB:
                for level in self.levels:
                    for channel in self.channels:
                        self.upstream_queue.put([level, [channel]])
                    time.sleep(self.action_times.THROB)
                if not self.action_queue.empty():
                    break
                for level in reversed(self.levels): 
                    for channel in self.channels:
                        self.upstream_queue.put([level, [channel]])
                    time.sleep(self.action_times.THROB)
                if not self.action_queue.empty():
                    break
            if action_name == self.action_names.TRACE: 
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.WINK:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[7], [channel]])
                time.sleep(self.action_times.WINK)
                if not self.action_queue.empty():
                    break
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                time.sleep(self.action_times.WINK)
                if not self.action_queue.empty():
                    break

class Lights(threading.Thread):
    class pattern_channels():
        TRAIL_ROLLOVER_RIGHT = [16,15,14,13,12]
        TRAIL_ROLLOVER_LEFT = [19,20,21,22,23]
        TRAIL_SLING_RIGHT = [11,10,9]
        TRAIL_SLING_LEFT = [0,1,2]
        TRAIL_POP_LEFT =  [66,65,64,63,62,61,60]
        TRAIL_POP_CENTER = [69,68,67]
        TRAIL_POP_RIGHT =  [36,37,38]
        TRAIL_SPINNER = [39,40,41,42,43,44,45,46,47]
        PIE = [27,28,29,54,55,56,24,25,26,57,58,59,51,52,52,48,49,50,33,34,35,30,31,32]
        PIE_ROLLOVER_RIGHT = [27,28,29]
        PIE_ROLLOVER_LEFT = [54,55,56]
        PIE_SLING_RIGHT = [24,25,26]
        PIE_SLING_LEFT = [57,58,59]
        PIE_POP_LEFT =  [51,52,52]
        PIE_POP_CENTER = [48,49,50]
        PIE_POP_RIGHT =  [33,34,35]
        PIE_SPINNER = [30,31,32]

        RIPPLE_1 = [47]
        RIPPLE_2 = [46]
        RIPPLE_3 = [45, 60]
        RIPPLE_4 = [44, 61]
        RIPPLE_5 = [43, 38, 67, 62]
        RIPPLE_6 = [42, 37, 68, 63]
        RIPPLE_7 = [41, 36, 69, 64]
        RIPPLE_8 = [40, 35, 50, 65]
        RIPPLE_9 = [39, 34, 49, 66]
        RIPPLE_10 = [32, 33, 48, 52, 53]
        RIPPLE_11 = [31,30,51]
        RIPPLE_12 = [8, 27, 24,57,54,55,3]
        RIPPLE_13 = [29, 28, 6, 4, 56]
        RIPPLE_14 = [7, 15, 16, 5, 19, 25, 58, 20]
        RIPPLE_15 = [12, 13, 14, 25, 58, 21, 22, 23]
        RIPPLE_16 = [26, 59]
        RIPPLE_17 = [11, 0]
        RIPPLE_18 = [9,10, 1, 2]

        SIGN_ARROW_LEFT = [5,4,3]
        SIGN_ARROW_RIGHT = [6,7,8]
        SIGN_BOTTOM_LEFT = [17]
        SIGN_BOTTOM_RIGHT = [18]
        SIGN_TOP = [70,71]
        ALL_RADIAL = [
            0,1,2,9,
            10,11,12,13,14,15,16,19,
            20,21,22,23,24,25,26,27,28,29,
            30,31,32,33,34,35,36,37,38,39,
            40,41,42,43,44,45,46,47,48,49,
            50,51,52,53,54,55,56,57,58,59,
            60,61,62,63,64,65,66,67,68,69
            ]
        #ALL_CLOCKWISE = []

    def __init__(self):
        threading.Thread.__init__(self)
        self.channels = [0]*72
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D22)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=3)
        
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.tlc5947.create_pwm_out(channel_number)

        self.queue = queue.Queue()
        self.trail_rollover_right = Lights_Pattern(self.pattern_channels.TRAIL_ROLLOVER_RIGHT, self.queue)
        self.trail_rollover_left = Lights_Pattern(self.pattern_channels.TRAIL_ROLLOVER_LEFT, self.queue)
        self.trail_sling_right = Lights_Pattern(self.pattern_channels.TRAIL_SLING_RIGHT, self.queue)
        self.trail_sling_left = Lights_Pattern(self.pattern_channels.TRAIL_SLING_LEFT, self.queue)
        self.trail_pop_left = Lights_Pattern(self.pattern_channels.TRAIL_POP_LEFT, self.queue)
        self.trail_pop_right = Lights_Pattern(self.pattern_channels.TRAIL_POP_RIGHT, self.queue)
        self.trail_pop_middle = Lights_Pattern(self.pattern_channels.TRAIL_POP_CENTER, self.queue)
        self.trail_spinner = Lights_Pattern(self.pattern_channels.TRAIL_SPINNER, self.queue)
        self.pie_rollover_right = Lights_Pattern(self.pattern_channels.PIE_ROLLOVER_RIGHT, self.queue)
        self.pie_rollover_left = Lights_Pattern(self.pattern_channels.PIE_ROLLOVER_LEFT, self.queue)
        self.pie_sling_right = Lights_Pattern(self.pattern_channels.PIE_SLING_RIGHT, self.queue)
        self.pie_sling_left = Lights_Pattern(self.pattern_channels.PIE_SLING_LEFT, self.queue)
        self.pie_pop_left = Lights_Pattern(self.pattern_channels.PIE_POP_LEFT, self.queue)
        self.pie_pop_right = Lights_Pattern(self.pattern_channels.PIE_POP_RIGHT, self.queue)
        self.pie_pop_middle = Lights_Pattern(self.pattern_channels.PIE_POP_CENTER, self.queue)
        self.pie_spinner = Lights_Pattern(self.pattern_channels.PIE_SPINNER, self.queue)
        self.pie = Lights_Pattern(self.pattern_channels.PIE, self.queue)
        self.ripple_1 = Lights_Pattern(self.pattern_channels.RIPPLE_1, self.queue)
        self.ripple_2 = Lights_Pattern(self.pattern_channels.RIPPLE_2, self.queue)
        self.ripple_3 = Lights_Pattern(self.pattern_channels.RIPPLE_3, self.queue)
        self.ripple_4 = Lights_Pattern(self.pattern_channels.RIPPLE_4, self.queue)
        self.ripple_5 = Lights_Pattern(self.pattern_channels.RIPPLE_5, self.queue)
        self.ripple_6 = Lights_Pattern(self.pattern_channels.RIPPLE_6, self.queue)
        self.ripple_7 = Lights_Pattern(self.pattern_channels.RIPPLE_7, self.queue)
        self.ripple_8 = Lights_Pattern(self.pattern_channels.RIPPLE_8, self.queue)
        self.ripple_9 = Lights_Pattern(self.pattern_channels.RIPPLE_9, self.queue)
        self.ripple_10 = Lights_Pattern(self.pattern_channels.RIPPLE_10, self.queue)
        self.ripple_11 = Lights_Pattern(self.pattern_channels.RIPPLE_11, self.queue)
        self.ripple_12 = Lights_Pattern(self.pattern_channels.RIPPLE_12, self.queue)
        self.ripple_13 = Lights_Pattern(self.pattern_channels.RIPPLE_13, self.queue)
        self.ripple_14 = Lights_Pattern(self.pattern_channels.RIPPLE_14, self.queue)
        self.ripple_15 = Lights_Pattern(self.pattern_channels.RIPPLE_15, self.queue)
        self.ripple_16 = Lights_Pattern(self.pattern_channels.RIPPLE_16, self.queue)
        self.ripple_17 = Lights_Pattern(self.pattern_channels.RIPPLE_17, self.queue)
        self.ripple_18 = Lights_Pattern(self.pattern_channels.RIPPLE_18, self.queue)
        self.sign_arrow_left = Lights_Pattern(self.pattern_channels.SIGN_ARROW_LEFT, self.queue)
        self.sign_bottom_left = Lights_Pattern(self.pattern_channels.SIGN_BOTTOM_LEFT, self.queue)
        self.sign_bottom_right = Lights_Pattern(self.pattern_channels.SIGN_BOTTOM_RIGHT, self.queue)
        self.sign_top = Lights_Pattern(self.pattern_channels.SIGN_TOP, self.queue)
        self.all_radial = Lights_Pattern(self.pattern_channels.ALL_RADIAL, self.queue)
        #self.all_clockwise = Lights_Pattern(self.pattern_channels.ALL_CLOCKWISE, self.queue)
        self.start()

    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))

    def run(self):
        while True:
            level, channel_numbers = self.queue.get(True)
            #foo = self.queue.get(True)
            #print(level, channel_numbers)
            for channel_number in channel_numbers:
                self.channels[channel_number].duty_cycle = level

#lights = Lights()

"""
lights.trail_rollover_right.off()
lights.trail_rollover_right.on()
lights.trail_rollover_right.sparkle()
lights.trail_rollover_right.throb()
lights.trail_rollover_right.energize()
lights.trail_rollover_right.blink()
lights.trail_rollover_right.stroke_on()
lights.trail_rollover_right.stroke_off()
lights.trail_rollover_right.back_stroke_on()
lights.trail_rollover_right.back_stroke_off()
lights.trail_rollover_right.trace()
lights.trail_rollover_right.back_trace()

lights.trail_rollover_left  ...
lights.trail_sling_right  ...
lights.trail_sling_left  ...
lights.trail_pop_left  ...
lights.trail_pop_right  ...
lights.trail_pop_middle  ...
lights.trail_spinner  ...
lights.pie_rollover_right  ...
lights.pie_rollover_left  ...
lights.pie_sling_right  ...
lights.pie_sling_left  ...
lights.pie_pop_left  ...
lights.pie_pop_right  ...
lights.pie_pop_middle  ...
lights.pie_spinner  ...
lights.sign_arrow_left  ...
lights.sign_bottom_right  ...
lights.sign_top  ...
lights.all_radial ...
lights.all_clockwise ...

"""