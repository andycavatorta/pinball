"""






"""
import codecs
import os
import queue
import random
import settings
import threading
import time

"""
class Matrix(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

"""

class states:
    NO_PLAYER = "NO_PLAYER"
    TRADE_NOT_NEEDED = "TRADE_NOT_NEEDED"
    TRADE_NEEDED_BALL_IN_TROUGH = "TRADE_NEEDED_BALL_IN_TROUGH"
    TRADE_NEEDED_BALL_IN_PLAY = "TRADE_NEEDED_BALL_IN_PLAY"
    TRADE_INITIATOR_START_TRADE = "TRADE_INITIATOR_START_TRADE"
    TRADE_INITIATOR_IGNORED = "TRADE_INITIATOR_IGNORED"
    TRADE_RESPONDER_IGNORES = "TRADE_RESPONDER_IGNORES"
    TRADE_RESPONDER_START_TRADE = "TRADE_RESPONDER_START_TRADE"
    TRADE_SUCCEEDED = "TRADE_SUCCEEDED"

class trade_roles:
    INITIATOR = "initiator"
    RESPONDER = "responder"
    NONE = "none"

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

class Game(threading.Thread):
    def __init__(self,hosts,game_name,carousel_name,display_name):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()

        self.hosts = hosts
        self.game_name = game_name
        self.carousel_name = carousel_name
        self.display_name = display_name
        self.state = states.NO_PLAYER # default overwritten after creation
        self.score = 0
        self.trade_initated = False
        self.trade_role = trade_roles.NONE # is this redundant?  is this not inferred in state?
        self.pie = Pie(self.game_name, hosts, self.pie_full_handler)
        """
        todo: create animation cycles for each state and system to switch between them simply
            same as animation with counter?
                counter that may reset for cycles or may timeout and end state?
        what kinda data is received? 
        are these methods about 

        """
        self.start()

    def pie_full_handler(self):
        # increment score
        self.score += 100
        if self.score > 999:
            self.score = 999
            # to do: transition to next mode
        # update score
        self.hosts.hostnames[self.display_name].request_number(self.score)
        # alert matrix with new score
        # to do: alert matrix

    def transition_to_state(self, state_name):
        print(1, self.game_name, state_name)
        if state_name == states.NO_PLAYER:
            """
            game is inactive because no player pressed comienza button during previous modes
            This state does not end until the game restarts
            """
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False)
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False)
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False) # also initiate trade
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)   
            #light animation:
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all","off")
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("all","off")
            #chimes:# all off
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
            self.hosts.hostnames[self.display_name].request_number(0)

            #next state: n/a until attraction or countdown modes

        if state_name == states.TRADE_NOT_NEEDED:
            """
            Regular pinball gameplay.
            Next states:
                TRADE_NEEDED_BALL_IN_TROUGH : if ball in trough, local game has enough fruits to trade, and other game has enough fruits to trade
                TRADE_NEEDED_BALL_IN_PLAY : if local game has enough to trade and other game enters TRADE_NEEDED_BALL_IN_TROUGH state
            """
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left","off")
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off")
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", True) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", True) # to do: logical way to communicate state in which comienza button as reacting to inductive sensor
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", True) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(True)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(True)
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(True)

            #light animation:
            # the pie
            # the collected fruits
            #chimes:
                # game reactions
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
                # score

            #next state: 

        if state_name == states.TRADE_NEEDED_BALL_IN_TROUGH:
            """
            gameplay is off.
            player is told their only option is to trade
                how does the animation tell them who they can trade with?
            Next states:
                TRADE_INITIATOR_START_TRADE: if player pushes trueque button first
                TRADE_RESPONDER_START_TRADE: if player pushes trueque button second
                TRADE_RESPONDER_IGNORES : if other player is initiator and local player does not respond before timeout
            """
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","on") # to do: add to blink cycle for this game
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", True) # to do: add to blink cycle for this game
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(True) # also initiate trade
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)            
            #light animation:
                # the pie
                # some kind of carousel blinking
            #chimes:
                # alternating ding between trading partners
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
                # score

        if state_name == states.TRADE_NEEDED_BALL_IN_PLAY:
            """
            gameplay is still on
            player has options to trade and to keep playing
                how does the animation tell them about the trading option?
            Next states:
                TRADE_NEEDED_BALL_IN_TROUGH: if ball enters trough before timeout and before player pushes trueque
                TRADE_INITIATOR_START_TRADE: if player pushes trueque button first
                TRADE_RESPONDER_START_TRADE: if player pushes trueque button second
                TRADE_RESPONDER_IGNORES : if other player is initiator and local player does not respond before timeout
            """
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","on") # to do: add to blink cycle for this game
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", True) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", True) # to do: add to blink cycle for this game
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", True) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(True)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(True) # also initiate trade
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(True)            
            #light animation:
                # the pie
                # some kind of carousel blinking
            #chimes:
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:

        if state_name == states.TRADE_INITIATOR_START_TRADE:
            """
            start acceptance timer.  does this live outside of the two games, in the container for the matrix? animations??
            player has no options while trade request animation plays

            Next states:
                TRADE_INITIATOR_IGNORED : if acceptance timer timeout
                TRADE_SUCCEEDED : if responder transitions out of TRADE_RESPONDER_START_TRADE into TRADE_SUCCEEDED
            """

            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off") # to do: add to blink cycle for this game
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)            
            #light animation:
                # playfield off
                # carousel burst
                # carousel all fruits dim except for one which blinks
                # carousel bright fruit moves through origin carousel to back
                # carousel bright fruit moves through center carousel via longer route to trading partner carousel
                # carousel bright fruit moves through destination carousel to occupy empty spot
                # carousel bright fruit in destination carousel blinks in time with trueque button and lower-right sign
            #chimes:
                # ascending musical theme based on number of steps
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
                # score

        if state_name == states.TRADE_INITIATOR_IGNORED:
            """
            short state that times out after animation and reduction of score
            Next states:
                TRADE_NOT_NEEDED
            """
            #signs:
                # none
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)  
            #light animation:
                # playfield off
                # carousel burst
                # carousel bright fruit moves through responder carousel to back
                # carousel bright fruit moves through center carousel via shorter route to initiator carousel
                # carousel bright fruit moves through initiator carousel to occupy empty spot
            #chimes:
                # disappointment theme
            #phrase:
                # trueque
            #numbers:
                # score decreased decrementally during animation

        if state_name == states.TRADE_RESPONDER_IGNORES:
            """
            if the resonder does not respond for timeout
            short state that times out after animation and reduction of score
            Next states:
                TRADE_NOT_NEEDED
            """
            #signs:
                # none
            #button lights:
                #izquierda: off
                #trueque: off
                #comienza: off
                #dinero: off
                #derecho: off
            #button actions:
                #izquierda: off
                #trueque: off
                #comienza: off
                #dinero: off
                #derecho: off
            #light animation:
                # playfield off
                # carousel burst
                # carousel bright fruit moves through responder carousel to back
                # carousel bright fruit moves through center carousel via shorter route to initiator carousel
                # carousel bright fruit moves through initiator carousel to occupy empty spot
            #chimes:
                # disappointment theme
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
                # score decreased decrementally during animation

        if state_name == states.TRADE_RESPONDER_START_TRADE:
            """
            short state that times out after animation and increase of score
            Next states:
                TRADE_NOT_NEEDED
            """

            # actions: start acceptance window timer, 

            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off") 
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)  
            #light animation:
                # playfield off
                # carousel burst
                # carousel all fruits dim except for one which blinks
                # carousel bright fruit moves through origin carousel to back
                # carousel bright fruit moves through center carousel via longer route to trading partner carousel
                # carousel bright fruit moves through destination carousel to occupy empty spot
                # carousel bright fruit in destination carousel blinks in time with trueque button and lower-right sign
            #chimes:
                # ascending musical theme based on number of steps
            #phrase:
                # trueque
            #numbers:
                # score

            #actions: change state to TRADE_SUCCEEDED


        if state_name == states.TRADE_SUCCEEDED: # same for initiator and responder
            """
            short state that times out after animation and increase of score
            Next states:
                TRADE_NOT_NEEDED
            """
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off") 
            #button lights:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #button actions:
            self.hosts.hostnames[self.game_name].enable_izquierda_coil(False)
            self.hosts.hostnames[self.game_name].enable_trueque_coil(False)
            self.hosts.hostnames[self.game_name].enable_dinero_coil(False)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
            self.hosts.hostnames[self.game_name].enable_derecha_coil(False)  
            #light animation:
            #chimes:
            #phrase:
            #numbers:

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))


    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                print("mode_barter.py Game.run",topic, message)
                if topic == "event_button_comienza":
                    if self.state == states.NO_PLAYER:
                        # no action
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        # no action
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        # no action
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        # no action
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        # no action
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        # no action
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        # no action
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        # no action
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        # no action
                        pass
                if topic == "event_button_trueque":
                    if self.state == states.NO_PLAYER:
                        # no action
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        # no action
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        # no action
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        # no action
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        # no action
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_left_stack_ball_present":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_left_stack_motion_detected":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_pop_left":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            self.pie.target_hit("pop_left")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            self.pie.target_hit("pop_left")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_pop_middle":
                    print(">>> event_pop_middle 1", self.state, message)
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        print(">>> event_pop_middle 2", self.state, message)
                        if message:
                            print(">>> event_pop_middle 4", self.state, message)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            self.pie.target_hit("pop_middle")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            self.pie.target_hit("pop_middle")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_pop_right":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                            self.pie.target_hit("pop_right")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                            self.pie.target_hit("pop_right")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_right_stack_ball_present":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_right_stack_motion_detected":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_roll_inner_left":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("rollover_left")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")

                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("rollover_left")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_roll_inner_right":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("rollover_right")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")

                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("rollover_right")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")

                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_roll_outer_left":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
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
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
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
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_roll_outer_right":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
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
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
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
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_slingshot_left":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("sling_left")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("sling_left")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_slingshot_right":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("sling_right")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("sling_right")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_spinner":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("spinner")
                            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("spinner")
                            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "event_trough_sensor":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "response_lefttube_present":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
                        pass
                if topic == "response_rightttube_present":
                    if self.state == states.NO_PLAYER:
                        pass
                    if self.state == states.TRADE_NOT_NEEDED:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        pass
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        pass
                    if self.state == states.TRADE_INITIATOR_START_TRADE:
                        pass
                    if self.state == states.TRADE_INITIATOR_IGNORED:
                        pass
                    if self.state == states.TRADE_RESPONDER_IGNORES:
                        pass
                    if self.state == states.TRADE_RESPONDER_START_TRADE:
                        pass
                    if self.state == states.TRADE_SUCCEEDED:
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
        self.countdown_seconds = 150
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.games = [
            Game(self.hosts,"pinball1game","carousel1","pinball1display"),
            Game(self.hosts,"pinball2game","carousel2","pinball2display"),
            Game(self.hosts,"pinball3game","carousel3","pinball3display"),
            Game(self.hosts,"pinball4game","carousel4","pinball4display"),
            Game(self.hosts,"pinball5game","carousel5","pinball5display")
        ]
        self.display_to_game = {
            "pinball1display":self.games[0],
            "pinball2display":self.games[1],
            "pinball3display":self.games[2],
            "pinball4display":self.games[3],
            "pinball5display":self.games[4],
        }
        self.carousel_to_game = {
            "carousel1":self.games[0],
            "carousel2":self.games[1],
            "carousel3":self.games[2],
            "carousel4":self.games[3],
            "carousel5":self.games[4],
        }
        self.game_to_game = {
            "pinball1game":self.games[0],
            "pinball2game":self.games[1],
            "pinball3game":self.games[2],
            "pinball4game":self.games[3],
            "pinball5game":self.games[4],
        }
        # need system above self.games to keep track of states of trades
        self.start()

    def begin(self):
        self.active = True
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("trueque")
        hostname_lookup = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        for ordinal,game_ref in enumerate(self.games):
            hostname = hostname_lookup[ordinal]
            if hostname in self.hosts.get_games_with_players():
                game_ref.transition_to_state(states.TRADE_NOT_NEEDED)
            else:
                game_ref.transition_to_state(states.NO_PLAYER)

    def end(self):
        self.countdown.end()
        self.active = False

    def event_button_comienza(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_button_comienza",message)

    def event_button_derecha(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_button_derecha",message)

    def event_button_dinero(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_button_dinero",message)

    def event_button_izquierda(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_button_izquierda",message)

    def event_button_trueque(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_button_trueque",message)

    def event_left_stack_ball_present(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_left_stack_ball_present",message)

    def event_left_stack_motion_detected(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_left_stack_motion_detected",message)

    def event_pop_left(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_pop_left",message)

    def event_pop_middle(self, message, origin, destination):
        print("mode_barter.py Mode_Barter.event_pop_middle",message, origin, destination)
        self.game_to_game[origin].add_to_queue("event_pop_middle",message)

    def event_pop_right(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_pop_right",message)

    def event_right_stack_ball_present(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_right_stack_ball_present",message)

    def event_right_stack_motion_detected(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_right_stack_motion_detected",message)

    def event_roll_inner_left(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_roll_inner_left",message)

    def event_roll_inner_right(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_roll_inner_right",message)

    def event_roll_outer_left(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_roll_outer_left",message)

    def event_roll_outer_right(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_roll_outer_right",message)

    def event_slingshot_left(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_slingshot_left",message)

    def event_slingshot_right(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_slingshot_right",message)

    def event_spinner(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_spinner",message)

    def event_trough_sensor(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("event_trough_sensor",message)

    def response_lefttube_present(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("response_lefttube_present",message)

    def response_rightttube_present(self, message, origin, destination):
        self.game_to_game[origin].add_to_queue("response_rightttube_present",message)

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print("mode_barter.py Mode_Barter.run",topic, message, origin, destination)
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
