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


class Matrix(threading.Thread):
    """
    this class handles animations in the carousels.  and possiblly a little in playfields
    this class handles most transitions between states transition_to_state()
    """
    def __init__(self, hosts, games):
        class trade_states():
            NO_TRADE = "no_trade"
            TRADE_INITIATED = "trade_initiated"
            TRADE_IGNORED = "trade_ignored"
            TRADE_RECIPROCATED = "trade_reciprocated"
            TRADE_SUCCEEDED = "trade_succeeded"

        threading.Thread.__init__(self)

        self.hosts = hosts
        self.games = games
        self.queue = queue.Queue()
        self.trade_state = trade_states.NO_TRADE
        self.trader_a_ref = None
        self.trader_b_ref = None
        self.initiator = None
        self.responder = None
        self.rejection_countdown = 0 # idling at zero
        self.animation_interval = 0.2
        self.start()

    def reset(self):
        self.trade_state = trade_states.NO_TRADE
        self.trader_a_ref = None
        self.trader_b_ref = None
        self.initiator = None
        self.responder = None
        self.rejection_countdown = 0 # idling at zero

    def find_long_path_around_center_carousel(self, origin_fruit, destination_fruit):
        cw = find_path_around_center_carousel(origin_fruit, destination_fruit, True)
        ccw = find_path_around_center_carousel(origin_fruit, destination_fruit, False)
        if (len(cw)>len(ccw)):
            return cw
        else:
            return ccw

    def find_path_around_center_carousel(self, origin_fruit, destination_fruit, clockwise):
        if clockwise:
            if origin_fruit == "coco":
                if destination_fruit == "naranja":
                    return ["coco", "naranja"]
                if destination_fruit == "mango":
                    return ["coco", "naranja", "mango"]
                if destination_fruit == "sandia":
                    return ["coco", "naranja", "mango","sandia"]
                if destination_fruit == "pina":
                    return ["coco", "naranja", "mango","sandia","pina"]
            if origin_fruit == "naranja":
                if destination_fruit == "mango":
                    return ["naranja","mango"]
                if destination_fruit == "sandia":
                    return ["naranja","mango","sandia"]
                if destination_fruit == "pina":
                    return ["naranja","mango","sandia","pina"]
                if destination_fruit == "coco":
                    return ["naranja","mango","sandia","pina","coco"]
            if origin_fruit == "mango":
                if destination_fruit == "sandia":
                    return ["mango","sandia"]
                if destination_fruit == "pina":
                    return ["mango","sandia","pina"]
                if destination_fruit == "coco":
                    return ["mango","sandia","pina","coco"]
                if destination_fruit == "naranja":
                    return ["mango","sandia","pina","coco","naranja"]
            if origin_fruit == "sandia":
                if destination_fruit == "pina":
                    return ["sandia","pina"]
                if destination_fruit == "coco":
                    return ["sandia","pina","coco"]
                if destination_fruit == "naranja":
                    return ["sandia","pina","coco","naranja"]
                if destination_fruit == "mango":
                    return ["sandia","pina","coco","naranja","mango"]
            if origin_fruit == "pina":
                if destination_fruit == "coco":
                    return ["pina","coco"]
                if destination_fruit == "naranja":
                    return ["pina","coco","naranja"]
                if destination_fruit == "mango":
                    return ["pina","coco","naranja","mango"]
                if destination_fruit == "sandia":
                    return ["pina","coco","naranja","mango","sandia"]
        else:
            if origin_fruit == "coco":
                if destination_fruit == "naranja":
                    return ["coco", "naranja"].reverse()
                if destination_fruit == "mango":
                    return ["coco", "naranja", "mango"].reverse()
                if destination_fruit == "sandia":
                    return ["coco", "naranja", "mango","sandia"].reverse()
                if destination_fruit == "pina":
                    return ["coco", "naranja", "mango","sandia","pina"].reverse()
            if origin_fruit == "naranja":
                if destination_fruit == "mango":
                    return ["naranja","mango"].reverse()
                if destination_fruit == "sandia":
                    return ["naranja","mango","sandia"].reverse()
                if destination_fruit == "pina":
                    return ["naranja","mango","sandia","pina"].reverse()
                if destination_fruit == "coco":
                    return ["naranja","mango","sandia","pina","coco"].reverse()
            if origin_fruit == "mango":
                if destination_fruit == "sandia":
                    return ["mango","sandia"].reverse()
                if destination_fruit == "pina":
                    return ["mango","sandia","pina"].reverse()
                if destination_fruit == "coco":
                    return ["mango","sandia","pina","coco"].reverse()
                if destination_fruit == "naranja":
                    return ["mango","sandia","pina","coco","naranja"].reverse()
            if origin_fruit == "sandia":
                if destination_fruit == "pina":
                    return ["sandia","pina"].reverse()
                if destination_fruit == "coco":
                    return ["sandia","pina","coco"].reverse()
                if destination_fruit == "naranja":
                    return ["sandia","pina","coco","naranja"].reverse()
                if destination_fruit == "mango":
                    return ["sandia","pina","coco","naranja","mango"].reverse()
            if origin_fruit == "pina":
                if destination_fruit == "coco":
                    return ["pina","coco"].reverse()
                if destination_fruit == "naranja":
                    return ["pina","coco","naranja"].reverse()
                if destination_fruit == "mango":
                    return ["pina","coco","naranja","mango"].reverse()
                if destination_fruit == "sandia":
                    return ["pina","coco","naranja","mango","sandia"].reverse()

    def trade_initiated_animation(self):
        self.rejection_countdown = 50 # 5 seconds
        fruit_path_momentary = []
        fruit_path_after = []
        start_fruits = list(self.initiator.carousel_fruits) # break reference before reversing
        start_fruits.reverse()
        for fruit_name in start_fruits:
            animation_frame = (
                ["cmd_carousel_lights",self.initiator.carousel_name, fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights",self.initiator.carousel_name, fruit_name, "med"]
                )
            fruit_path_after.append(animation_frame)
        center_fruits = self.find_long_path_around_center_carousel(self.initiator.fruit_name, self.responder.fruit_name)
        for fruit_name in center_fruits:
            animation_frame = (
                ["cmd_carousel_lights","carouselcenter", fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights","carouselcenter", fruit_name, "off"]
                )
            fruit_path_after.append(animation_frame)
        end_fruits = list(self.responder.carousel_fruits)
        for fruit_name in end_fruits:
            animation_frame = (
                ["cmd_carousel_lights",self.responder.carousel_name, fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights",self.responder.carousel_name, fruit_name, "med"]
                )
            fruit_path_after.append(animation_frame)
        self.add_to_queue(fruit_path_momentary)
        self.add_to_queue(fruit_path_after)

    def trade_responded_animation(self):
        fruit_path_momentary = []
        fruit_path_after = []
        start_fruits = list(self.responder.carousel_fruits) # break reference before reversing
        start_fruits.reverse()
        for fruit_name in start_fruits:
            animation_frame = (
                ["cmd_carousel_lights",self.responder.carousel_name, fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights",self.responder.carousel_name, fruit_name, "med"]
                )
            fruit_path_after.append(animation_frame)
        center_fruits = self.find_long_path_around_center_carousel(self.responder.fruit_name, self.initiator.fruit_name)
        for fruit_name in center_fruits:
            animation_frame = (
                ["cmd_carousel_lights","carouselcenter", fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights","carouselcenter", fruit_name, "off"]
                )
            fruit_path_after.append(animation_frame)
        end_fruits = list(self.initiator.carousel_fruits)
        for fruit_name in end_fruits:
            animation_frame = (
                ["cmd_carousel_lights",self.initiator.carousel_name, fruit_name, "throb"]
                )
            fruit_path_momentary.append(animation_frame)
            animation_frame = (
                ["cmd_carousel_lights",self.initiator.carousel_name, fruit_name, "med"]
                )
            fruit_path_after.append(animation_frame)
        self.add_to_queue("animation",fruit_path_momentary)
        self.add_to_queue("animation",fruit_path_after)
        self.add_to_queue("transition",[self.initiator, states.TRADE_SUCCEEDED])
        self.add_to_queue("transition",[self.responder, states.TRADE_SUCCEEDED])

    def initiate_trade_if_possible(self, trader_a_ref):
        # if this game has enough fruits to trade. >1? >2?
        if len(trader_a_ref.carousel_fruits) >= 2:
            # find trader_b game with lowest self.successful_trades that is eligible to trade
            trade_candidates = []
            for game_name in self.games:
                game_ref = self.self.games[game_name]
                if game_ref.fruit_name != trader_a_ref.fruit_name: # if these aren't the same
                    if game_ref.state == states.TRADE_NOT_NEEDED: # if this game is in play
                        if len(game_ref.carousel_fruits) >= 2:
                            trade_candidates.append(game_ref)
            if len(trade_candidates) == 0:
                return
            if len(trade_candidates) == 1:
                trader_b_ref = trade_candidates[0]
            if len(trade_candidates) > 1:
                highest_successful_trades = 0
                for trade_candidate in trade_candidates:
                    if trade_candidate.successful_trades > highest_successful_trades:
                        trader_b_ref = trade_candidate
                        highest_successful_trades = trade_candidate.successful_trades
            # it's on
            self.trade_state = trade_states.TRADE_INITIATED
            self.trader_a_ref = trader_a_ref
            self.trader_b_ref = trader_b_ref
            trader_a_ref.transition_to_state(states.TRADE_NEEDED_BALL_IN_TROUGH)
            if trader_b_ref.ball_in_trough: # to do : not thread safe
                trader_b_ref.transition_to_state(states.TRADE_NEEDED_BALL_IN_TROUGH)
            else:
                trader_b_ref.transition_to_state(states.TRADE_NEEDED_BALL_IN_PLAY)

    def initiate_or_respond(self,game_ref):
        # this is where self.initiator and self.responder are assigned, 
        # using trader_a_ref and trader_b_ref to figure figure out who the trading partner is
        if self.initiator == None:
            self.initiator = game_ref
            # is game_ref trader_a_ref or trader_a_ref?
            if game_ref.fruit_name == self.trader_a_ref.fruit_name:
                self.responder = self.trader_b_ref
            else:
                self.responder = self.trader_a_ref
            self.trade_initiated_animation()
        else:
            # game initiator and responder will be set by this point
            self.trade_responded_animation()
    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            topic, message = self.queue.get(True)
            if topic == "animation":
                for frame in message:
                    command, destination_hostname, device, value = frame
                    if command == "cmd_carousel_lights":
                        self.hosts.hostnames[destination_hostname].cmd_carousel_lights(device, value)
                        time.sleep(self.animation_interval)
            if topic == "transition":
                game_ref,state = message
                game_ref.transition_to_state(state)




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
    WINNER = "winner"
    NOT_WINNER = "not_winner"

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
        print("target_hit",target_name)
        if self.pie_segments_triggered[target_name] == False:
            self.pie_segments_triggered[target_name] = True
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_{}".format(target_name),"on")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_{}".format(target_name),"back_stroke_off")# light segment
            if len([True for k,v in self.pie_segments_triggered.items() if v == True])==8:
                time.sleep(.33)
                self.reset_pie()
                self.pie_full_handler()

    def reset_pie(self):
        for target_name in self.pie_segments_triggered:
            self.hosts.hostnames[self.origin].cmd_playfield_lights("pie_{}".format(target_name),"off")# light animation
            self.hosts.hostnames[self.origin].cmd_playfield_lights("trail_{}".format(target_name),"stroke_on")# light segment

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
        self.state = states.NO_PLAYER # default overwritten after creation
        self.score = 0
        self.ball_in_trough = True
        self.trade_initated = False
        self.trade_role = trade_roles.NONE # is this redundant?  is this not inferred in state?
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
            time.sleep(0.01)
            if self.score == 999:
                # to do: transition to states.WINNER and others to states.NOT_WINNER
                break

    def increment_decrement_fruits(self,increment_decrement_bool):
        if len(self.carousel_fruits) > 4:
            return False
        if increment_decrement_bool: # incrementing
            self.carousel_fruits.append(self.fruit_order[len(self.carousel_fruits)])
        else: # decrementing
            self.fruit_name.pop()
        for carousel_fruit_name in self.fruit_order:
            if carousel_fruit_name in  self.carousel_fruits:
                self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(carousel_fruit_name,"med")
            else:
                self.hosts.hostnames[self.carousel_name].cmd_carousel_lights(carousel_fruit_name,"off")
        return True
                
    def pie_full_handler(self):
        self.increment_score(100)
        self.increment_decrement_fruits(True)

    def transition_to_state(self, state_name):
        self.state = state_name
        print("mode_barter.py, Game transition_to_state 0",state_name)
        if state_name == states.NO_PLAYER:
            print("mode_barter.py, Game transition_to_state 1")
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
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("all_radial","off")
            #chimes:# all off
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
            self.hosts.hostnames[self.display_name].request_number(0)

            #next state: n/a until attraction or countdown modes

            print("mode_barter.py, Game transition_to_state 3")
        if state_name == states.TRADE_NOT_NEEDED:
            print("mode_barter.py, Game transition_to_state 4")
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
            self.hosts.hostnames[self.carousel_name].cmd_carousel_lights("all","off")
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("all_radial","off")
            # the pie
            # the collected fruits
            #chimes:
                # game reactions
            #phrase:
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
                # score

            self.pie.reset_pie()
            #next state: 
            print("mode_barter.py, Game transition_to_state 5")

        if state_name == states.TRADE_NEEDED_BALL_IN_TROUGH:
            print("mode_barter.py, Game transition_to_state 6")
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
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
                # score
            print("mode_barter.py, Game transition_to_state 7")

        if state_name == states.TRADE_NEEDED_BALL_IN_PLAY:
            print("mode_barter.py, Game transition_to_state 8")
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
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
            print("mode_barter.py, Game transition_to_state 9")

        if state_name == states.TRADE_INITIATOR_START_TRADE:
            print("mode_barter.py, Game transition_to_state 10")
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
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
                # score
            print("mode_barter.py, Game transition_to_state 11")

        if state_name == states.TRADE_INITIATOR_IGNORED:
            print("mode_barter.py, Game transition_to_state 12")
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
            print("mode_barter.py, Game transition_to_state 13")

        if state_name == states.TRADE_RESPONDER_IGNORES:
            print("mode_barter.py, Game transition_to_state 14")
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
            self.hosts.hostnames[self.display_name].request_phrase("dinero")
            #numbers:
                # score decreased decrementally during animation
            print("mode_barter.py, Game transition_to_state 15")

        if state_name == states.TRADE_RESPONDER_START_TRADE:
            print("mode_barter.py, Game transition_to_state 16")
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
            print("mode_barter.py, Game transition_to_state 17")


        if state_name == states.TRADE_SUCCEEDED: # same for initiator and responder
            print("mode_barter.py, Game transition_to_state 18")
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
            print("mode_barter.py, Game transition_to_state 19")

        if state_name == states.WINNER: # same for initiator and responder
            print("mode_barter.py, Game transition_to_state 20")
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off") 
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left","off") 
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
                #to do: matrix animation
            #chimes:
                #to do: matrix animation
            #phrase:
                # blink?
            #numbers:
                # blink?
            print("mode_barter.py, Game transition_to_state 21")

        if state_name == states.NOT_WINNER: # same for initiator and responder
            print("mode_barter.py, Game transition_to_state 22")
            #signs:
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_right","off") 
            self.hosts.hostnames[self.game_name].cmd_playfield_lights("sign_bottom_left","off") 
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
                #to do: matrix animation
            #chimes:
                #to do: matrix animation
            #phrase:
                # blink?
            #numbers:
                # blink?
            print("mode_barter.py, Game transition_to_state 23")


    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            try:
                topic, message = self.queue.get(True)
                print("mode_barter.py Game.run",topic, message)
                if topic == "event_button_trueque":
                    if self.state == states.TRADE_NEEDED_BALL_IN_TROUGH:
                        self.parent_ref.matrix.initiate_or_respond(self)
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        self.parent_ref.matrix.initiate_or_respond(self)

                if topic == "event_left_stack_ball_present":
                    # to be completed in thorough version of game
                    pass
                if topic == "event_left_stack_motion_detected":
                    # to be completed in thorough version of game
                    pass
                if topic == "event_pop_left":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            self.pie.target_hit("pop_left")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.increment_score()
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            self.pie.target_hit("pop_left")
                if topic == "event_pop_middle":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            self.pie.target_hit("pop_middle")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.increment_score()
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            self.pie.target_hit("pop_middle")
                if topic == "event_pop_right":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                            self.pie.target_hit("pop_right")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
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
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("rollover_left")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")

                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("rollover_left")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                if topic == "event_roll_inner_right":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.pie.target_hit("rollover_right")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")

                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.pie.target_hit("rollover_right")
                            self.hosts.hostnames[self.display_name].request_score("gsharp_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("g_mezzo")
                            time.sleep(0.1)
                            self.hosts.hostnames[self.display_name].request_score("f_mezzo")
                if topic == "event_roll_outer_left":
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
                if topic == "event_roll_outer_right":
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
                if topic == "event_slingshot_left":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("sling_left")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("sling_left")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                if topic == "event_slingshot_right":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("sling_right")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("sling_right")
                            self.hosts.hostnames[self.display_name].request_score("asharp_mezzo")
                if topic == "event_spinner":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("spinner")
                            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                    if self.state == states.TRADE_NEEDED_BALL_IN_PLAY:
                        if message:
                            self.increment_score()
                            self.pie.target_hit("spinner")
                            self.hosts.hostnames[self.display_name].request_score("c_mezzo")
                if topic == "event_trough_sensor":
                    if self.state == states.TRADE_NOT_NEEDED:
                        if message:
                            trade_is_possible = self.parent_ref.matrix.initiate_trade_if_possible(self.game_name)
                            self.ball_in_trough = True
                        else:
                            self.ball_in_trough = False
                        # matrix: initiate_trade_if_possible
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
        self.countdown_seconds = 150
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
        # need system above self.games to keep track of states of trades
        self.matrix = Matrix(self.hosts, self.games)
        self.start()

    def begin(self):
        self.active = True
        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_phrase("dinero")
            self.hosts.hostnames[display_hostname].request_number(000)
        time.sleep(0.2)
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_score("c_piano")
            self.hosts.hostnames[display_hostname].request_score("f_piano")
            self.hosts.hostnames[display_hostname].request_score("gsharp_piano")
        for pinball_hostname in self.pinball_hostnames:
            game_ref = self.pinball_to_game[pinball_hostname]
            if pinball_hostname in self.hosts.get_games_with_players():
                game_ref.transition_to_state(states.TRADE_NOT_NEEDED)
                self.hosts.hostnames[pinball_hostname].cmd_kicker_launch()
            else:
                game_ref.transition_to_state(states.NO_PLAYER)


    def end(self):
        self.countdown.end()
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
