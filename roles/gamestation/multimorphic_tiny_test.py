import p3_jab
import time
p3 = p3_jab.P3Jab()
p3.pulse_coil("A0-B0-2", 20)
time.sleep(0.5)
p3.pulse_coil("A0-B1-0", 20)
time.sleep(0.5)
p3.pulse_coil("A0-B1-1", 20)
time.sleep(0.5)
p3.pulse_coil("A0-B1-2", 20)
time.sleep(0.5)
p3.pulse_coil("A0-B1-5", 20)
time.sleep(0.5)
p3.pulse_coil("A0-B1-4", 20)
time.sleep(0.5)

while True:
    p3.poll()
    time.sleep(.005)