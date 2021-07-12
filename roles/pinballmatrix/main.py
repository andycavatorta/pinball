import importlib
import mido
import os
import queue
import sys
import threading
import time
import traceback

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

import settings
from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.actuators import roboteq_command_wrapper
from thirtybirds3.adapters.sensors.AMT203_encoder import AMT203_absolute_encoder


##################################################
# SAFETY SYSTEMS #
##################################################

# DEADMAN SWITCH ( SEND ANY OUT-OF-BOUNDS VALUES FROM OTHER SYSTEMS)

class Safety_Enable(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()

    def add_to_queue(self, topic, message):
        self.queue.put((topic, message))

    def run(self):
        while True:
            #self.queue.get(True)
            self.tb.publish("deadman", "safe")
            time.sleep(1)

# COMPUTER STATUS CHECK
    # runs on slower rhythm than deadman
    # only log report if there is a problem

# 48V CURRENT METER current_sensor_handler

##################################################
# LOGGING AND REPORTING #
##################################################

# EXCEPTION

# STATUS MESSAGES

# LOCAL LOGGING / ROTATION

##################################################
# MAIN, TB, STATES, AND TOPICS #
##################################################


##########
# STATES #
##########

###################
# HARDWARE SETUP  #
###################

# set up motor controllers
# set up references to motors
# set up proxies for carousels?

class Roboteq_Data_Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.start()

    def add_to_queue(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get(True)
            print("data",message)
            #if "internal_event" in message:
            #    pass
roboteq_data_receiver = Roboteq_Data_Receiver()

class Motor_Controllers(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.controller_names = ["carousel1and2", "carousel3and4","carousel5and6"]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]
        self.chip_select_pins_for_abs_enc = [8,7,18,17,16,5]
        self.ppr = 4096
        self.queue = queue.Queue()
        self.create_controllers_and_motors()
        time.sleep(1)
        #self.set_rel_encoder_position_to_abs_encoder_position()
        #self.home()
        self.start()

    def create_controllers_and_motors(self):
        self.controllers = roboteq_command_wrapper.Controllers(
            roboteq_data_receiver.add_to_queue, 
            self.status_receiver, 
            self.network_status_change_handler, 
            {
                "carousel1and2":settings.Roboteq.BOARDS["carousel1and2"],
                "carousel3and4":settings.Roboteq.BOARDS["carousel3and4"],
                "carousel5and6":settings.Roboteq.BOARDS["carousel5and6"],
            },
            {
                "carousel_1":settings.Roboteq.MOTORS["carousel_1"],
                "carousel_2":settings.Roboteq.MOTORS["carousel_2"],
                "carousel_3":settings.Roboteq.MOTORS["carousel_3"],
                "carousel_4":settings.Roboteq.MOTORS["carousel_4"],
                "carousel_5":settings.Roboteq.MOTORS["carousel_5"],
                "carousel_6":settings.Roboteq.MOTORS["carousel_6"],
            }
        )
        for motor_name_ordinal in enumerate(self.motor_names):
            self.controllers.motors[motor_name_ordinal[1]].absolute_encoder = AMT203_absolute_encoder.AMT203(cs=self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)

    """
    def set_rel_encoder_position_to_abs_encoder_position(self):
        for motor_name in self.motor_names:
            abs_pos = self.controllers.motors[motor_name].absolute_encoder.get_position()
            self.controllers.motors[motor_name].set_encoder_counter(abs_pos)

    def ppr_to_mils(self, ppr):
        return int(((ppr-2048)/2048*1000))

    def mils_to_ppr(self, mils):
        return int(((float(mils)/1000.0)*2048.0)+2048.0)

    def home(self):
        for motor_name in self.motor_names:
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()
            rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            self.controllers.motors[motor_name].go_to_speed_or_relative_position(self.ppr_to_mils(0))
            time.sleep(2)
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()

    def ball_transfer(self, gamestation_a, gamestation_b):
        # start timer_a and timer_b
        # confirm bridges a and b are down
        # turn gamestation_a carousel to receive ball
        # turn gamestation_b carousel to receive ball
        # if gamestation_a and gamestation_b receive balls before time runs out:
            # rotate carousels to bridges
            # confirm carousel positions
            # lift bridges
            # confirm balls are received in central carousel
            # rotate 
        time.sleep(1)
    """

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

main = Motor_Controllers()


################################################
# HARDWARE SEMANTICS (map of callable methods) #
################################################

motor_controller = {
    "carousel1and2":{},
    "carousel3and4":{},
    "carousel5and6":{},
}

motor = {
    "carousel_1":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_2":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_3":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_4":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_5":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_to_barter_tube_position":None,#(fruit_number)
        "rotate_to_money_tube_position":None,#(fruit_number)
        "rotate_to_center":None,#(fruit_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
    "carousel_6":{
        "set_rel_encoder_position":None,#(relative position in encoder pulses)
        "get_rel_encoder_position":None,
        "get_abs_encoder_position":None,
        "rotate_to_position_in_mills":None,#(relative position in mills)
        "rotate_to_position_in_degrees":None,#(relative position in degrees)
        "rotate_to_position_in_pulses":None,#(relative position in encoder pulses)
        "rotate_fruit_number_to_gamestation_number":None,#(fruit_number,gamestation_number)
        "eject_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "detect_ball":None,#(fruit_number) (send messages to carousel pi via controller)
        "lights":{ #(send messages to carousel pi via controller)
            "spinner":None,
            "ripple":None,
            "sparkle":None,
            "fruit_1":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_2":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_3":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_4":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "fruit_5":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
            "dinero":{
                "off":None,
                "on":None,
                "sparkle":None,
                "blink":None
            },
        }
    },
}


#############################################
# ROUTINES (time, events, multiple systems) # 
#############################################



#############################################

# Main handles network send/recv and can see all other classes directly
class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        class States:
            WAITING_FOR_CONNECTIONS = "waiting_for_connections"
        self.states =States()
        self.state = self.states.WAITING_FOR_CONNECTIONS
        self.controller_names = ["carousel1and2", "carousel3and4","carousel5and6"]
        self.motor_names = ["carousel_1","carousel_2","carousel_3","carousel_4","carousel_5","carousel_6"]
        self.chip_select_pins_for_abs_enc = [8,7,18,17,16,5]
        self.ppr = 4096


        # SET UP TB
        self.queue = queue.Queue()
        self.tb = thirtybirds.Thirtybirds(
            settings, 
            app_path,
            self.network_message_handler,
            self.network_status_change_handler,
            self.exception_handler
        )
        self.game_modes = settings.Game_Modes()
        self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
        self.safety_enable = Safety_Enable(self.tb)
        self.tb.subscribe_to_topic("set_game_mode")
        self.tb.subscribe_to_topic("connected")

        #self.create_controllers_and_motors()
        #time.sleep(3)
        #self.set_rel_encoder_position_to_abs_encoder_position()
        #time.sleep(1)
        #self.home()
        self.start()


    def create_controllers_and_motors(self):
        self.controllers = roboteq_command_wrapper.Controllers(
            roboteq_data_receiver.add_to_queue, 
            self.status_receiver, 
            self.network_status_change_handler, 
            {
                "carousel1and2":settings.Roboteq.BOARDS["carousel1and2"],
                "carousel3and4":settings.Roboteq.BOARDS["carousel3and4"],
                "carousel5and6":settings.Roboteq.BOARDS["carousel5and6"],
            },
            {
                "carousel_1":settings.Roboteq.MOTORS["carousel_1"],
                "carousel_2":settings.Roboteq.MOTORS["carousel_2"],
                "carousel_3":settings.Roboteq.MOTORS["carousel_3"],
                "carousel_4":settings.Roboteq.MOTORS["carousel_4"],
                "carousel_5":settings.Roboteq.MOTORS["carousel_5"],
                "carousel_6":settings.Roboteq.MOTORS["carousel_6"],
            }
        )
        for motor_name_ordinal in enumerate(self.motor_names):
            self.controllers.motors[motor_name_ordinal[1]].absolute_encoder = AMT203_absolute_encoder.AMT203(cs=self.chip_select_pins_for_abs_enc[motor_name_ordinal[0]])


    def set_rel_encoder_position_to_abs_encoder_position(self):
        for motor_name in self.motor_names:
            abs_pos = self.controllers.motors[motor_name].absolute_encoder.get_position()
            #rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            #print(motor_name,abs_pos,rel_pos)
            self.controllers.motors[motor_name].set_encoder_counter(abs_pos)
            #rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            #print(motor_name,abs_pos,rel_pos)

    def ppr_to_mils(self, ppr):
        return int(((ppr-2048)/2048*1000))

    def mils_to_ppr(self, mils):
        return int(((float(mils)/1000.0)*2048.0)+2048.0)

    def home(self):
        for motor_name in self.motor_names:
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()
            rel_pos = self.controllers.motors[motor_name].get_encoder_counter_absolute(True)
            self.controllers.motors[motor_name].go_to_speed_or_relative_position(self.ppr_to_mils(0))
            time.sleep(2)
            abs_position = self.controllers.motors[motor_name].absolute_encoder.get_position()

    def ball_transfer(self, gamestation_a, gamestation_b):
        # start timer_a and timer_b
        # confirm bridges a and b are down
        # turn gamestation_a carousel to receive ball
        # turn gamestation_b carousel to receive ball
        # if gamestation_a and gamestation_b receive balls before time runs out:
            # rotate carousels to bridges
            # confirm carousel positions
            # lift bridges
            # confirm balls are received in central carousel
            # rotate 
        time.sleep(1)

    def status_receiver(self, msg):
        print("status_receiver", msg)
    def network_message_handler(self, topic, message, origin, destination):
        self.add_to_queue(topic, message, origin, destination)
    def exception_handler(self, exception):
        print("exception_handler",exception)
    def network_status_change_handler(self, status, hostname):
        print("network_status_change_handler", status, hostname)
    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))
    def set_game_mode(self, mode):
        if mode == self.game_modes.WAITING_FOR_CONNECTIONS:
            print("Mode Attraction")
            self.game_mode = self.game_modes.WAITING_FOR_CONNECTIONS
            pass # peripheral power should be off during this mode
        if mode == self.game_modes.RESET:
            print("Mode : Reset ")
            
            self.game_mode = self.game_modes.RESET
            time.sleep(6)
            self.tb.publish("ready_state",True)
            print("Done with reset, initiating attraction")

        if mode == self.game_modes.ATTRACTION:
            print("Mode Attraction")

            self.game_mode = self.game_modes.ATTRACTION
        # waits for press of start button 
        """
        if mode == self.game_modes.COUNTDOWN:
            #self.player.play("countdown_mode")
        if mode == self.game_modes.BARTER_MODE_INTRO:
            self.player.play("barter_mode_intro")
        if mode == self.game_modes.BARTER_MODE:
            self.player.play("barter_mode")
        if mode == self.game_modes.MONEY_MODE_INTRO:
            self.player.play("money_mode_intro")
        if mode == self.game_modes.MONEY_MODE:
            self.player.play("money_mode")
        if mode == self.game_modes.ENDING:
            self.player.play("closing_theme")
        if mode == self.game_modes.RESET:
            self.player.play("reset")
        if mode == self.game_modes.ERROR:
            pass
        """

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True)
                print(topic, message)
                if topic == b'set_game_mode':
                    self.set_game_mode(message)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
#main = Main()

