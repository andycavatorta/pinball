import importlib
import mido
import os
import queue
import RPi.GPIO as GPIO
import sys
import threading
import time
import json

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds

setting_safety_enable_duration = 1.5
setting_safety_enable_gpio = 5

##################################################
# SAFETY SYSTEMS #
##################################################

class Safety_Enable(threading.Thread):
    def __init__(self, tb, enable_state_change_handler):
        threading.Thread.__init__(self)
        self.enable_state_change_handler = enable_state_change_handler
        GPIO.setmode(GPIO.BCM)
        GPIO.setup( setting_safety_enable_gpio, GPIO.OUT )
        GPIO.output(setting_safety_enable_gpio, GPIO.LOW)
        self.enabled = False # used for detecting when state changes
        self.queue = queue.Queue()
        self.tb = tb
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        self.hosts_alive = set()
        self.start()

    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            """
            time.sleep(setting_safety_enable_duration)
            GPIO.output(setting_safety_enable_gpio, GPIO.HIGH)
            time.sleep(setting_safety_enable_duration)
            GPIO.output(setting_safety_enable_gpio, GPIO.LOW)
            """
            time.sleep(setting_safety_enable_duration)
            try:
                while True:
                    deadman_message = self.queue.get(False)
                    topic, message, origin, destination = deadman_message
                    self.hosts_alive.add(origin)
            except queue.Empty:
                pass
            print(self.hosts_alive)
            missing_hosts = self.required_hosts.difference(self.hosts_alive)
            #if len(missing_hosts) > 0:
            #    print("missing hosts:", self.required_hosts.difference(self.hosts_alive))
            if True:#self.required_hosts.issubset(self.hosts_alive):
                if not self.enabled: # if changing state
                    self.enabled = True
                    GPIO.output(setting_safety_enable_gpio, GPIO.HIGH)
                    self.enable_state_change_handler(self.enabled)
            else:
                if self.enabled: # if changing state
                    self.enabled = False
                    GPIO.output(setting_safety_enable_gpio, GPIO.LOW)
                    self.enable_state_change_handler(self.enabled)
            self.hosts_alive = set()



##################################################
# LOGGING AND REPORTING #
##################################################

# EXCEPTION

# STATUS MESSAGES

# LOCAL LOGGING / ROTATION


##########
# STATES #
##########


class Host_State_Manager():
    def __init__(self, host_state_change_handler):
        self.host_state_change_handler = host_state_change_handler
        self.required_hosts = set(settings.Roles.hosts.keys())
        self.required_hosts.remove("controller")
        self.hosts_alive = set() # hosts responding to heartbeats
        self.hosts_ready = set() # hosts confirming readiness
        #self.start()
    def reset_hosts_alive(self):
        self.hosts_alive = set()
    def add_host_alive(self, hostname):
        self.hosts_alive.add(hostname)
        self.are_all_hosts_alive()
    def remove_host_alive(self, hostname):
        self.hosts_alive.remove(hostname)
        self.are_all_hosts_alive()
    def are_all_hosts_alive(self):
        missing_hosts = self.required_hosts.difference(self.hosts_alive)
        print("Numb of missing hosts : ", len(missing_hosts))
        if len(missing_hosts) == 0:
            self.host_state_change_handler("all_hosts_alive")
        else:
            print(missing_hosts)
            self.host_state_change_handler("missing_hosts")

    def reset_hosts_ready(self):
        self.hosts_ready = set()
    def add_host_ready(self, hostname):
        self.hosts_ready.add(hostname)
        self.are_all_hosts_ready()
    def remove_host_ready(self, hostname):
        self.hosts_ready.remove(hostname)
    def are_all_hosts_ready(self):
        unready_hosts = self.required_hosts.difference(self.hosts_ready)
        print("Current unready hosts : ", len(unready_hosts))
        if len(unready_hosts) == 0:
            print("Found no hosts left starting attraction mode")
            self.host_state_change_handler("all_hosts_ready")

    """
    def set_game_mode(self, game_mode):
        self.game_mode = game_mode
        self.host_state_change_handler(self.game_mode)
    def get_game_mode(self):
        return self.game_mode
    """

