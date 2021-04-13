#!/usr/bin/env python

import time
import math
import random
import RPi.GPIO as GPIO
import threading

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

class Scores():
    attraction_mode = {
        "tempo_multiplier":4,
        "beats":[[1,2],[2,3],[3,4],[4,5],[5,1]]
    }
    countdown_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    barter_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    money_mode = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    score = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    scorex10 = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    barter_request = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    fail_theme = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    closing_theme = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }
    empty = {
        "tempo_multiplier":4,
        "beats":[
        ]
    }

class Chimes(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.gpio_numbers =  [ 2, 3, 4, 17, 18,   27, 22, 23, 24, 10,   9, 25, 11, 8, 0,   1, 5, 6, 12, 13,   19, 16, 26, 20, 21 ] 
        self.stations = [
            self.gpio_numbers[0:5],
            self.gpio_numbers[5:10],
            self.gpio_numbers[10:15],
            self.gpio_numbers[15:20],
            self.gpio_numbers[20:25],
        ]
        self.duration = 0.010
        GPIO.setmode(GPIO.BCM)
        for gpio_number in self.gpio_numbers:
          GPIO.setup( gpio_number, GPIO.OUT )
        self.all_off()

    def all_off(self):
        for gpio_number in self.gpio_numbers:
          GPIO.output(gpio_number, GPIO.LOW)

    def set_duration(self, duration):
        self.duration = duration

    def pulse(self, list_of_station_pitch_pairs):
        self.queue.put(list_of_station_pitch_pairs)

    def run(self):
        while True:
            try:
                list_of_station_pitch_pairs = self.queue.get(True)
                for station_pitch_pair in list_of_station_pitch_pairs:
                    station, pitch = station_pitch_pair
                    gpio = self.stations[station][pitch]
                    GPIO.output( gpio, GPIO.HIGH )
                time.sleep(self.duration)
                self.all_off()
            except Exception as e:
                self.all_off()

class Player(threading.Thread):
    """
    A player receives the name of a score and spools it out to the chimes of its assigned target.
    A target could be a station, a pair of stations, or all stations.
    """
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.target = target
        self.base_tempo = 0.1
        self.chimes = Chimes()

    def play(self, score):
        self.queue.put(score)

    def run(self):
        while True:
            try:
                score = self.queue.get(True)
                tempo_multiplier = score.tempo_multiplier_mul
                for beat in score.beats:
                    self.chimes.pulse(self.target, beat)
                time.sleep(self.base_tempo * tempo_multiplier)
                self.chimes.all_off() # for safety
            except Exception as e:
                self.chimes.all_off()
            finally:
                self.chimes.all_off()


# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class States:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
        self.states =States()
        self.state = self.states.WAITING_FOR_CONNECTIONS

        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.players = [
            Player(0),
            Player(1),
            Player(2),
            Player(3),
            Player(4),
            Player(5)
        ]
        self.tb.subscribe_to_topic("connected")
        self.start()

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self, topic, message):
        self.add_to_queue(topic, message)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))
    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                if topic == "sound_event":
                    target, score = message
                    self.players[target].play(score)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Main()



main.add_to_queue("sound_event",(1,"attraction_mode"))











class gpios():
  def __init__(self, chimeGPIOs, deviceId=0 ):
    self.deviceId = deviceId
    self.chimeGPIOs = chimeGPIOs
    GPIO.setmode(GPIO.BCM)

    # config and turn off
    for gpio in self.chimeGPIOs:
      GPIO.setup( gpio, GPIO.OUT )
      GPIO.output( gpio, GPIO.LOW )


  # send a vector of 5 ints, no bit packing etc. to GPIOs
  def write( self, chime_vec ):
    #print("values are: ", chime_vec )
    for idx in range( 0, len( chime_vec ) ):
      outval = GPIO.LOW
      chime_val = chime_vec[ idx ]
      if chime_val != 0:
        outval = GPIO.HIGH
      gpio = self.chimeGPIOs[ idx ]
      GPIO.output( gpio, outval )
    
  # disable GPIOs driving
  def disable_GPIOs( self ):
    for gpio in self.chimeGPIOs:
      print( f"disabling gpio {gpio}" )
      GPIO.output( gpio, GPIO.LOW )
      #GPIO.setup( gpio, GPIO.IN )


