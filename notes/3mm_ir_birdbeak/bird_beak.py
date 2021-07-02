import time

import RPi.GPIO as GPIO


def gpio_reset( pin_num ):
    GPIO.setup( pin_num, GPIO.IN)
    #GPIO.output( pin_num, GPIO.HIGH)

class bird_beak():
  def __init__( self, gpio_pin = 17 ):
    self.gpio_pin = gpio_pin
    GPIO.setmode( GPIO.BCM )
    try:
      pass
    except:
      print("Could not")

    GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP )
    #GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN )

  def read_it( self ):
    val = GPIO.input( self.gpio_pin )
    return val

