"""
this module 
creates organized and simplified access to host actions and properties
creates a local cache of states of hosts
is queried by http_server to provide current states to client
is used by all game_mode modules to provide continuity fo state

hooks for pushing updates maybe go in controller main()

multi-host routines maybe to here in the Controller class.

verbs:
request - send request to host for data
set - store response to request, called by controller.main()
get - return locally stored data
cmd - send command that returns nothing

detect

how real-time and detailed should this data be?
    start lower res and then increase res after verified 

thread safety???
    controller.main().run() writes to these
    game mode modules read from these
    http_server reads from these



        self.send_to_dashboard(
            "update_status",
            [
                hostname, #hostname
                "rpi", # device
                "",#data_name
                dashboard.STATUS_PRESENT if status else dashboard.STATUS_ABSENT
            ]
        )




"""
# native python imports
import codecs
import os
import queue
import sys
import threading
import time

# local module imports
import settings

app_path = os.path.dirname((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.split(app_path)[0])

from thirtybirds3 import thirtybirds
from thirtybirds3.adapters.sensors.ina260 import ina260 

class Host():
    def __init__(self, hostname):
        self.hostname = hostname
        self.connected = False
        self.ready = False
        self.last_deadman = 0 #unix timestamp
        self.queue = queue.Queue
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
    def set_connected(self, connected):
        self.connected = connected
    def get_connected(self):
        return self.connected

    def set_ready(self, ready):
        self.ready = ready
    def get_ready(self, ready):
        return self.ready
    def set_last_deadman(self, last_deadman):
        self.last_deadman = last_deadman
    def get_last_deadman(self, last_deadman):
        return self.last_deadman

    def set_computer_details(self,computer_details):
        self.df = computer_details["df"]
        self.cpu_temp = computer_details["cpu_temp"]
        self.pinball_git_timestamp = computer_details["pinball_git_timestamp"]
        self.tb_git_timestamp = computer_details["tb_git_timestamp"]
    def get_computer_details(self):
        return {
            "df":self.df,
            "cpu_temp":self.cpu_temp,
            "pinball_git_timestamp":self.pinball_git_timestamp,
            "tb_git_timestamp":self.tb_git_timestamp,
        }
    def get_computer_details_received(self):
        if self.df == -1:
            return False
        if self.cpu_temp == -1:
            return False
        if self.pinball_git_timestamp == "":
            return False
        if self.tb_git_timestamp == "":
            return False
        return True




class Controller(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.power_sensor = ina260.INA260()
        self.high_power_enabled = False
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
        #self.start()

    def get_computer_details(self):
        df = self.tb.get_system_disk[0]
        temp = self.tb.get_core_temp
        git_pin = self.tb.app_get_git_timestamp
        git_tb = self.tb.tb_get_git_timestamp
        return {
            "df":[df,df < self.settings.Nominal_Ranges_For_Tests.minimum_disk_free],
            "temp":[temp,temp < self.settings.Nominal_Ranges_For_Tests.maximum_cpu_temperature],
            "git_pin":[git_pin,True],
            "git_tb":[git_tb,True],
        }

    def get_carousels_current(self):
        return self.power_sensor.get_current()

    def detect_carousel_solenoid_stuck_on(self):
        # turn off all solenoid power
        # measure 24v current
        pass

    def detect_carousel_solenoid_stuck_off(self):
        # turn off all solenoid power
        # cycle through carousels
            # cycle through solenoids
                # publish solenoid eject message 
                # minmax = self.carousel_current_sensor.get_min_max_sample(.5)
        pass

    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                # if any system tests return False, stop Safety_Enable, cutting higher power, write to log
                # if any tests do not return before timestamp,, stop Safety_Enable, cutting higher power, write to log
                # if all tests return True before timestamp, 
                    # if inventory_complete == True
                        # transition to settings.Game_Modes.RESET
                    # else
                        # transition to settings.Game_Modes.INVENTORY
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))

