"""
This module controls 
    the playfield for each player 
    the commands for sounds and numbers
    the requirements for trading
    exchanges using the exchange matrix
        best to interact with matrix at high level from here
    the countdown
    lights the trueque sign

create abstractions for each station 
"""
import codecs
import os
import queue
import random
import settings
import threading
import time

class Countdown(threading.Thread):
    def __init__(self, hosts, set_current_mode):
        threading.Thread.__init__(self)
        self.hosts = hosts
        self.set_current_mode = set_current_mode
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.counter = 180
        self.active = False
        self.game_mode_names = settings.Game_Modes
        self.start()

    def begin(self):
        self.active = True
        self.counter = 180

    def end(self):
        self.active = False

    def run(self):
        while True:
            if self.active == True:
                for display_hostname in self.display_hostnames:
                    self.hosts.hostnames[display_hostname].request_number(self.counter)
                if self.counter % 10 == 0:
                    for display_hostname in self.display_hostnames:
                        self.hosts.hostnames[display_hostname].request_score("c_piano")
                        self.hosts.hostnames[display_hostname].request_score("f_piano")
                        self.hosts.hostnames[display_hostname].request_score("gsharp_piano")
                self.counter -= 1
                if self.counter <= 0:
                    self.set_current_mode(self.game_mode_names.ATTRACTION)
            time.sleep(1)

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
        if self.pie_segments_triggered[target_name] == False:
            self.pie_segments_triggered[target_name] = True
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_".join(target_name),"on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail".join(target_name),"back_stroke_off")# light segment
            if len([True for k,v in self.pie_segments_triggered.items() if v == True])==8:
                time.sleep(.33)
                self.reset_pie()
                self.pie_full_handler()

    def reset_pie(self):
        for target_name in self.pie_segments_triggered:
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_".join(target_name),"off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail".join(target_name),"back_stroke_on")# light segment

