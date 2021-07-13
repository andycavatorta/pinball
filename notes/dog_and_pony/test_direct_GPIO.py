#!/usr/bin/env python

import time
import math

import direct_GPIO as solenoid_driver


chimes = solenoid_driver.gpio_based( chimeGPIOs = [ 25, 8, 7,   21, 1, 12, 20, 16 ] )


# attraction mode
seq = [ [ 0, 0, 0,  1, 0, 0, 0, 0  ],
        [ 0, 0, 0,  1, 1, 0, 0, 0  ],
        [ 0, 0, 0,  1, 1, 1, 0, 0  ],
        [ 0, 0, 0,  1, 1, 1, 1, 0  ],
        [ 0, 0, 0,  1, 1, 1, 1, 1  ],
        [ 0, 0, 0,  0, 0, 0, 0, 0  ],
        [ 0, 0, 0,  0, 1, 0, 1, 0  ],
        [ 0, 0, 0,  1, 0, 1, 0, 1  ],
        [ 0, 0, 0,  0, 1, 0, 1, 0  ],
        [ 0, 0, 0,  1, 0, 1, 0, 1  ],
        [ 0, 0, 0,  0, 1, 0, 1, 0  ],
        [ 0, 0, 0,  0, 0, 1, 0, 0  ],
        [ 1, 0, 0,  0, 0, 0, 0, 0  ],
        [ 0, 1, 0,  0, 0, 0, 0, 0  ],
        [ 0, 0, 1,  0, 0, 0, 0, 0  ],
        [ 0, 1, 0,  0, 0, 0, 0, 0  ],
        [ 1, 0, 0,  0, 0, 0, 0, 0  ],
        [ 0, 0, 1,  1, 1, 1, 1, 1  ],
        [ 0, 1, 0,  0, 1, 1, 1, 0  ],
        [ 1, 0, 0,  0, 0, 1, 0, 0  ],
        [ 0, 1, 0,  0, 0, 0, 0, 0  ] ]

print( len(seq), len(seq[0]))     # 13, 8

seq_step = 0


lfo = 0 # initial phase of lfo, tyically statr quiet

# this is put inside a try block so it can clean up 
# the output enable.  very important to protect relays from
# being left on!!!!
try:
    while True:
        # compute LFOs
        lfo = lfo + 0.13
        mag = 0.5 + 0.5 * math.sin( lfo ) # leave this LFO output to always range from 0.0 to 1.0
        print( mag )

        BPM = 80
        period = 60 / BPM
        
        # compute ontime
        # these are in seconds.  e.g. 0.10  = 100 millisec
        ontime = 0.600 + 0.100 * mag   # pretty hard 10ms is ideal
        offtime = period - ontime     # auto-calc offtime to maintain BPM as specified above
        print( ontime, offtime )    

    
        # turn em on from seq array
        #chime_vec = [ 0 ] * len( seq[ 0 ] )
        chime_vec = []
        for trk in range( 0, len( seq[ 0 ] ) ):
            chime_vec.append( seq[ seq_step ][ trk ] )
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( ontime )
        
        # turn em off
        chime_vec = [ 0 ] * len( seq[ 0 ] ) # [ 0, 0, 0, 0, 0 ]
        print( chime_vec )
        chimes.write( chime_vec )
        time.sleep( offtime )

        seq_step = seq_step + 1
        if seq_step >= len( seq ):
            seq_step = 0

except KeyboardInterrupt:       
    print( "You've exited the program." )

finally:
    print( "cleaning up GPIO now." )
    chimes.disable_GPIOs()    
    
    
    
    
    





