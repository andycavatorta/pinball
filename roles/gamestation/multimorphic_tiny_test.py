import p3_jab
import time
p3 = p3_jab.P3Jab()
p3.pulse_coil("A2-B0-0", 100)

while True:
    p3.poll()
    time.sleep(.005)