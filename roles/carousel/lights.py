
class LED_Group(threading.Thread):
    class action_times():
        SPARKLE = 0.025
        THROB = 0.025
        ENERGIZE = 0.25
        BLINK = 0.25
        STROKE = 0.125
        BACK_TRACE = 0.125
        TRACE = 0.125

    class action_names():
        ON = "on"
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

    def __init__(self, channels, upstream_queue,):
        threading.Thread.__init__(self)
        self.levels = [0,1024,2048,4096,8192,16384,32768,65535] # just guesses for now
        self.upstream_queue = upstream_queue
        self.channels = channels
        self.local_queue = queue.Queue()
        self.actions = {1
        }
        self.start()
    def off(self):
        self.local_queue.put([self.action_names.OFF, self.channels])
    def on(self):
        self.local_queue.put([self.action_names.ON, self.channels])
    def sparkle(self):
        self.local_queue.put([self.action_names.SPARKLE, self.channels])
    def throb(self):
        self.local_queue.put([self.action_names.THROB, self.channels])
    def energize(self):
        self.local_queue.put([self.action_names.ENERGIZE, self.channels])
    def blink(self):
        self.local_queue.put([self.action_names.BLINK, self.channels])
    def stroke_on(self):
        self.local_queue.put([self.action_names.STROKE_ON, self.channels])
    def stroke_off(self):
        self.local_queue.put([self.action_names.STROKE_OFF, self.channels])
    def back_stroke_on(self):
        self.local_queue.put([self.action_names.BACK_STROKE_ON, self.channels])
    def back_stroke_off(self):
        self.local_queue.put([self.action_names.BACK_STROKE_OFF, self.channels])
    def trace(self):
        self.local_queue.put([self.action_names.TRACE, self.channels])
    def back_trace(self):
        self.local_queue.put([self.action_names.BACK_TRACE, self.channels])
    def run(self):
        while True:
            # new actions in local_queue will override previous actions
            action_name, channel = self.local_queue.get(True)

            if action_name == self.action_names.OFF:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)

            if action_name == self.action_names.ON:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)

            if action_name == self.action_names.SPARKLE: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                        time.sleep(self.action_times.SPARKLE)
                        self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.THROB:
                while True:
                    for level in self.levels:
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.local_queue.empty():
                        break
                    for level in reversed(self.levels): 
                        for channel in self.channels:
                            self.upstream_queue.put(level, channel)
                        time.sleep(self.action_times.THROB)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.ENERGIZE: 
                for divisor in [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0]:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.ENERGIZE/divisor)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BLINK: 
                while True:
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.BLINK)
                    for channel in self.channels:
                        self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.BLINK)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.STROKE_ON:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_ON: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.STROKE)
                    self.upstream_queue.put(self.levels[0], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_STROKE_OFF: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[0], channel)
                    time.sleep(self.action_times.STROKE)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.TRACE: 
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break
            if action_name == self.action_names.BACK_TRACE:
                for channel in self.channels:
                    self.upstream_queue.put(self.levels[0], channel)
                for channel in reverse(self.channels):
                    self.upstream_queue.put(self.levels[-1], channel)
                    time.sleep(self.action_times.TRACE)
                    self.upstream_queue.put(self.levels[-1], channel)
                    if not self.local_queue.empty():
                        break

class Lights(threading.Thread):
    class group_channels():
        FRUIT_0 = [0,1,2]
        FRUIT_1 = [0,1,2]
        FRUIT_2 = [0,1,2]
        FRUIT_3 = [0,1,2]
        FRUIT_4 =  [0,1,2]
        FRUIT_5 =  [0,1,2]
        ALL_RADIAL = [0,1,2]
        ALL_CLOCKWISE = [0,1,2]

    def __init__(self):
        threading.Thread.__init__(self)
        self.channels = [0]*12
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        latch = digitalio.DigitalInOut(board.D5)
        self.tlc5947 = adafruit_tlc5947.TLC5947(spi, latch, num_drivers=1)
        for channel_number in range(len(self.channels)):
            self.channels[channel_number] = self.tlc5947.create_pwm_out(channel_number)
        self.queue = queue.Queue()
        self.led_groups = {
            "fruit_0": LED_Group(self.group_channels.FRUIT_0, self.queue),
            "fruit_1": LED_Group(self.group_channels.FRUIT_1, self.queue),  
            "fruit_2": LED_Group(self.group_channels.FRUIT_2, self.queue),  
            "fruit_3": LED_Group(self.group_channels.FRUIT_3, self.queue),  
            "fruit_4": LED_Group(self.group_channels.FRUIT_4, self.queue),  
            "dinero": LED_Group(self.group_channels.FRUIT_5, self.queue),  
            "all_radial":LED_Group(self.group_channels.ALL_RADIAL, self.queue),  
            "all_clockwise":LED_Group(self.group_channels.ALL_CLOCKWISE, self.queue),  
        }
    def add_to_queue(self, level, channel_number):
        self.queue.put((level, channel_number))
    def run(self):
        while True:
            level, channel_number = self.queue.get(True)
            self.channels[channel_number].duty_cycle = level

