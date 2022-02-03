"""
increment_decrement_fruits
    what to do if fruits are full?
    can this be prevented from happening?
    does 5 fruits make a winner?
"""
import codecs
import os
import queue
import random
import settings
import threading
import time

class Pie():
    def __init__(self, origin, hosts, pie_full_handler):
        self.origin = origin
        self.hosts = hosts
        self.pie_full_handler = pie_full_handler
        self.pie_segments_triggered = {
            "pop_left":False,
            "pop_middle":False,
            "pop_right":False,
            "spinner":False,
            "sling_right":False,
            "rollover_right":False,
            "rollover_left":False,
            "sling_left":False,
        }
        self.reset_pie()

    def target_hit(self,target_name):
        #print("target_hit",target_name)
        if self.pie_segments_triggered[target_name] == False:
            self.pie_segments_triggered[target_name] = True
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_{}".format(target_name),"on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_{}".format(target_name),"back_stroke_off")# light segment
            if len([True for k,v in self.pie_segments_triggered.items() if v == True])==8:
                self.hosts.hostnames[self.origin].cmd_playfield_lights("pie","energize")# light animation
                time.sleep(.5)
                self.reset_pie()
                self.pie_full_handler()

    def reset_pie(self):
        for target_name in self.pie_segments_triggered:
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_{}".format(target_name),"off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_{}".format(target_name),"stroke_on")# light segment
        self.pie_segments_triggered = {
            "pop_left":False,
            "pop_middle":False,
            "pop_right":False,
            "spinner":False,
            "sling_right":False,
            "rollover_right":False,
            "rollover_left":False,
            "sling_left":False,
        }

class Carousel_Fruits():
    # does this class animate lights and sounds or just track the state?
    def __init__(self, this_fruit_name, get_games_with_players):
        #self.this_fruit_name = this_fruit_name
        self.this_fruit_name = this_fruit_name
        self.get_games_with_players = get_games_with_players
        self.fruit_presence={
            "coco":False,
            "naranja":False,
            "mango":False,
            "sandia":False,
            "pina":False,
        }
        self.fruit_order_clockwise = [
            "coco",
            "naranja",
            "mango",
            "sandia",
            "pina",
            "coco",
            "naranja",
            "mango",
            "sandia",
            "pina",
        ]
        self.fruit_order_counterclockwise = [
            "pina",
            "sandia",
            "mango",
            "naranja",
            "coco",
            "pina",
            "sandia",
            "mango",
            "naranja",
            "coco",
        ]
        self.fruit_name_from_pinball_hostname = {
            "pinball1game":"coco",
            "pinball2game":"naranja",
            "pinball3game":"mango",
            "pinball4game":"sandia",
            "pinball5game":"pina",
        }
 
    def is_fruit_present(self, fruit_name):
        return self.fruit_presence[fruit_name]

    def list_fruits_present(self):
        present = []
        for fruit_name, presence in self.fruit_presence.items():
            if presence:
               present.append(fruit_name) 
        return present

    def list_other_fruits_present(self):
        present = []
        for fruit_name, presence in self.fruit_presence.items():
            if presence and self.this_fruit_name != fruit_name:
               present.append(fruit_name) 
        return present

    def list_missing_other_fruits(self):
        self.fruits_with_players = []
        for game_with_player in self.get_games_with_players():
            self.fruits_with_players.append(self.fruit_name_from_pinball_hostname[game_with_player])
        missing = []
        for fruit_with_player in self.fruits_with_players:
            if self.fruit_presence[fruit_with_player] == False:
                missing.append(fruit_with_player)
        return missing

    #def get_next_empty_otherfruit(self):
    #    for game_with_player in self.games_with_players:

    def add_fruit(self, fruit_name):
        self.fruit_presence[fruit_name] = True

    def remove_fruit(self, fruit_name=""):
        self.fruit_presence[fruit_name] = False

    def get_radial_path(self, start_fruit_name, end_fruit_name, clockwise_b):
        path = [] # list of fruit names
        if clockwise_b:
            start_fruit_cursor = self.fruit_order_clockwise.index(start_fruit_name)
            end_fruit_cursor = self.fruit_order_clockwise.index(end_fruit_name, start_fruit_name)
            for cursor in range(start_fruit_cursor,end_fruit_cursor+1):
                path.append(self.fruit_order_clockwise[cursor])
        else: # counterclockwise
            start_fruit_cursor = self.fruit_order_counterclockwise.index(start_fruit_name)
            end_fruit_cursor = self.fruit_order_counterclockwise.index(end_fruit_name, start_fruit_name)
            for cursor in range(start_fruit_cursor,end_fruit_cursor+1):
                path.append(self.fruit_order_counterclockwise[cursor])
        return path

    def get_shorter_radial_path(self, start_fruit_name, end_fruit_name):
        path_cw = self.get_radial_path(start_fruit_name, end_fruit_name, True)
        path_cc = self.get_radial_path(start_fruit_name, end_fruit_name, False)
        return path_cc if len(path_cw) > len(path_cc) else path_cw

    def populate_this_fruit(self):
        self.fruit_presence[self.this_fruit_name] = True


