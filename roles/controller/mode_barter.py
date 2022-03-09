"""
todo:

trueque mode animation


dinero mode animation:
    make it clear that we are doing business with the center carousel
    make it clear that add_Fruit trades fruit with center for peso
    make is clear that pesos are exchanged with center for fruit
    different music
    



questions:

1st level:
    does the game play well mechanically?
    does the trade frequency need to be adjusted?
    does the length of the game need to be adjusted?

2nd level:
    does the game communicate well enough for tomorrow?
        the center carousel is a problem


known issues:
    the pie doesn't start filling during the first ball of the game.
    the animations aren't perfect in the current version but are they good enough?
    

trade frequency:
    players can trade when they have one of their own fruits or a peso to trade
    we add a new fruit to trade every 20 points and when pie fills
game length:
    trueque and dinero rounds are 120 seconds.  


send email when restarting controller
add current sensors
in attraction mode, check presence of balls
detect runaway pinball assemblies by counting event frequency



"""


# todo: why does trueque happen infrequently?  why does potential trading parners fail later?   
# todo: make repeat matrix animations repeat.


# todo: why does pie not light sometimes? 


import codecs
import os
import queue
import random
import settings
import threading
import time
import traceback


CAROUSEL_FRUIT_ORDER = {
    "coco":["coco","naranja","mango","sandia","pina"],
    "naranja":["naranja","mango","sandia","pina","coco"],
    "mango":["mango","sandia","pina","coco","naranja"],
    "sandia":["sandia","pina","coco","naranja","mango"],
    "pina":["pina","coco","naranja","mango","sandia"]
}


class phase_names():
    NOPLAYER="noplayer"
    COMIENZA="comienza"
    PINBALL="pinball"
    INVITOR="invitor"
    INVITEE="invitee"
    TRADE="trade"
    FAIL="fail"


class Animation_Score(threading.Thread):
    def __init__(self, commands, fruit_name):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.commands = commands
        self.fruit_name = fruit_name
        self.start()


    def flipboard(self, start_number, end_number):
        #print("Animation_Score 0", start_number, end_number, self.fruit_name)
        if start_number < end_number:
            for display_score in range(start_number, end_number+1):
                self.commands.request_number(display_score)
                #print("Animation_Score 1", display_score)
                time.sleep(0.05)
        if start_number > end_number:
            for display_score in range(end_number, start_number, -1):
                self.commands.request_number(display_score)
                #print("Animation_Score 2", display_score)
                time.sleep(0.05)


    def add_to_queue(self, name, data=[]):
        self.queue.put((name, data))


    def run(self):
        while True:
            name, data = self.queue.get()
            if name == "flipboard":
                self.flipboard(data[0],data[1])