class Game_Mode_Manager():
    def __init__(self, tb):
        self.tb = tb
        self.game_modes = settings.Game_Modes
        self.set_game_mode(self.game_modes.WAITING_FOR_CONNECTIONS)

    def get_game_mode(self):
        return self.game_mode

    def set_game_mode(self, game_mode):
        if self.game_mode == game_mode:
            return
        self.game_mode = game_mode
        if self.game_mode == self.game_modes.ERROR:
            pass
            # stop Safety_Enable? 
            # log errors (elsewSafety_Enablehere?)
            # send error message to maintenance
        if self.game_mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            pass
            # send start message to maintenance
            # log start time
            # poll host_state_manager until timeout or until all hosts alive
        if self.game_mode == self.game_modes.SYSTEM_TEST:
            pass
            # request system tests from all hosts
            # poll host_state_manager until timeout or until all hosts ready
        if self.game_mode == self.game_modes.INVENTORY:
            pass
            # NEED TO ENCODE INVENTORY ALGORITHM HERE OR SOMEWHERE
            # UPDATE DISPLAYS TO SHOW COUNT IN TUBE CURRENTLY INVENTORIED
            # thought: shift all balls in one direction until upper limit is detected,
        if self.game_mode == self.game_modes.SHIFT_BALLS_IN_TUBES:
            pass
            # distribute correct number of balls into each tube
            # WRITE SYSTEM FOR BALL EXCHANGES HERE IN CONTROLLER
        if self.game_mode == self.game_modes.ATTRACTION:
            pass
            # send attraction mode messages to all hosts
            # listen for light up start button
        if self.game_mode == self.game_modes.COUNTDOWN:
            pass
            # send COUNTDOWN mode messages to all hosts
        if self.game_mode == self.game_modes.BARTER_MODE_INTRO:
            pass
            # send BARTER_MODE_INTRO mode messages to all hosts
        if self.game_mode == self.game_modes.BARTER_MODE:
            pass
            # send BARTER_MODE mode messages to all hosts
        if self.game_mode == self.game_modes.MONEY_MODE_INTRO:
            pass
            # send MONEY_MODE_INTRO mode messages to all hosts
        if self.game_mode == self.game_modes.MONEY_MODE:
            pass
            # send MONEY_MODE mode messages to all hosts
        if self.game_mode == self.game_modes.ENDING:
            pass
            # send ENDING mode messages to all hosts
        if self.game_mode == self.game_modes.RESET:
            pass
            # IS THIS DIFFERENT FROM SHIFT_BALLS_IN_TUBES?


############
# ROUTINES #
############


class Matrix_Pocket():
    """ just routines related to ball handling """
    def __init__(self):
        self.ball_present = False
    def request_ball_status(self):
        pass
    def receive_ball_status(self, status):
        self.ball_present = status
    def eject_ball(self):
        pass

class Matrix_Carousel():
    """ just routines related to ball handling """
    def __init__(self):
        self.fruits = [
            Matrix_Pocket(0),
            Matrix_Pocket(1),
            Matrix_Pocket(2),
            Matrix_Pocket(3),
            Matrix_Pocket(4),
        ]
    def get_inventory(self):# an accumulation of request_sensor_state
        pass
    def turn_fruit_to_barter_tube(self,fruit_number):
        pass
    def turn_fruit_to_money_tube(self,fruit_number):
        pass
    def turn_fruit_to_center(self, fruit_number):
        pass
    def request_sensor_state(self, fruit_number):
        pass
    def eject_ball(self, fruit_number):
        pass

