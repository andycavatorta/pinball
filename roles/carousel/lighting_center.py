import adafruit_tlc5947
import board
import busio
import digitalio
import queue
import threading
import time

# Special remap for weird central carousel LED wiring
# CENTER_REMAP[intended_led] = corresponding_led_on_central_carousel
CENTER_REMAP = [
    11,
    10,
    9,
    8,
    7,
    4,
    5,
    6,
    15,
    14,
    13,
    12,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    0,
    1,
    2,
    3
]

class Lights_Pattern(threading.Thread):
    class action_times():
        SPARKLE = 0.025
        THROB = 0.025
        ENERGIZE = 0.25
        BLINK = 0.50
        STROKE = 0.125
        BACK_TRACE = 0.125
        TRACE = 0.125
        SERPENTINE = 0.3
        SINGLE_DOT = 0.125

    class action_names():
        ON = "on"
        LOW = "low"
        MED = "med"
        HIGH = "high"
        OFF = "off"
        SPARKLE = "sparkle"
        THROB = "throb"
        ENERGIZE = "energize"
        BLINK = "blink"
        STROKE_ON = "stroke_on"
        STROKE_OFF = "stroke_off"
        BACK_STROKE_ON = "back_stroke_on"
        BACK_STROKE_OFF = "back_stroke_off"
        TRACE = "trace"
        BACK_TRACE = "back_trace"

        SERPENTINE_EDGE = "serpentine_edge"
        SERPENTINE_CENTER = "serpentine_center"

        SINGLE_DOT = "single_dot"

    def __init__(self, channels, upstream_queue,):
        threading.Thread.__init__(self )
        self.levels = [0,1024,2048,4096,8192,16384,32768,65535] # just guesses for now
        self.upstream_queue = upstream_queue
        self.channels = channels
        self.action_queue = queue.Queue()

        self.serpentine_edge_frames = [
            [2,2,2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2,2,2],
            [7,2,2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2,2,2],
            [7,7,2,2,2,2,2,2,2,2, 2,7,2,2,2,2,2,2,2,2],
            [6,7,7,2,2,2,2,2,2,2, 2,7,7,2,2,2,2,2,2,2],
            [5,6,7,7,2,2,2,2,2,2, 2,6,7,7,2,2,2,2,2,2],
            [4,5,6,7,7,2,2,2,2,2, 2,5,6,7,7,2,2,2,2,2],
            [3,4,5,6,7,7,2,2,2,2, 2,4,5,6,7,7,2,2,2,2],
            [2,3,4,5,6,7,7,2,2,2, 2,3,4,5,6,7,7,2,2,2],
            [2,2,3,4,5,6,7,7,2,2, 2,2,3,4,5,6,7,7,2,2],
            [2,2,2,3,4,5,6,7,7,2, 2,2,2,3,4,5,6,7,6,2],

            [
                2,2,2,2,3,4,5,6,7,7,
                2,2,2,2,3,4,5,6,7,7
            ],
            [
                7,2,2,2,2,3,4,5,6,7,
                7,2,2,2,2,3,4,5,6,7
            ],
            [
                7,7,2,2,2,2,3,4,5,6,
                7,2,2,2,2,2,3,4,5,6
            ],
            [
                6,7,2,2,2,2,2,3,4,5,
                6,2,2,2,2,2,2,3,4,5
            ],
            [
                5,6,2,2,2,2,2,2,3,4,
                5,2,2,2,2,2,2,2,3,4
            ],
            [
                4,5,2,2,2,2,2,2,2,3,
                4,2,2,2,2,2,2,2,2,3
            ],
            [
                3,4,2,2,2,2,2,2,2,2,
                3,2,2,2,2,2,2,2,2,2
            ],
            [
                3,3,2,2,2,2,2,2,2,2,
                2,2,2,2,2,2,2,2,2,2
            ]
        ]
        self.serpentine_center_frames = [
            [2,2,2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2,2,2],
            [7,2,2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2,2,2],
            [7,7,2,2,2,2,2,2,2,2, 2,7,2,2,2,2,2,2,2,2],
            [6,7,7,2,2,2,2,2,2,2, 2,7,7,2,2,2,2,2,2,2],
            [5,6,7,7,2,2,2,2,2,2, 2,6,7,7,2,2,2,2,2,2],
            [4,5,6,7,7,2,2,2,2,2, 2,5,6,7,7,2,2,2,2,2],
            [3,4,5,6,7,7,2,2,2,2, 2,4,5,6,7,7,2,2,2,2],
            [2,3,4,5,6,7,7,2,2,2, 2,3,4,5,6,7,7,2,2,2],
            [2,2,3,4,5,6,7,7,2,2, 2,2,3,4,5,6,7,7,2,2],
            [2,2,2,3,4,5,6,7,7,2, 2,2,2,3,4,5,6,7,6,2],

            [2,2,2,2,3,4,5,6,7,7, 2,2,2,2,3,4,5,6,7,2],
            [2,2,2,2,2,3,4,5,6,7, 2,2,2,2,2,3,4,5,6,2],
            [2,2,2,2,2,2,3,4,5,6, 2,2,2,2,2,2,3,4,5,2],
            [2,2,2,2,2,2,2,3,4,5, 2,2,2,2,2,2,2,3,4,2],
            [2,2,2,2,2,2,2,2,3,4, 2,2,2,2,2,2,2,2,3,2],
            [2,2,2,2,2,2,2,2,2,3, 2,2,2,2,2,2,2,2,2,2]
        ]
        self.start()
    def off(self):
        self.action_queue.put([self.action_names.OFF, self.channels])
    def on(self):
        self.action_queue.put([self.action_names.ON, self.channels])
    def med(self):
        self.action_queue.put([self.action_names.MED, self.channels])
    def low(self):
        self.action_queue.put([self.action_names.LOW, self.channels])
    def high(self):
        self.action_queue.put([self.action_names.HIGH, self.channels])
    def sparkle(self):
        self.action_queue.put([self.action_names.SPARKLE, self.channels])
    def throb(self):
        self.action_queue.put([self.action_names.THROB, self.channels])
    def energize(self):
        self.action_queue.put([self.action_names.ENERGIZE, self.channels])
    def blink(self):
        self.action_queue.put([self.action_names.BLINK, self.channels])
    def stroke_on(self):
        self.action_queue.put([self.action_names.STROKE_ON, self.channels])
    def stroke_off(self):
        self.action_queue.put([self.action_names.STROKE_OFF, self.channels])
    def back_stroke_on(self):
        self.action_queue.put([self.action_names.BACK_STROKE_ON, self.channels])
    def back_stroke_off(self):
        self.action_queue.put([self.action_names.BACK_STROKE_OFF, self.channels])
    def trace(self):
        self.action_queue.put([self.action_names.TRACE, self.channels])
    def back_trace(self):
        self.action_queue.put([self.action_names.BACK_TRACE, self.channels])
    def serpentine_edge(self):
        self.action_queue.put([self.action_names.SERPENTINE_EDGE, self.channels])
    def serpentine_center(self):
        self.action_queue.put([self.action_names.SERPENTINE_CENTER, self.channels])

    def single_dot(self):
        self.action_queue.put([self.action_names.SINGLE_DOT, self.channels])
    def run(self):
        while True:
            # new actions in action_queue will override previous actions
            action_name, channel = self.action_queue.get(True)
            print("Lights_Pattern",action_name, channel)
            if action_name == self.action_names.OFF:
                self.upstream_queue.put([self.levels[0], channel])

            if action_name == self.action_names.ON:
                self.upstream_queue.put([self.levels[6], channel])

            if action_name == self.action_names.LOW:
                self.upstream_queue.put([self.levels[3], channel])
            if action_name == self.action_names.MED:
                self.upstream_queue.put([self.levels[5], channel])
            if action_name == self.action_names.HIGH:
                self.upstream_queue.put([self.levels[7], channel])

            if action_name == self.action_names.SPARKLE:
                while True:
                    for channel in self.channels:

                        self.upstream_queue.put([self.levels[0], [channel]])
                        time.sleep(self.action_times.SPARKLE)
                        self.upstream_queue.put([self.levels[-1], [channel]])
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
            if action_name == self.action_names.ENERGIZE:
                for divisor in [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]:
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    for channel in self.channels:
                        self.upstream_queue.put([self.levels[6], [channel]])
                    time.sleep(self.action_times.ENERGIZE/divisor)
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
            if action_name == self.action_names.STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.STROKE)
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
            if action_name == self.action_names.BACK_STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.STROKE)
                    self.upstream_queue.put([self.levels[0], [channel]])
                    if not self.action_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_OFF:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[-1], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[0], [channel]])
                    time.sleep(self.action_times.STROKE)
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
            if action_name == self.action_names.BACK_TRACE:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in reversed(self.channels):
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put([self.levels[-1], [channel]])
                    if not self.action_queue.empty():
                        break

            if action_name == self.action_names.SERPENTINE_EDGE:
                for serpentine_edge_frame in self.serpentine_edge_frames:
                    for radial_position in range(10):
                        outer_pin = self.channels[radial_position]
                        inner_pin = self.channels[radial_position + 10]
                        outer_level = serpentine_edge_frame[radial_position]
                        inner_level = serpentine_edge_frame[radial_position + 10]
                        print(outer_pin, outer_level, inner_pin, inner_level)
                        self.upstream_queue.put([self.levels[outer_level], [outer_pin]])
                        self.upstream_queue.put([self.levels[inner_level], [inner_pin]])
                time.sleep(self.action_times.SERPENTINE)
                if not self.action_queue.empty():
                    break

            if action_name == self.action_names.SERPENTINE_CENTER:
                for serpentine_center_frame in self.serpentine_center_frames:
                    for radial_position in range(10):
                        outer_pin = self.channels[radial_position]
                        inner_pin = self.channels[radial_position + 10]
                        outer_level = serpentine_center_frame[radial_position]
                        inner_level = serpentine_center_frame[radial_position + 10]
                        print(outer_pin, outer_level, inner_pin, inner_level)
                        self.upstream_queue.put([self.levels[outer_level], [outer_pin]])
                        self.upstream_queue.put([self.levels[inner_level], [inner_pin]])
                time.sleep(self.action_times.SERPENTINE)
                if not self.action_queue.empty():
                    break

            if action_name == self.action_names.SINGLE_DOT:
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[0], [channel]])
                for channel in self.channels:
                    self.upstream_queue.put([self.levels[6], [channel]])
                    time.sleep(self.action_times.SINGLE_DOT)
                    self.upstream_queue.put([self.levels[0], [channel]])
                    if not self.action_queue.empty():
                        break