class Carousel(Host):
    """
    do matrix values go in here or should they live only in Matrix?
    is a compound class needed that combines matrix, carousels, and tubes?

    carousel_detect_ball
    carousel_eject_ball
    carousel_lights
    """
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
        self.fruit_id = [
            "carousel1",
            "carousel2",
            "carousel3",
            "carousel4",
            "carousel5",
            "carouselcenter"
        ].index(hostname)
        self.current_sensor_present = False
        self.solenoids_present = [
            False,
            False,
            False,
            False,
            False
        ]
        self.balls_present = [
            False,
            False,
            False,
            False,
            False
        ]
        self.light_animation = [ #name of last requested animation
            None,
            None,
            None,
            None,
            None,
            None,
        ]

    def request_computer_details(self):
        self.tb.publish(topic="request_computer_details",message=True,destination=self.hostname)
    def set_computer_details(self,computer_details):
        self.df = computer_details["df"]
        self.cpu_temp = computer_details["cpu_temp"]
        self.pinball_git_timestamp = computer_details["pinball_git_timestamp"]
        self.tb_git_timestamp = computer_details["tb_git_timestamp"]
    def get_computer_details(self):
        return {
            "df":self.df,
            "cpu_temp":self.cpu_temp,
            "pinball_git_timestamp":self.pinball_git_timestamp,
            "tb_git_timestamp":self.tb_git_timestamp,
        }

    def request_current_sensor_present(self):
        self.tb.publish(topic="current_sensor_present",message=True,destination="controller")
    def set_current_sensor_present(self, present):
        self.current_sensor_present= present
    def get_current_sensor_present(self):
        return self.current_sensor_present

    def request_solenoids_present(self):
        self.tb.publish(topic="request_solenoids_present",message=True,destination=self.hostname)
    def set_solenoids_present(self, solenoids_present):
        self.solenoids_present = solenoids_present
    def get_solenoids_present(self):
        return self.solenoids_present

    #no request method for balls_present. event is recurring scan of sensors 
    def set_balls_present(self, balls_present):
        self.balls_present = balls_present
    def get_balls_present(self):
        return self.balls_present

    def request_light_animation(self, fruit_id, animation):
        self.tb.publish(topic="request_light_animation",message=[fruit_id, animation],destination=self.hostname)
        self.light_animation[fruit_id] = animation

    def request_system_tests(self):
        self.tb.publish(topic="request_system_tests",message=True,destination=self.hostname)

    def request_eject_ball(self, fruit_id):
        self.tb.publish(topic="carousel_eject_ball",message=True,destination=self.hostname)


