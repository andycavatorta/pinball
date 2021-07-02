import time
import RPi.GPIO as GPIO


class gpio_based():
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

    for idx in range( 0, 5 ):
      gpio = self.chimeGPIOs[ idx ]
      
      # for high val, switch to input and let SW-16's pull-up make it high
      if chime_vec[ idx ] != 0:
        outval = GPIO.LOW
        GPIO.output( gpio, outval )
        GPIO.setup( gpio, GPIO.IN, pull_up_down = GPIO.PUD_OFF )

      # for low val, drive low
      else:
        GPIO.setup( gpio, GPIO.OUT )
        outval = GPIO.LOW
        GPIO.output( gpio, outval )

