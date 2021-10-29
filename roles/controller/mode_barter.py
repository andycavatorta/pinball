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
        print("target_hit",target_name)
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

class Game(threading.Thread):
    def __init__(self,fruit_name,hosts,game_name,carousel_name,display_name, parent_ref):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.fruit_name = fruit_name
        self.hosts = hosts
        self.game_name = game_name
        self.carousel_name = carousel_name
        self.display_name = display_name
        self.parent_ref = parent_ref
        self.score = 0
        self.ball_in_trough = True
        self.trade_initated = False
        self.pie = Pie(self.game_name, hosts, self.pie_full_handler)
        self.carousel_fruits = []
        self.successful_trades = 0
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

        """
        todo: create animation cycles for each state and system to switch between them simply
            same as animation with counter?
                counter that may reset for cycles or may timeout and end state?
        what kinda data is received? 
        are these methods about 

        """
        self.start()

    def increment_score(self, increment_value = 1):
        for iterator in range(increment_value):
            self.score += 1
            self.hosts.hostnames[self.display_name].request_number(self.score)
            if self.score % 10 == 0:
                self.hosts.hostnames[self.display_name].request_score("f_piano")
            time.sleep(0.05)
            self.hosts.hostnames[self.game_name].barter_mode_score = int(self.score)
            if self.score == 999:
                self.parent_ref.end()
                break
                
    def pie_full_handler(self):
        self.increment_score(25)
        #self.increment_decrement_fruits(True)

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                print("mode_barter.py Game.run",topic, message)
                if topic == "event_button_trueque":
                    pass
                if topic == "event_left_stack_ball_present":
                    # to be completed in thorough version of game
                    pass
                if topic == "event_left_stack_motion_detected":
                    # to be completed in thorough version of game
                    pass
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
                if topic == "event_right_stack_ball_present":
                    # to be completed in thorough version of game
                    pass
                if topic == "event_right_stack_motion_detected":
                    # to be completed in thorough version of game
                    pass
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
                        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                if topic == "event_slingshot_right":
                    if message:
                        self.increment_score()
                        self.pie.target_hit("sling_right")
                        self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                if topic == "event_spinner":
                    if message:
                        self.increment_score()
                        self.pie.target_hit("spinner")
                        self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                if topic == "event_trough_sensor":
                        pass
                if topic == "response_lefttube_present":
                    # to be completed in thorough version of game
                    pass
                if topic == "response_rightttube_present":
                    # to be completed in thorough version of game
                    pass
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
        self.mode_timer_limit = 120
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]

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
        self.start()

    def begin(self):
        self.active = True
        self.mode_timer = 0

        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("peso","off")
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("inner_circle","on")
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("outer_circle","on")

        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("trueque")
            self.hosts.hostnames[display_hostname].request_number(000)
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_score("c_piano")
            self.hosts.hostnames[display_hostname].request_score("f_piano")
            self.hosts.hostnames[display_hostname].request_score("gsharp_piano")

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].barter_mode_score = 0
            self.hosts.hostnames[pinball_hostname].money_mode_score = 0
            self.pinball_to_game[pinball_hostname].pie.reset_pie()
            self.pinball_to_game[pinball_hostname].score = 0
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", True) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False) 
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", True) 
            self.hosts.hostnames[pinball_hostname].enable_izquierda_coil(True,20)
            self.hosts.hostnames[pinball_hostname].enable_trueque_coil(False) # also initiate trade
            self.hosts.hostnames[pinball_hostname].enable_kicker_coil(True,20)
            self.hosts.hostnames[pinball_hostname].enable_dinero_coil(False)
            self.hosts.hostnames[pinball_hostname].enable_derecha_coil(True,20)
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
            if pinball_hostname in self.hosts.get_games_with_players():
                self.hosts.hostnames[pinball_hostname].cmd_kicker_launch()

    def end(self):
        self.active = False

    def event_button_derecha(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_button_derecha",message)

    def event_button_dinero(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_button_dinero",message)

    def event_button_izquierda(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_button_izquierda",message)

    def event_button_trueque(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_button_trueque",message)

    def event_left_stack_ball_present(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_left_stack_ball_present",message)

    def event_left_stack_motion_detected(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_left_stack_motion_detected",message)

    def event_pop_left(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_pop_left",message)

    def event_pop_middle(self, message, origin, destination):
        print("mode_barter.py Mode_Barter.event_pop_middle",message, origin, destination)
        self.pinball_to_game[origin].add_to_queue("event_pop_middle",message)

    def event_pop_right(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_pop_right",message)

    def event_right_stack_ball_present(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_right_stack_ball_present",message)

    def event_right_stack_motion_detected(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_right_stack_motion_detected",message)

    def event_roll_inner_left(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_roll_inner_left",message)

    def event_roll_inner_right(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_roll_inner_right",message)

    def event_roll_outer_left(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_roll_outer_left",message)

    def event_roll_outer_right(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_roll_outer_right",message)

    def event_slingshot_left(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_slingshot_left",message)

    def event_slingshot_right(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_slingshot_right",message)

    def event_spinner(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_spinner",message)

    def event_trough_sensor(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("event_trough_sensor",message)

    def response_lefttube_present(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("response_lefttube_present",message)

    def response_rightttube_present(self, message, origin, destination):
        self.pinball_to_game[origin].add_to_queue("response_rightttube_present",message)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        time.sleep(5)
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True,1)
                #print("mode_barter.py Mode_Barter.run",topic, message, origin, destination)
                if isinstance(topic, bytes):
                    topic = codecs.decode(topic, 'UTF-8')
                if isinstance(message, bytes):
                    message = codecs.decode(message, 'UTF-8')
                if isinstance(origin, bytes):
                    origin = codecs.decode(origin, 'UTF-8')
                if isinstance(destination, bytes):
                    destination = codecs.decode(destination, 'UTF-8')
                getattr(self,topic)(
                        message, 
                        origin, 
                        destination,
                    )
            except AttributeError:
                pass
            except queue.Empty:
                if self.active:
                    self.mode_timer += 1
                    if self.mode_timer >= self.mode_timer_limit:
                        self.active = False
                        self.set_current_mode(self.game_mode_names.MONEY_MODE_INTRO)
                        self.end()
