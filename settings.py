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
        "transport":"sliders",
        "horsewheel":"horsewheel"
    }

class Reporting():
    app_name = "amygdala"
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
    github_repo_name = "amygdala"
    branch = "master"

class Roboteq:
    BOARDS = {
        "sliders":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "serial_data_watchdog":0, #miliseconds
            "serial_echo":0, #0 = enabled, 1 is disabled
        },
        "bow":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "serial_data_watchdog":0, #miliseconds
            "serial_echo":0, #0 = enabled, 1 is disabled
        }
    }
    MOTORS = {
        "pitch_slider":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"1",
            "limit_switch_pin":14,
            "limit_switch_direction":-1,
            "limit_end_position":3300000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "bow_position_slider":{
            "mcu_id":"300:1058:3014688:1429493507:540422710",
            "channel":"2",
            "limit_switch_pin":15,
            "limit_switch_direction":-1,
            "limit_end_position":2500000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":3, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "bow_height":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"1",
            "limit_switch_pin":14,
            "limit_switch_direction":1,
            "limit_end_position":400000,
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":1, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":1, # 0-255
            "pid_proportional_gain":1, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        },
        "bow_rotation":{
            "mcu_id":"300:1058:2031663:1429493506:540422710",
            "channel":"2",
            "motor_acceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "motor_deceleration_rate":500, # Min:0, Max:500000, Default: 10000 = 1000.0 RPM/s
            "operating_mode":1, #0: Open-loop,1: Closed-loop speed,2: Closed-loop position relative,3: Closed-loop count position,4: Closed-loop position tracking,5: Torque,6: Closed-loop speed position
            "pid_differential_gain":1, # 0-255
            "pid_integral_gain":10, # 0-255
            "pid_proportional_gain":5, # 0-255
            "encoder_ppr_value":4000,
            # todo: more variable names will be added as needed
        }
    }