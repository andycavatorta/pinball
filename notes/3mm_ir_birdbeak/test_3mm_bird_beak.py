#!/usr/bin/env python

import time

import bird_beak as bird_beak

cheep = bird_beak.bird_beak()

while True:

    val = cheep.read_it()
    print( val )
    time.sleep( 0.0205 )