###################
### P H A S E S ###
###################

class phase_names():
    NOPLAYER="noplayer"
    COMIENZA="comienza"
    PINBALL="pinball"
    INVITOR="invitor"
    INVITEE="invitee"
    TRADE="trade"
    FAIL="fail"

class Phase_NoPlayer(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        #self.start()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.set_phase = parent_ref.set_phase
        self.phase_name = phase_names.NOPLAYER

    def setup(self):
        self.trading_partner = None
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)
        self.hosts.hostnames[self.game_name].disable_gameplay()
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("all_radial", "off")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all", "off")

    def respond(self, topic, message):
        pass

    def end(self):
        pass

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        pass

class Phase_Comienza(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.carousel_fruits = parent_ref.carousel_fruits
        self.get_games_missing_other_fruit = parent_ref.get_games_missing_other_fruit
        self.set_phase = parent_ref.set_phase
        self.score = parent_ref.score
        self.decrement_score = parent_ref.decrement_score
        self.pinball_hostnames_with_players = self.hosts.get_games_with_players()
        self.other_hostnames_with_players = []
        self.fruit_name_from_pinball_hostname = {
            "pinball1game":"coco",
            "pinball2game":"naranja",
            "pinball3game":"mango",
            "pinball4game":"sandia",
            "pinball5game":"pina",
        }
        self.phase_name = phase_names.COMIENZA
        self.sacrificial_fruit = None
        self.start()

    def setup(self):
        self.other_hostnames_with_players = []
        self.pinball_hostnames_with_players = self.hosts.get_games_with_players()
        for pinball_hostname_with_player in self.pinball_hostnames_with_players:
            if pinball_hostname_with_player != self.game_name:
                self.other_hostnames_with_players.append(pinball_hostname_with_player)

        self.trading_partner = None
        #print("---> trading_partner",self.trading_partner, self.fruit_name)
        #self.hosts.hostnames[self.game_name].disable_gameplay()
        self.hosts.hostnames[self.game_name].enable_gameplay()
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",True)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)
        other_fruits = self.carousel_fruits.list_other_fruits_present()
        #print("---> other_fruits", other_fruits, self.fruit_name)
        if len(other_fruits) > 0:
            self.sacrificial_fruit = other_fruits[0]
            #print("--->a self.sacrificial_fruit",self.sacrificial_fruit, self.fruit_name)
        else: # if there are no otherfruits
            if self.score > 0:
                point_loss = int(self.score * 0.1)
                self.decrement_score(point_loss)

            games_missing_other_fruit = self.get_games_missing_other_fruit(self.game_name)
            #print("---> games_missing_other_fruit", games_missing_other_fruit, self.fruit_name)
            if len(games_missing_other_fruit) > 0:
                other_pinball_hostname = random.choice(games_missing_other_fruit)
            else:
                other_pinball_hostname = random.choice(self.other_hostnames_with_players)
            self.sacrificial_fruit = self.fruit_name_from_pinball_hostname[other_pinball_hostname]
            #print("--->b sacrificial_fruit", self.sacrificial_fruit, self.fruit_name)

            # populate sacrificial_fruit
            self.carousel_fruits.add_fruit(self.sacrificial_fruit)
            self.update_carousel_lights_to_data()
            # animate gain of one fruit
            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(self.sacrificial_fruit,  "low")
            time.sleep(0.15)
            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(self.sacrificial_fruit,  "med")
            time.sleep(0.15)
            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(self.sacrificial_fruit,  "high")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",True)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",True)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")


    def respond(self, topic, message):
        if topic == "event_button_comienza":
            self.end()


    def end(self):
        self.carousel_fruits.remove_fruit(self.sacrificial_fruit)
        self.update_carousel_lights_to_data
        self.add_to_queue("spend_fruit", self.sacrificial_fruit)
        self.hosts.hostnames[self.game_name].cmd_kicker_launch() 
        self.set_phase(phase_names.PINBALL)


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))


    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                if topic == "spend_fruit":
                    self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(message,  "on")
                    time.sleep(0.15)
                    self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(message,  "med")
                    time.sleep(0.15)
                    self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(message,  "low")
                    time.sleep(0.15)
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(message,  "off")

            except AttributeError:
                pass
            except queue.Empty:
                pass
 