class Matrix_Tube():
    def __init__(self):
        self.ball_count = -1 # -1 means unknown
    def fire(self):
        pass
    def request_sensor_0_state(self):
        pass
    def request_sensor_16_state(self):
        pass
    def increment_ball_count(self):
        self.ball_count += self.ball_count
    def decrement_ball_count(self):
        self.ball_count -= self.ball_count

class Matrix_Station():
    def __init__(self):
        self.barter_tube = Matrix_tube()
        self.carousel = Matrix_Carousel()
    def pass_ball_from_carousel_to_tube(self, fruit_number, receiving_tube_name):
        if receiving_tube_name == "barter":
            self.carousel.turn_fruit_to_barter_tube(fruit_number)
            # block until finished
            self.carousel.eject_ball(fruit_number, settings.Sound_Motif_Names.LOSS)
            # how to verify? can we scan optical sensors fast enough to catch it passing the upper sensor?
            self.barter_tube.increment_ball_count()
        pass 
    def pass_ball_from_tube_to_carousel(self, source_tube_name, fruit_number):
        pass 
    def pass_ball_between_local_tubes(self, source_tube_name, receiving_tube_name):
        pass 

class Matrix_Modes:
    ERROR = "error"
    AVAILABLE = "available"
    TRADING_GOODS = "trading_goods"
    TRADING_MONEY = "trading_money"
    SETTING_UP_BARTER_MODE = "setting_up_barter_mode"
    SETTING_UP_MONEY_MODE = "setting_up_money_mode"
    PERFORMING_INVENTORY = "performing_inventory"
    EXPIRING_GOODS = "expiring_goods"

