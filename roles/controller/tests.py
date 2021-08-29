import random
import time

class Displays():
    def __init__(self, tb):
        self.tb = tb
        self.destinations = ("pinball1display","pinball2display","pinball3display","pinball4display","pinball5display")
        self.phrases = ("juega","dinero","trueque","como","fue","juega","dinero","trueque","como","fue")
        self.chime_pattern = (
            ("f_piano","g_piano","gsharp_piano"),
            ("f_piano","g_piano","asharp_piano"),
            ("f_piano","gsharp_piano","asharp_piano"),
            ("f_piano","gsharp_piano","c_piano"),
            ("g_mezzo","gsharp_mezzo","asharp_mezzo"),
            ("g_mezzo","gsharp_mezzo","c_mezzo"),
            ("g_mezzo","asharp_piano","c_piano"),
            ("gsharp_mezzo","asharp_mezzo","c_mezzo"),
            ("gsharp_forte","asharp_forte","c_forte"),
            ("gsharp_forte","asharp_forte","c_forte"),
        )
    def circular_countown(self):
        displayed_number = 999        
        for destination in self.destinations:
            self.tb.publish(topic="set_number",message=displayed_number,destination=destination)
        time.sleep(.5)
        while displayed_number > 0:
            cycle_of_ten = int(displayed_number/100)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=displayed_number-1,destination=destination)
                self.tb.publish(topic="play_score",message="c_mezzo",destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-11,destination=destination)
                self.tb.publish(topic="play_score",message="asharp_mezzo",destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-111,destination=destination)
                self.tb.publish(topic="play_score",message="gsharp_mezzo",destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_phrase",message=self.phrases[cycle_of_ten],destination=destination)
                self.tb.publish(topic="play_score",message="g_mezzo",destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_phrase",message=self.phrases[cycle_of_ten],destination=destination)
                self.tb.publish(topic="play_score",message="f_mezzo",destination=destination)
                time.sleep(.5)

            time.sleep(.5)
            displayed_number -= 111


    def circular_countown_just_displays(self):
        displayed_number = 999        
        for destination in self.destinations:
            self.tb.publish(topic="set_number",message=displayed_number,destination=destination)
        time.sleep(.5)
        while displayed_number > 0:
            cycle_of_ten = int(displayed_number/100)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=displayed_number-1,destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-11,destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_number",message=displayed_number-111,destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_phrase",message=self.phrases[cycle_of_ten],destination=destination)
                time.sleep(.5)
                self.tb.publish(topic="set_phrase",message=self.phrases[cycle_of_ten],destination=destination)
                time.sleep(.5)

            time.sleep(.5)
            displayed_number -= 111


    def blinking_juega_and_number_show(self):
        interval = 0.2
        while True:
            for destination in self.destinations:
                self.tb.publish(topic="set_phrase",message="",destination=destination)
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_phrase",message="juega",destination=destination)
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    
            time.sleep(interval)
            for destination in self.destinations:
                self.tb.publish(topic="set_number",message=random.randint(0,999),destination=destination)    


    def wave(self):
        interval = 0.3
        pitches = [
            "c_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "f_mezzo"
        ]
        """
        pitches = [
            "c_piano",
            "asharp_piano",
            "gsharp_piano",
            "g_piano",
            "f_piano"
        ]
        """
        while True:
            for pitch_i in range(5):
                for destination in self.destinations:
                    self.tb.publish(topic="set_phrase",message="",destination=destination)
                    self.tb.publish(topic="set_number",message=999,destination=destination)    
                for destination in self.destinations:
                    self.tb.publish(topic="play_score",message=pitches[pitch_i],destination=destination)
                    if pitch_i != 0:
                        self.tb.publish(topic="play_score",message=pitches[0],destination=destination)
                    time.sleep(interval/5)
                #time.sleep(interval/2)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=000,destination=destination)    
                    self.tb.publish(topic="set_phrase",message="juega",destination=destination)
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)


                for destination in self.destinations:
                    self.tb.publish(topic="set_phrase",message="",destination=destination)
                    self.tb.publish(topic="set_number",message=999,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=000,destination=destination)    
                    self.tb.publish(topic="set_phrase",message="juega",destination=destination)
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)


                for destination in self.destinations:
                    self.tb.publish(topic="set_phrase",message="",destination=destination)
                    self.tb.publish(topic="set_number",message=999,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=000,destination=destination)    
                    self.tb.publish(topic="set_phrase",message="juega",destination=destination)
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)


                for destination in self.destinations:
                    self.tb.publish(topic="set_phrase",message="",destination=destination)
                    self.tb.publish(topic="set_number",message=999,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:
                    self.tb.publish(topic="set_number",message=000,destination=destination)    
                    self.tb.publish(topic="set_phrase",message="juega",destination=destination)
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=111,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=222,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=333,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=444,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=555,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=666,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=777,destination=destination)    
                time.sleep(interval)
                for destination in self.destinations:                
                    self.tb.publish(topic="set_number",message=888,destination=destination)    
                time.sleep(interval)



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