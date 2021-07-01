"""
sudo modprobe i2c_bcm2708

pin info:
the pitch key sensors are daisy-chained together in an I2C bus with four wires.
    pin 1: +3.3VDC
    pin 9: GND
    pin 3: SDA [ Serial Data ]
    pin 5: SCL [ Serial Clock ]

"""

import os
import time
import threading
import traceback
import sys


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
UPPER_PATH = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
THIRTYBIRDS_PATH = "%s/thirtybirds3" % (UPPER_PATH )

print("BASE_PATH=",BASE_PATH)
print("UPPER_PATH=",UPPER_PATH)
print("THIRTYBIRDS_PATH=",THIRTYBIRDS_PATH)


#sys.path.append(BASE_PATH)
#sys.path.append(UPPER_PATH)

from thirtybirds3.adapters.sensors.MPR121 import MPR121

class Capacitive_Sensors(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor = MPR121.MPR121()
        self.keybanks = [MPR121.MPR121() for i in xrange(4)]
        for i, addr in enumerate([0x5A]):
            print self.keybanks[i].begin(addr)

    def run(self):
        last_state_of_all_keys = [keybank.touched() for keybank in self.keybanks]
        while True:
            current_state_of_all_keys = [keybank.touched() for keybank in self.keybanks]
            for j in xrange(4):
                for i in xrange(12):
                    pin_bit = 1 << i
                    if current_state_of_all_keys[j] & pin_bit and not last_state_of_all_keys[j] & pin_bit:
                        #global_key_number = 12 + (j * 12) + (11-i)
                        global_key_number = (j * 12) + i
                        print(global_key_number)
                        print('touched: keybank ' + str(j) + ', key ' + str(i)) 

            last_state_of_all_keys = current_state_of_all_keys
            time.sleep(0.01)


def init():
    capcitive_sensors = Capacitive_Sensors()
    #capcitive_sensors.daemon = True
    capcitive_sensors.start()

init()