class Display(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
        self.phrases = ("juega","dinero","trueque","como","fue")
        self.current_number = 0
        self.current_phrase_key = "juega"
        self.last_score_name = ""
        self._24v_current = 0
        self.shift_registers_connected = False
        self.current_sensor_present= False
        self.solenoids_present = [
            False,
            False,
            False,
            False,
            False,
        ]
        self.leds_present = {
            "A":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "B":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "C":[
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "words":[
                False,
                False,
                False,
                False,
                False,
            ]
        }
        #self.start()

    def request_computer_details(self):
        self.tb.publish(topic="request_computer_details",message=True,destination=self.hostname)
    def set_computer_details(self,computer_details):
        self.df = computer_details["df"]
        self.cpu_temp = computer_details["cpu_temp"]
        self.pinball_git_timestamp = computer_details["pinball_git_timestamp"]
        self.tb_git_timestamp = computer_details["tb_git_timestamp"]
    def get_computer_details(self):
        return {
            "df":self.df,
            "cpu_temp":self.cpu_temp,
            "pinball_git_timestamp":self.pinball_git_timestamp,
            "tb_git_timestamp":self.tb_git_timestamp,
        }

    def request_current_sensor_present(self):
        self.tb.publish(topic="current_sensor_present",message=True,destination=self.hostname)
    def set_current_sensor_present(self, present):
        self.current_sensor_present= present
    def get_current_sensor_present(self):
        return self.current_sensor_present




    def request_score(self, score_name):
        self.current_score_name = score_name
        self.tb.publish(topic="play_score",message=score_name,destination=self.hostname)
    def get_score(self):
        return self.current_score_name

    def request_phrase(self, phrase_key):
        self.current_phrase_key = phrase_key
        self.tb.publish(topic="set_phrase",message=phrase_key,destination=self.hostname)
    def set_phrase(self,phrase_key): # in case phrase is set through method othe than self.request_phrase
        self.current_phrase_key = phrase_key
    def get_phrase(self):
        return self.current_phrase_key

    def request_number(self, number):
        self.current_number = number
        self.tb.publish(topic="set_number",message=number,destination=self.hostname)
    def set_number(self, number):
        self.current_number = number
    def get_number(self):
        return self.current_number

    def request_system_tests(self):
        self.tb.publish(topic="get_system_tests",message=True,destination=self.hostname)

    def request_leds_present(self):
        self.tb.publish(topic="request_leds_present", message="",destination="pinball1display")
    def set_leds_present(self,leds_present):
        self.leds_present = leds_present
    def get_leds_present(self):
        return self.leds_present

    def request_solenoids_present(self):
        self.tb.publish(topic="request_solenoids_present", message="",destination="pinball1display")
    def set_solenoids_present(self,solenoids_present):
        self.solenoids_present = solenoids_present
    def get_solenoids_present(self):
        return self.solenoids_present

    #methods affecting all displays
    def request_24v_current(self): # request current usage for all displays
        self.tb.publish(topic="request_24v_current", message="",destination="pinball1display")
    def set_24v_current(self,_24v_current):
        self._24v_current = _24v_current
    def get_24v_current(self):
        return self._24v_current

    def request_all_power_off(self):
        self.tb.publish(topic="request_all_power_off",message="")



class Matrix(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.hostname = hostname
        self.tb = tb
        self.df = -1
        self.cpu_temp = -1
        self.pinball_git_timestamp = ""
        self.tb_git_timestamp = ""
        self._24v_current = -1
        self.sdc2160_present = {
            "carousel1and2":False,
            "carousel3and4":False,
            "carousel5and6":False,        
        }
        self.sdc2160_controller_faults = [
            None,None,None,
        ]
        self.sdc2160_channel_faults = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.amt203_present = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.amt203_zeroed = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        self.amt203_absolute_position = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.sdc2160_relative_position = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.sdc2160_closed_loop_error = [
            None,
            None,
            None,
            None,
            None,
            None,
        ]
        self.motors = [
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
            {
                "current":0,
                "temp":0,
                "pid_error":0,
                "status":0,
                "target":0,
                "discrepancy":0
            },
        ]
        self.target_position = [
            0,0,0,0,0,0
        ]
        self.target_position_confirmed = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]
        #self.start()

    def request_computer_details(self):
        self.tb.publish(topic="request_computer_details",message=True,destination=self.hostname)
    def set_computer_details(self,computer_details):
        self.df = computer_details["df"]
        self.cpu_temp = computer_details["cpu_temp"]
        self.pinball_git_timestamp = computer_details["pinball_git_timestamp"]
        self.tb_git_timestamp = computer_details["tb_git_timestamp"]
    def get_computer_details(self):
        return {
            "df":self.df,
            "cpu_temp":self.cpu_temp,
            "pinball_git_timestamp":self.pinball_git_timestamp,
            "tb_git_timestamp":self.tb_git_timestamp,
        }

    def request_24v_current(self): # request current usage for all displays
        self.tb.publish(topic="request_24v_current", message="")
    def set_24v_current(self,_24v_current):
        self._24v_current = _24v_current
    def get_24v_current(self):
        return self._24v_current

    def request_sdc2160_present(self):
        self.tb.publish(topic="request_sdc2160_present", message="")
    def set_sdc2160_present(self,presence):
        self.sdc2160_present = presence
    def get_sdc2160_present(self):
        return all(self.sdc2160_present.values())

    def request_sdc2160_faults(self):
        self.tb.publish(topic="request_sdc2160_faults", message="")
    def set_sdc2160_faults(self,sdc2160_present):
        self.sdc2160_present =sdc2160_present
    def get_sdc2160_faults(self):
        return self.sdc2160_presen_amt203_present

    def request_amt203_present(self):
        self.tb.publish(topic="request_amt203_present", message="")
    def set_amt203_present(self,amt203_present):
        self.amt203_present =amt203_present
    def get_amt203_present(self):
        return all(self.amt203_present)

    def request_amt203_zeroed(self):
        self.tb.publish(topic="request_amt203_zeroed", message="")
    def set_amt203_zeroed(self,amt203_zeroed):
        self.amt203_zeroed =amt203_zeroed
    def get_amt203_zeroed(self):
        return False in self.amt203_zeroed

    #encoder positions are locally scanned and updated by push
    def request_amt203_absolute_position(self, fruit_id):
        self.tb.publish(topic="request_amt203_absolute_position", message="")
    def set_amt203_absolute_position(self, absolute_position, fruit_id=-1):
        if fruit_id == -1 or fruit_id == None:
            self.amt203_absolute_position = absolute_position
        else:
            self.amt203_absolute_position[fruit_id] = absolute_position

    def get_amt203_absolute_position(self, fruit_id):
        return self.amt203_absolute_position[fruit_id]

    def get_amt203_absolute_position_populated(self):
        print("self.amt203_absolute_position",self.amt203_absolute_position)
        print("None in self.amt203_absolute_position=",None in self.amt203_absolute_position)
        if None in self.amt203_absolute_position:
            return False
        return True


    #encoder positions are locally scanned and updated by push
    def request_sdc2160_relative_position(self, fruit_id):
        self.tb.publish(topic="request_sdc2160_relative_position", message="")
    def set_sdc2160_relative_position(self, relative_position, fruit_id = -1):
        if fruit_id == -1:
            self.sdc2160_relative_position = relative_position
        else:
            self.sdc2160_relative_position[fruit_id] = relative_position
    def get_sdc2160_relative_position(self, fruit_id=-1):
        if fruit_id == -1:
            return self.sdc2160_relative_position
        else:
            return self.sdc2160_relative_position[fruit_id]

    def sdc2160_relative_position_populated(self):
        if None in self.sdc2160_relative_position:
            return False
        return True

    def request_motor_details(self, property, fruit_id):
        self.tb.publish(topic="request_motor_details", message=[property, fruit_id])
    def set_motor_details(self, property, fruit_id, value):
        self.motors[fruit_id][property] = value
    def get_motor_details(self, property, fruit_id):
        return self.motors[fruit_id][property]

    def request_sdc2160_controller_faults(self): 
        self.tb.publish(topic="request_sdc2160_controller_faults", message="")
    def set_sdc2160_controller_faults(self,sdc2160_controller_faults):
        self.sdc2160_controller_faults = sdc2160_controller_faults
    def get_sdc2160_controller_faults(self):
        return self.sdc2160_controller_faults
    def sdc2160_controller_faults_populated(self):
        if None in self.sdc2160_controller_faults:
            return False
        return True

    def request_sdc2160_channel_faults(self): 
        self.tb.publish(topic="request_sdc2160_channel_faults", message="")
    def set_sdc2160_channel_faults(self,sdc2160_channel_faults):
        self.sdc2160_channel_faults = sdc2160_channel_faults
    def get_sdc2160_channel_faults(self):
        return self.sdc2160_channel_faults
    def sdc2160_channel_faults_populated(self):
        if None in self.sdc2160_channel_faults:
            return False
        return True

    def request_sdc2160_closed_loop_error(self): 
        self.tb.publish(topic="request_sdc2160_closed_loop_error", message="")
    def set_sdc2160_closed_loop_error(self,sdc2160_closed_loop_error):
        self.sdc2160_closed_loop_error = sdc2160_closed_loop_error
    def get_sdc2160_closed_loop_error(self):
        return self.sdc2160_closed_loop_error
    def sdc2160_closed_loop_error_populated(self):
        if None in self.sdc2160_closed_loop_error:
            return False
        return True


    def cmd_rotate_fruit_to_target(self, fruit_id, degrees):
        self.target_position[fruit_id] = degrees
        self.set_target_position_confirmed(fruit_id,False)
        self.tb.publish(topic="cmd_rotate_fruit_to_target", message=[fruit_id, degrees])

    def request_target_position_confirmed(self): 
        self.tb.publish(topic="request_target_position_confirmed", message="")
    def set_target_position_confirmed(self,fruit_id,state_bool):
        self.target_position_confirmed[fruit_id] = state_bool
    def get_target_position_confirmed(self):
        return self.target_position_confirmed


class Pinball(Host):
    def __init__(self, hostname, tb):
        Host.__init__(self, hostname)
        self.tb = tb
        self._48v_current = -1
        self.left_stack_inventory = -1
        self.right_stack_inventory = -1
        self.gutter_ball_detected = False
        self.barter_points = -1
        self.money_points = -1
        self.current_sensor_present= False
        self.button_active = {
            "izquierda":False,
            "trueque":False,
            "comienza":False,
            "dinero":False,
            "derecha":False,
        }
        #is this list useful here?
        self.playfield_animations = {
            "trail_rollover_right":None,
            "trail_rollover_left":None,
            "trail_sling_right":None,
            "trail_sling_left":None,
            "trail_pop_left":None,
            "trail_pop_right":None,
            "trail_pop_center":None,
            "trail_spinner":None,
            "pie_rollover_right":None,
            "pie_rollover_left":None,
            "pie_sling_right":None,
            "pie_sling_left":None,
            "pie_pop_left":None,
            "pie_pop_right":None,
            "pie_pop_center":None,
            "pie_spinner":None,
            "sign_arrow_left":None,
            "sign_bottom_right":None,
            "sign_top":None,
        }


    def request_current_sensor_present(self):
        self.tb.publish(topic="current_sensor_present",message=True,destination=self.hostname)
    def set_current_sensor_present(self, present):
        self.current_sensor_present= present
    def get_current_sensor_present(self):
        return self.current_sensor_present


    def request_48v_current(self): 
        self.tb.publish(
            topic="request_48v_current", 
            message="",
            destination=self.hostname
        )
    def set_48v_current(self,_48v_current):
        self._48v_current = _48v_current
    def get_48v_current(self):
        return self._48v_current

    def request_left_stack_inventory(self): 
        self.tb.publish(
            topic="request_left_stack_inventory", 
            message="",
            destination=self.hostname
        )
    def set_left_stack_inventory(self,left_stack_inventory):
        self.left_stack_inventory = left_stack_inventory
    def get_left_stack_inventory(self):
        return self.left_stack_inventory

    def request_right_stack_inventory(self): 
        self.tb.publish(
            topic="request_right_stack_inventory", 
            message="",
            destination=self.hostname
        )
    def set_right_stack_inventory(self,right_stack_inventory):
        self.right_stack_inventory = right_stack_inventory
    def get_right_stack_inventory(self):
        return self.right_stack_inventory

    def request_gutter_ball_detected(self): 
        self.tb.publish(
            topic="request_gutter_ball_detected", 
            message="",
            destination=self.hostname
        )
    def set_gutter_ball_detected(self,gutter_ball_detected):
        self.gutter_ball_detected = gutter_ball_detected
    def get_gutter_ball_detected(self):
        return self.gutter_ball_detected

    def request_barter_points(self): 
        self.tb.publish(
            topic="request_barter_points", 
            message="",
            destination=self.hostname
        )
    def set_barter_points(self,barter_points):
        self.barter_points = barter_points
    def get_barter_points(self):
        return self.barter_points

    def request_money_points(self): 
        self.tb.publish(
            topic="request_money_points", 
            message="",
            destination=self.hostname
        )
    def set_money_points(self,money_points):
        self.money_points = money_points
    def get_money_points(self):
        return self.money_points

    def request_button_active(self, button_name, state_bool): 
        self.tb.publish(
            topic="request_request_button_active", 
            message=[button_name, state_bool],
            destination=self.hostname
        )
    def set_button_active(self,button_name, state_bool):
        self.button_active[button_name] = state_bool
    def get_button_active(self):
        return self.button_active[button_name]

    def cmd_gamestation_all_off(self, state_bool):
        self.tb.publish(
            topic="cmd_gamestation_all_off", 
            message=state_bool,
            destination=self.hostname
        )

    def cmd_playfield_lights(self, group, animation):
        self.tb.publish(
            topic="cmd_playfield_lights", 
            message=[group, animation],
            destination=self.hostname
        )

    def cmd_right_stack_launch(self):
        self.tb.publish(
            topic="cmd_right_stack_launch", 
            message=True,
            destination=self.hostname
        )

    def cmd_left_stack_launch(self):
        self.tb.publish(
            topic="cmd_left_stack_launch", 
            message=True,
            destination=self.hostname
        )

    def cmd_gutter_launch(self):
        self.tb.publish(
            topic="cmd_gutter_launch", 
            message=True,
            destination=self.hostname
        )

class All():
    def __init__(self, main):
        self.main = main




    def get_host_connected(self):
        for name in self.main.hostname:
            if name != "controller":
                if self.main.hostname[name].get_connected() == False:
                    return False
        return True

    def request_computer_details(self):
        self.main.tb.publish("request_computer_details",None)

    def get_computer_details_received(self):
        for name in self.main.hostname:
            if name != "controller":
                if self.main.hostname[name].get_computer_details_received() == False:
                    return False
        return True

    def get_current_sensor_present(self):
        return True
        # todo: use real values instead of dummy value
        names = ['carousel1','pinball1display','pinball1game','pinball2game','pinball3game','pinball4game','pinball5game']
        for name in names:
            if self.main.hostname[name].get_current_sensor_present() == False:
                return False

    def get_current_sensor_value(self):
        names = ['carousel1','pinball1display','pinball1game','pinball2game','pinball3game','pinball4game','pinball5game']
        for name in names:
            if self.main.hostname[name].get_current_sensor_value() == False:
                return False

    def get_current_sensor_populated(self):
        return True



class Hosts:
    def __init__(self, tb):
        self.tb = tb
        self.queue = queue.Queue()

        self.controller = Controller("controller", tb)
        self.carousel1 = Carousel("carousel1", tb)
        self.carousel2 = Carousel("carousel2", tb)
        self.carousel3 = Carousel("carousel3", tb)
        self.carousel4 = Carousel("carousel4", tb)
        self.carousel5 = Carousel("carousel5", tb)
        self.carouselcenter = Carousel("carouselcenter", tb)
        self.pinball1display = Display("pinball1display", tb)
        self.pinball2display = Display("pinball2display", tb)
        self.pinball3display = Display("pinball3display", tb)
        self.pinball4display = Display("pinball4display", tb)
        self.pinball5display = Display("pinball5display", tb)
        self.pinball1game = Pinball("pinball1game", tb)
        self.pinball2game = Pinball("pinball2game", tb)
        self.pinball3game = Pinball("pinball3game", tb)
        self.pinball4game = Pinball("pinball4game", tb)
        self.pinball5game = Pinball("pinball5game", tb)
        self.pinballmatrix = Matrix("pinballmatrix", tb)
        self.hostname = {
            'controller':self.controller,
            'carousel1':self.carousel1,
            'carousel2':self.carousel2,
            'carousel3':self.carousel3,
            'carousel4':self.carousel4,
            'carousel5':self.carousel5,
            'carouselcenter':self.carouselcenter,
            'pinball1display':self.pinball1display,
            'pinball2display':self.pinball2display,
            'pinball3display':self.pinball3display,
            'pinball4display':self.pinball4display,
            'pinball5display':self.pinball5display,
            'pinball1game':self.pinball1game,
            'pinball2game':self.pinball2game,
            'pinball3game':self.pinball3game,
            'pinball4game':self.pinball4game,
            'pinball5game':self.pinball5game,
            'pinballmatrix':self.pinballmatrix,
        }
        self.all = All(self)

    def dispatch(self, topic, message, origin, destination):
        if isinstance(topic, bytes):
            topic = codecs.decode(topic, 'UTF-8')
        if isinstance(message, bytes):
            message = codecs.decode(message, 'UTF-8')
        if isinstance(origin, bytes):
            origin = codecs.decode(origin, 'UTF-8')
        if isinstance(destination, bytes):
            destination = codecs.decode(destination, 'UTF-8')
        print("DISPATCH", topic, message, origin, destination)
        #getattr(self,topic)(message, origin, destination)
        if topic == "respond_host_connected":
            self.hostname[origin].set_connected(message)
        if topic == "respond_sdc2160_relative_position":
            # todo: accommodate data format {"fruit_id:x,position:x"}
            self.hostname[origin].set_sdc2160_relative_position(message)
        if topic == "respond_amt203_absolute_position":
            # todo: accommodate data format {"fruit_id:x,position:x"}
            self.hostname[origin].set_amt203_absolute_position(message)
        if topic == "respond_amt203_present":
            self.hostname[origin].set_amt203_present(message)
        if topic == "respond_sdc2160_present":
            self.hostname[origin].set_sdc2160_present(message)
        if topic == "respond_computer_details":
            self.hostname[origin].set_computer_details(message)
        if topic == "respond_sdc2160_controller_faults":
            self.hostname[origin].set_sdc2160_controller_faults(message)
        if topic == "respond_sdc2160_channel_faults":
            self.hostname[origin].set_sdc2160_channel_faults(message)






    """
        self.start()
    def add_to_queue(self, topic, message, origin, destination):
        # if topic=system_tests, update self.hosts[hostname].set_connected() 
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            topic, message, origin, destination = self.queue.get(True)
            print("Hosts.run",topic, message, origin, destination)
    """

    """

    def request_(self): 
        self.tb.publish(topic="request_", message="")
    def set_(self,):
        self. = 
    def get_(self):
        return self.




            self.carousel_measured_position = 0
            self.carousel_target_position = 0
            self.carousel_target_reached = False
            self.carousel_balls = [False,False,False,False,False]

        def get_carousel_measured_position(self, carousel_measured_position):
            return self.carousel_measured_position    
        def set_carousel_measured_position(self, carousel_measured_position):
            self.carousel_measured_position = carousel_measured_position

        def get_carousel_target_position(self, carousel_target_position):
            return self.carousel_target_position    
        def set_carousel_target_position(self, carousel_target_position):
            self.carousel_target_position = carousel_target_position
        def get_carousel_target_reached(self, carousel_target_reached):
            return self.carousel_target_reached    
        def set_carousel_target_reached(self, carousel_target_reached):
            self.carousel_target_reached = carousel_target_reached
        def get_carousel_ball(self, ball_number):
            return self.carousel_ball_1    



        This class choreographs the passing of balls through stacks, carousels, and the pinball matrix.
        actions:
        expire ball to right stack
            0:
            lights for fruit x: energize animation
            1:
            lights for fruit x: blink animation
            sounds: something in sync with blink.  how to do that?
            command motor to rotate so fruit x aligns with right stack
            2: 
            confirm motor position
                if not?
            3: 
            turn on solenoid x for n ms
            sound: loss sound
            4: 
            confirm sensor x reads negative
            rotate carousel so fruit x faces player
            confirm motor position
                if not?

        expire ball to left stack
            0:
            lights for fruit x: energize animation
            1:
            lights for fruit x: blink animation
            sounds: something in sync with blink.  how to do that?
            command motor to rotate so fruit x aligns with left stack
            2: 
            confirm motor position
                if not?
            3: 
            turn on solenoid x for n ms
            sound: loss sound
            4: 
            confirm sensor x reads negative
            rotate carousel so fruit x faces player
            confirm motor position
                if not?

        add money point (transfer ball from left stack to right stack in same game)
            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?
            
        add money point (transfer ball from right stack to left stack in same game)
            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?
            
        trade goods (transfer ball from left stack to self fruit in other game)
            0: 
            player A lights: instructions for trading
            player A lights: trade goods button: blink animation
            player A sound: single-pitch alarm

            player B ball expires when their playfield ball is in the gutter?

            0:
            sound: anticipation sound
            lights: playfield animation?
            lights: self fruit on
            lights: right arrow: energize animaition
            rotate motor: self fruit to right stack
            1: 
            confirm motor position
                if not?
            2: 
            eject ball
            sound: win sound
            lights: self fruit off
            3: 
            rotate motor: self fruit to left stack
            4: 
            confirm motor position
                if not?
            5: 
            launch ball from left stack
            6: 
            sensor: confirm presence of ball
                if not?
            7:
            lights: self fruit on
            8:
            rotate motor: self fruit to center
            9:
            confirm motor position
                if not?

        
        trade money
        trade goods

        inventory and reset routines

        transfer ball from left stack to right stack in different game
        transfer ball from right stack to left stack in different game
        transfer ball from left stack to left stack in different game
        transfer ball from right stack to right stack in different game

        lights?
        sensors?
    """
