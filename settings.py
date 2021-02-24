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
        "feral":"controller",
        "pinball1lights":"pinball1lights",
        "pinball1game":"pinball1game",
        "pinball1display":"pinball1display",
        "pinball2lights":"pinball2lights",
        "pinball2game":"pinball2game",
        "pinball2display":"pinball2display",
        "pinball3lights":"pinball3lights",
        "pinball3game":"pinball3game",
        "pinball3display":"pinball3display",
        "pinball4lights":"pinball4lights",
        "pinball4game":"pinball4game",
        "pinball4display":"pinball4display",
        "pinball5lights":"pinball5lights",
        "pinball5game":"pinball5game",
        "pinball5display":"pinball5display",
        "pinballmatrix":"pinballmatrix"
    }

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
        }
    }
    MOTORS = {
        "carousel_1":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"1",
            "limit_switch_pin":14,
            "limit_switch_direction":-1,
            "limit_end_position":3300000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":2, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "carousel_2":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"2",
            "limit_switch_pin":15,
            "limit_switch_direction":-1,
            "limit_end_position":2500000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":2, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "carousel_3":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"1",
            "limit_switch_pin":14,
            "limit_switch_direction":1,
            "limit_end_position":400000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":2, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "carousel_4":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"2",
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":2, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":10, # 0-255
            "pid_proportional_gain":5, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        }
    }