class Station(threading.Thread):
    """
    things that happen:
        collecting and clearing segments

    to do: initialize state of lights, buttons, carousel
    """
    def __init__(self, origin, tb, hosts):
        threading.Thread.__init__(self)
        self.origin = origin
        self.tb = tb
        self.hosts = hosts
        self.queue = queue.Queue()

        #states
        self.trade_required = False
        display_hostname_map = {
            "pinball1game":"pinball1display",
            "pinball2game":"pinball2display",
            "pinball3game":"pinball3display",
            "pinball4game":"pinball4display",
            "pinball5game":"pinball5display",
        }
        self.display_hostname = display_hostname_map[origin]
        self.pie = Pie(origin, hosts, self.pie_full_handler)
        self.start()

    def pie_full_handler(self):
        self.hosts.hostnames[self.origin].cmd_playfield_lights("sign_arrow_left","on")

    # event handlers
    def event_button_comienza(self, message):
        self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.display_hostname].request_score("asharp_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.display_hostname].request_score("c_mezzo")

    def event_button_derecha(self, message):
        pass
        # to do

    def event_button_dinero(self, message):
        pass
        # to do

    def event_button_izquierda(self, message):
        pass
        # to do

    def event_button_trueque(self, message):
        pass
        # to do

    def event_left_stack_ball_present(self, message):
        pass
        # to do

    def event_left_stack_motion_detected(self, message):
        pass
        # to do

    def event_pop_left(self, message):
        if message:
            self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
            self.pie.target_hit("pop_left")

    def event_pop_middle(self, message):
        if message:
            self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
            self.pie.target_hit("pop_middle")

    def event_pop_right(self, message):
        if message:
            self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")
            self.pie.target_hit("pop_right")

    def event_right_stack_ball_present(self, message):
        pass
        # to do

    def event_right_stack_motion_detected(self, message):
        pass
        # to do

    def event_roll_inner_left(self, message):
        if message:
            self.pie.target_hit("rollover_left")
            self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")

    def event_roll_inner_right(self, message):
        if message:
            self.pie.target_hit("rollover_right")
            self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")

    def event_roll_outer_left(self, message):
        if message:
            self.pie.target_hit("rollover_left")
            self.hosts.hostnames[self.display_hostname].request_score("c_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("asharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")

    def event_roll_outer_right(self, message):
        if message:
            self.pie.target_hit("rollover_right")
            self.hosts.hostnames[self.display_hostname].request_score("c_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("asharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("gsharp_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("g_mezzo")
            time.sleep(0.1)
            self.hosts.hostnames[self.display_hostname].request_score("f_mezzo")

    def event_slingshot_left(self, message):
        if message:
            self.pie.target_hit("sling_left")
            self.hosts.hostnames[self.display_hostname].request_score("asharp_mezzo")

    def event_slingshot_right(self, message):
        if message:
            self.pie.target_hit("sling_right")
            self.hosts.hostnames[self.display_hostname].request_score("asharp_mezzo")

    def event_spinner(self, message):
        if message:
            self.pie.target_hit("spinner")
            self.hosts.hostnames[self.display_hostname].request_score("c_mezzo")
                
    def event_trough_sensor(self, message):
        if message: # True or 1
            self.hosts.hostnames[self.origin].request_button_light_active("comienza", True)
        else:
            self.hosts.hostnames[self.origin].request_button_light_active("comienza", False)
        # to do: this is where trades will be triggered

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            topic, message = self.queue.get(True)
            getattr(self,topic)(
                    message
                )

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
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.countdown = Countdown(hosts, set_current_mode)
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.countdown_seconds = 150
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.stations = {
            "pinball1game":Station("pinball1game",self.tb,self.hosts,),
            "pinball2game":Station("pinball2game",self.tb,self.hosts,),
            "pinball3game":Station("pinball3game",self.tb,self.hosts,),
            "pinball4game":Station("pinball4game",self.tb,self.hosts,),
            "pinball5game":Station("pinball5game",self.tb,self.hosts,),
        }
        self.start()

    def begin(self):
        self.active = True
        self.countdown.begin()
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("trueque")
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", True)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", True)
            self.hosts.hostnames[pinball_hostname].enable_gameplay()

    def end(self):
        self.countdown.end()
        self.active = False

    def event_button_comienza(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_button_comienza",message)

    def event_button_derecha(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_button_derecha",message)

    def event_button_dinero(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_button_dinero",message)

    def event_button_izquierda(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_button_izquierda",message)

    def event_button_trueque(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_button_trueque",message)

    def event_left_stack_ball_present(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_left_stack_ball_present",message)

    def event_left_stack_motion_detected(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_left_stack_motion_detected",message)

    def event_pop_left(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_pop_left",message)

    def event_pop_middle(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_pop_middle",message)

    def event_pop_right(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_pop_right",message)

    def event_right_stack_ball_present(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_right_stack_ball_present",message)

    def event_right_stack_motion_detected(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_right_stack_motion_detected",message)

    def event_roll_inner_left(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_roll_inner_left",message)

    def event_roll_inner_right(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_roll_inner_right",message)

    def event_roll_outer_left(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_roll_outer_left",message)

    def event_roll_outer_right(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_roll_outer_right",message)

    def event_slingshot_left(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_slingshot_left",message)

    def event_slingshot_right(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_slingshot_right",message)

    def event_spinner(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_spinner",message)

    def event_trough_sensor(self, message, origin, destination):
        self.stations[origin].add_to_queue("event_trough_sensor",message)

    def response_lefttube_present(self, message, origin, destination):
        self.stations[origin].add_to_queue("response_lefttube_present",message)

    def response_rightttube_present(self, message, origin, destination):
        self.stations[origin].add_to_queue("response_rightttube_present",message)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
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
                    #for display_hostname in self.display_hostnames:
                    #    self.hosts.hostnames[display_hostname].request_number(self.countdown_seconds)
                    #if self.countdown_seconds <= 0:
                    #    self.set_current_mode(self.game_mode_names.MONEY_MODE_INTRO)
                    if self.countdown_seconds % 10 == 0:
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_score("c_mezzo")
                            self.hosts.hostnames[display_hostname].request_score("f_mezzo")
                            self.hosts.hostnames[display_hostname].request_score("gsharp_mezzo")
                    self.countdown_seconds =- 1