chimes = gpios( chimeGPIOs = [ 2, 3, 4, 17, 18,   27, 22, 23, 24, 10,   9, 25, 11, 8, 0,   1, 5, 6, 12, 13,   19, 16, 26, 
20, 21 ] )


# attraction mode
seq = [ [ 1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0 ],
        [ 0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1 ],
        [ 0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0,  0, 0, 0, 0,  0, 0, 0, 0 ],
        [ 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 1, 0, 1,  0, 1, 0, 1,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0,  1, 0, 1, 0 ] ]

seq_step = 0
seq_step_last = 25
seq_step_delta = 1

lfo = 0 # initial phase of lfo, tyically statr quiet
lfo2 = 0

#BPM = 96  # set this
#BPM = 566  # super fast mode
#period = 60 / BPM # let this get computed

# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        # compute LFOs
        lfo = lfo + 0.13
        lfo2 = lfo2 + 0.21
        mag = 0.5 + 0.5 * math.sin( lfo ) # leave this LFO output to always range from 0.0 to 1.0
        mag2 = 0.5 + 0.5 * math.sin( lfo2 )
        #print( mag )

        #BPM = 80 + 86 * mag2
        BPM = 80
        if random.random() > 0.9:
            BPM = BPM * 2
        if random.random() > 0.9:
            BPM = BPM * 2
        if random.random() > 0.9:
            BPM = BPM / 2
        if random.random() > 0.98:
            seq_step_delta = -1 * seq_step_delta
        period = 60 / BPM
        
        # compute ontime
        # these are in seconds.  e.g. 0.10  = 100 millisec
        #ontime = 0.004 + 0.007 * mag   # very subtle cross over hardest part
        ontime = 0.010
        #ontime = 0.100 + 0.100 * mag   # pretty hard 10ms is ideal
        #ontime = 0.006 + 0.006 * mag   # should be pretty optimal
        #ontime = period / 2 # good for testing  to see on scope
        offtime = period - ontime     # auto-calc offtime to maintain BPM as specified above
        print( ontime, offtime )    

    
        # turn em on from seq array
        chime_vec = []
        for trk in range( 0, 25 ):
            if seq_step == trk:
                chime_vec.append( 1 )
                print( trk )
            else:
                chime_vec.append( 0 )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        # turn em off
        chime_vec = 25 * [ 0 ]
        lfo = lfo + 0.13
        lfo2 = lfo2 + 0.21
        mag = 0.5 + 0.5 * math.sin( lfo ) # leave this LFO output to always range from 0.0 to 1.0
        mag2 = 0.5 + 0.5 * math.sin( lfo2 )
        #print( mag )

        #BPM = 80 + 86 * mag2
        BPM = 80
        if random.random() > 0.9:
            BPM = BPM * 2
        if random.random() > 0.9:
            BPM = BPM * 2
        if random.random() > 0.9:
            BPM = BPM / 2
        if random.random() > 0.98:
            seq_step_delta = -1 * seq_step_delta
        period = 60 / BPM
        
        # compute ontime
        # these are in seconds.  e.g. 0.10  = 100 millisec
        #ontime = 0.004 + 0.007 * mag   # very subtle cross over hardest part
        ontime = 0.010
        #ontime = 0.100 + 0.100 * mag   # pretty hard 10ms is ideal
        #ontime = 0.006 + 0.006 * mag   # should be pretty optimal
        #ontime = period / 2 # good for testing  to see on scope
        offtime = period - ontime     # auto-calc offtime to maintain BPM as specified above
        print( ontime, offtime )    

    
        # turn em on from seq array
        chime_vec = []
        for trk in range( 0, 25 ):
            if seq_step == trk:
                chime_vec.append( 1 )
                print( trk )
            else:
                chime_vec.append( 0 )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        # turn em off
        chime_vec = 25 * [ 0 ]
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( offtime )

        seq_step = seq_step + seq_step_delta
        if seq_step >= seq_step_last:
            seq_step = seq_step - 25
        if seq_step < 0:
            seq_step = seq_step + 25

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    chimes.disable_GPIOs()    
    
