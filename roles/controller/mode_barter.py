"""






"""
import codecs
import os
import queue
import random
import settings
import threading
import time

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

class Game():

    def __init__(self,hosts,game_name,carousel_name,display_name):
        self.hosts = hosts
        self.game_name = game_name
        self.carousel_name = carousel_name
        self.display_name = display_name
        self.state = self.states.NO_PLAYER # default overwritten after creation
        self.score = 0
        self.trade_initated = False
        self.trade_initated = False

        """
        todo: create animation cycles for each state and system to switch between them simply
            same as animation with counter?
                counter that may reset for cycles or may timeout and end state?
        what kinda data is received? 
        are these methods about 

        """
    def transition_to_state(self, state_name):
        if state_name == states.NO_PLAYER:
            #button lights:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("all","off")
            #button actions:
            self.hosts.hostnames[self.game_name].request_button_light_active("izquierda", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("trueque", False)
            self.hosts.hostnames[self.game_name].request_button_light_active("comienza", False) 
            self.hosts.hostnames[self.game_name].request_button_light_active("dinero", False)
            self.hosts.hostnames[self.game_name].request_button_light_active("derecha", False) 
            #light animation:
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all","off")
            #chimes:# all off
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("trueque")
            #numbers:
            self.hosts.hostnames[self.display_name].request_number(int(self.animation_frame_counter/10))

            #next state: n/a until attraction or countdown modes

        if state_name == states.TRADE_NOT_NEEDED:
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
            self.hosts.hostnames[self.game_name].enable_dinero_coil(True)
            self.hosts.hostnames[self.game_name].enable_kicker_coil(False)
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

            #next state: TRADE_NEEDED_BALL_IN_TROUGH or TRADE_NEEDED_BALL_IN_PLAY

        if state_name == states.TRADE_NEEDED_BALL_IN_TROUGH:
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
            #next state: TRADE_INITIATOR_START_TRADE (trueque button) | TRADE_RESPONDER_START_TRADE (trueque button)| TRADE_RESPONDER_IGNORES (timeout)

        if state_name == states.TRADE_NEEDED_BALL_IN_PLAY:
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
            #next state: TRADE_NEEDED_BALL_IN_TROUGH | TRADE_INITIATOR_START_TRADE (trueque button) | TRADE_RESPONDER_START_TRADE (trueque button)| TRADE_RESPONDER_IGNORES (timeout)

        if state_name == states.TRADE_INITIATOR_START_TRADE:
            # actions: start acceptance window timer, 

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

            #next state: TRADE_INITIATOR_IGNORED (timeout) | TRADE_SUCCEEDED (after responder TRADE_RESPONDER_START_TRADE animation ends)

        if state_name == states.TRADE_INITIATOR_IGNORED:
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

            #actions: change state to TRADE_NOT_NEEDED

        if state_name == states.TRADE_RESPONDER_IGNORES:
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

            #next state: TRADE_NOT_NEEDED

        if state_name == states.TRADE_RESPONDER_START_TRADE:
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


    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True,self.animaition_interval)
                if topic == "event_button_comienza":
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
                if topic == "event_button_derecha":
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
                if topic == "event_button_dinero":
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
                if topic == "event_button_izquierda":
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
                if topic == "event_button_trueque":
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
                if topic == "event_pop_middle":
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
                if topic == "event_pop_right":
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
                if topic == "event_roll_inner_right":
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
                if topic == "event_roll_outer_left":
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
                if topic == "event_roll_outer_right":
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
                if topic == "event_slingshot_left":
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
                if topic == "event_slingshot_right":
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
                if topic == "event_spinner":
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
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].enable_gameplay()
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha", True)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza", True)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque", False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda", True)
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("trueque")
        self.countdown.begin()

    def end(self):
        self.countdown.end()
        self.active = False

    def event_button_comienza(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_button_comienza",message)

    def event_button_derecha(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_button_derecha",message)

    def event_button_dinero(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_button_dinero",message)

    def event_button_izquierda(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_button_izquierda",message)

    def event_button_trueque(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_button_trueque",message)

    def event_left_stack_ball_present(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_left_stack_ball_present",message)

    def event_left_stack_motion_detected(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_left_stack_motion_detected",message)

    def event_pop_left(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_pop_left",message)

    def event_pop_middle(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_pop_middle",message)

    def event_pop_right(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_pop_right",message)

    def event_right_stack_ball_present(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_right_stack_ball_present",message)

    def event_right_stack_motion_detected(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_right_stack_motion_detected",message)

    def event_roll_inner_left(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_roll_inner_left",message)

    def event_roll_inner_right(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_roll_inner_right",message)

    def event_roll_outer_left(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_roll_outer_left",message)

    def event_roll_outer_right(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_roll_outer_right",message)

    def event_slingshot_left(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_slingshot_left",message)

    def event_slingshot_right(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_slingshot_right",message)

    def event_spinner(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_spinner",message)

    def event_trough_sensor(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("event_trough_sensor",message)

    def response_lefttube_present(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("response_lefttube_present",message)

    def response_rightttube_present(self, message, origin, destination):
        self.games[self.game_to_game[origin]].add_to_queue("response_rightttube_present",message)

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
