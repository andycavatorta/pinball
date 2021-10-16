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
        self.start()

    def check_pie_wholeness(self):
        if all([True for k,v in self.pie_segments_triggered.items() if v == True]):
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
            time.sleep(0.5)
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_left","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_middle","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_right","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_left","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_right","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_sling_left","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_sling_right","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_spinner","off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_left","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_middle","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_right","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_left","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_right","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_sling_left","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_sling_right","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_spinner","stroke_on")# light segment
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_spinner","stroke_on")# light segment
            # blink tu fruta sign
            self.hosts.hostnames[self.origin].cmd_playfield_lights("sign_arrow_left","energize")
            # ring chimes
            self.hosts.hostnames[self.origin].request_score("f_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("g_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("c_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("f_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("g_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
            time.sleep(0.05)
            self.hosts.hostnames[self.origin].request_score("c_mezzo")
            # to do 

    # event handlers
    def event_button_comienza(self, message):
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
        time.sleep(0.1)
        self.hosts.hostnames[self.origin].request_score("c_mezzo")

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
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        if self.pie_segments_triggered["pop_left"] == False:
            self.pie_segments_triggered["pop_left"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_left","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_left","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_pop_middle(self, message):
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        if self.pie_segments_triggered["pop_middle"] == False:
            self.pie_segments_triggered["pop_middle"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_middle","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_middle","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_pop_right(self, message):
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        if self.pie_segments_triggered["pop_right"] == False:
            self.pie_segments_triggered["pop_right"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_pop_right","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_pop_right","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_right_stack_ball_present(self, message):
        pass
        # to do

    def event_right_stack_motion_detected(self, message):
        pass
        # to do

    def event_roll_inner_left(self, message):
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        time.sleep(0.2)
        if self.pie_segments_triggered["rollover_left"] == False:
            self.pie_segments_triggered["rollover_left"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_left","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_left","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_roll_inner_right(self, message):
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        time.sleep(0.2)
        if self.pie_segments_triggered["rollover_right"] == False:
            self.pie_segments_triggered["rollover_right"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_right","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_right","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_roll_outer_left(self, message):
        self.hosts.hostnames[self.origin].request_score("c_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        time.sleep(0.2)
        if self.pie_segments_triggered["rollover_left"] == False:
            self.pie_segments_triggered["rollover_left"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_left","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_left","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_roll_outer_right(self, message):
        self.hosts.hostnames[self.origin].request_score("c_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("gsharp_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("g_mezzo")
        time.sleep(0.2)
        self.hosts.hostnames[self.origin].request_score("f_mezzo")
        time.sleep(0.2)
        if self.pie_segments_triggered["rollover_right"] == False:
            self.pie_segments_triggered["rollover_right"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_rollover_right","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_rollover_right","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_slingshot_left(self, message):
        self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
        if self.pie_segments_triggered["sling_left"] == False:
            self.pie_segments_triggered["sling_left"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_sling_left","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_sling_left","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_slingshot_right(self, message):
        self.hosts.hostnames[self.origin].request_score("asharp_mezzo")
        if self.pie_segments_triggered["sling_right"] == False:
            self.pie_segments_triggered["sling_right"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_sling_right","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_sling_right","back_stroke_off")# light segment
            self.check_pie_wholeness()

    def event_spinner(self, message):
        self.hosts.hostnames[self.origin].request_score("c_mezzo")
        if self.pie_segments_triggered["spinner"] == False:
            self.pie_segments_triggered["spinner"] = True # store state
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_spinner","on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_spinner","back_stroke_off")# light segment
            self.check_pie_wholeness()
                
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

class Mode_Money(threading.Thread):
    """
    This class watches for incoming messages
    Its only action will be to change the current mode
    """
    def __init__(self, tb, hosts, set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.choreography = choreography
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.game_mode_names = settings.Game_Modes
        self.countdown_seconds = 150
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]

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
        self.animation.add_to_queue("begin")
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("trueque")

    def end(self):
        self.active = False
        self.animation.add_to_queue("end")

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
                topic, message, origin, destination = self.queue.get(True, 1)
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
                    for display_hostname in self.display_hostnames:
                        self.hosts.hostnames[display_hostname].request_number(countdown_seconds)
                    if countdown_seconds <= 0:
                        self.set_current_mode(self.game_mode_names.MONEY_MODE_INTRO)
                    if countdown_seconds % 10 == 0:
                        for display_hostname in self.display_hostnames:
                            self.hosts.hostnames[display_hostname].request_score("c_mezzo")
                            self.hosts.hostnames[display_hostname].request_score("f_mezzo")
                            self.hosts.hostnames[display_hostname].request_score("gsharp_mezzo")
                    self.countdown_seconds =- 1