class Matrix(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.matrix_stations = [
            Matrix_Station(0),
            Matrix_Station(1),
            Matrix_Station(2),
            Matrix_Station(3),
            Matrix_Station(4),
        ]
        self.center_carousel = Matrix_Carousel()
        self.modes = Matrix_Modes
        self.mode = self.modes.AVAILABLE
        self.start()
    def trade_goods(self, source_fruit_number, destination_fruit_number):
        # source and destination are fruit_numbers
        # this is called AFTER 
        #   both users have goods
        #   two players have agreed to trade goods
        self.mode = self.modes.TRADING_GOODS
        self.matrix_stations[source_fruit_number].pass_ball_from_tube_to_carousel("barter", source_fruit_number)
        # this action will block until verified
        self.matrix_stations[destination_fruit_number].pass_ball_from_tube_to_carousel("barter", destination_fruit_number)
        # this action will block until verified
        self.matrix_stations[source_fruit_number].carousel.turn_fruit_to_center(source_fruit_number)
        # this action will block until verified
        self.matrix_stations[destination_fruit_number].carousel.turn_fruit_to_center(destination_fruit_number)
        # this action will block until verified
        self._pass_ball_from_edge_carousel_to_center_carousel_(source_carousel_fruit_number, source_pocket_fruit_number)
        # this action will block until verified
        self._pass_ball_from_edge_carousel_to_center_carousel_(destination_carousel_fruit_number, destination_pocket_fruit_number)
        # this action will block until verified
        self._pass_ball_from_center_carousel_to_edge_carousel_(source_pocket_fruit_number, destination_carousel_fruit_number)
        # this action will block until verified
        self._pass_ball_from_center_carousel_to_edge_carousel_(destination_pocket_fruit_number, source_carousel_fruit_number)
        # this action will block until verified
        self.mode = self.modes.AVAILABLE
    def trade_money(self, source, destination):
        self.mode = self.modes.TRADING_MONEY
        self.mode = self.modes.AVAILABLE
    def setup_barter_mode(self):
        self.mode = self.modes.SETTING_UP_BARTER_MODE
        
        self.mode = self.modes.AVAILABLE
    def setup_money_mode(self):
        self.mode = self.modes.SETTING_UP_MONEY_MODE
        
        self.mode = self.modes.AVAILABLE
    def perform_inventory(self):
        self.mode = self.modes.PERFORMING_INVENTORY
        
        self.mode = self.modes.AVAILABLE
    def expire_goods(self, station_fruit_number, expired_fruit_number):
        self.mode = self.modes.EXPIRING_GOODS
        self.matrix_stations[station_fruit_number].pass_ball_from_carousel_to_tube(expired_fruit_number, "money")
        self.mode = self.modes.AVAILABLE
    def _pass_ball_from_edge_carousel_to_center_carousel_(self, source_station_fruit_number, pocket_fruit_number):
        pass
    def _pass_ball_from_center_carousel_to_edge_carousel_(self, pocket_fruit_number, destination_station_fruit_number):
        pass



##################################################
# MAIN, TB, STATES, AND TOPICS #
##################################################

# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.game_modes = settings.Game_Modes
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.host_state_manager = Host_State_Manager(self.host_state_change_handler)

        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.safety_enable = Safety_Enable(self.tb, self.enable_state_change_handler)
        self.queue = queue.Queue()
        self.tb.subscribe_to_topic("connected")
        self.tb.subscribe_to_topic("deadman")
        self.tb.subscribe_to_topic("ready_state")
        #self.tb.subscribe_to_topic("game_event")
        #self.tb.subscribe_to_topic("attraction_complete")
        #self.tb.subscribe_to_topic("confirm_countdown")
        #self.tb.subscribe_to_topic("confirm_barter_mode_intro")
        #self.tb.subscribe_to_topic("confirm_barter_mode")
        #self.tb.subscribe_to_topic("confirm_money_mode_intro")
        #self.tb.subscribe_to_topic("confirm_money_mode")
        #self.tb.subscribe_to_topic("confirm_ending")
        #self.pinball_event_to_sound_map = {
        #    "s_left_flipper" :"score",
        #    "s_right_flipper" : "scorex10",
        #    "s_pop_bumper_2" : "note1", 
        #    "s_pop_bumper_3" : "note2", 
        #    "s_pop_bumper_4" : "note3"
        #}
        self.start()

    def enable_state_change_handler(self, enabled):
        print("enable_state_change_handler",enabled)
        #if enabled: # when changing to enabled mode
        #    self.host_state_manager.are_all_hosts_alive()
        #else:
        #    print("+++ handle game_mode change when enable state becomes False")
        #    #self.host_state_manager.set_game_mode(self.game_modes.ERROR)

    def host_state_change_handler(self, host_change):
        print("host_state_change_handler 1", host_change)
        # print('Current game mode is ', self.game_mode)
        if host_change == "missing_hosts":
            self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
            self.tb.publish("set_game_mode",self.game_modes.WAITING_FOR_CONNECTIONS)

        if host_change == "all_hosts_alive":
            # this should happen only game_mode is WAITING_FOR_CONNECTIONS
            if self.game_mode == self.game_modes.WAITING_FOR_CONNECTIONS:
                self.game_mode = self.game_modes.RESET
                self.tb.publish("set_game_mode",self.game_modes.RESET)

        if host_change == "all_hosts_ready":
            print("got correct host change")
            print(self.game_mode)
            # this should happen only game_mode is self.game_modes.RESET
            if self.game_mode == self.game_modes.RESET:
                print("sending message for attraction")
                self.game_mode = self.game_modes.ATTRACTION
                self.tb.publish("set_game_mode",self.game_modes.ATTRACTION)
        if host_change == "start_countdown":
            print('Got a host event to change to count my game mode is ', self.game_mode)
            if self.game_mode == self.game_modes.ATTRACTION:
                print("setting mode to countdown")
                self.game_mode = self.game_modes.COUNTDOWN
                self.tb.publish("set_game_mode",self.game_modes.COUNTDOWN)

        if host_change == "start_barter_mode_intro":
            print('Got a host event to change to count my game mode is ', self.game_mode)
            if self.game_mode == self.game_modes.COUNTDOWN:
                print("setting mode to barter mode intro")
                self.game_mode = self.game_modes.BARTER_MODE_INTRO
                self.tb.publish("set_game_mode",self.game_modes.BARTER_MODE_INTRO)

        if host_change == "start_barter_mode":
            print('Got a host event to change to count my game mode is ', self.game_mode)
            if self.game_mode == self.game_modes.BARTER_MODE_INTRO:
                print("setting mode to barter mode proper")
                self.game_mode = self.game_modes.BARTER_MODE
                self.tb.publish("set_game_mode",self.game_modes.BARTER_MODE)


        if host_change == "start_money_mode_intro":
            print('Got a host event to change to count my game mode is ', self.game_mode)
            if self.game_mode == self.game_modes.BARTER_MODE:
                print("setting mode to money mode intro")
                self.game_mode = self.game_modes.MONEY_MODE_INTRO
                self.tb.publish("set_game_mode",self.game_modes.MONEY_MODE_INTRO)

        if host_change == "start_money_mode":
            if self.game_mode == self.game_modes.MONEY_MODE_INTRO:
                self.game_mode = self.game_modes.MONEY_MODE
                self.tb.publish("set_game_mode",self.game_modes.MONEY_MODE)

        if host_change == "start_ending":
            if self.game_mode == self.game_modes.MONEY_MODE:
                self.game_mode = self.game_modes.ENDING
                self.tb.publish("set_game_mode",self.game_modes.ENDING)
        if host_change == "reset":
            print("Got command for ending game mode is ", self.game_mode)
            if self.game_mode == self.game_modes.ENDING:
                print("resetting")
                self.game_mode = self.game_modes.RESET
                self.tb.publish("set_game_mode",self.game_modes.RESET)

        self.tb.publish("game_mode", self.game_mode)
    
    def handle_game_event(self,topic, message, origin, destination):
        print(">>>",topic, message, origin, destination)
        # print('Got a game event my game mode is ', self.game_mode)
        # If we get any message from the pinball machine in attraction mode, move to countdown

        if self.game_mode == self.game_modes.ATTRACTION:
            print("Currently in attraction and got a new message so triggering countdown")
            self.host_state_change_handler("start_countdown")

        try:

            game_event = json.loads(message)
            if game_event["new_state"] == "active":
                print("got an active for {}".format(game_event["component"]))
                self.tb.publish("sound_event", self.pinball_event_to_sound_map[game_event["component"]])
        except Exception as e:
            print("exception while loading json message from pinball game update", e)


    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
        if status == True:
            self.host_state_manager.add_host_alive(hostname)
        else: # if a host is removed
            self.host_state_manager.remove_host_alive(hostname)


    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                if topic==b"deadman":
                    self.safety_enable.add_to_queue(topic, message, origin, destination)
                if topic==b"ready_state":
                    print("ready state",topic, message, origin, destination)
                    self.host_state_manager.add_host_ready(origin)
                if topic==b"game_event":
                    self.handle_game_event(topic, message, origin, destination)
                if topic==b"gameupdate":
                    self.handle_game_state(topic, message, origin, destination)
                if topic==b"confirm_countdown":
                    self.host_state_change_handler("start_barter_mode_intro")
                if topic==b"confirm_barter_mode_intro":
                    print("Here i got a message for barter mode intro done time for barter mode proper")
                    self.host_state_change_handler("start_barter_mode")
                if topic==b"confirm_barter_mode":
                    print("Here i got a message for barter mode done time for money mode")
                    self.host_state_change_handler("start_money_mode_intro")
                if topic==b"confirm_money_mode_intro":
                    self.host_state_change_handler("start_money_mode")
                if topic==b"confirm_money_mode":
                    self.host_state_change_handler("start_ending")
                if topic==b"confirm_ending":
                    self.host_state_change_handler("reset")


            

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
main = Main()

