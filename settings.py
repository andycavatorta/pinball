"""
This file contains the default config data for the reports system

On start-up thirtybirds loads config data.  It loads default configs from config/ unless otherwise specified.  New config data can be loaded dynamically at runtime.

Typical usage example:

from config import reports

foo = ClassFoo(reports.foo_config)

"""

class Roles():
    controller_hostname="feral"
    hosts={
        "controller":"controller",
        #"pinball1lights":"pinball1lights",
        "pinball1game":"pinball1game",
        "pinball1display":"display",
        #"pinball2lights":"pinball2lights",
        "pinball2game":"pinball2game",
        "pinball2display":"display",
        #"pinball3lights":"pinball3lights",
        "pinball3game":"pinball3game",
        "pinball3display":"display",
        #"pinball4lights":"pinball4lights",
        "pinball4game":"pinball4game",
        "pinball4display":"display",
        #"pinball5lights":"pinball5lights",
        "pinball5game":"pinball5game",
        "pinball5display":"display",
        "pinballmatrix":"pinballmatrix"
    }


class Game_Modes:
    WAITING_FOR_CONNECTIONS = "waiting_for_connections"
    ERROR = "error"
    ATTRACTION = "attraction"
    COUNTDOWN = "countdown"
    BARTER_MODE_INTRO = "barter_mode_intro"
    BARTER_MODE = "barter_mode"
    MONEY_MODE_INTRO = "money_mode_intro"
    MONEY_MODE = "money_mode"
    ENDING = "ending"
    RESET = "reset"

class Reporting():
    app_name = "pinball"
    #level = "ERROR" #[DEBUG | INFO | WARNING | ERROR | CRITICAL]
    #log_to_file = True
    #print_to_stdout = True
    publish_to_dash = True
    
    class Status_Types:
        EXCEPTIONS = True
        INITIALIZATIONS = True
        NETWORK_CONNECTIONS = True
        NETWORK_MESSAGES = True
        SYSTEM_STATUS = True
        VERSION_STATUS = True
        ADAPTER_STATUS = True

class Version_Control():
    update_on_start = False
    github_repo_owner = "andycavatorta"
    github_repo_name = "pinball"
    branch = "master"

class Roboteq:
    BOARDS = {
        "carousel1and2":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "serial_data_watchdog":0, #miliseconds
            "serial_echo":0, #0 = enabled, 1 is disabled
        },
        "carousel3and4":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "serial_data_watchdog":0, #miliseconds
            "serial_echo":0, #0 = enabled, 1 is disabled
        },
        "carousel5and6":{
            "mcu_id":"100:1042:107610164:876103217:1124222537",
            "serial_data_watchdog":0, #miliseconds
            "serial_echo":0, #0 = enabled, 1 is disabled
        }
    }
    MOTORS = {
        "carousel_1":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"1",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":1, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":2, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        },
        "carousel_2":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"2",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":2, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":1, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        },
        "carousel_3":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"1",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":2, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":1, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        },
        "carousel_4":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"2",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":2, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":5, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        },
        "carousel_5":{
            "mcu_id":"100:1042:107610164:876103217:1124222537",
            "channel":"1",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":2, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":5, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        },
        "carousel_6":{
            "mcu_id":"100:1042:107610164:876103217:1124222537",
            "channel":"2",
            #"motor_acceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            #"motor_deceleration_rate":600, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            #"pid_differential_gain":2, # 0-255
            #"pid_integral_gain":1, # 0-255
            #"pid_proportional_gain":5, # 0-255
            #"encoder_ppr_value":4096,
            # todo: more variable names will be added as needed
        }
    }

class Display_LED_Mapping:
    shift_reg_mapping = {
            "display_number":  {
                0: {
                    0: {"bit": 0, "shift_register_index": 4},
                    1: {"bit": 2, "shift_register_index": 4},
                    2: {"bit": 1, "shift_register_index": 4},
                    3: {"bit": 3, "shift_register_index": 4},
                    4: {"bit": 4, "shift_register_index": 4},
                    5: {"bit": 5, "shift_register_index": 4},
                    6: {"bit": 6, "shift_register_index": 4},
                    7: {"bit": 7, "shift_register_index": 4},
                    8: {"bit": 0, "shift_register_index": 3},
                    9: {"bit": 1, "shift_register_index": 3}
                },
                1: {
                    0: {"bit": 2, "shift_register_index": 3},
                    1: {"bit": 3, "shift_register_index": 3},
                    2: {"bit": 4, "shift_register_index": 3},
                    3: {"bit": 5, "shift_register_index": 3},
                    4: {"bit": 6, "shift_register_index": 3},
                    5: {"bit": 7, "shift_register_index": 3},
                    6: {"bit": 0, "shift_register_index": 2},
                    7: {"bit": 1, "shift_register_index": 2},
                    8: {"bit": 2, "shift_register_index": 2},
                    9: {"bit": 3, "shift_register_index": 2}
                },
                2: {
                    0: {"bit": 0, "shift_register_index": 1},
                    1: {"bit": 1, "shift_register_index": 1},
                    2: {"bit": 2, "shift_register_index": 1},
                    3: {"bit": 3, "shift_register_index": 1},
                    4: {"bit": 4, "shift_register_index": 1},
                    5: {"bit": 5, "shift_register_index": 1},
                    6: {"bit": 6, "shift_register_index": 1},
                    7: {"bit": 7, "shift_register_index": 1},
                    8: {"bit": 0, "shift_register_index": 0},
                    9: {"bit": 1, "shift_register_index": 0}
                }
            },
            "display_sentence": {
                "countdown": {"bit": 2, "shift_register_index": 4},
                "barter_mode_intro": {"bit": 3, "shift_register_index": 4},
                "barter_mode": {"bit": 4, "shift_register_index": 4},
                "money_mode": {"bit": 5, "shift_register_index": 4},
                "money_mode_intro": {"bit": 6, "shift_register_index": 4}
            }
    }
        