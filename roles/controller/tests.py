import time

class Displays():
    def __init__(self, tb):
        self.tb = tb
        self.destinations = ("pinball1display","pinball2display","pinball3display","pinball4display","pinball5display")
        self.phrases = ("juega","dinero","trueque","como","fue","juega","dinero","trueque","como","fue")

    def circular_countown(self):
        displayed_number = 999        
        for destination in self.destinations:
            self.tb.publish(topic="set_number",message=displayed_number,destination=destination)
        time.sleep(.5)
        while displayed_number > 0:
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=displayed_number-1,destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-10,destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-100,destination=destination)
                time.sleep(.5)
            displayed_number -= 111

"""

while True:
    for ai in range(10):
        for bi in range(10):
            for ci in range(10):
                number = (ai * 100) + (bi * 10) + ci
                for destination in destinations:
                    role_module.main.tb.publish(topic="set_number",message=number,destination=destination)
                time.sleep(0.4)
            for destination in destinations:
                print(phrases[bi], destination)
                role_module.main.tb.publish(topic="set_phrase",message=phrases[bi],destination=destination)


for destination in destinations:
    role_module.main.tb.publish(topic="set_phrase",message="fue",destination=destination)


while True:
    role_module.main.tb.publish(topic="set_phrase",message="juega",destination="pinball3display")
    role_module.main.tb.publish(topic="set_number",message=000,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=111,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="dinero",destination="pinball3display")
    role_module.main.tb.publish(topic="set_number",message=222,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=333,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="trueque",destination="pinball3display")
    role_module.main.tb.publish(topic="set_number",message=444,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=555,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="como",destination="pinball3display")
    role_module.main.tb.publish(topic="set_number",message=666,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=777,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="fue",destination="pinball3display")
    role_module.main.tb.publish(topic="set_number",message=888,destination="pinball3display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=999,destination="pinball3display")


while True:
    role_module.main.tb.publish(topic="set_phrase",message="juega",destination="pinball4display")
    role_module.main.tb.publish(topic="set_number",message=000,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=111,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="dinero",destination="pinball4display")
    role_module.main.tb.publish(topic="set_number",message=222,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=333,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="trueque",destination="pinball4display")
    role_module.main.tb.publish(topic="set_number",message=444,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=555,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="como",destination="pinball4display")
    role_module.main.tb.publish(topic="set_number",message=666,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=777,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="fue",destination="pinball4display")
    role_module.main.tb.publish(topic="set_number",message=888,destination="pinball4display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=999,destination="pinball4display")
    time.sleep(2)


while True:
    role_module.main.tb.publish(topic="set_phrase",message="juega",destination="pinball5display")
    role_module.main.tb.publish(topic="set_number",message=000,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=111,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="dinero",destination="pinball5display")
    role_module.main.tb.publish(topic="set_number",message=222,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=333,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="trueque",destination="pinball5display")
    role_module.main.tb.publish(topic="set_number",message=444,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=555,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="como",destination="pinball5display")
    role_module.main.tb.publish(topic="set_number",message=666,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=777,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_phrase",message="fue",destination="pinball5display")
    role_module.main.tb.publish(topic="set_number",message=888,destination="pinball5display")
    time.sleep(2)
    role_module.main.tb.publish(topic="set_number",message=999,destination="pinball5display")
    time.sleep(2)
"""