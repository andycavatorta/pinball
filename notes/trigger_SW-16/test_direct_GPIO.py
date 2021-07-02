#!/usr/bin/env python

import time
import math

import direct_GPIO as solenoid_driver
#import HC595_shift_reg as shifter

chimes = solenoid_driver.gpio_based( chimeGPIOs = [ 3, 23, 24, 25, 26 ] )


# attraction mode
seq = [ [ 1, 0 ],
        [ 0, 0 ],
        [ 0, 0 ],
        [ 0, 0 ],
        [ 0, 0 ] ]

seq_step = 0



# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        BPM = 80
        period = 60 / BPM
        
        # compute ontime
        # these are in seconds.  e.g. 0.10  = 100 millisec
        ontime = 1

        # turn em on from seq array
        chime_vec = []
        for trk in range( 0, 5 ):
            chime_vec.append( seq[ trk ][ seq_step ] )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        seq_step = seq_step + 1
        if seq_step >= 2:
            seq_step = 0

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    chimes.disable_GPIOs()    
    
    
    
    
    