class Animation_Transactions(threading.Thread):
    def __init__(self, commands):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.commands = commands
        self.start()


    def animation_fill_carousel(self, fruit_order):
        fruit_name = fruit_order[1]
        self.commands.request_score("f_piano")
        self.commands.cmd_carousel_lights(fruit_name,"low")
        time.sleep(0.2)
        self.commands.request_score("g_piano")
        self.commands.cmd_carousel_lights(fruit_name,"med")
        time.sleep(0.2)
        self.commands.request_score("gsharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"high")
        time.sleep(0.4)
        fruit_name = fruit_order[2]
        self.commands.request_score("g_piano")
        self.commands.cmd_carousel_lights(fruit_name,"low")
        time.sleep(0.2)
        self.commands.request_score("gsharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"med")
        time.sleep(0.2)
        self.commands.request_score("asharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"high")
        time.sleep(0.4)
        fruit_name = fruit_order[3]
        self.commands.request_score("gsharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"low")
        time.sleep(0.2)
        self.commands.request_score("asharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"med")
        time.sleep(0.2)
        self.commands.request_score("c_piano")
        self.commands.cmd_carousel_lights(fruit_name,"high")
        time.sleep(0.4)
        fruit_name = fruit_order[4]
        self.commands.request_score("g_piano")
        self.commands.request_score("asharp_piano")
        self.commands.cmd_carousel_lights(fruit_name,"low")
        time.sleep(0.2)
        self.commands.cmd_carousel_lights(fruit_name,"med")
        time.sleep(0.2)
        self.commands.request_score("f_piano")
        self.commands.request_score("gsharp_piano")
        self.commands.request_score("c_piano")
        self.commands.cmd_carousel_lights(fruit_name,"high")
        time.sleep(0.4)


    def add_to_queue(self, name, data=[]):
        self.queue.put((name, data))


    def run(self):
        while True:
            name, data = self.queue.get()
            if name == "animation_fill_carousel":
                self.animation_fill_carousel(data)


class Animation_Pinball_Game(threading.Thread):
    def __init__(self, commands):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.commands = commands
        self.start()


    def pie_full(self):
        self.commands.cmd_playfield_lights("pie","energize")# light animation
        self.commands.request_score("f_mezzo")
        self.commands.cmd_playfield_lights("pie_pop_left","off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_left","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_pop_middle","off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_middle","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("g_mezzo")
        self.commands.cmd_playfield_lights("pie_pop_right","off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_right","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_spinner","off")# light animation
        self.commands.cmd_playfield_lights("trail_spinner","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("gsharp_mezzo")
        self.commands.cmd_playfield_lights("pie_sling_right","off")# light animation
        self.commands.cmd_playfield_lights("trail_sling_right","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_rollover_right","off")# light animation
        self.commands.cmd_playfield_lights("trail_rollover_right","stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("asharp_mezzo")
        self.commands.cmd_playfield_lights("pie_rollover_left","off")# light animation
        self.commands.cmd_playfield_lights("trail_rollover_left","stroke_on")# light segment
        time.sleep(.15)
        self.commands.cmd_playfield_lights("pie_sling_left","off")# light animation
        self.commands.cmd_playfield_lights("trail_sling_left","stroke_on")# light segment
        self.commands.request_score("c_mezzo")
        time.sleep(.15)
        self.commands.request_score("f_mezzo")
        self.commands.request_score("gsharp_mezzo")
        self.commands.request_score("c_mezzo")


    def chime_sequence(self, pitches, ms):
        for pitch in pitches:
            if pitch == "": # rest
                continue
            self.commands.request_score(pitch)
            time.sleep(ms)


    def add_to_queue(self, name, data=[]):
        self.queue.put((name, data))


    def run(self):
        while True:
            name, data = self.queue.get()
            if name == "pie_full":
                self.pie_full()
            if name == "chime_sequence":
                self.chime_sequence(data[0],data[1])


class Station(threading.Thread):
    def __init__(self, fruit_name, commands, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.fruit_name = fruit_name
        self.commands = commands
        self.parent_ref = parent_ref
        self.animation_pinball_game = Animation_Pinball_Game(commands)
        self.animation_transactions = Animation_Transactions(commands)
        self.animation_score = Animation_Score(commands, fruit_name)
        self.fruit_to_spend = ""
        self.current_phase = phase_names.NOPLAYER
        self.last_trade_time = time.time() # initiated on first boot. hereafter set only by MODE_BARTER for thread safety
        self.pie_data_segments = {
            "pop_left":False,
            "pop_middle":False,
            "pop_right":False,
            "spinner":False,
            "sling_right":False,
            "rollover_right":False,
            "rollover_left":False,
            "sling_left":False,
        }
        self.carousel_data_segments = {
            "coco":False,
            "naranja":False,
            "mango":False,
            "sandia":False,
            "pina":False,
            "peso":False,
        }
        self.carousel_fruit_order = CAROUSEL_FRUIT_ORDER[self.fruit_name]
        self.start()


    def pie_target_hit(self, target_name):
        if self.pie_data_segments[target_name] == False:
            self.pie_data_segments[target_name] = True
            self.commands.cmd_playfield_lights("pie_{}".format(target_name),"on")# light animation
            self.commands.cmd_playfield_lights("trail_{}".format(target_name),"back_stroke_off")# light segment
            if len([True for k,v in self.pie_data_segments.items() if v == True])==8:
                self.animation_pinball_game.add_to_queue("pie_full")
                self.animation_score.add_to_queue("flipboard",[self.commands.get_barter_points(),self.commands.get_barter_points()+25])
                self.add_to_queue("increment_score",25)
                self.pie_data_reset()


    def pie_data_reset(self):
        self.pie_data_segments = {
            "pop_left":False,
            "pop_middle":False,
            "pop_right":False,
            "spinner":False,
            "sling_right":False,
            "rollover_right":False,
            "rollover_left":False,
            "sling_left":False,
        }


    def pie_update_display(self):
        for name, val in self.pie_data_segments.items():
            self.commands.cmd_playfield_lights("pie_{}".format(name),"on" if val else "off")


    def carousel_add_fruit(self, fruit_name):
        self.carousel_data_segments[fruit_name] = True


    def carousel_remove_fruit(self, fruit_name):
        self.carousel_data_segments[fruit_name] = False


    def carousel_get_fruit_presence(self, fruit_name):
        return self.carousel_data_segments[fruit_name]


    def carousel_get_fruits_present(self, exclude_this_fruit=False):
        present = []
        for name, val in self.carousel_data_segments.items():
            if exclude_this_fruit:
                if name == self.fruit_name:
                    continue
            if val:
                present.append(name)
        return present


    def carousel_get_fruits_missing(self, exclude_this_fruit=False):
        missing = []
        for name, val in self.carousel_data_segments.items():
            if exclude_this_fruit:
                if name == self.fruit_name:
                    continue
                if name == "peso": # todo: this should be fixed somewhere upstream
                    continue
            if not val:
                missing.append(name)
        return missing


    def carousel_display_fruit_presences(self, level = "on"):
        for fruit_name, presence in self.carousel_data_segments.items():
            self.commands.cmd_carousel_lights(fruit_name, level if presence else "off")


    def increment_score(self, points=1):
        old_score = self.commands.get_barter_points()
        new_score = self.commands.get_barter_points() + points
        self.animation_score.add_to_queue("flipboard",[old_score,new_score])
        # end mode if player scores over 900 points
        if new_score > 900:
            self.parent_ref.set_current_mode(settings.Game_Modes.RESET)
            self.parent_ref.set_current_mode(settings.Game_Modes.MONEY_MODE_INTRO)
        self.commands.set_barter_points(new_score)


    def decrement_score(self, points=-1):
        """
        negative scores must be prevented elsewhere
        """
        self.animation_score.add_to_queue("flipboard",[self.commands.get_barter_points(),self.commands.get_barter_points()-points])
        self.commands.set_barter_points(self.commands.get_barter_points()-1)


    def setup(self):
        if self.current_phase == phase_names.NOPLAYER:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            self.commands.enable_izquierda_coil(False)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(False)
            self.commands.request_button_light_active("izquierda",False)
            self.commands.request_button_light_active("trueque",False)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",False)
            self.commands.cmd_playfield_lights("all_radial", "off")
            self.commands.cmd_carousel_lights("all", "off")

        if self.current_phase == phase_names.COMIENZA:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== COMIENZA =====================", self.fruit_name)
            self.commands.enable_izquierda_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(True)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(True)
            self.commands.request_button_light_active("izquierda",True)
            self.commands.request_button_light_active("trueque",False)
            self.commands.request_button_light_active("comienza",True)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",True)
            # if there are other fruits, one fruit will be spent when comienza is pushed.
            other_fruits_present = self.carousel_get_fruits_present(True)
            if len(other_fruits_present) > 0:
                self.fruit_to_spend = random.choice(other_fruits_present)
            else:
                self.fruit_to_spend = ""
                lower_score = self.commands.get_barter_points()-5 if self.commands.get_barter_points() >5 else 1
                #self.decrement_score(lower_score)
                self.commands.set_barter_points(lower_score)
            self.commands.cmd_carousel_lights(self.fruit_to_spend,  "high")
            time.sleep(0.2)
            self.commands.request_score("g_mezzo")
            time.sleep(0.2)
            self.commands.request_button_light_active("comienza",True)
            self.commands.request_score("gsharp_mezzo")
            time.sleep(0.2)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_score("g_mezzo")
            time.sleep(0.2)
            self.commands.request_button_light_active("comienza",True)
            self.commands.request_score("gsharp_mezzo")

        if self.current_phase == phase_names.PINBALL:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== PINBALL =====================", self.fruit_name)
            self.commands.request_button_light_active("izquierda",True)
            self.commands.request_button_light_active("trueque",False)
            self.commands.request_button_light_active("comienza",True)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",True)
            self.commands.enable_izquierda_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_dinero_coil(False)

        if self.current_phase == phase_names.INVITOR:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== INVITOR =====================", self.fruit_name)
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(False)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(False)
            self.commands.request_button_light_active("izquierda",False)
            self.commands.request_button_light_active("trueque",True)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",False)
            self.commands.cmd_playfield_lights("sign_arrow_left", "on")
            self.commands.cmd_playfield_lights("sign_bottom_left", "on")

        if self.current_phase == phase_names.INVITEE:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== INVITEE =====================", self.fruit_name)
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(True)
            self.commands.request_button_light_active("izquierda",True)
            self.commands.request_button_light_active("trueque",True)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",True)
            self.commands.cmd_playfield_lights("sign_arrow_left", "on")
            self.commands.cmd_playfield_lights("sign_bottom_left", "on")


        if self.current_phase == phase_names.TRADE:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== TRADE =====================", self.fruit_name)
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(False)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(False)
            self.commands.request_button_light_active("izquierda",False)
            self.commands.request_button_light_active("trueque",False)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",False)
            self.commands.cmd_playfield_lights("sign_arrow_left", "off")
            self.commands.cmd_playfield_lights("sign_bottom_left", "on")


        if self.current_phase == phase_names.FAIL:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, False)
            print(time.ctime(time.time()),"===================== FAIL =====================", self.fruit_name)
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(False)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(False)
            self.commands.request_button_light_active("izquierda",False)
            self.commands.request_button_light_active("trueque",False)
            self.commands.request_button_light_active("comienza",False)
            self.commands.request_button_light_active("dinero",False)
            self.commands.request_button_light_active("derecha",False)
            self.commands.cmd_playfield_lights("sign_arrow_left", "off")
            self.commands.cmd_playfield_lights("sign_bottom_left", "on")

    def event_handler(self, topic, message):
        #print("event_handler",topic, message,self.current_phase)
        if self.current_phase == phase_names.NOPLAYER:
            pass

        if self.current_phase == phase_names.COMIENZA:
            if topic == "event_pop_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("gsharp_mezzo")
                    self.pie_target_hit("pop_left")
            if topic == "event_pop_middle":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("g_mezzo")
                    self.pie_target_hit("pop_middle")
            if topic == "event_pop_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("f_mezzo")
                    self.pie_target_hit("pop_right")
            if topic == "event_roll_inner_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_inner_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_slingshot_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_left")
                    self.pie_target_hit("rollover_left")
                    self.commands.request_score("asharp_mezzo")

            if topic == "event_slingshot_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_right")
                    self.pie_target_hit("rollover_right")
                    self.commands.request_score("asharp_mezzo")
                    
            if topic == "event_spinner":
                if message:
                    self.add_to_queue("increment_score",1)
                    self.pie_target_hit("spinner")
                    self.commands.request_score("c_mezzo")

            if topic == "event_button_comienza":
                print("Station.event_handler COMIENZA", topic, self.fruit_name, message, message==True)
                self.end()
            """
            if topic == "event_trough_sensor":
                if message==False:
                    print("Station.event_handler COMIENZA",topic, self.fruit_name, message, message==True)
                    self.set_phase(phase_names.PINBALL)
            """

        if self.current_phase == phase_names.PINBALL:
            if topic == "event_pop_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("gsharp_mezzo")
                    self.pie_target_hit("pop_left")
            if topic == "event_pop_middle":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("g_mezzo")
                    self.pie_target_hit("pop_middle")
            if topic == "event_pop_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("f_mezzo")
                    self.pie_target_hit("pop_right")
            if topic == "event_roll_inner_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_inner_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.add_to_queue("increment_score",3)
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_slingshot_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_left")
                    self.pie_target_hit("rollover_left")
                    self.commands.request_score("asharp_mezzo")

            if topic == "event_slingshot_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_right")
                    self.pie_target_hit("rollover_right")
                    self.commands.request_score("asharp_mezzo")
                    
            if topic == "event_spinner":
                if message:
                    self.add_to_queue("increment_score",1)
                    self.pie_target_hit("spinner")
                    self.commands.request_score("c_mezzo")
            if topic == "event_trough_sensor":
                if message:
                    print("Station.event_handler PINBALL", self.fruit_name, message, message==True)
                    self.end()

        if self.current_phase == phase_names.INVITOR:
            if topic == "event_button_trueque":
                if message == True:
                    self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, True)

                # todo: all of the following in top thread
                """
                if not self.trade_initiated: #only run this once
                    self.trade_initiated = True
                    self.commands.cmd_lefttube_launch()
                    if self.trading_partner.get_trade_initiated():
                        # if trading parter pushed trueque first
                        #trading
                        self.add_to_queue("stop", True)
                        self.trading_partner.add_to_queue("stop", True)
                        self.set_phase(phase_names.TRADE)
                        self.trading_partner.set_phase(phase_names.TRADE)
                    else:
                        # if this player pushed trueque first
                        #waiting
                        # todo: animation to confirm button push
                        #   draw sparkly path between carousels
                        self.trading_partner.add_to_queue("other_pushed", True)
                        self.add_to_queue("local_pushed", True)
                """

        if self.current_phase == phase_names.INVITEE:

            if topic == "event_pop_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("gsharp_mezzo")
                    self.pie_target_hit("pop_left")
            if topic == "event_pop_middle":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("g_mezzo")
                    self.pie_target_hit("pop_middle")
            if topic == "event_pop_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.commands.request_score("f_mezzo")
                    self.pie_target_hit("pop_right")
            if topic == "event_roll_inner_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_inner_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_slingshot_left":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_left")
                    self.pie_target_hit("rollover_left")
                    self.commands.request_score("asharp_mezzo")

            if topic == "event_slingshot_right":
                if message:
                    self.add_to_queue("increment_score",3)
                    self.pie_target_hit("sling_right")
                    self.pie_target_hit("rollover_right")
                    self.commands.request_score("asharp_mezzo")
                    
            if topic == "event_spinner":
                if message:
                    self.add_to_queue("increment_score",1)
                    self.pie_target_hit("spinner")
                    self.commands.request_score("c_mezzo")
            if topic == "event_trough_sensor":
                print("Station.event_handler INVITEE", self.fruit_name, message, message==True)
                if message:
                    self.commands.request_button_light_active("izquierda",False)
                    self.commands.request_button_light_active("trueque",True)
                    self.commands.request_button_light_active("comienza",False)
                    self.commands.request_button_light_active("dinero",False)
                    self.commands.request_button_light_active("derecha",False)
            if topic == "event_button_trueque":
                if message == True:
                    self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, True)

        if self.current_phase == phase_names.TRADE:
            #todo?
            pass

        if self.current_phase == phase_names.FAIL:
            #todo?
            pass

    def end(self):

        if self.current_phase == phase_names.NOPLAYER:
            #todo?
            pass

        if self.current_phase == phase_names.COMIENZA:
            print("Station.end COMIENZA", self.fruit_name,)
            # if there is a fruit to spend
            self.commands.cmd_kicker_launch() 
            self.set_phase(phase_names.PINBALL)
            return

        if self.current_phase == phase_names.PINBALL:
            print("Station.end PINBALL", self.fruit_name,)
            print("----------------------------------------> 1", self.fruit_name)
            self.set_phase(self.parent_ref.get_trade_option(self.fruit_name))
            return

        if self.current_phase == phase_names.INVITOR:
            pass
            #todo: go to phase_names.TRADE or phase_names.FAIL
            # self.set_phase(phase_names.PINBALL)
            return

        if self.current_phase == phase_names.INVITEE:
            pass
            #todo: go to phase_names.TRADE or phase_names.FAIL
            # self.set_phase(phase_names.PINBALL)
            return

        if self.current_phase == phase_names.TRADE:
            print("----------------------------------------> 2", self.fruit_name)
            self.add_to_queue("set_phase", phase_names.COMIENZA)
            return

        if self.current_phase == phase_names.FAIL:
            print("----------------------------------------> 3", self.fruit_name)
            self.add_to_queue("set_phase", phase_names.COMIENZA)
            return


    def set_phase(self, phase_name):
        print("Station.set_phase", self.fruit_name, self.current_phase, phase_name)
        if self.current_phase != phase_name:
            #self.end()
            self.current_phase = phase_name
            self.setup()


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))


    def run(self):
        while True:
            topic,message = self.queue.get()
            #print("Station run", self.fruit_name, topic,message)
            if topic == "set_phase":
                print("----------------------------------------> 4",message)
                self.set_phase(message)
            if topic == "animation_fill_carousel":
                self.animation_transactions.add_to_queue("animation_fill_carousel", self.carousel_fruit_order)
            if topic == "cmd_kicker_launch":
                self.commands.cmd_kicker_launch()
            if topic == "increment_score":
                if isinstance(message, int):
                    self.increment_score(int(message))
                else:
                    self.increment_score()
            if topic == "decrement_score":
                if isinstance(message, int):
                    self.decrement_score(message)
                else:
                    self.decrement_score()

            self.event_handler(topic,message)


class Trade_Fail_Timer(threading.Thread):
    def __init__(self, parent_ref_add_to_queue):
        threading.Thread.__init__(self)
        self.parent_ref_add_to_queue = parent_ref_add_to_queue
        self.timer = -1
        self.timer_limit = 15
        self.queue = queue.Queue()
        self.start()


    def add_to_queue(self, action):
        self.queue.put(action)


    def run(self):
        while True:
            print("Trade_Fail_Timer", self.timer)
            try:
                action = self.queue.get(timeout=1)
                if action == "begin":
                    self.timer = 0
                if action == "end":
                    self.timer = -1
            except queue.Empty:
                if self.timer > -1:
                    self.timer += 1
                    if self.timer >= self.timer_limit:
                        self.timer = -1
                        self.parent_ref_add_to_queue("handle_station_phase_change", "", phase_names.FAIL, False)


class Mode_Timer(threading.Thread):
    def __init__(self, set_current_mode):
        threading.Thread.__init__(self)
        self.set_current_mode = set_current_mode
        self.timer = -1
        self.timer_limit = 120
        self.queue = queue.Queue()
        self.start()


    def add_to_queue(self, action):
        self.queue.put(action)


    def run(self):
        while True:
            try:
                action = self.queue.get(timeout=1)
                if action == "begin":
                    self.timer = 0
                if action == "end":
                    self.timer = -1
            except queue.Empty:
                if self.timer > -1:
                    self.timer += 1
                    #if self.timer %10 == 0:
                    #    print("Mode_Timer run self.timer=",self.timer)
                    if self.timer >= self.timer_limit:
                        self.timer = -1
                        self.set_current_mode(settings.Game_Modes.RESET)
                        #self.set_current_mode(settings.Game_Modes.MONEY_MODE_INTRO)


class Matrix_Animations(threading.Thread):
    """
    todo: change animation methods to generators to make them easy to interrupt 
    """
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.hosts = hosts
        self.queue = queue.Queue()
        self.animation_frame_period = 0.25
        class station_to_host_coco():
            request_eject_ball = self.hosts.hostnames['carousel1'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carousel1'].cmd_carousel_lights
            cmd_lefttube_launch = self.hosts.hostnames['pinball1game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball1game'].cmd_playfield_lights
            cmd_righttube_launch = self.hosts.hostnames['pinball1game'].cmd_righttube_launch
            request_button_light_active = self.hosts.hostnames['pinball1game'].request_button_light_active
            request_phrase = self.hosts.hostnames['pinball1display'].request_phrase
            request_score = self.hosts.hostnames['pinball1display'].request_score

        class station_to_host_naranja:
            request_eject_ball = self.hosts.hostnames['carousel2'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carousel2'].cmd_carousel_lights
            cmd_lefttube_launch = self.hosts.hostnames['pinball2game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball2game'].cmd_playfield_lights
            cmd_righttube_launch = self.hosts.hostnames['pinball2game'].cmd_righttube_launch
            request_button_light_active = self.hosts.hostnames['pinball2game'].request_button_light_active
            request_phrase = self.hosts.hostnames['pinball2display'].request_phrase
            request_score = self.hosts.hostnames['pinball2display'].request_score

        class station_to_host_mango:
            request_eject_ball = self.hosts.hostnames['carousel3'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carousel3'].cmd_carousel_lights
            cmd_lefttube_launch = self.hosts.hostnames['pinball3game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball3game'].cmd_playfield_lights
            cmd_righttube_launch = self.hosts.hostnames['pinball3game'].cmd_righttube_launch
            request_button_light_active = self.hosts.hostnames['pinball3game'].request_button_light_active
            request_phrase = self.hosts.hostnames['pinball3display'].request_phrase
            request_score = self.hosts.hostnames['pinball3display'].request_score

        class station_to_host_sandia:
            request_eject_ball = self.hosts.hostnames['carousel4'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carousel4'].cmd_carousel_lights
            cmd_lefttube_launch = self.hosts.hostnames['pinball4game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball4game'].cmd_playfield_lights
            cmd_righttube_launch = self.hosts.hostnames['pinball4game'].cmd_righttube_launch
            request_button_light_active = self.hosts.hostnames['pinball4game'].request_button_light_active
            request_phrase = self.hosts.hostnames['pinball4display'].request_phrase
            request_score = self.hosts.hostnames['pinball4display'].request_score

        class station_to_host_pina:
            request_eject_ball = self.hosts.hostnames['carousel5'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carousel5'].cmd_carousel_lights
            cmd_lefttube_launch = self.hosts.hostnames['pinball5game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball5game'].cmd_playfield_lights
            cmd_righttube_launch = self.hosts.hostnames['pinball5game'].cmd_righttube_launch
            request_button_light_active = self.hosts.hostnames['pinball5game'].request_button_light_active
            request_phrase = self.hosts.hostnames['pinball5display'].request_phrase
            request_score = self.hosts.hostnames['pinball5display'].request_score

        class station_to_host_center:
            request_eject_ball = self.hosts.hostnames['carouselcenter'].request_eject_ball
            cmd_carousel_lights = self.hosts.hostnames['carouselcenter'].cmd_carousel_lights

        self.carousels = {
            "coco":station_to_host_coco,
            "naranja":station_to_host_naranja,
            "mango":station_to_host_mango,
            "sandia":station_to_host_sandia,
            "pina":station_to_host_pina,
            "center":station_to_host_center,
        }

        self.calculated_paths = {
            "coco":{
                "naranja":[# 13
                    ["coco",18,17,"coco"],
                    ["coco",19,16,"coco"],
                    ["center",15,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",8,11,"mango"],
                    ["naranja",12,15,"naranja"],
                    ["naranja",13,15,"naranja"],
                    ["naranja",14,15,"naranja"],
                    ["naranja",17,16,"coco"],
                    ["naranja",18,19,"coco"],
                ],
                "mango":[# 17
                    ["coco",18,17,"coco"],
                    ["coco",19,16,"coco"],
                    ["center",15,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",0,3,"sandia"],
                    ["mango",8,11,"mango"],
                    ["mango",9,11,"mango"],
                    ["mango",10,11,"mango"],
                    ["mango",13,12,"naranja"],
                    ["mango",14,15,"naranja"],
                    ["mango",17,16,"coco"],
                    ["mango",18,19,"coco"],
                ],
                "sandia":[ # 17
                    ["coco",17,18,"coco"],
                    ["coco",16,19,"coco"],
                    ["center",12,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",23,20,"pina"],
                    ["sandia",3,0,"sandia"],
                    ["sandia",2,0,"sandia"],
                    ["sandia",1,0,"sandia"],
                    ["sandia",22,23,"pina"],
                    ["sandia",21,20,"pina"],
                    ["sandia",18,19,"coco"],
                    ["sandia",17,16,"coco"],
                ],
                "pina":[# 13
                    ["coco",17,18,"coco"],
                    ["coco",16,19,"coco"],
                    ["center",12,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",19,16,"coco"],
                    ["pina",23,20,"pina"],
                    ["pina",22,20,"pina"],
                    ["pina",21,20,"pina"],
                    ["pina",18,19,"coco"],
                    ["pina",17,16,"coco"],
                ],
            },
            "naranja":{
                "coco":[# 13
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",8,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",15,12,"naranja"],
                    ["coco",19,16,"coco"],
                    ["coco",18,16,"coco"],
                    ["coco",17,16,"coco"],
                    ["coco",14,15,"naranja"],
                    ["coco",13,12,"naranja"],
                ],
                "mango":[ # 13
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",11,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",0,3,"sandia"],
                    ["mango",8,11,"mango"],
                    ["mango",9,11,"mango"],
                    ["mango",10,11,"mango"],
                    ["mango",13,12,"naranja"],
                    ["mango",14,15,"naranja"],
                ],
                "sandia":[ # 17
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",11,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",20,23,"pina"],
                    ["sandia",0,3,"sandia"],
                    ["sandia",1,3,"sandia"],
                    ["sandia",2,3,"sandia"],
                    ["sandia",9,8,"mango"],
                    ["sandia",10,11,"mango"],
                    ["sandia",13,12,"naranja"],
                    ["sandia",14,15,"naranja"],
                ],
                "pina":[ # 17
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",8,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",19,16,"coco"],
                    ["pina",23,20,"pina"],
                    ["pina",22,20,"pina"],
                    ["pina",21,20,"pina"],
                    ["pina",18,19,"coco"],
                    ["pina",17,16,"coco"],
                    ["pina",14,15,"naranja"],
                    ["pina",13,12,"naranja"],
                ],
            },
            "mango":{
                "coco":[ # 17
                    ["mango",9,10,"mango"],
                    ["mango",8,11,"mango"],
                    ["center",0,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",15,12,"naranja"],
                    ["coco",19,16,"coco"],
                    ["coco",18,16,"coco"],
                    ["coco",17,16,"coco"],
                    ["coco",14,15,"naranja"],
                    ["coco",13,12,"naranja"],
                    ["coco",10,11,"mango"],
                    ["coco",9,8,"mango"],
                ],
                "naranja":[# 13
                    ["mango",9,10,"mango"],
                    ["mango",8,11,"mango"],
                    ["center",0,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",11,8,"mango"],
                    ["naranja",15,12,"naranja"],
                    ["naranja",14,12,"naranja"],
                    ["naranja",13,12,"naranja"],
                    ["naranja",10,11,"mango"],
                    ["naranja",9,8,"mango"],
                ],
                "sandia":[ # 13
                    ["mango",10,9,"mango"],
                    ["mango",11,8,"mango"],
                    ["center",3,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",20,23,"pina"],
                    ["sandia",0,3,"sandia"],
                    ["sandia",1,3,"sandia"],
                    ["sandia",2,3,"sandia"],
                    ["sandia",9,8,"mango"],
                    ["sandia",10,11,"mango"],
                ],
                "pina":[ # 17
                    ["mango",9,10,"mango"],
                    ["mango",8,11,"mango"],
                    ["center",3,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",16,19,"coco"],
                    ["pina",20,23,"pina"],
                    ["pina",21,23,"pina"],
                    ["pina",22,23,"pina"],
                    ["pina",1,0,"sandia"],
                    ["pina",2,3,"sandia"],
                    ["pina",9,8,"mango"],
                    ["pina",10,11,"mango"],
                ],
            },
            "sandia":{
                "coco":[ # 17
                    ["sandia",2,1,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["center",23,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",12,15,"naranja"],
                    ["coco",16,19,"coco"],
                    ["coco",17,19,"coco"],
                    ["coco",18,19,"coco"],
                    ["coco",21,20,"pina"],
                    ["coco",22,23,"pina"],
                    ["coco",1,0,"sandia"],
                    ["coco",2,3,"sandia"],
                ],
                "naranja":[ # 17
                    ["sandia",2,1,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["center",20,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",11,8,"mango"],
                    ["naranja",15,12,"naranja"],
                    ["naranja",14,12,"naranja"],
                    ["naranja",13,12,"naranja"],
                    ["naranja",10,11,"mango"],
                    ["naranja",9,8,"mango"],
                    ["naranja",2,3,"sandia"],
                    ["naranja",1,0,"sandia"],
                ],
                "mango":[ # 13
                    ["sandia",2,1,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["center",20,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",3,0,"sandia"],
                    ["mango",11,8,"mango"],
                    ["mango",10,8,"mango"],
                    ["mango",9,8,"mango"],
                    ["mango",2,3,"sandia"],
                    ["mango",1,0,"sandia"],
                ],
                "pina":[ # 13
                    ["sandia",2,1,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["center",23,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",16,19,"coco"],
                    ["pina",20,23,"pina"],
                    ["pina",21,23,"pina"],
                    ["pina",22,23,"pina"],
                    ["pina",1,0,"sandia"],
                    ["pina",2,3,"sandia"],
                ],
            },
            "pina":{
                "coco":[ # 13
                    ["pina",22,21,"pina"],
                    ["pina",23,20,"pina"],
                    ["center",19,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",12,15,"naranja"],
                    ["coco",16,19,"coco"],
                    ["coco",17,19,"coco"],
                    ["coco",18,19,"coco"],
                    ["coco",21,20,"pina"],
                    ["coco",22,23,"pina"],
                ],
                "naranja":[  # 17
                    ["pina",22,21,"pina"],
                    ["pina",23,20,"pina"],
                    ["center",19,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",8,11,"mango"],
                    ["naranja",12,15,"naranja"],
                    ["naranja",13,15,"naranja"],
                    ["naranja",14,15,"naranja"],
                    ["naranja",17,16,"coco"],
                    ["naranja",18,19,"coco"],
                    ["naranja",21,20,"pina"],
                    ["naranja",22,23,"pina"],
                ],
                "mango":[ # 17
                    ["pina",21,22,"pina"],
                    ["pina",20,23,"pina"],
                    ["center",16,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",3,0,"sandia"],
                    ["mango",11,8,"mango"],
                    ["mango",10,8,"mango"],
                    ["mango",9,8,"mango"],
                    ["mango",2,3,"sandia"],
                    ["mango",1,0,"sandia"],
                    ["mango",22,23,"pina"],
                    ["mango",21,20,"pina"],
                ],
                "sandia":[ # 13
                    ["pina",21,22,"pina"],
                    ["pina",20,23,"pina"],
                    ["center",16,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",23,20,"pina"],
                    ["sandia",3,0,"sandia"],
                    ["sandia",2,0,"sandia"],
                    ["sandia",1,0,"sandia"],
                    ["sandia",22,23,"pina"],
                    ["sandia",21,20,"pina"],
                ],
            },
        }

        self.fail_theme_chimes_18 = [
            "c_mezzo",
            "asharp_mezzo",
            "c_mezzo",
            "c_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "asharp_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "gsharp_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "f_mezzo",
        ]

        self.fail_theme_chimes_14 = [
            "c_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "asharp_mezzo",
            "asharp_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "gsharp_mezzo",
            "g_mezzo",
            "f_mezzo",
        ]

        self.start()



    def draw_pong_fade(self, path, ordinal, levels=["high","med","low","off"]):
        # todo, clear tail when end is reached
        if ordinal+1 > -1 and ordinal+1 < len(path):
            self.set_pair_to_level(
                path[ordinal+1][0], 
                path[ordinal+1][1], 
                path[ordinal+1][2], 
                levels[0]
            )
        if ordinal > -1 and ordinal < len(path):
            self.set_pair_to_level(
                path[ordinal][0], 
                path[ordinal][1], 
                path[ordinal][2], 
                levels[0]
            )
        if ordinal-1 > -1 and ordinal-1 < len(path):
            self.set_pair_to_level(
                path[ordinal-1][0], 
                path[ordinal-1][1], 
                path[ordinal-1][2], 
                levels[1]
            )
        if ordinal-2 > -1 and ordinal-2 < len(path):
            self.set_pair_to_level(
                path[ordinal-2][0], 
                path[ordinal-2][1], 
                path[ordinal-2][2], 
                levels[2]
            )
        if ordinal-2 > -1 and ordinal-2 < len(path):
            self.set_pair_to_level(
                path[ordinal-2][0], 
                path[ordinal-2][1], 
                path[ordinal-2][2], 
                levels[3]
            )


    def set_pair_to_level(self, carousel_name, led_1, led_2, level):
        led_1_str = "channel_%s" % led_1
        led_2_str = "channel_%s" % led_2
        #print("set_pair_to_level",led_1_str,led_2_str)
        self.carousels[carousel_name].cmd_carousel_lights(str(led_1_str),level)
        self.carousels[carousel_name].cmd_carousel_lights(str(led_2_str),level)


    def trade_invited_setup(self, invitor, invitee):
        print("trade_invited_setup",invitor, invitee)
        # alternating pong trail animations
        # path_a = self.calculated_paths[invitor][invitee]
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[invitor].cmd_carousel_lights("all","off")
        self.carousels[invitee].cmd_carousel_lights("all","off")


    def trade_invited_repeat(self, invitor, invitee):
        print("trade_invited_repeat",invitor, invitee)
        self.carousels[invitor].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("g_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", True)
        self.carousels[invitee].request_button_light_active("trueque", True)
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("gsharp_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", False)
        self.carousels[invitee].request_button_light_active("trueque", False)
        time.sleep(self.animation_frame_period)
        self.carousels[invitee].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitee].request_score("g_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", True)
        self.carousels[invitee].request_button_light_active("trueque", True)
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[invitor].cmd_carousel_lights("all","off")
        self.carousels[invitee].cmd_carousel_lights("all","off")
        self.carousels[invitor].request_button_light_active("trueque", False)
        self.carousels[invitee].request_button_light_active("trueque", False)
        time.sleep(self.animation_frame_period)
        self.carousels[invitee].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitee].request_score("g_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", True)
        self.carousels[invitee].request_button_light_active("trueque", True)
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("gsharp_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", False)
        self.carousels[invitee].request_button_light_active("trueque", False)
        time.sleep(self.animation_frame_period)
        self.carousels[invitor].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("g_mezzo")
        self.carousels[invitor].request_button_light_active("trueque", True)
        self.carousels[invitee].request_button_light_active("trueque", True)
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[invitor].cmd_carousel_lights("all","off")
        self.carousels[invitee].cmd_carousel_lights("all","off")
        self.carousels[invitor].request_button_light_active("trueque", False)
        self.carousels[invitee].request_button_light_active("trueque", False)
        time.sleep(self.animation_frame_period)


    def trade_initiated_setup(self, initiator, initiatee):
        print("trade_initiated_setup",initiator, initiatee)
        #self.carousels[initiator].cmd_lefttube_launch()
        self.carousels[initiator].request_button_light_active("trueque", False)
        self.carousels[initiator].request_score("f_mezzo")
        self.carousels[initiator].request_score("gsharp_mezzo")
        self.carousels[initiator].request_score("c_mezzo")


    def trade_initiated_repeat(self, initiator, initiatee):
        print("trade_initiated_repeat",initiator, initiatee)
        self.carousels[initiator].request_button_light_active("trueque", False)
        self.carousels[initiatee].cmd_carousel_lights("inner_circle","on")
        self.carousels[initiatee].cmd_carousel_lights("outer_circle","on")
        self.carousels[initiatee].request_score("asharp_mezzo")
        time.sleep(self.animation_frame_period)
        self.carousels[initiatee].request_button_light_active("trueque", True)
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[initiatee].request_score("gsharp_mezzo")
        time.sleep(self.animation_frame_period)
        self.carousels[initiatee].request_button_light_active("trueque", False)
        self.carousels[initiator].cmd_carousel_lights("inner_circle","on")
        self.carousels[initiator].cmd_carousel_lights("outer_circle","on")
        self.carousels[initiator].request_score("asharp_mezzo")
        time.sleep(self.animation_frame_period)
        self.carousels[initiatee].request_button_light_active("trueque", True)
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[initiator].cmd_carousel_lights("all","off")
        self.carousels[initiator].cmd_carousel_lights("all","off")
        self.carousels[initiatee].request_button_light_active("trueque", False)
        time.sleep(self.animation_frame_period)


    def trade_succeeded_setup(self, invitor, invitee):
        print("trade_succeeded_setup",invitor, invitee)
        self.carousels[invitor].request_button_light_active("trueque", False)
        self.carousels[invitee].request_button_light_active("trueque", False)
        self.carousels[invitor].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","on")
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("f_mezzo")
        self.carousels[invitor].request_score("gsharp_mezzo")
        self.carousels[invitor].request_score("c_mezzo")
        self.carousels[invitee].request_score("f_mezzo")
        self.carousels[invitee].request_score("gsharp_mezzo")
        self.carousels[invitee].request_score("c_mezzo")
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[invitor].cmd_carousel_lights("all","off")
        self.carousels[invitee].cmd_carousel_lights("all","off")
        time.sleep(self.animation_frame_period)
        self.carousels[invitor].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","on")
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("f_mezzo")
        self.carousels[invitor].request_score("gsharp_mezzo")
        self.carousels[invitor].request_score("c_mezzo")
        self.carousels[invitee].request_score("f_mezzo")
        self.carousels[invitee].request_score("gsharp_mezzo")
        self.carousels[invitee].request_score("c_mezzo")
        time.sleep(self.animation_frame_period)
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[invitor].cmd_carousel_lights("all","off")
        self.carousels[invitee].cmd_carousel_lights("all","off")


    def trade_failed_setup(self, invitor, invitee):
        print("trade_succeeded_setup",invitor, invitee)
        self.carousels[invitor].cmd_carousel_lights("inner_circle","high")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","high")
        self.carousels["center"].cmd_carousel_lights("inner_circle","high")
        self.carousels["center"].cmd_carousel_lights("outer_circle","high")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","high")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","high")
        self.carousels[invitor].request_score("c_mezzo")
        self.carousels[invitee].request_score("c_mezzo")
        time.sleep(self.animation_frame_period)

        self.carousels[invitor].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","on")
        self.carousels["center"].cmd_carousel_lights("inner_circle","on")
        self.carousels["center"].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","on")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","on")
        self.carousels[invitor].request_score("asharp_mezzo")
        self.carousels[invitee].request_score("asharp_mezzo")
        time.sleep(self.animation_frame_period)

        self.carousels[invitor].cmd_carousel_lights("inner_circle","med")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","med")
        self.carousels["center"].cmd_carousel_lights("inner_circle","med")
        self.carousels["center"].cmd_carousel_lights("outer_circle","med")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","med")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","med")
        self.carousels[invitor].request_score("gsharp_mezzo")
        self.carousels[invitee].request_score("gsharp_mezzo")
        time.sleep(self.animation_frame_period)

        self.carousels[invitor].cmd_carousel_lights("inner_circle","low")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","low")
        self.carousels["center"].cmd_carousel_lights("inner_circle","low")
        self.carousels["center"].cmd_carousel_lights("outer_circle","low")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","low")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","low")
        self.carousels[invitor].request_score("g_mezzo")
        self.carousels[invitee].request_score("g_mezzo")
        time.sleep(self.animation_frame_period)

        self.carousels[invitor].cmd_carousel_lights("inner_circle","off")
        self.carousels[invitor].cmd_carousel_lights("outer_circle","off")
        self.carousels["center"].cmd_carousel_lights("inner_circle","off")
        self.carousels["center"].cmd_carousel_lights("outer_circle","off")
        self.carousels[invitee].cmd_carousel_lights("inner_circle","off")
        self.carousels[invitee].cmd_carousel_lights("outer_circle","off")
        self.carousels[invitor].request_score("f_mezzo")
        self.carousels[invitee].request_score("f_mezzo")
        time.sleep(self.animation_frame_period)


    def add_to_queue(self, animation, station_a_name, station_b_name):
        # trade_invited, trade_initiated, trade_succeeded, trade_failed, pause_animations
        self.queue.put((animation, station_a_name, station_b_name))


    def run(self):
        animation = "pause_animations"
        station_a_name = ""
        station_b_name = ""
        while True:
            try:
                #print("Matrix_Animations run 1 animation==",animation, station_a_name, station_b_name)
                animation, station_a_name, station_b_name = self.queue.get(False)
                print("Matrix_Animations run 2 animation==",animation, station_a_name, station_b_name)
                if animation == "trade_invited":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_invited_setup(station_a_name, station_b_name) #invitor, invitee
                    animation = "trade_invited_repeat"

                if animation == "trade_initiated":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_initiated_setup(station_a_name, station_b_name)
                    animation = "trade_initiated_repeat"
                
                if animation == "trade_succeeded":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_succeeded_setup(station_a_name, station_b_name)
                    animation = "pause_animations"
                
                if animation == "trade_failed":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_failed_setup(station_a_name, station_b_name)
                    animation = "pause_animations"
                #if animation == "pause_animations":
                #    animation = "pause_animations"

            except queue.Empty:
                if animation == "trade_invited_repeat":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_invited_repeat(station_a_name, station_b_name) #invitor, invitee
                if animation == "trade_initiated_repeat":
                    #print("Matrix_Animations run animation==",animation)
                    self.trade_initiated_repeat(station_a_name, station_b_name)
                time.sleep(0.1)


class Mode_Barter(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.pinball_hostnames_with_players = [] # updated in begin()
        self.mode_timer = Mode_Timer(self.set_current_mode)
        self.matrix_animations = Matrix_Animations(self.hosts)
        self.trade_fail_timer = Trade_Fail_Timer(self.add_to_queue)
        self.trade_time_threshold = 15
        class station_to_host_coco():
            cmd_all_off = self.hosts.hostnames['pinball1display'].cmd_all_off
            cmd_carousel_all_off = self.hosts.hostnames['carousel1'].cmd_carousel_all_off
            cmd_carousel_lights = self.hosts.hostnames['carousel1'].cmd_carousel_lights
            cmd_kicker_launch = self.hosts.hostnames['pinball1game'].cmd_kicker_launch
            cmd_lefttube_launch = self.hosts.hostnames['pinball1game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball1game'].cmd_playfield_lights
            cmd_pulse_coil = self.hosts.hostnames['pinball1game'].cmd_pulse_coil
            cmd_righttube_launch = self.hosts.hostnames['pinball1game'].cmd_righttube_launch
            disable_gameplay = self.hosts.hostnames['pinball1game'].disable_gameplay
            enable_derecha_coil = self.hosts.hostnames['pinball1game'].enable_derecha_coil
            enable_dinero_coil = self.hosts.hostnames['pinball1game'].enable_dinero_coil
            enable_gameplay = self.hosts.hostnames['pinball1game'].enable_gameplay
            enable_izquierda_coil = self.hosts.hostnames['pinball1game'].enable_izquierda_coil
            enable_kicker_coil = self.hosts.hostnames['pinball1game'].enable_kicker_coil
            enable_trueque_coil = self.hosts.hostnames['pinball1game'].enable_trueque_coil
            get_barter_points = self.hosts.hostnames['pinball1game'].get_barter_points
            get_money_points = self.hosts.hostnames['pinball1game'].get_money_points
            money_mode_score = self.hosts.hostnames['pinball1game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball1game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball1display'].request_number
            request_phrase = self.hosts.hostnames['pinball1display'].request_phrase
            request_score = self.hosts.hostnames['pinball1display'].request_score
            set_barter_points = self.hosts.hostnames['pinball1game'].set_barter_points
            set_money_points = self.hosts.hostnames['pinball1game'].set_money_points

        class station_to_host_naranja:
            cmd_all_off = self.hosts.hostnames['pinball2display'].cmd_all_off
            cmd_carousel_all_off = self.hosts.hostnames['carousel2'].cmd_carousel_all_off
            cmd_carousel_lights = self.hosts.hostnames['carousel2'].cmd_carousel_lights
            cmd_kicker_launch = self.hosts.hostnames['pinball2game'].cmd_kicker_launch
            cmd_lefttube_launch = self.hosts.hostnames['pinball2game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball2game'].cmd_playfield_lights
            cmd_pulse_coil = self.hosts.hostnames['pinball2game'].cmd_pulse_coil
            cmd_righttube_launch = self.hosts.hostnames['pinball2game'].cmd_righttube_launch
            disable_gameplay = self.hosts.hostnames['pinball2game'].disable_gameplay
            enable_derecha_coil = self.hosts.hostnames['pinball2game'].enable_derecha_coil
            enable_dinero_coil = self.hosts.hostnames['pinball2game'].enable_dinero_coil
            enable_gameplay = self.hosts.hostnames['pinball2game'].enable_gameplay
            enable_izquierda_coil = self.hosts.hostnames['pinball2game'].enable_izquierda_coil
            enable_kicker_coil = self.hosts.hostnames['pinball2game'].enable_kicker_coil
            enable_trueque_coil = self.hosts.hostnames['pinball2game'].enable_trueque_coil
            get_barter_points = self.hosts.hostnames['pinball2game'].get_barter_points
            get_money_points = self.hosts.hostnames['pinball2game'].get_money_points
            money_mode_score = self.hosts.hostnames['pinball2game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball2game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball2display'].request_number
            request_phrase = self.hosts.hostnames['pinball2display'].request_phrase
            request_score = self.hosts.hostnames['pinball2display'].request_score
            set_barter_points = self.hosts.hostnames['pinball2game'].set_barter_points
            set_money_points = self.hosts.hostnames['pinball2game'].set_money_points

        class station_to_host_mango:
            cmd_all_off = self.hosts.hostnames['pinball3display'].cmd_all_off
            cmd_carousel_all_off = self.hosts.hostnames['carousel3'].cmd_carousel_all_off
            cmd_carousel_lights = self.hosts.hostnames['carousel3'].cmd_carousel_lights
            cmd_kicker_launch = self.hosts.hostnames['pinball3game'].cmd_kicker_launch
            cmd_lefttube_launch = self.hosts.hostnames['pinball3game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball3game'].cmd_playfield_lights
            cmd_pulse_coil = self.hosts.hostnames['pinball3game'].cmd_pulse_coil
            cmd_righttube_launch = self.hosts.hostnames['pinball3game'].cmd_righttube_launch
            disable_gameplay = self.hosts.hostnames['pinball3game'].disable_gameplay
            enable_derecha_coil = self.hosts.hostnames['pinball3game'].enable_derecha_coil
            enable_dinero_coil = self.hosts.hostnames['pinball3game'].enable_dinero_coil
            enable_gameplay = self.hosts.hostnames['pinball3game'].enable_gameplay
            enable_izquierda_coil = self.hosts.hostnames['pinball3game'].enable_izquierda_coil
            enable_kicker_coil = self.hosts.hostnames['pinball3game'].enable_kicker_coil
            enable_trueque_coil = self.hosts.hostnames['pinball3game'].enable_trueque_coil
            get_barter_points = self.hosts.hostnames['pinball3game'].get_barter_points
            get_money_points = self.hosts.hostnames['pinball3game'].get_money_points
            money_mode_score = self.hosts.hostnames['pinball3game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball3game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball3display'].request_number
            request_phrase = self.hosts.hostnames['pinball3display'].request_phrase
            request_score = self.hosts.hostnames['pinball3display'].request_score
            set_barter_points = self.hosts.hostnames['pinball3game'].set_barter_points
            set_money_points = self.hosts.hostnames['pinball3game'].set_money_points

        class station_to_host_sandia:
            cmd_all_off = self.hosts.hostnames['pinball4display'].cmd_all_off
            cmd_carousel_all_off = self.hosts.hostnames['carousel4'].cmd_carousel_all_off
            cmd_carousel_lights = self.hosts.hostnames['carousel4'].cmd_carousel_lights
            cmd_kicker_launch = self.hosts.hostnames['pinball4game'].cmd_kicker_launch
            cmd_lefttube_launch = self.hosts.hostnames['pinball4game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball4game'].cmd_playfield_lights
            cmd_pulse_coil = self.hosts.hostnames['pinball4game'].cmd_pulse_coil
            cmd_righttube_launch = self.hosts.hostnames['pinball4game'].cmd_righttube_launch
            disable_gameplay = self.hosts.hostnames['pinball4game'].disable_gameplay
            enable_derecha_coil = self.hosts.hostnames['pinball4game'].enable_derecha_coil
            enable_dinero_coil = self.hosts.hostnames['pinball4game'].enable_dinero_coil
            enable_gameplay = self.hosts.hostnames['pinball4game'].enable_gameplay
            enable_izquierda_coil = self.hosts.hostnames['pinball4game'].enable_izquierda_coil
            enable_kicker_coil = self.hosts.hostnames['pinball4game'].enable_kicker_coil
            enable_trueque_coil = self.hosts.hostnames['pinball4game'].enable_trueque_coil
            get_barter_points = self.hosts.hostnames['pinball4game'].get_barter_points
            get_money_points = self.hosts.hostnames['pinball4game'].get_money_points
            money_mode_score = self.hosts.hostnames['pinball4game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball4game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball4display'].request_number
            request_phrase = self.hosts.hostnames['pinball4display'].request_phrase
            request_score = self.hosts.hostnames['pinball4display'].request_score
            set_barter_points = self.hosts.hostnames['pinball4game'].set_barter_points
            set_money_points = self.hosts.hostnames['pinball4game'].set_money_points

        class station_to_host_pina:
            cmd_all_off = self.hosts.hostnames['pinball5display'].cmd_all_off
            cmd_carousel_all_off = self.hosts.hostnames['carousel5'].cmd_carousel_all_off
            cmd_carousel_lights = self.hosts.hostnames['carousel5'].cmd_carousel_lights
            cmd_kicker_launch = self.hosts.hostnames['pinball5game'].cmd_kicker_launch
            cmd_lefttube_launch = self.hosts.hostnames['pinball5game'].cmd_lefttube_launch
            cmd_playfield_lights = self.hosts.hostnames['pinball5game'].cmd_playfield_lights
            cmd_pulse_coil = self.hosts.hostnames['pinball5game'].cmd_pulse_coil
            cmd_righttube_launch = self.hosts.hostnames['pinball5game'].cmd_righttube_launch
            disable_gameplay = self.hosts.hostnames['pinball5game'].disable_gameplay
            enable_derecha_coil = self.hosts.hostnames['pinball5game'].enable_derecha_coil
            enable_dinero_coil = self.hosts.hostnames['pinball5game'].enable_dinero_coil
            enable_gameplay = self.hosts.hostnames['pinball5game'].enable_gameplay
            enable_izquierda_coil = self.hosts.hostnames['pinball5game'].enable_izquierda_coil
            enable_kicker_coil = self.hosts.hostnames['pinball5game'].enable_kicker_coil
            enable_trueque_coil = self.hosts.hostnames['pinball5game'].enable_trueque_coil
            get_barter_points = self.hosts.hostnames['pinball5game'].get_barter_points
            get_money_points = self.hosts.hostnames['pinball5game'].get_money_points
            money_mode_score = self.hosts.hostnames['pinball5game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball5game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball5display'].request_number
            request_phrase = self.hosts.hostnames['pinball5display'].request_phrase
            request_score = self.hosts.hostnames['pinball5display'].request_score
            set_barter_points = self.hosts.hostnames['pinball5game'].set_barter_points
            set_money_points = self.hosts.hostnames['pinball5game'].set_money_points

        self.stations = {
            "coco":Station("coco",station_to_host_coco, self),
            "naranja":Station("naranja",station_to_host_naranja, self),
            "mango":Station("mango",station_to_host_mango, self),
            "sandia":Station("sandia",station_to_host_sandia, self),
            "pina":Station("pina",station_to_host_pina, self),
        }

        self.PINBALL_HOSTNAME_TO_STATION = {
            "pinball1game":self.stations["coco"],
            "pinball2game":self.stations["naranja"],
            "pinball3game":self.stations["mango"],
            "pinball4game":self.stations["sandia"],
            "pinball5game":self.stations["pina"],
        }
        self.FRUIT_NAME_TO_PINBALL_HOSTNAME = {
            "coco":"pinball1game",
            "naranja":"pinball2game",
            "mango":"pinball3game",
            "sandia":"pinball4game",
            "pina":"pinball5game",
        }
        self.invitor_invitee = ["",""]
        self.initiator_initiatee = ["",""]
        self.start()
    # todo: reset self.invitor_invitee after trade or fail

    def get_trade_option(self, fruit_name):
        print("get_trade_option 1", fruit_name)
        self.lock.acquire()
        # if no other trade is happening
        if self.invitor_invitee != ["",""]:
            #print("Mode_Barter get_trade_option() 2")
            self.lock.release()
            return phase_names.COMIENZA

        print("get_trade_option 2", fruit_name)
        # return if too soon 
        if self.stations[fruit_name].last_trade_time > time.time() - self.trade_time_threshold:
            self.lock.release()
            return phase_names.COMIENZA

        print("get_trade_option 3", fruit_name)
        least_recent_station = False
        for pinball_hostname_with_player in self.pinball_hostnames_with_players:
            #skip this fruit name
            if pinball_hostname_with_player == self.FRUIT_NAME_TO_PINBALL_HOSTNAME[fruit_name]:
                continue
            #set first value
            if least_recent_station == False:
                least_recent_station = self.PINBALL_HOSTNAME_TO_STATION[pinball_hostname_with_player]
            else: 
                if least_recent_station.last_trade_time > self.PINBALL_HOSTNAME_TO_STATION[pinball_hostname_with_player].last_trade_time:
                    least_recent_station = self.PINBALL_HOSTNAME_TO_STATION[pinball_hostname_with_player]
        # return if too soon for least_recent_station

        print("get_trade_option 4", fruit_name,least_recent_station)
        if least_recent_station.last_trade_time  > time.time() - self.trade_time_threshold:
            self.lock.release()
            return phase_names.COMIENZA
        # start trade
        print("get_trade_option 5", fruit_name)
        least_recent_station.last_trade_time = time.time()
        self.stations[fruit_name].last_trade_time = time.time()
        invitee_fruit_name = least_recent_station.fruit_name
        self.invitor_invitee = [fruit_name,invitee_fruit_name]
        self.stations[invitee_fruit_name].add_to_queue("set_phase", phase_names.INVITEE)
        self.lock.release()
        print("get_trade_option 6", fruit_name)
        return phase_names.INVITOR


    def handle_station_phase_change(self, station_fruit_name, phase_name, initiator_hint):
        if phase_name == phase_names.NOPLAYER:
            pass
        if phase_name == phase_names.COMIENZA:
            if station_fruit_name in self.invitor_invitee:
                self.matrix_animations.add_to_queue("pause_animations", self.invitor_invitee[0], self.invitor_invitee[1])
                self.invitor_invitee = ["",""]

        if phase_name == phase_names.PINBALL:
            if station_fruit_name in self.invitor_invitee:
                self.matrix_animations.add_to_queue("pause_animations", self.invitor_invitee[0], self.invitor_invitee[1])
                self.invitor_invitee = ["",""]


        if phase_name == phase_names.INVITOR:
            print("Mode_Barter.handle_station_phase_change 0",phase_name, self.invitor_invitee, self.initiator_initiatee)
            # this is called first by the setup() of a station's INVITOR phase
            # this is called second by the pressing of Trueque
            # if not called by button

            # is this the a new trade session?
            if self.invitor_invitee[0] == "":
                self.invitor_invitee[0] = station_fruit_name
            # is an invitee already selected?
            # ^ is there ever a case when only one is selected?
            # they are assigned together in get_trade_option
            print("Mode_Barter.handle_station_phase_change 1",phase_name, self.invitor_invitee, self.initiator_initiatee)

            # avoiding a possible race condition in the threads between get_trade_option and this function
            if self.invitor_invitee[1] != "":
                # if trueque button has been pressed
                if not initiator_hint:
                    self.trade_fail_timer.add_to_queue("begin")

                print("Mode_Barter.handle_station_phase_change 2",phase_name, self.invitor_invitee, self.initiator_initiatee)
                if initiator_hint:
                    # trueque button has been hit
                    # if this is the first trueque button pushed
                    if self.initiator_initiatee[0] == "":
                        # INVITOR is the first to hit the trueque button
                        self.initiator_initiatee[0] = station_fruit_name
                        self.stations[station_fruit_name].commands.cmd_lefttube_launch()
                        self.matrix_animations.add_to_queue("trade_initiated", self.invitor_invitee[0],self.invitor_invitee[1])
                    else:
                        if self.initiator_initiatee[0] != station_fruit_name:
                            # INVITOR is the second to hit the trueque button
                            self.initiator_initiatee[1] = station_fruit_name
                            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.TRADE)
                            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.TRADE)
                else:
                    # trueque button has not been hit by invitor
                    self.matrix_animations.add_to_queue("trade_invited", self.invitor_invitee[0],self.invitor_invitee[1])
            print("Mode_Barter.handle_station_phase_change 4",phase_name, self.invitor_invitee, self.initiator_initiatee)

        if phase_name == phase_names.INVITEE:
            if self.invitor_invitee[1] == "":
                self.invitor_invitee[1] = station_fruit_name
            if self.invitor_invitee[0] != "":
                if initiator_hint:
                    # trueque button has been hit
                    # is INVITEE the first or second to hit the trueque button?
                    if self.initiator_initiatee[0] == "":
                        # INVITEE is the first to hit the trueque button
                        self.initiator_initiatee[0] = station_fruit_name
                        self.stations[station_fruit_name].commands.cmd_lefttube_launch()
                        self.matrix_animations.add_to_queue("trade_initiated", self.invitor_invitee[0],self.invitor_invitee[1])
                    else:
                        if self.initiator_initiatee[0] != station_fruit_name:
                            # INVITOR is the second to hit the trueque button
                            self.initiator_initiatee[1] = station_fruit_name
                            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.TRADE)
                            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.TRADE)

            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)

        if phase_name == phase_names.TRADE:
            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)
            self.trade_fail_timer.add_to_queue("end")
            if self.initiator_initiatee[0] == station_fruit_name:
                self.matrix_animations.add_to_queue("trade_succeeded", str(self.invitor_invitee[0]),str(self.invitor_invitee[1]))
                self.matrix_animations.add_to_queue("pause_animations", str(self.invitor_invitee[1]),str(self.invitor_invitee[0]))
                print("----------------------------------------> 5",self.invitor_invitee[0])
                self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.COMIENZA)
                self.stations[self.invitor_invitee[0]].add_to_queue("increment_score", 25)

                print("----------------------------------------> 6", self.invitor_invitee[0])
                self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.COMIENZA)
                self.stations[self.invitor_invitee[1]].add_to_queue("increment_score", 25)
                self.invitor_invitee = ["",""]
                self.initiator_initiatee = ["",""]

        if phase_name == phase_names.FAIL:
            # this is called only once, by the timer
            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)
            # todoL switch to initiator_initiatee below, after confirming that they get assigned correctly
            self.trade_fail_timer.add_to_queue("end")
            self.matrix_animations.add_to_queue("trade_failed", str(self.invitor_invitee[0]),str(self.invitor_invitee[1]))
            self.matrix_animations.add_to_queue("pause_animations", str(self.invitor_invitee[1]),str(self.invitor_invitee[0]))

            print("----------------------------------------> 7", self.invitor_invitee[0])
            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.COMIENZA)
            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.COMIENZA)
            self.invitor_invitee = ["",""]
            self.initiator_initiatee = ["",""]


    """
    def get_trade_option(self, fruit_name):
        # todo: how does this vary with different numbers of players?
        # todo: self.invitor_invitee is not threadsafe between get_trade_option and handle_station_phase_change
        # what are the conditions for trading?
        self.lock.acquire()
        # if no other trade is happening
        if self.invitor_invitee != ["",""]:
            self.lock.release()
            return phase_names.COMIENZA
        # if station_a has fruit_a to trade
        if not self.stations[fruit_name].carousel_get_fruit_presence(fruit_name):
            self.lock.release()
            return phase_names.COMIENZA
        # if station_a is missing fruit_b
        station_a_missing_fruits = self.stations[fruit_name].carousel_get_fruits_missing(True)
        if len(station_a_missing_fruits) == 0:
            self.lock.release()
            return phase_names.COMIENZA
        potential_trading_partners = []
        # if station_b has fruit_b to trade
        for station_a_missing_fruit in station_a_missing_fruits:
            # todo: thread safety for carousel_data_segments
            # if this fruit corresponds to a game with a player
            if self.FRUIT_NAME_TO_PINBALL_HOSTNAME[station_a_missing_fruit] in self.pinball_hostnames_with_players:
                if self.stations[station_a_missing_fruit].carousel_get_fruit_presence(station_a_missing_fruit):
                    # if station_b is missing fruit_a
                    if not self.stations[station_a_missing_fruit].carousel_get_fruit_presence(fruit_name):
                        potential_trading_partners.append(station_a_missing_fruit)
        if len(potential_trading_partners) == 0:
            self.lock.release()
            return phase_names.COMIENZA
        invitee_fruit_name = random.choice(potential_trading_partners)
        self.invitor_invitee = [fruit_name,invitee_fruit_name]
        self.stations[invitee_fruit_name].add_to_queue("set_phase", phase_names.INVITEE)
        self.lock.release()
        return phase_names.INVITOR

    def handle_station_phase_change(self, station_fruit_name, phase_name, initiator_hint):

        if phase_name == phase_names.NOPLAYER:
            pass
        if phase_name == phase_names.COMIENZA:
            if station_fruit_name in self.invitor_invitee:
                self.matrix_animations.add_to_queue("pause_animations", self.invitor_invitee[0], self.invitor_invitee[1])
                self.invitor_invitee = ["",""]

        if phase_name == phase_names.PINBALL:
            if station_fruit_name in self.invitor_invitee:
                self.matrix_animations.add_to_queue("pause_animations", self.invitor_invitee[0], self.invitor_invitee[1])
                self.invitor_invitee = ["",""]

        if phase_name == phase_names.INVITOR:
            # this is called at the setup() of a station's INVITOR phase
            #print(">>>>>>>> phase_names.INVITOR 0",self.invitor_invitee,self.initiator_initiatee)
            # is this the a new trade session?
            self.trade_fail_timer.add_to_queue("begin")
            if self.invitor_invitee[0] == "":
                self.invitor_invitee[0] = station_fruit_name
            # is an invitee already selected?
            # ^ is there ever a case when only one is selected?
            # they are assigned together in get_trade_option
            if self.invitor_invitee[1] != "":
                # if trueque button has been pressed
                if initiator_hint:
                    #print(">>>>>>>> phase_names.INVITOR 1",self.invitor_invitee,self.initiator_initiatee)
                    # trueque button has been hit
                    # if this is the first trueque button pushed
                    if self.initiator_initiatee[0] == "":
                        #print(">>>>>>>> phase_names.INVITOR 2",self.invitor_invitee,self.initiator_initiatee)
                        # INVITOR is the first to hit the trueque button
                        self.initiator_initiatee[0] = station_fruit_name
                        self.stations[station_fruit_name].commands.cmd_lefttube_launch()
                        self.matrix_animations.add_to_queue("trade_initiated", self.invitor_invitee[0],self.invitor_invitee[1])
                    else:
                        #print(">>>>>>>> phase_names.INVITOR 3",self.invitor_invitee,self.initiator_initiatee)
                        if self.initiator_initiatee[0] != station_fruit_name:
                            #print(">>>>>>>> phase_names.INVITOR 4",self.invitor_invitee,self.initiator_initiatee)
                            # INVITOR is the second to hit the trueque button
                            self.initiator_initiatee[1] = station_fruit_name
                            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.TRADE)
                            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.TRADE)
                            #print(">>>>>>>> phase_names.INVITOR 5",self.invitor_invitee,self.initiator_initiatee)    
                else:
                    self.matrix_animations.add_to_queue("trade_invited", self.invitor_invitee[0],self.invitor_invitee[1])
            #print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)

        if phase_name == phase_names.INVITEE:
            #print(">>>>>>>> phase_names.INVITEE 0",self.invitor_invitee,self.initiator_initiatee)
            if self.invitor_invitee[1] == "":
                self.invitor_invitee[1] = station_fruit_name
            if self.invitor_invitee[0] != "":
                if initiator_hint:
                    #print(">>>>>>>> phase_names.INVITEE 1",self.invitor_invitee,self.initiator_initiatee)
                    # trueque button has been hit
                    # is INVITEE the first or second to hit the trueque button?
                    if self.initiator_initiatee[0] == "":
                        #print(">>>>>>>> phase_names.INVITEE 2",self.invitor_invitee,self.initiator_initiatee)
                        # INVITEE is the first to hit the trueque button
                        self.stations[station_fruit_name].commands.cmd_lefttube_launch()
                        self.initiator_initiatee[0] = station_fruit_name
                        self.matrix_animations.add_to_queue("trade_initiated", self.invitor_invitee[0],self.invitor_invitee[1])
                    else:
                        #print(">>>>>>>> phase_names.INVITEE 3",self.invitor_invitee,self.initiator_initiatee)
                        if self.initiator_initiatee[0] != station_fruit_name:
                            #print(">>>>>>>> phase_names.INVITEE 4",self.invitor_invitee,self.initiator_initiatee)
                            # INVITOR is the second to hit the trueque button
                            self.initiator_initiatee[1] = station_fruit_name
                            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.TRADE)
                            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.TRADE)
                            #print(">>>>>>>> phase_names.INVITEE 5",self.invitor_invitee,self.initiator_initiatee)    

            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)

        if phase_name == phase_names.TRADE:
            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)
            #print("-------------", self.initiator_initiatee, station_fruit_name, self.initiator_initiatee[0] == station_fruit_name)
            if self.initiator_initiatee[0] == station_fruit_name:
                #print("************* 0")
                self.matrix_animations.add_to_queue("trade_succeeded", str(self.invitor_invitee[0]),str(self.invitor_invitee[1]))
                #print("************* 1")
                self.matrix_animations.add_to_queue("pause_animations", str(self.invitor_invitee[1]),str(self.invitor_invitee[0]))
                #print("************* 2")
                self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.COMIENZA)
                self.stations[self.invitor_invitee[0]].add_to_queue("increment_score", 25)
                self.stations[self.invitor_invitee[0]].carousel_add_fruit(self.stations[self.invitor_invitee[1]].fruit_name)
                self.stations[self.invitor_invitee[0]].carousel_display_fruit_presences()

                #print("************* 3")
                self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.COMIENZA)
                self.stations[self.invitor_invitee[1]].add_to_queue("increment_score", 25)
                self.stations[self.invitor_invitee[1]].carousel_add_fruit(self.stations[self.invitor_invitee[0]].fruit_name)
                self.stations[self.invitor_invitee[1]].carousel_display_fruit_presences()
                #print("************* 4")
                self.trade_fail_timer.add_to_queue("end")
                #print("************* 5")
                self.invitor_invitee = ["",""]
                #print("************* 6")
                self.initiator_initiatee = ["",""]
                #print("************* 7")

        if phase_name == phase_names.FAIL:
            # this is called only once, by the timer
            print("Mode_Barter.handle_station_phase_change",phase_name, self.invitor_invitee, self.initiator_initiatee)
            # todoL switch to initiator_initiatee below, after confirming that they get assigned correctly
            self.trade_fail_timer.add_to_queue("end")
            self.matrix_animations.add_to_queue("trade_failed", str(self.invitor_invitee[0]),str(self.invitor_invitee[1]))
            self.matrix_animations.add_to_queue("pause_animations", str(self.invitor_invitee[1]),str(self.invitor_invitee[0]))
            self.stations[self.invitor_invitee[0]].add_to_queue("set_phase", phase_names.COMIENZA)
            self.stations[self.invitor_invitee[1]].add_to_queue("set_phase", phase_names.COMIENZA)
            self.invitor_invitee = ["",""]
            self.initiator_initiatee = ["",""]
    """

    def begin(self):
        #print("Mode_Barter, begin() 1")
        self.active = True
        self.pinball_hostnames_with_players = self.hosts.get_games_with_players()
        # set all stations to phase comienza or noplayer
        self.mode_timer.add_to_queue("begin")
        #print("Mode_Barter, begin() 2", self.pinball_hostnames_with_players)
        for pinball_hostname, station_ref in self.PINBALL_HOSTNAME_TO_STATION.items():
            phase_name = phase_names.COMIENZA if pinball_hostname in self.pinball_hostnames_with_players else phase_names.NOPLAYER
            print("----------------------------------------> 7", pinball_hostname)

            station_ref.add_to_queue("set_phase", phase_name)
            #if phase_name == phase_names.COMIENZA:
                #station_ref.add_to_queue("animation_fill_carousel", True) 
                #print("Mode_Barter, begin() 3",station_ref )
        time.sleep(3.5) # wait for animation_fill_carousel to run
        #print("Mode_Barter, begin() 4")
        for pinball_hostname, station_ref in self.PINBALL_HOSTNAME_TO_STATION.items():
            phase_name = phase_names.COMIENZA if pinball_hostname in self.pinball_hostnames_with_players else phase_names.NOPLAYER
            print("----------------------------------------> 7", pinball_hostname)
            station_ref.add_to_queue("set_phase", phase_name)
            if phase_name == phase_names.COMIENZA:
                station_ref.add_to_queue("cmd_kicker_launch", "")
                #print("Mode_Barter, begin() 3",station_ref )


    def end(self):
        # stop all timers
        self.trade_fail_timer.add_to_queue("end")
        # stop all animations
        self.matrix_animations.add_to_queue("pause_animations", "","")
        self.active = False


    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))


    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get()
                #todo: finish the calls
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')
                if topic == "handle_station_phase_change":
                    self.handle_station_phase_change(message, origin, destination)
                else:
                    self.PINBALL_HOSTNAME_TO_STATION[origin].add_to_queue(topic, message)

            except AttributeError as e:
                print(traceback.format_exc())

        # todo: where do animations get called?

