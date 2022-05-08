import queue
import spidev 
import threading
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

class Square_Wave_Generator(threading.Thread):
    def __init__(self, gpio_number, frequency_in_hz):
        threading.Thread.__init__(self)
        self.gpio_number = gpio_number
        self.period = 1.0/frequency_in_hz
        GPIO.setup(self.gpio_number, GPIO.OUT)

    def run(self):
        while True:
          GPIO.output(self.gpio_number, GPIO.LOW )
          time.sleep(self.period)
          GPIO.output(self.gpio_number, GPIO.HIGH )
          time.sleep(self.period)

class SPI_16_Bit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        GPIO.setup(19, GPIO.OUT)
        GPIO.output(19, GPIO.HIGH )

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.open = True
        self.spi.mode = 0b00
        self.spi.bits_per_word = 16
        #self.spi.no_cs = True
        self.spi.max_speed_hz = 500000

    def add_to_queue(self, gain_int):
        self.queue.put(gain_int)

    def run(self):
        while True:
            gain_int = self.queue.get(True)
            gain_16_bits = int(65536.0 * float(gain_int) /100.0)
            print("")
            print(gain_16_bits)
            self.spi.writebytes(gain_16_bits)

class CLI(threading.Thread):
    def __init__(self, ):
        threading.Thread.__init__(self)
        self.square_wave_generator = Square_Wave_Generator(26, 1000)
        self.square_wave_generator.start()
        self.spi_16_bit = SPI_16_Bit()
        self.spi_16_bit.start()

    def run(self):
        while True:
            input_str = input("please enter gain as a number between 0-100: ")
            input_float = float(input_str)
            self.spi_16_bit.add_to_queue(input_float)

cli = CLI()
cli.start()