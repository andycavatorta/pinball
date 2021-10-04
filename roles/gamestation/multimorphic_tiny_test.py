import p3_jab
import time
p3 = p3_jab.P3Jab()
p3.pulse_coil("A0-B0-2", 20)

while True:
    p3.poll()
    time.sleep(.005)