class Phase_Pinball(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.set_phase = parent_ref.set_phase
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.increment_score = parent_ref.increment_score
        self.pie = parent_ref.pie
        self.get_trade_option = parent_ref.get_trade_option
        self.carousel_fruits = parent_ref.carousel_fruits
        self.phase_name = phase_names.PINBALL
        self.start()


    def setup(self):
        self.trading_partner = None
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",True)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",True)
        self.hosts.hostnames[self.game_name].enable_gameplay()
        #self.hosts.hostnames[self.game_name].disable_gameplay()
        self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
        self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
        #self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
        #self.hosts.hostnames[self.game_name].enable_izquierda_coil(True)
        #self.hosts.hostnames[self.game_name].enable_derecha_coil(True)


    def respond(self, topic, message):
        if topic == "event_pop_left":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                self.pie.target_hit("pop_left")
        if topic == "event_pop_middle":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                self.pie.target_hit("pop_middle")
        if topic == "event_pop_right":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                self.pie.target_hit("pop_right")
        if topic == "event_roll_inner_left":
            if message:
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_roll_inner_right":
            if message:
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_roll_outer_left":
            if message:
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
        if topic == "event_roll_outer_right":
            if message:
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_slingshot_left":
            if message:
                self.increment_score()
                self.pie.target_hit("sling_left")
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")

        if topic == "event_slingshot_right":
            if message:
                self.increment_score()
                self.pie.target_hit("sling_right")
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                
        if topic == "event_spinner":
            if message:
                self.increment_score()
                self.pie.target_hit("spinner")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        if topic == "event_trough_sensor":
            if message:
                self.end()

    def end(self):
        # does this game have a fruit to trade?
        if self.carousel_fruits.is_fruit_present(self.fruit_name):
            self.set_phase(phase_names.COMIENZA)
        # is this game missing an active other_fruit?
        missing_other_fruits = self.carousel_fruits.list_missing_other_fruits()
        print("missing_other_fruits",missing_other_fruits)
        if len(missing_other_fruits) == 0:
            self.set_phase(phase_names.COMIENZA)
        trade_option = self.get_trade_option(self, missing_other_fruits)
        print("trade_option",trade_option)
        self.set_phase(trade_option)


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
            except AttributeError:
                pass
            except queue.Empty:
                pass

class Phase_Invitor(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.carousel_fruits = parent_ref.carousel_fruits
        self.set_phase = parent_ref.set_phase
        self.trade_role = parent_ref.trade_role
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.add_to_parent_queue = parent_ref.add_to_queue
        self.get_trading_partner = parent_ref.get_trading_partner
        self.get_trade_initiated = parent_ref.get_trade_initiated
        self.set_trade_initiated = parent_ref.set_trade_initiated
        self.trading_partner = None
        self.set_trade_initiated(False)
        self.timeout_limit = 6
        self.trueque_button_pressed = False
        self.add_to_queue("stop", True)
        self.phase_name = phase_names.INVITOR
        self.start()

    def setup(self):
        self.trade_role = phase_names.INVITOR # this is a hack to preserve role after this phase
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",True)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)
        self.hosts.hostnames[self.game_name].enable_gameplay()
        #self.hosts.hostnames[self.game_name].disable_gameplay()
        #self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
        #self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
        #self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
        #self.hosts.hostnames[self.game_name].enable_izquierda_coil(True)
        #self.hosts.hostnames[self.game_name].enable_derecha_coil(True)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_right", animation)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right", animation)
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("coco")    
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("naranja")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("mango")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("sandia")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("pina")
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("coco",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("naranja",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("mango",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("sandia",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("pina",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("peso",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all",  animation)
        self.trading_partner = self.get_trading_partner(self.fruit_name)

        ### D R A W   P A T H ###
        self.trading_partner.fruit_name
        self.fruit_name

        # invitor carousel
        invitor_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)
        center_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.fruit_name,self.trading_partner.fruit_name)
        invitee_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)

        # draw path
        # dim lit fruits in local carousel
        # light this_fruit
        # plot path
            # local_carousel this_fruit
            # center carousel, clockwise from local fruit to trading partner fruit.
            # trading partner carousel, counter-clockwise to trading partner self_fruit
        # animate bright light along path


        self.add_to_queue("double")

    def respond(self, topic, message):
        """
        animations = #"stop"|"double"|"local_pushed"|"other_pushed"
        """
        if topic == "event_button_trueque":
            if not self.get_trade_initiated(): #only run this once
                self.set_trade_initiated(True)
                self.hosts.hostnames[self.game_name].cmd_lefttube_launch()
                # todo: animation to confirm button push
                #   draw sparkly path between carousels
                if self.trading_partner.get_trade_initiated():
                    #trading
                    self.add_to_queue("stop")
                    self.set_phase(phase_names.TRADE)
                else:
                    #waiting
                    self.trading_partner.add_to_queue("other_pushed", True)
                    self.add_to_queue("local_pushed")

    def end(self):
        """
        Getting to here might be more complicated that it's worth for consistency
        """
        pass


    def animation_carousel_path_blink(self, frame):
        # invitor carousel
        invitor_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)
        center_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.fruit_name,self.trading_partner.fruit_name)
        invitee_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)
        if frame == 0:
            for path_fruit_name in invitor_carousel_path:
                self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(path_fruit_name, "off")
            for path_fruit_name in center_carousel_path:
                self.hosts.hostnames["carouselcenter"].cmd_carousel_lights(path_fruit_name, "off")
            for path_fruit_name in invitee_carousel_path:
                self.hosts.hostnames[self.trading_partner.carousel_name].cmd_carousel_lights(path_fruit_name, "off")
        if frame == 1:
            for path_fruit_name in invitor_carousel_path:
                self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(path_fruit_name, "on")
            for path_fruit_name in center_carousel_path:
                self.hosts.hostnames["carouselcenter"].cmd_carousel_lights(path_fruit_name, "on")
            for path_fruit_name in invitee_carousel_path:
                self.hosts.hostnames[self.trading_partner.carousel_name].cmd_carousel_lights(path_fruit_name, "on")


    def animation_double(self, frame):
        if frame == 0:
            self.animation_carousel_path_blinBk(1)
            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",True)
        if frame == 1:
            self.animation_carousel_path_blink(1)
            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",True)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",False)


    def animation_local_pushed(self, frame):
        if frame == 0:
            self.animation_carousel_path_blink(1)
            self.hosts.hostnames[self.trading_partner.display_name].request_score("c_mezzo")
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",True)
        if frame == 1:
            self.animation_carousel_path_blink(0)
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",False)


    def animation_other_pushed(self, frame):
        if frame == 0:
            self.animation_carousel_path_blink(1)
            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",True)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",False)
        if frame == 1:
            self.animation_carousel_path_blink(0)
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
            self.hosts.hostnames[self.trading_partner.game_name].request_button_light_active("trueque",False)


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        # "stop"|"double"|"local_pushed"|"other_pushed"
        do_animation = False
        timeout_counter = 0
        while True:
            try:
                topic, message = self.queue.get(timeout=1)
                if topic == "stop":
                    do_animation = topic
                    timeout_counter = 0
                if topic == "double":
                    timeout_counter = 0
                    do_animation = topic
                if topic == "local_pushed":
                    do_animation = topic
                if topic == "other_pushed":
                    do_animation = topic

            except AttributeError:
                pass
            except queue.Empty:
                if do_animation == "stop":
                    time.sleep(0.1)
                else:
                    timeout_counter += 1
                    if timeout_counter >= self.timeout_limit:
                        do_animation = "stop"
                        self.set_phase(phase_names.FAIL)
                        # no need to sync. 
                        continue
                    if do_animation == "double":
                        self.animation_double(0)
                        time.sleep(0.5)
                        self.animation_double(1)
                        time.sleep(0.5)

                    if do_animation == "local_pushed":
                        self.animation_local_pushed(0)
                        time.sleep(0.25)
                        self.animation_local_pushed(1)
                        time.sleep(0.25)
                        self.animation_local_pushed(0)
                        time.sleep(0.25)
                        self.animation_local_pushed(1)
                        time.sleep(0.25)

                    if do_animation == "other_pushed":
                        self.animation_other_pushed(0)
                        time.sleep(0.25)
                        self.animation_other_pushed(1)
                        time.sleep(0.25)
                        self.animation_other_pushed(0)
                        time.sleep(0.25)
                        self.animation_other_pushed(1)
                        time.sleep(0.25)

