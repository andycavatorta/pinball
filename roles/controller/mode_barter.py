# todo: in attraction mode , check presence of balls
# todo: add this_fruit every x points or x seconds

import codecs
import os
import queue
import random
import settings
import threading
import time




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
    def __init__(self, commands):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.commands = commands
        self.start()


    def flipboard(self, start_number, end_number):
        if start_number < end_number:
            for display_score in range(start_number, end_number+1):
                self.commands.request_number(display_score)
                time.sleep(0.05)
        if start_number > end_number:
            for display_score in range(end_number, start_number, -1):
                self.commands.request_number(display_score)
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


    def animation_fill_carousel(self, carousel_fruit_order):
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
        self.commands.cmd_playfield_lights("pie_pop_left".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_left".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_pop_middle".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_middle".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("g_mezzo")
        self.commands.cmd_playfield_lights("pie_pop_right".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_pop_right".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_spinner".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_spinner".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("gsharp_mezzo")
        self.commands.cmd_playfield_lights("pie_sling_right".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_sling_right".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("c_mezzo")
        self.commands.cmd_playfield_lights("pie_rollover_right".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_rollover_right".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.request_score("asharp_mezzo")
        self.commands.cmd_playfield_lights("pie_rollover_left".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_rollover_left".format(postfix),"stroke_on")# light segment
        time.sleep(.15)
        self.commands.cmd_playfield_lights("pie_sling_left".format(postfix),"off")# light animation
        self.commands.cmd_playfield_lights("trail_sling_left".format(postfix),"stroke_on")# light segment
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
        self.animation_pinball_game = Animation_Pinball_Game()
        self.animation_transactions = Animation_Transactions()
        self.animation_score = Animation_Score()
        self.fruit_to_spend = ""
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


    def pie_target_hit(self, target_name):
        if self.pie_data_segments[target_name] == False:
            self.pie_data_segments[target_name] = True
            self.commands.cmd_playfield_lights("pie_{}".format(target_name),"on")# light animation
            self.commands.cmd_playfield_lights("trail_{}".format(target_name),"back_stroke_off")# light segment
            if len([True for k,v in self.pie_data_segments.items() if v == True])==8:
                self.animation_pinball_game.add_to_queue("pie_full")
                self.animation_score.add_to_queue("flipboard",[int(self.commands.barter_mode_score),self.commands.barter_mode_score+25])
                self.carousel_add_fruit(self.fruit_name)
                self.carousel_display_fruit_presences()
                #todo: use queue to adjust barter_mode_score
                self.increment_score(25)
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
            if not val:
                missing.append(name)
        return missing


    def carousel_display_fruit_presences(self, fruit_name, level = "on"):
        for fruit_name, presence in self.carousel_data_segments.items():
            self.commands.cmd_carousel_lights(fruit_name, level if presence else "off")


    def increment_score(self, points=1):
        self.animation_score.add_to_queue("flipboard",[int(self.commands.barter_mode_score),self.commands.barter_mode_score+points])
        self.barter_mode_score += points


    def decrement_score(self, points=-1):
        self.animation_score.add_to_queue("flipboard",[int(self.commands.barter_mode_score),self.commands.barter_mode_score-points])
        self.barter_mode_score -= points


    def setup(self):
        if self.current_phase == phase_names.NOPLAYER:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
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
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
            #todo first time run issue
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
                lower_score = self.commands.barter_mode_score-5 if self.commands.barter_mode_score >5 else 1
                self.decrement_score(lower_score)
                self.animation_score.add_to_queue("flipboard",[self.commands.barter_mode_score,lower_score])
                self.commands.barter_mode_score = lower_score
            self.commands.cmd_carousel_lights(self.sacrificial_fruit,  "high")
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
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
            print(time.ctime(time.time()),"===================== PINBALL =====================", self.fruit_name)
            self.commands.enable_izquierda_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_kicker_coil(False)
            self.commands.enable_dinero_coil(False)
            self.commands.enable_derecha_coil(True)
            self.commands.enable_trueque_coil(False)
            self.commands.enable_dinero_coil(False)

        if self.current_phase == phase_names.INVITOR:
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
            print(time.ctime(time.time()),"===================== INVITOR =====================", self.fruit_name)
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(False)
            self.commands.enable_trueque_coil(True)
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
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
            # todo start animation in matrix
            self.commands.enable_izquierda_coil(True)
            self.commands.enable_trueque_coil(True)
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
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
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
            self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "")
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
        if self.current_phase == phase_names.NOPLAYER:
            pass

        if self.current_phase == phase_names.COMIENZA:
            #todo: first time run issue
            if topic == "event_button_comienza":
                self.end()

        if self.current_phase == phase_names.PINBALL:
            if topic == "event_pop_left":
                if message:
                    self.increment_score()
                    self.commands.request_score("gsharp_mezzo")
                    self.pie_target_hit("pop_left")
            if topic == "event_pop_middle":
                if message:
                    self.increment_score()
                    self.commands.request_score("g_mezzo")
                    self.pie_target_hit("pop_middle")
            if topic == "event_pop_right":
                if message:
                    self.increment_score()
                    self.commands.request_score("f_mezzo")
                    self.pie_target_hit("pop_right")
            if topic == "event_roll_inner_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_inner_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_slingshot_left":
                if message:
                    self.increment_score()
                    self.pie_target_hit("sling_left")
                    self.pie_target_hit("rollover_left")
                    self.commands.request_score("asharp_mezzo")

            if topic == "event_slingshot_right":
                if message:
                    self.increment_score()
                    self.pie_target_hit("sling_right")
                    self.pie_target_hit("rollover_right")
                    self.commands.request_score("asharp_mezzo")
                    
            if topic == "event_spinner":
                if message:
                    self.increment_score()
                    self.pie_target_hit("spinner")
                    self.commands.request_score("c_mezzo")
            if topic == "event_trough_sensor":
                if message:
                    self.end()

        if self.current_phase == phase_names.INVITOR:
            if topic == "event_button_trueque":
                self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "event_button_trueque")

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
                    self.increment_score()
                    self.commands.request_score("gsharp_mezzo")
                    self.pie_target_hit("pop_left")
            if topic == "event_pop_middle":
                if message:
                    self.increment_score()
                    self.commands.request_score("g_mezzo")
                    self.pie_target_hit("pop_middle")
            if topic == "event_pop_right":
                if message:
                    self.increment_score()
                    self.commands.request_score("f_mezzo")
                    self.pie_target_hit("pop_right")
            if topic == "event_roll_inner_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_inner_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_left":
                if message:
                    self.pie_target_hit("rollover_left")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_roll_outer_right":
                if message:
                    self.pie_target_hit("rollover_right")
                    self.animation_pinball_game.add_to_queue("chime_sequence",[["c_mezzo","asharp_mezzo","gsharp_mezzo","g_mezzo","f_mezzo"], 0.1])

            if topic == "event_slingshot_left":
                if message:
                    self.increment_score()
                    self.pie_target_hit("sling_left")
                    self.pie_target_hit("rollover_left")
                    self.commands.request_score("asharp_mezzo")

            if topic == "event_slingshot_right":
                if message:
                    self.increment_score()
                    self.pie_target_hit("sling_right")
                    self.pie_target_hit("rollover_right")
                    self.commands.request_score("asharp_mezzo")
                    
            if topic == "event_spinner":
                if message:
                    self.increment_score()
                    self.pie_target_hit("spinner")
                    self.commands.request_score("c_mezzo")
            if topic == "event_trough_sensor":
                if message:
                    self.commands.request_button_light_active("izquierda",False)
                    self.commands.request_button_light_active("trueque",True)
                    self.commands.request_button_light_active("comienza",False)
                    self.commands.request_button_light_active("dinero",False)
                    self.commands.request_button_light_active("derecha",False)
            if topic == "event_button_trueque":
                self.parent_ref.add_to_queue("handle_station_phase_change",self.fruit_name, self.current_phase, "event_button_trueque")

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
            #todo:  first time run should go to end()
            #    or kicker can fire during begin()
            # if there is a fruit to spend
            if self.fruit_to_spend != "":
                #remove the fruit data
                self.carousel_remove_fruit(self.fruit_to_spend)
                #update the led state
                self.carousel_display_fruit_presences()
            self.commands.cmd_kicker_launch() 
            self.set_phase(phase_names.PINBALL)

        if self.current_phase == phase_names.PINBALL:
            # todo: add necessary parameters to call to get_trade_option after writing get_trade_option
            self.set_phase(self.parent_ref.get_trade_option(self.fruit_name))

        if self.current_phase == phase_names.INVITOR:
            pass
            #todo: go to phase_names.TRADE or phase_names.FAIL

        if self.current_phase == phase_names.INVITEE:
            pass
            #todo: go to phase_names.TRADE or phase_names.FAIL

        if self.current_phase == phase_names.TRADE:
            station_ref.add_to_queue("set_phase", phase_names.COMIENZA)

        if self.current_phase == phase_names.FAIL:
            station_ref.add_to_queue("set_phase", phase_names.COMIENZA)


    def set_phase(self, phase_name):
        print("set_phase", self.fruit_name, phase_name)
        if self.current_phase != phase_name:
            #self.end()
            self.current_phase = phase_name
            self.setup()


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            topic,message = self.queue.get()
            if topic == "set_phase":
                self.set_phase(message)
            if topic == "animation_fill_carousel":
                self.animation_transactions.add_to_queue("animation_fill_carousel", self.carousel_fruit_order)
                self.carousel_add_fruit(self.carousel_fruit_order[1])
                self.carousel_add_fruit(self.carousel_fruit_order[2])
                self.carousel_add_fruit(self.carousel_fruit_order[3])
                self.carousel_add_fruit(self.carousel_fruit_order[4])
            else:
                self.event_handler(topic,message)



class Mode_Timer(threading.Thread):
    def __init__(self, set_current_mode, end):
        threading.Thread.__init__(self)
        self.set_current_mode = set_current_mode
        self.end = end
        self.timer = -1
        self.timer_limit = 90
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
                    print("Mode_Timer run self.timer=",self.timer)
                    if self.timer >= self.timer_limit:
                        self.timer = -1
                        self.end()
                        self.set_current_mode(settings.Game_Modes.MONEY_MODE_INTRO)


class Matrix_Animations(threading.Thread):
    """
    
    todo: change animation methods to generators to make them easy to interrupt 
    """
    def __init__(self, hosts):
        threading.Thread.__init__(self)
        self.hosts = hosts
        self.queue = queue.Queue()
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
        calculated_paths = {
            "coco":{
                "naranja":[# 13
                    ["coco",18,17,"coco"],
                    ["coco",19,16,"coco"],
                    ["center",19,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",12,15,"naranja"],
                    ["naranja",12,15,"naranja"],
                    ["naranja",13,15,"naranja"],
                    ["naranja",14,15,"naranja"],
                    ["naranja",17,16,"coco"],
                    ["naranja",18,19,"coco"],
                ],
                "mango":[# 17
                    ["coco",18,17,"coco"],
                    ["coco",19,16,"coco"],
                    ["center",19,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",8,11,"mango"],
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
                    ["center",16,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",3,0,"sandia"],
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
                    ["center",16,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",23,20,"pina"],
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
                    ["center",12,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",19,16,"coco"],
                    ["coco",19,16,"coco"],
                    ["coco",18,16,"coco"],
                    ["coco",17,16,"coco"],
                    ["coco",14,15,"naranja"],
                    ["coco",13,12,"naranja"],
                ],
                "mango":[ # 13
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",15,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",8,11,"mango"],
                    ["mango",8,11,"mango"],
                    ["mango",9,11,"mango"],
                    ["mango",10,11,"mango"],
                    ["mango",13,12,"naranja"],
                    ["mango",14,15,"naranja"],
                ],
                "sandia":[ # 17
                    ["naranja",14,13,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["center",15,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",13,12,"naranja"],
                    ["center",10,11,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",0,3,"sandia"],
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
                    ["center",12,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,19,"coco"],
                    ["center",21,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",23,20,"pina"],
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
                    ["center",8,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,15,"naranja"],
                    ["center",17,16,"coco"],
                    ["center",18,16,"coco"],
                    ["center",19,16,"coco"],
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
                    ["center",8,11,"mango"],
                    ["center",9,11,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",15,12,"naranja"],
                    ["naranja",15,12,"naranja"],
                    ["naranja",14,12,"naranja"],
                    ["naranja",13,12,"naranja"],
                    ["naranja",10,11,"mango"],
                    ["naranja",9,8,"mango"],
                ],
                "sandia":[ # 13
                    ["mango",10,9,"mango"],
                    ["mango",11,8,"mango"],
                    ["center",11,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",0,3,"sandia"],
                    ["sandia",0,3,"sandia"],
                    ["sandia",1,3,"sandia"],
                    ["sandia",2,3,"sandia"],
                    ["sandia",9,8,"mango"],
                    ["sandia",10,11,"mango"],
                ],
                "pina":[ # 17
                    ["mango",9,10,"mango"],
                    ["mango",8,11,"mango"],
                    ["center",11,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",9,8,"mango"],
                    ["center",2,3,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",20,23,"pina"],
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
                    ["center",3,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",16,19,"coco"],
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
                    ["center",0,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,11,"mango"],
                    ["center",13,12,"naranja"],
                    ["center",14,12,"naranja"],
                    ["center",15,12,"naranja"],
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
                    ["center",0,3,"sandia"],
                    ["center",1,3,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",11,8,"mango"],
                    ["mango",11,8,"mango"],
                    ["mango",10,8,"mango"],
                    ["mango",9,8,"mango"],
                    ["mango",2,3,"sandia"],
                    ["mango",1,0,"sandia"],
                ],
                "pina":[ # 13
                    ["sandia",2,1,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["center",3,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",1,0,"sandia"],
                    ["center",22,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",20,23,"pina"],
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
                    ["center",23,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,19,"coco"],
                    ["center",16,19,"coco"],
                    ["coco",16,19,"coco"],
                    ["coco",17,19,"coco"],
                    ["coco",18,19,"coco"],
                    ["coco",21,20,"pina"],
                    ["coco",22,23,"pina"],
                ],
                "naranja":[  # 17
                    ["pina",22,21,"pina"],
                    ["pina",23,20,"pina"],
                    ["center",23,20,"pina"],
                    ["center",22,20,"pina"],
                    ["center",21,20,"pina"],
                    ["center",18,19,"coco"],
                    ["center",17,16,"coco"],
                    ["center",14,15,"naranja"],
                    ["center",13,15,"naranja"],
                    ["center",12,15,"naranja"],
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
                    ["center",20,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,3,"sandia"],
                    ["center",9,8,"mango"],
                    ["center",10,8,"mango"],
                    ["center",11,8,"mango"],
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
                    ["center",20,23,"pina"],
                    ["center",21,23,"pina"],
                    ["center",22,23,"pina"],
                    ["center",1,0,"sandia"],
                    ["center",2,0,"sandia"],
                    ["center",3,0,"sandia"],
                    ["sandia",3,0,"sandia"],
                    ["sandia",2,0,"sandia"],
                    ["sandia",1,0,"sandia"],
                    ["sandia",22,23,"pina"],
                    ["sandia",21,20,"pina"],
                ],
            },
        } 





    def trade_invited_setup(self, invitor, invitee):
        # alternating pong trail animations
        path_a = self.calculated_paths[invitor][invitee]
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[path_a[0][0]].cmd_carousel_lights("all","off")
        self.carousels[path_a[-1][0]].cmd_carousel_lights("all","off")


    def draw_pong_fade(self, path, ordinal, levels=["high","med","low","off"]):
        # todo, clear tail when end is reached
        if ordinal+1 > -1 and ordinal+1 < len(path):
            self.set_pair_to_level(
                self, 
                path[ordinal+1][0], 
                path[ordinal+1][1], 
                path[ordinal+1][2], 
                levels[0]
            )
        if ordinal > -1 and ordinal < len(path):
            self.set_pair_to_level(
                self, 
                path[ordinal][0], 
                path[ordinal][1], 
                path[ordinal][2], 
                levels[0]
            )
        if ordinal-1 > -1 and ordinal-1 < len(path):
            self.set_pair_to_level(
                self, 
                path[ordinal-1][0], 
                path[ordinal-1][1], 
                path[ordinal-1][2], 
                levels[1]
            )
        if ordinal-2 > -1 and ordinal-2 < len(path):
            self.set_pair_to_level(
                self, 
                path[ordinal-2][0], 
                path[ordinal-2][1], 
                path[ordinal-2][2], 
                levels[2]
            )
        if ordinal-2 > -1 and ordinal-2 < len(path):
            self.set_pair_to_level(
                self, 
                path[ordinal-2][0], 
                path[ordinal-2][1], 
                path[ordinal-2][2], 
                levels[3]
            )


    def set_pair_to_level(self, carousel_name, led_1, led_2, level):
        self.carousels[carousel_name].cmd_carousel_lights(str(led_1),level)
        self.carousels[carousel_name].cmd_carousel_lights(str(led_2),level)


    def trade_invited_repeat(self, invitor, invitee):
        # alternating pong trail animations
        path_a = self.calculated_paths[invitor][invitee]
        path_b = self.calculated_paths[invitee][invitor]

        # cycle 0
        # dim all fruits in invitor carousel, invitee carousel, center carousel
        self.carousels["center"].cmd_carousel_lights("all","off")
        self.carousels[path_a[0][0]].cmd_carousel_lights("all","off")
        self.carousels[path_b[0][0]].cmd_carousel_lights("all","off")
        time.sleep(0.05)
        # todo: add button blink and chimes
        self.carousels[path_a[0][0]].request_button_light_active("trueque", True)
        self.carousels[path_b[0][0]].request_button_light_active("trueque", False)
        self.carousels[path_a[0][0]].request_score("g_mezzo")

        for ordinal in range(len(path_a)):
            self.draw_pong_fade(path_a, ordinal)
            time.sleep(0.05)

        self.carousels[path_a[0][0]].request_button_light_active("trueque", False)
        self.carousels[path_b[0][0]].request_button_light_active("trueque", True)
        self.carousels[path_b[0][0]].request_score("gsharp_mezzo")
        for ordinal in range(len(path_b)):
            self.draw_pong_fade(path_b, ordinal)
            time.sleep(0.05)


    def trade_initiated_setup(self, initiator, invitee):
        # alternating pong trail animations
        path_a = self.calculated_paths[initiator][invitee]
        path_b = self.calculated_paths[invitee][initiator]

        # todo: launch trueque tube
        self.carousels[path_a[0][0]].cmd_lefttube_launch()
        self.carousels[path_a[0][0]].request_button_light_active("trueque", True)

        # animate path of initiator fruit to destination lights, chimes, solenoids
        for ordinal in range(len(path_a)):
            self.draw_pong_fade(path_a, ordinal)
            if ordinal%2==0:
                self.carousels[path_a[0][0]].request_eject_ball(path_a[0][3])
            time.sleep(0.05)
        self.set_pair_to_level(path_b[0][0], path_b[0][1], path_b[0][2], "on")
        self.set_pair_to_level(path_b[0][0], path_b[0][1], path_b[0][2], "on")
        self.carousels[path_b[0][0]].request_score("f_mezzo")
        self.carousels[path_b[0][0]].request_score("gsharp_mezzo")
        self.carousels[path_b[0][0]].request_score("c_mezzo")


    def trade_initiated_repeat(self, initiator, invitee):
        path_a = self.calculated_paths[initiator][invitee]
        path_b = self.calculated_paths[invitee][initiator]

        # todo: test
        self.carousels[path_b[0][0]].request_button_light_active("trueque", True)
        self.carousels[path_b[0][0]].request_score("gsharp_mezzo")
        for ordinal in range(len(path_b)):
            self.draw_pong_fade(path_b, ordinal)
            time.sleep(0.05)
        self.carousels[path_b[0][0]].request_button_light_active("trueque", False)
        time.sleep(0.2)


    def trade_succeeded_setup(self, initiator, invitee):
        path_a = self.calculated_paths[initiator][invitee]
        path_b = self.calculated_paths[invitee][initiator]

        # todo: launch trueque tube
        self.carousels[path_b[0][0]].cmd_lefttube_launch()
        self.carousels[path_b[0][0]].request_button_light_active("trueque", True)

        # animate path of initiator fruit to destination lights, chimes, solenoids
        for ordinal in range(len(path_a)):
            self.draw_pong_fade(path_a, ordinal)
            if ordinal%2==0:
                self.carousels[path_a[0][0]].request_eject_ball(path_a[0][3])
            time.sleep(0.05)
        self.set_pair_to_level(path_a[-1][0], path_a[-1][1], path_a[-1][2], "on")
        self.set_pair_to_level(path_a[-2][0], path_a[-2][1], path_a[-2][2], "on")
        self.carousels[path_b[0][0]].request_score("f_mezzo")
        self.carousels[path_b[0][0]].request_score("gsharp_mezzo")
        self.carousels[path_b[0][0]].request_score("c_mezzo")


    def trade_failed_setup(self, initiator, invitee):
        path_a = self.calculated_paths[initiator][invitee]
        path_b = self.calculated_paths[invitee][initiator]
        # animate path_a backward with fail sound
        # light all of path b, then fade
        path_a_reversed = reverse(list[path_a])
        for ordinal in range(len(path_a_reversed)):
            self.draw_pong_fade(path_a_reversed, ordinal)
            time.sleep(0.05)
        self.carousels[path_b[0][0]].request_score("f_mezzo")
        self.carousels[path_b[0][0]].request_score("g_mezzo")
        self.carousels[path_b[0][0]].request_score("gsharp_mezzo")
        self.carousels[path_b[0][0]].request_score("asharp_mezzo")
        self.carousels[path_b[0][0]].request_score("c_mezzo")


    def add_to_queue(self, animation, station_a_name, station_b_name):
        self.queue.put((animation, station_a_name, station_b_name))


    def run(self):
        while True:
            animation, station_a_name, station_b_name = self.queue.get()
            if animation == "trade_invited":
                self.trade_invited(station_a_name, station_b_name) #invitor, invitee
            if animation == "trade_initiated":
                self.trade_initiated(station_a_name, station_b_name)
            if animation == "trade_succeeded":
                self.trade_succeeded(station_a_name, station_b_name)
            if animation == "trade_failed":
                self.trade_failed(station_a_name, station_b_name)


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
        self.mode_timer = Mode_Timer(self.set_current_mode, self.end)
        self.matrix_animations = Matrix_Animations(self.hosts)
        class station_to_host_coco():
            barter_mode_score = self.hosts.hostnames['pinball1game'].barter_mode_score
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
            money_mode_score = self.hosts.hostnames['pinball1game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball1game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball1display'].request_number
            request_phrase = self.hosts.hostnames['pinball1display'].request_phrase
            request_score = self.hosts.hostnames['pinball1display'].request_score
            set_money_points = self.hosts.hostnames['pinball1game'].set_money_points

        class station_to_host_naranja:
            barter_mode_score = self.hosts.hostnames['pinball2game'].barter_mode_score
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
            money_mode_score = self.hosts.hostnames['pinball2game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball2game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball2display'].request_number
            request_phrase = self.hosts.hostnames['pinball2display'].request_phrase
            request_score = self.hosts.hostnames['pinball2display'].request_score
            set_money_points = self.hosts.hostnames['pinball2game'].set_money_points

        class station_to_host_mango:
            barter_mode_score = self.hosts.hostnames['pinball3game'].barter_mode_score
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
            money_mode_score = self.hosts.hostnames['pinball3game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball3game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball3display'].request_number
            request_phrase = self.hosts.hostnames['pinball3display'].request_phrase
            request_score = self.hosts.hostnames['pinball3display'].request_score
            set_money_points = self.hosts.hostnames['pinball3game'].set_money_points

        class station_to_host_sandia:
            barter_mode_score = self.hosts.hostnames['pinball4game'].barter_mode_score
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
            money_mode_score = self.hosts.hostnames['pinball4game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball4game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball4display'].request_number
            request_phrase = self.hosts.hostnames['pinball4display'].request_phrase
            request_score = self.hosts.hostnames['pinball4display'].request_score
            set_money_points = self.hosts.hostnames['pinball4game'].set_money_points

        class station_to_host_pina:
            barter_mode_score = self.hosts.hostnames['pinball5game'].barter_mode_score
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
            money_mode_score = self.hosts.hostnames['pinball5game'].money_mode_score
            request_button_light_active = self.hosts.hostnames['pinball5game'].request_button_light_active
            request_number = self.hosts.hostnames['pinball5display'].request_number
            request_phrase = self.hosts.hostnames['pinball5display'].request_phrase
            request_score = self.hosts.hostnames['pinball5display'].request_score
            set_money_points = self.hosts.hostnames['pinball5game'].set_money_points

        self.PINBALL_TO_STATION = {
            "pinball1game":self.stations["coco"],
            "pinball2game":self.stations["naranja"],
            "pinball3game":self.stations["mango"],
            "pinball4game":self.stations["sandia"],
            "pinball5game":self.stations["pina"],
        }
        self.stations = {
            "coco":Station("coco",station_to_host_coco),
            "naranja":Station("naranja",station_to_host_naranja),
            "mango":Station("mango",station_to_host_mango),
            "sandia":Station("sandia",station_to_host_sandia),
            "pina":Station("pina",station_to_host_pina),
        }

        self.invitor_invitee = []

        self.start()
        #'carouselcenter':self.carouselcenter,
        #'pinballmatrix':self.pinballmatrix,

    # todo: reset self.invitor_invitee after trade or fail

    def get_trade_option(self, fruit_name):
        # todo: how does this vary with different numbers of players?
        # maybe don't use invitor_invitee
        # what are the conditions for trading?
        self.lock.acquire()
        # if no other trade is happening
        if self.invitor_invitee != []:
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
            if self.stations[station_a_missing_fruit].carousel_get_fruit_presence(station_a_missing_fruit):
                # if station_b is missing fruit_a
                if not self.stations[station_a_missing_fruit].carousel_get_fruit_presence(fruit_name):
                    potential_trading_partners.append(station_a_missing_fruit)
        if len(potential_trading_partners) == 0:
            self.lock.release()
            return phase_names.COMIENZA
        invitee_fruit_name = random.choice(potential_trading_partners)
        self.invitor_invitee = [fruit_name,invitee_fruit_name]
        self.stations[invitee_fruit_name].set_phase(phase_names.INVITEE)
        self.lock.release()
        return phase_names.INVITOR

    def handle_station_phase_change(self, station_fruit_name, phase_name, initiator_hint):
        if phase_name == phase_names.NOPLAYER:
            pass
        if phase_name == phase_names.COMIENZA:
            if station_fruit_name in self.invitor_invitee:
                self.invitor_invitee = ["",""]

        if phase_name == phase_names.PINBALL:
            if station_fruit_name in self.invitor_invitee:
                self.invitor_invitee = ["",""]

        if phase_name == phase_names.INVITOR:
            if self.invitor_invitee[0] == "":
                self.invitor_invitee[0] = station_fruit_name

        if phase_name == phase_names.INVITEE:
            if self.invitor_invitee[1] == "":
                self.invitor_invitee[1] = station_fruit_name

        if phase_name == phase_names.TRADE:
            self.invitor_invitee = ""
        if phase_name == phase_names.FAIL:
            self.invitor_invitee = ""

        #handle_station_phase_change",self.fruit_name, self.current_phase, "event_button_trueque"
        # thread safe!
        #self.matrix_animations.add_to_queue(animation, station_a_name, station_b_name)


    def begin(self):
        self.active = True
        self.pinball_hostnames_with_players = self.hosts.get_games_with_players()
        # set all stations to phase comienza or noplayer
        self.mode_timer.add_to_queue("begin")
        for pinball_hostname, station_ref in self.PINBALL_TO_STATION.items():
            phase_name = phase_names.COMIENZA if pinball_hostname in self.pinball_hostnames_with_players else phase_names.NOPLAYER
            station_ref.add_to_queue("set_phase", phase_name)
            if phase_name == phase_names.COMIENZA:
                station_ref.add_to_queue("animation_fill_carousel", True) 


    def end(self):
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
                    self.PINBALL_TO_STATION[origin].add_to_queue(topic, message)

            except AttributeError:
                pass

        # todo: where do animations get called?