class Lights(threading.Thread):
    class pattern_channels():
        ALL = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        PESO = [4,5,6,7]
        COCO = [16,17,18,19]
        NARANJA = [12,13,14,15]
        MANGO = [8,9,10,11]
        SANDIA = [0,1,2,3]
        PINA = [20,21,22,23]
        SPOKE_1 = [2,3]
        SPOKE_2 = [0,1]
        SPOKE_3 = [10,11]
        SPOKE_4 = [8,9]
        SPOKE_5 = [12,13]
        SPOKE_6 = [14,15]
        SPOKE_7 = [16,17]
        SPOKE_8 = [18,19]
        SPOKE_9 = [20,21]
        SPOKE_10 = [22,23]
        RIPPLE_NARANJA_1 = [12,15]
        RIPPLE_NARANJA_2 = [13,14]
        RIPPLE_NARANJA_3 = [16,17,9,8]
        RIPPLE_NARANJA_4 = [18,21,22,2,1,10]
        RIPPLE_NARANJA_5 = [19,20,23,3,0,11]
        RIPPLE_MANGO_1 = [8,11]
        RIPPLE_MANGO_2 = [9,10]
        RIPPLE_MANGO_3 = [12,13,1,0]
        RIPPLE_MANGO_4 = [14,17,18,21,22,2]
        RIPPLE_MANGO_5 = [15,16,19,20,23,3]
        RIPPLE_SANDIA_1 = [3,0]
        RIPPLE_SANDIA_2 = [2,1]
        RIPPLE_SANDIA_3 = [11,10,22,23]
        RIPPLE_SANDIA_4 = [9,13,14,17,18,21]
        RIPPLE_SANDIA_5 = [8,12,15,16,19,20]
        RIPPLE_PINA_1 = [20,23]
        RIPPLE_PINA_2 = [21,22]
        RIPPLE_PINA_3 = [3,2,18,19]
        RIPPLE_PINA_4 = [10,9,13,14,17,18]
        RIPPLE_PINA_5 = [11,8,12,15,16,19]
        RIPPLE_COCO_1 = [16,19]
        RIPPLE_COCO_2 = [18,17]
        RIPPLE_COCO_3 = [20,21,14,15]
        RIPPLE_COCO_4 = [22,2,1,10,9,13]
        RIPPLE_COCO_5 = [23,3,0,11,8,12]
        INNER_CIRCLE = [2, 1, 10, 9, 14, 13, 17, 18, 21, 22]
        OUTER_CIRCLE = [3, 0, 11, 8, 15, 12, 16, 19, 20, 23]
        SERPENTINE_EDGE_COCO = [
            19,16,12,15,8,11,0,3,23,20,
            18,17,13,14,9,10,1,2,22,21
        ]
        SERPENTINE_EDGE_NARANJA = [
            12,15,8,11,0,3,23,20,19,16,
            13,14,9,10,1,2,22,21,18,17
        ]
        SERPENTINE_EDGE_MANGO = [
            8,11,0,3,23,20,19,16,12,15,
            9,10,1,2,22,21,18,17,13,14
        ]
        SERPENTINE_EDGE_SANDIA = [
            0,3,23,20,19,16,12,15,8,11,
            1,2,22,21,18,17,13,14,9,10
        ]
        SERPENTINE_EDGE_PINA = [
            23,20,19,16,12,15,8,11,0,3,
            22,21,18,17,13,14,9,10,1,2
        ]

        SERPENTINE_CENTER_COCO = [
            20, 23, 3, 0, 11, 8, 15, 12, 16, 19,
            21, 22, 2, 1, 10, 9, 14, 13, 17, 18
        ]
        SERPENTINE_CENTER_NARANJA = [
            16, 19, 20, 23, 3, 0, 11, 8, 15, 12,
            17, 18, 21, 22, 2, 1, 10, 9, 14, 13
        ]
        SERPENTINE_CENTER_MANGO = [
            15, 12, 16, 19, 20, 23, 3, 0, 11, 8,
            14, 13, 17, 18, 21, 22, 2, 1, 10, 9
        ]
        SERPENTINE_CENTER_SANDIA = [
            11, 8, 15, 12, 16, 19, 20, 23, 3, 0,
            10, 9, 14, 13, 17, 18, 21, 22, 2, 1
        ]
        SERPENTINE_CENTER_PINA = [
            3, 0, 11, 8, 15, 12, 16, 19, 20, 23,
            2, 1, 10, 9, 14, 13, 17, 18, 21, 22
        ]


    def __init__(self):
        threading.Thread.__init__(self)
        self.channels = [0]*24
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D26)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=1)
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.tlc5947.create_pwm_out(channel_number)
        self.queue = queue.Queue()
        self.all = Lights_Pattern(self.pattern_channels.ALL, self.queue)
        self.peso = Lights_Pattern(self.pattern_channels.PESO, self.queue)
        self.coco = Lights_Pattern(self.pattern_channels.COCO, self.queue)
        self.naranja = Lights_Pattern(self.pattern_channels.NARANJA, self.queue)
        self.mango = Lights_Pattern(self.pattern_channels.MANGO, self.queue)
        self.sandia = Lights_Pattern(self.pattern_channels.SANDIA, self.queue)
        self.pina = Lights_Pattern(self.pattern_channels.PINA, self.queue)
        self.spoke_1 = Lights_Pattern(self.pattern_channels.SPOKE_1, self.queue)
        self.spoke_2 = Lights_Pattern(self.pattern_channels.SPOKE_2, self.queue)
        self.spoke_3 = Lights_Pattern(self.pattern_channels.SPOKE_3, self.queue)
        self.spoke_4 = Lights_Pattern(self.pattern_channels.SPOKE_4, self.queue)
        self.spoke_5 = Lights_Pattern(self.pattern_channels.SPOKE_5, self.queue)
        self.spoke_6 = Lights_Pattern(self.pattern_channels.SPOKE_6, self.queue)
        self.spoke_7 = Lights_Pattern(self.pattern_channels.SPOKE_7, self.queue)
        self.spoke_8 = Lights_Pattern(self.pattern_channels.SPOKE_8, self.queue)
        self.spoke_9 = Lights_Pattern(self.pattern_channels.SPOKE_9, self.queue)
        self.spoke_10 = Lights_Pattern(self.pattern_channels.SPOKE_10, self.queue)
        self.ripple_naranja_1 = Lights_Pattern(self.pattern_channels.RIPPLE_NARANJA_1, self.queue)
        self.ripple_naranja_2 = Lights_Pattern(self.pattern_channels.RIPPLE_NARANJA_2, self.queue)
        self.ripple_naranja_3 = Lights_Pattern(self.pattern_channels.RIPPLE_NARANJA_3, self.queue)
        self.ripple_naranja_4 = Lights_Pattern(self.pattern_channels.RIPPLE_NARANJA_4, self.queue)
        self.ripple_naranja_5 = Lights_Pattern(self.pattern_channels.RIPPLE_NARANJA_5, self.queue)
        self.ripple_mango_1 = Lights_Pattern(self.pattern_channels.RIPPLE_MANGO_1, self.queue)
        self.ripple_mango_2 = Lights_Pattern(self.pattern_channels.RIPPLE_MANGO_2, self.queue)
        self.ripple_mango_3 = Lights_Pattern(self.pattern_channels.RIPPLE_MANGO_3, self.queue)
        self.ripple_mango_4 = Lights_Pattern(self.pattern_channels.RIPPLE_MANGO_4, self.queue)
        self.ripple_mango_5 = Lights_Pattern(self.pattern_channels.RIPPLE_MANGO_5, self.queue)
        self.ripple_sandia_1 = Lights_Pattern(self.pattern_channels.RIPPLE_SANDIA_1, self.queue)
        self.ripple_sandia_2 = Lights_Pattern(self.pattern_channels.RIPPLE_SANDIA_2, self.queue)
        self.ripple_sandia_3 = Lights_Pattern(self.pattern_channels.RIPPLE_SANDIA_3, self.queue)
        self.ripple_sandia_4 = Lights_Pattern(self.pattern_channels.RIPPLE_SANDIA_4, self.queue)
        self.ripple_sandia_5 = Lights_Pattern(self.pattern_channels.RIPPLE_SANDIA_5, self.queue)
        self.ripple_pina_1 = Lights_Pattern(self.pattern_channels.RIPPLE_PINA_1, self.queue)
        self.ripple_pina_2 = Lights_Pattern(self.pattern_channels.RIPPLE_PINA_2, self.queue)
        self.ripple_pina_3 = Lights_Pattern(self.pattern_channels.RIPPLE_PINA_3, self.queue)
        self.ripple_pina_4 = Lights_Pattern(self.pattern_channels.RIPPLE_PINA_4, self.queue)
        self.ripple_pina_5 = Lights_Pattern(self.pattern_channels.RIPPLE_PINA_5, self.queue)
        self.ripple_coco_1 = Lights_Pattern(self.pattern_channels.RIPPLE_COCO_1, self.queue)
        self.ripple_coco_2 = Lights_Pattern(self.pattern_channels.RIPPLE_COCO_2, self.queue)
        self.ripple_coco_3 = Lights_Pattern(self.pattern_channels.RIPPLE_COCO_3, self.queue)
        self.ripple_coco_4 = Lights_Pattern(self.pattern_channels.RIPPLE_COCO_4, self.queue)
        self.ripple_coco_5 = Lights_Pattern(self.pattern_channels.RIPPLE_COCO_5, self.queue)
        self.inner_circle = Lights_Pattern(self.pattern_channels.INNER_CIRCLE, self.queue)
        self.outer_circle = Lights_Pattern(self.pattern_channels.OUTER_CIRCLE, self.queue)
        self.serpentine_edge_coco = Lights_Pattern(self.pattern_channels.SERPENTINE_EDGE_COCO, self.queue)
        self.serpentine_edge_naranja = Lights_Pattern(self.pattern_channels.SERPENTINE_EDGE_NARANJA, self.queue)
        self.serpentine_edge_mango = Lights_Pattern(self.pattern_channels.SERPENTINE_EDGE_MANGO, self.queue)
        self.serpentine_edge_sandia = Lights_Pattern(self.pattern_channels.SERPENTINE_EDGE_SANDIA, self.queue)
        self.serpentine_edge_pina = Lights_Pattern(self.pattern_channels.SERPENTINE_EDGE_PINA, self.queue)

        self.serpentine_center_coco = Lights_Pattern(self.pattern_channels.SERPENTINE_CENTER_COCO, self.queue)
        self.serpentine_center_naranja = Lights_Pattern(self.pattern_channels.SERPENTINE_CENTER_NARANJA, self.queue)
        self.serpentine_center_mango = Lights_Pattern(self.pattern_channels.SERPENTINE_CENTER_MANGO, self.queue)
        self.serpentine_center_sandia = Lights_Pattern(self.pattern_channels.SERPENTINE_CENTER_SANDIA, self.queue)
        self.serpentine_center_pina = Lights_Pattern(self.pattern_channels.SERPENTINE_CENTER_PINA, self.queue)

        self.start()

    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))

    def run(self):
        while True:
            level, channel_numbers = self.queue.get(True)
            #print(level, channel_numbers)
            for intended_channel_number in channel_numbers:
                # center carousel hack, see comment at top
                center_channel_number = CENTER_REMAP[intended_channel_number]
                self.channels[center_channel_number].duty_cycle = level