class Phase_Invitee(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.set_phase = parent_ref.set_phase
        self.trade_role = parent_ref.trade_role
        self.add_to_parent_queue = parent_ref.add_to_queue
        self.get_trading_partner = parent_ref.get_trading_partner
        self.get_trade_initiated = parent_ref.get_trade_initiated
        self.set_trade_initiated = parent_ref.set_trade_initiated
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.trading_partner = None
        self.set_trade_initiated(False)
        self.timeout_limit = 10
        self.trueque_button_pressed = False
        self.add_to_queue("stop", True)
        self.phase_name = phase_names.INVITEE        
        self.start()

    def setup(self):
        self.trade_role = phase_names.INVITEE # this is a hack to preserve role after this phase
        self.trading_partner = self.get_trading_partner(self.game_name)
        #self.add_to_queue("double")
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",True)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",True)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",True)
        self.hosts.hostnames[self.game_name].enable_gameplay()
        #self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
        #self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
        #self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
        #self.hosts.hostnames[self.game_name].enable_izquierda_coil(True)
        #self.hosts.hostnames[self.game_name].enable_derecha_coil(True)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_right", animation)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right", animation)
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("coco")    
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("naranja")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("mango")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("sandia")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("pina")
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("coco",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("naranja",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("mango",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("sandia",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("pina",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("peso",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all",  animation)

    def respond(self, topic, message):
        """
        animations = #"stop"|"double"|"local_pushed"|"other_pushed"
        """
        if topic == "event_pop_left":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                self.pie.target_hit("pop_left")
        if topic == "event_pop_middle":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                self.pie.target_hit("pop_middle")
        if topic == "event_pop_right":
            if message:
                self.increment_score()
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                self.pie.target_hit("pop_right")
        if topic == "event_roll_inner_left":
            if message:
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_roll_inner_right":
            if message:
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_roll_outer_left":
            if message:
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
        if topic == "event_roll_outer_right":
            if message:
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                time.sleep(0.1)
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")

        if topic == "event_slingshot_left":
            if message:
                self.increment_score()
                self.pie.target_hit("sling_left")
                self.pie.target_hit("rollover_left")
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")

        if topic == "event_slingshot_right":
            if message:
                self.increment_score()
                self.pie.target_hit("sling_right")
                self.pie.target_hit("rollover_right")
                self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                
        if topic == "event_spinner":
            if message:
                self.increment_score()
                self.pie.target_hit("spinner")
                self.hosts.hostnames[self.display_name].request_score("c_mezzo")

        if topic == "event_trough_sensor":
            if message:
                self.hosts.hostnames[self.game_name].enable_gameplay()
                #self.hosts.hostnames[self.game_name].disable_gameplay()
                self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
                self.hosts.hostnames[self.game_name].request_button_light_active("trueque",True)
                self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
                self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
                self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)

        if topic == "event_button_trueque":
            """
            animations = #"stop"|"double"|"local_pushed"|"other_pushed"
            """
            if not self.get_trade_initiated(): #only run this once
                self.set_trade_initiated(True)
                self.hosts.hostnames[self.game_name].cmd_lefttube_launch()
                # todo: animation to confirm button push
                if self.trading_partner.get_trade_initiated():
                    #trading
                    self.add_to_queue("stop")
                    self.set_phase(phase_names.TRADE)
                else:
                    #waiting
                    self.trading_partner.add_to_queue("other_pushed", True)
                    #self.add_to_queue("local_pushed")

    def end(self):
        """
        we get here if both invitor and invitee have pressed their trueque buttons 
        """
        pass

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        # "stop"|"double"|"local_pushed"|"other_pushed"
        do_animation = False
        timeout_counter = 0
        while True:
            try:
                topic, message = self.queue.get(timeout=1)
                if topic == "stop":
                    do_animation = topic
                    timeout_counter = 0
                if topic == "double":
                    timeout_counter = 0
                    do_animation = topic
                if topic == "local_pushed":
                    do_animation = topic
                if topic == "other_pushed":
                    do_animation = topic

            except AttributeError:
                pass
            except queue.Empty:
                if do_animation == "stop":
                    time.sleep(0.1)
                else:
                    timeout_counter += 1
                    if timeout_counter >= self.timeout_limit:
                        do_animation = "stop"
                        self.set_phase(phase_names.FAIL)
                        continue
                    if do_animation == "double":
                        pass

                    if do_animation == "local_pushed":
                        pass

                    if do_animation == "other_pushed":
                        pass

class Phase_Trade(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        #self.start()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.set_phase = parent_ref.set_phase
        self.trade_role = parent_ref.trade_role
        self.increment_score = parent_ref.increment_score
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.phase_name = phase_names.TRADE

    def setup(self):
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)
        self.hosts.hostnames[self.game_name].enable_gameplay()
        #self.hosts.hostnames[self.game_name].disable_gameplay()
        self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
        self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
        self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
        self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
        self.hosts.hostnames[self.game_name].enable_derecha_coil(False)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_left", "off")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_right", animation)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right", animation)

        #self.hosts.hostnames[self.carousel_name].request_eject_ball("coco")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("naranja")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("mango")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("sandia")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("pina")
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("coco",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("naranja",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("mango",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("sandia",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("pina",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("peso",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all",  animation)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("all",  "off")





        """
        if self.parent_ref.trade_role == phase_names.INVITOR:
            invitor_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)
            center_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.fruit_name,self.trading_partner.fruit_name)
            invitee_carousel_path = self.carousel_fruits.get_shorter_radial_path(self.trading_partner.fruit_name,self.fruit_name)
            if frame == 0:
                for path_fruit_name in invitor_carousel_path:
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(path_fruit_name, "off")
                for path_fruit_name in center_carousel_path:
                    self.hosts.hostnames["carouselcenter"].cmd_carousel_lights(path_fruit_name, "off")
                for path_fruit_name in invitee_carousel_path:
                    self.hosts.hostnames[self.trading_partner.carousel_name].cmd_carousel_lights(path_fruit_name, "off")
            if frame == 1:
                for path_fruit_name in invitor_carousel_path:
                    self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(path_fruit_name, "on")
                for path_fruit_name in center_carousel_path:
                    self.hosts.hostnames["carouselcenter"].cmd_carousel_lights(path_fruit_name, "on")
                for path_fruit_name in invitee_carousel_path:
                    self.hosts.hostnames[self.trading_partner.carousel_name].cmd_carousel_lights(path_fruit_name, "on")
        """
        # draw path
        # dim lit fruits in local carousel
        # light this_fruit
        # plot path
            # local_carousel this_fruit
            # center carousel, clockwise from local fruit to trading partner fruit.
            # trading partner carousel, counter-clockwise to trading partner self_fruit
        # animate bright light along path
        # 

        self.increment_score(100)
        self.end()
    def respond(self, topic, message):
        pass
    def end(self):
        self.trade_role = "" # this is a hack to preserve role after this phase
        self.set_phase(phase_names.COMIENZA)
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        pass

class Phase_Fail(threading.Thread):
    def __init__(self, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        #self.start()
        self.hosts = parent_ref.hosts
        self.game_name = parent_ref.game_name
        self.display_name = parent_ref.display_name
        self.fruit_name = parent_ref.fruit_name
        self.carousel_name = parent_ref.carousel_name
        self.set_phase = parent_ref.set_phase
        self.decrement_score = parent_ref.decrement_score
        self.update_carousel_lights_to_data = parent_ref.update_carousel_lights_to_data
        self.phase_name = phase_names.FAIL

    def setup(self):
        self.hosts.hostnames[self.game_name].request_button_light_active("izquierda",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("trueque",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("comienza",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("dinero",False)
        self.hosts.hostnames[self.game_name].request_button_light_active("derecha",False)
        self.hosts.hostnames[self.game_name].enable_gameplay()
        #self.hosts.hostnames[self.game_name].disable_gameplay()
        self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
        self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
        self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
        self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
        self.hosts.hostnames[self.game_name].enable_derecha_coil(False)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_left", "off")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_arrow_right", animation)
        self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left", "on")
        #self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right", animation)

        #self.hosts.hostnames[self.carousel_name].request_eject_ball("coco")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("naranja")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("mango")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("sandia")
        #self.hosts.hostnames[self.carousel_name].request_eject_ball("pina")
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("coco",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("naranja",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("mango",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("sandia",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("pina",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("peso",  animation)
        #self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all",  animation)
        self.hosts.hostnames["carouselcenter"].cmd_carousel_lights("all",  "off")
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        time.sleep(0.25)
        self.hosts.hostnames[self.display_name].request_score("f_mezzo")
        point_loss = int(self.score * 0.1)
        self.decrement_score(point_loss)
        self.end()
    def respond(self, topic, message):
        pass
    def end(self):
        self.trade_role = "" # this is a hack to preserve role after this phase
        self.set_phase(phase_names.COMIENZA)
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        pass

###############
### G A M E ###
###############

class Game(threading.Thread):
    """
    There is one instance of this class for each station.
    """
    def __init__(self,fruit_name,hosts,game_name,carousel_name,display_name, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.fruit_name = fruit_name
        self.hosts = hosts
        self.game_name = game_name
        self.carousel_name = carousel_name
        self.display_name = display_name
        self.parent_ref = parent_ref
        self.carousel_fruits = Carousel_Fruits(fruit_name,self.hosts.get_games_with_players)
        self.get_games_missing_other_fruit = parent_ref.get_games_missing_other_fruit
        self.score = 0
        self.ball_in_trough = True
        self.trade_initated = False
        self.pie = Pie(self.game_name, hosts, self.pie_full_handler)
        self.successful_trades = 0
        self.get_trading_partner =  parent_ref.get_trading_partner
        self.get_trade_option = parent_ref.get_trade_option
        self.trade_role = ""
        if self.fruit_name == "coco":
            self.fruit_order = ["coco","naranja","mango","sandia","pina"]
        if self.fruit_name == "naranja":
            self.fruit_order = ["naranja","mango","sandia","pina","coco"]
        if self.fruit_name == "mango":
            self.fruit_order = ["mango","sandia","pina","coco","naranja"]
        if self.fruit_name == "sandia":
            self.fruit_order = ["sandia","pina","coco","naranja","mango"]
        if self.fruit_name == "pina":
            self.fruit_order = ["pina","coco","naranja","mango","sandia"]
        self.current_phase = None
        self.phase_noplayer = Phase_NoPlayer(self)
        self.phase_comienza = Phase_Comienza(self)
        self.phase_pinball = Phase_Pinball(self)
        self.phase_invitor = Phase_Invitor(self)
        self.phase_invitee = Phase_Invitee(self)
        self.phase_trade = Phase_Trade(self)
        self.phase_fail = Phase_Fail(self)
        self.start()

    def get_trade_initiated(self):
        return self.trade_initated

    def set_trade_initiated(self, b):
        self.trade_initated = b

    def set_phase(self, phase_name):
        print("set_phase", self.fruit_name,phase_name)
        if phase_name == phase_names.NOPLAYER:
            self.current_phase = self.phase_noplayer
            self.current_phase.setup()
        if phase_name == phase_names.COMIENZA:
            # workaround for first-time case
            if self.current_phase == None:
                self.current_phase = self.phase_comienza
                self.current_phase.end()
            else:
                self.current_phase = self.phase_comienza
                self.current_phase.setup()
        if phase_name == phase_names.PINBALL:
            self.current_phase = self.phase_pinball
            self.current_phase.setup()
        if phase_name == phase_names.INVITOR:
            self.current_phase = self.phase_invitor
            self.current_phase.setup()
        if phase_name == phase_names.INVITEE:
            self.current_phase = self.phase_invitee
            self.current_phase.setup()
        if phase_name == phase_names.TRADE:
            self.current_phase = self.phase_trade
            self.current_phase.setup()
        if phase_name == phase_names.FAIL:
            self.current_phase = self.phase_fail
            self.current_phase.setup()

    def increment_score(self, increment_value = 1):
        for iterator in range(increment_value):
            self.score += 1
            self.hosts.hostnames[self.display_name].request_number(self.score)
            if self.score % 10 == 0:
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.game_name].barter_mode_score = int(self.score)
            if self.score == 999:
                self.parent_ref.end()
                break

    def decrement_score(self, decrement_value = 1):
        for iterator in range(decrement_value):
            self.score -= 1
            if self.score < 0:
                self.score == 0
            self.hosts.hostnames[self.display_name].request_number(self.score)
            if self.score % 10 == 0:
                self.hosts.hostnames[self.display_name].request_score("f_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.game_name].barter_mode_score = int(self.score)
                
    # todo: update function
    def pie_full_handler(self):
        self.increment_score(25)
        self.carousel_fruits.populate_this_fruit()
        self.update_carousel_lights_to_data()
        #self.increment_decrement_fruits(True)

    def update_carousel_lights_to_data(self, _level_="on"):
        for fruit_name in self.fruit_order:
            level = _level_ if self.carousel_fruits.is_fruit_present(fruit_name) else "off"
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fruit_name,level)

    def animation_fill_carousel(self):
        fname = self.fruit_order[1]
        self.carousel_fruits.add_fruit(fname)
        self.hosts.hostnames[self.display_name].request_score("f_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"low")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"med")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"high")
        time.sleep(0.4)

        fname = self.fruit_order[2]
        self.carousel_fruits.add_fruit(fname)

        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"low")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"med")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"high")
        time.sleep(0.4)

        fname = self.fruit_order[3]
        self.carousel_fruits.add_fruit(fname)
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"low")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"med")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"high")
        time.sleep(0.4)

        fname = self.fruit_order[4]
        self.carousel_fruits.add_fruit(fname)
        self.hosts.hostnames[self.display_name].request_score("g_mezzo")
        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"low")
        time.sleep(0.2)
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"med")
        time.sleep(0.2)
        self.hosts.hostnames[self.display_name].request_score("f_mezzo")
        self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
        self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(fname,"high")
        time.sleep(0.4)
        self.carousel_fruits.add_fruit(self.fruit_order[0])
        self.update_carousel_lights_to_data()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                #print("Game.add_to_queue",topic, message)
                #if topic == "set_phase":
                #    self.set_phase(message)
                if topic == "animation_fill_carousel":
                    self.animation_fill_carousel()
                else:
                    if self.current_phase:
                        self.current_phase.respond(topic, message)

            except queue.Empty:
                pass
                # animation goes here

class Mode_Barter(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        #self.choreography = choreography
        #self.countdown = Countdown(hosts, set_current_mode)
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.mode_timer_limit = 300
        self.invitor = None
        self.invitee = None
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.games_with_players = self.hosts.get_games_with_players()

        self.games = {
            "coco":Game("coco",self.hosts,"pinball1game","carousel1","pinball1display",self),
            "naranja":Game("naranja",self.hosts,"pinball2game","carousel2","pinball2display",self),
            "mango":Game("mango",self.hosts,"pinball3game","carousel3","pinball3display",self),
            "sandia":Game("sandia",self.hosts,"pinball4game","carousel4","pinball4display",self),
            "pina":Game("pina",self.hosts,"pinball5game","carousel5","pinball5display",self)
        }
        self.display_to_game = {
            "pinball1display":self.games["coco"],
            "pinball2display":self.games["naranja"],
            "pinball3display":self.games["mango"],
            "pinball4display":self.games["sandia"],
            "pinball5display":self.games["pina"],
        }
        self.carousel_to_game = {
            "carousel1":self.games["coco"],
            "carousel2":self.games["naranja"],
            "carousel3":self.games["mango"],
            "carousel4":self.games["sandia"],
            "carousel5":self.games["pina"],
        }
        self.pinball_to_game = {
            "pinball1game":self.games["coco"],
            "pinball2game":self.games["naranja"],
            "pinball3game":self.games["mango"],
            "pinball4game":self.games["sandia"],
            "pinball5game":self.games["pina"],
        }
        self.fruit_name_from_pinball_hostname = {
            "pinball1game":"coco",
            "pinball2game":"naranja",
            "pinball3game":"mango",
            "pinball4game":"sandia",
            "pinball5game":"pina",
        }
        self.fruit_to_display = {
            "coco":"pinball1display",
            "naranja":"pinball2display",
            "mango":"pinball3display",
            "sandia":"pinball4display",
            "pina":"pinball15display"
        }
        self.fruit_to_carousel = {
            "coco":"carousel1",
            "naranja":"carousel2",
            "mango":"carousel3",
            "sandia":"carousel4",
            "pina":"carousel5"
        }
        self.fruit_to_pinball = {
            "coco":"pinball1game",
            "naranja":"pinball2game",
            "mango":"pinball3game",
            "sandia":"pinball4game",
            "pina":"pinball15game"
        }
        self.carousel_sequence = [
            ["carouselcenter","serpentine_center_coco","serpentine_center"],
            ["carousel1","serpentine_edge_coco","serpentine_edge"],
            ["carouselcenter","serpentine_center_naranja","serpentine_center"],
            ["carousel2","serpentine_edge_naranja","serpentine_edge"],
            ["carouselcenter","serpentine_center_mango","serpentine_center"],
            ["carousel3","serpentine_edge_mango","serpentine_edge"],
            ["carouselcenter","serpentine_center_sandia","serpentine_center"],
            ["carousel4","serpentine_edge_sandia","serpentine_edge"],
            ["carouselcenter","serpentine_center_pina","serpentine_center"],
            ["carousel5","serpentine_edge_pina","serpentine_edge"]
        ]
        """
        self.routeable_events = [
            "event_button_derecha",
            "event_button_dinero",
            "event_button_izquierda",
            "event_button_trueque",
            "event_pop_left",
            "event_pop_middle",
            "event_pop_right",
            "event_roll_inner_left",
            "event_roll_inner_right",
            "event_roll_outer_left",
            "event_roll_outer_right",
            "event_slingshot_left",
            "event_slingshot_right",
            "event_spinner",
            "event_trough_sensor"
        ]
        """
        self.carousel_sequence_cursor = 0
        self.start()

    def begin(self):
        self.active = True
        self.mode_timer = 0
        self.pinball_hostnames_with_players = self.hosts.get_games_with_players()
        for pinball_hostname in self.pinball_hostnames:
            game_name = self.fruit_name_from_pinball_hostname[pinball_hostname]
            if pinball_hostname in self.pinball_hostnames_with_players:
                self.games[game_name].add_to_queue("animation_fill_carousel", True) 
                self.games[game_name].set_phase(phase_names.COMIENZA)
            else:
                self.games[game_name].set_phase(phase_names.NOPLAYER)

    # todo: how can this be made threadsafe?  It will be called by multiple games at once.
    def get_games_missing_other_fruit(self,other_fruit_name):
        matching_game_names = []
        for pinball_hostname_with_player in self.games_with_players:
            game_ref = self.pinball_to_game[pinball_hostname_with_player]
            if not game_ref.carousel_fruits.is_fruit_present(other_fruit_name):
                matching_game_names.append(game_ref.fruit_name)
        return matching_game_names

    def get_game_states(self):
        game_states = {}
        for game_fruit_name, game_ref in self.games.items():
            game_states[game_fruit_name] = game_ref.current_phase.phase_name
        return game_states

    def get_traders(self):
        traders = []
        states = self.get_game_states()
        for game_fruit_name, state in states.items():
            if state in [phase_names.INVITEE, phase_names.INVITOR, phase_names.TRADE, phase_names.FAIL]:
                traders.append(game_fruit_name)
        return traders

    def get_trading_partner(self, known_partner):
        traders = self.get_traders()
        # we expect traders have a length of zero or two 
        if len(traders) in [0,2]:
            if len(traders) == 0:
                return ""
            else:
                if known_partner in traders:
                    return traders.remove(known_partner)
                else:
                    print("get_trading_partner reports bad match for known_partner:", known_partner,traders)
        else: 
            print("get_trading_partner reports nonsensical number of traders:", traders)

    def get_trade_option(self, potential_invitor, potential_intitee_fruit_names):
        # are no trades currently happening?
        if len(self.get_traders()) > 0:
            return phase_names.COMIENZA
        # loop through all games
        matching_invitees = []
        for fruit_name, potential_intitee_game_ref in self.games.items():
            if fruit_name in potential_intitee_fruit_names:
                # does potential_invitee have potential_invitee.this_fruit?
                if not potential_intitee_game_ref.carousel_fruits.is_fruit_present(potential_intitee_game_ref.fruit_name):
                    return phase_names.COMIENZA
                # is potential_invitee missing potential_invitor.this_fruit?
                if not potential_intitee_game_ref.carousel_fruits.is_fruit_present(potential_invitor.fruit_name):
                    # this is a match
                    matching_invitees.append(potential_intitee_game_ref)
        if len(matching_invitees) == 0:
            return phase_names.COMIENZA
        if len(matching_invitees) == 1:
            invitee = matching_invitees[0]
        else:
            invitee = random.choice(other_stations_with_fruit)
        self.invitor = potential_invitor 
        self.invitee = invitee
        invitee.set_phase(phase_names.INVITEE)
        return phase_names.INVITOR

    def end(self):
        self.active = False

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        time.sleep(5)
        while True:
            try:
                topic, message, origin, destination = self.queue.get(timeout=1)
                #print("mode_barter.py Mode_Barter.run",topic, message, origin, destination)
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')

                self.pinball_to_game[origin].add_to_queue(topic, message)

            except AttributeError:
                pass
            except queue.Empty:
                if self.active:
                    self.mode_timer += 1
                    if self.mode_timer >= self.mode_timer_limit:
                        self.active = False
                        self.set_current_mode(self.game_mode_names.MONEY_MODE_INTRO)
                        self.end()
