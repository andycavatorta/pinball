"""
first sketch of inventory algorithm

?? inventory balls in carousels

##### empty the carousels #####

# process outer carousels and adjacent tubes
for each outer carousel
    for ball in carousel
        ?? while left tube is not full
            !! transfer ball into left tube
        ?? while right tube is not full
            !! transfer ball into left tube    
        continue

# process center carousel
for ball in center carousel
    !! transfer ball through outer carousel to nearest available tube
        
# process outer carousel and neighboring tubes 
for each outer carousel with
    locate nearest available tube in adjacent game
    transfer ball to tube in adjacent game

##### empty one tube #####

donor_tube = tubes[9]
try
    transfer ball from donor_tube to donor_tube.nearest_available_tube_right 
except 
    donor_tube.motion_not_detected
    break
except 
    donor_tube.carousel.ball_not_received # what abstraction for the receiving carousel is correct?
    break
# donor_tube is now empty
# donor_tube.ball_count is now known

for tube in tubes[8:0] # counting down from tube 5 right
    donor_tube = tube
    receiver_tube = donor_tube.nearest_available_tube_left
    while True
        try
            transfer ball from donor_tube to donor_tube 
        except 
            # capture case of overfilled receiver tube
            receiver_tube.full
            receiver_tube = donor_tube.nearest_available_tube
            break
        except 
            # donor_tube.motion_not_detected never thrown if static ball is detected in sensor
            # so, filled or overfilled tubes will not throw this exception
            donor_tube.motion_not_detected
            break
        except 
            donor_tube.carousel.ball_not_received # what abstraction for the receiving carousel is correct?
            break
        # donor_tube is now empty
        # donor_tube.ball_count is now known






donor_tube = None
for gamestation in gamestations:
    if gamestation.lefttube.get_empty() and gamestation.righttube.get_empty():
        donor_tube = gamestation.lefttube
            break

# if there was no ideal candidate

if not donor_tube
    for gamestation in gamestations:
        if gamestation.lefttube.get_empty() or gamestation.righttube.get_empty():
            if gamestation.lefttube.get_empty()
                donor_tube = gamestation.lefttube
                break
            else
                donor_tube = gamestation.righttube
                break

while True
    try
        transfer ball from donor_tube to donor_tube.nearest_available_tube 
    except 
        motion_not_detected
        break
    except 
        ball_not_received
        break
record empty state

recipient_tube = donor_tube.breakref() # break reference
donor_tube = donor_tube.get_adjacent_right()









"""
import codecs
import os
import queue
import settings
import threading
import time

class Mode_Inventory(threading.Thread):
    """
    When this system boots, there is no way to know how many balls are in the tubes.  
    This module 
        zeroes the motor positions in the matrix
        performs an inventory of the balls
        moves balls to populate tubes for game

    to do:
        write invenory algorithm
    """
    PHASE_ZERO = "phase_zero"
    PHASE_INVENTORY = "phase_inventory"
    PHASE_POPULATE = "phase_populate"
    def __init__(self, tb, hosts, set_current_mode, choreography):
        threading.Thread.__init__(self)
        self.active = False
        self.tb = tb 
        self.hosts = hosts
        self.choreography = choreography
        self.mode_names = settings.Game_Modes
        self.set_current_mode = set_current_mode
        self.queue = queue.Queue()
        self.pinball_hostnames = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.display_hostnames = ["pinball1display","pinball2display","pinball3display","pinball4display","pinball5display",]
        self.carousel_hostnames = ["carousel1","carousel2","carousel3","carousel4","carousel5","carouselcenter",]
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.phase = self.PHASE_ZERO
        self.start()
        # self.hosts["pinballmatrix"].request_amt203_zeroed()
        # bypass inventory
        #self.set_current_mode(self.game_mode_names.ATTRACTION)

    def begin(self):
        #self.timer = time.time()
        self.active = True
        #skipping zeroing, inventory, and set_balls_for_game
        self.visual_test_cycle()
        self.set_current_mode(self.game_mode_names.ATTRACTION)
        #for pinball_hostname in self.pinball_hostnames:
        #    self.hosts.hostnames[pinball_hostname].disable_gameplay()
        

    def end(self):
        self.active = False

    def visual_test_cycle(self):
        for display_hostname in self.display_hostnames:
            self.hosts.hostnames[display_hostname].request_score("f_piano")
            self.hosts.hostnames[display_hostname].request_number(999)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("f_mezzo")
            self.hosts.hostnames[display_hostname].request_number(888)
            time.sleep(0.5)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("g_piano")
            self.hosts.hostnames[display_hostname].request_number(777)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("g_mezzo")
            self.hosts.hostnames[display_hostname].request_number(666)
            time.sleep(0.5)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("gsharp_piano")
            self.hosts.hostnames[display_hostname].request_number(555)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("gsharp_mezzo")
            self.hosts.hostnames[display_hostname].request_number(444)
            time.sleep(0.5)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("asharp_piano")
            self.hosts.hostnames[display_hostname].request_number(333)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("asharp_mezzo")
            self.hosts.hostnames[display_hostname].request_number(222)
            time.sleep(0.5)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("c_piano")
            self.hosts.hostnames[display_hostname].request_number(111)
            time.sleep(0.5)
            self.hosts.hostnames[display_hostname].request_score("c_mezzo")
            self.hosts.hostnames[display_hostname].request_number(000)
            time.sleep(2)

        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("all","off")
            time.sleep(0.25)

        for carousel_hostname in self.carousel_hostnames:
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("coco","on")
            time.sleep(0.25)
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("naranja","on")
            time.sleep(0.25)
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("mango","on")
            time.sleep(0.25)
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("sandia","on")
            time.sleep(0.25)
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("pina","on")
            time.sleep(0.25)
            self.hosts.hostnames[carousel_hostname].cmd_carousel_lights("peso","on")
            time.sleep(0.25)

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",False)

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",True)
            time.sleep(0.25)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",True)
            time.sleep(0.25)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",True)
            time.sleep(0.25)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",True)
            time.sleep(0.25)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",True)
            time.sleep(0.25)

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].request_button_light_active("derecha",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("trueque",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("comienza",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("dinero",False)
            self.hosts.hostnames[pinball_hostname].request_button_light_active("izquierda",False)


        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")
            time.sleep(5)

        for pinball_hostname in self.pinball_hostnames:
            self.hosts.hostnames[pinball_hostname].cmd_playfield_lights("all_radial","off")

        coil_names = [
            "pop_left"
            "pop_middle"
            "pop_right"
            "sling_left"
            "sling_right"
            "derecha_main"
            "derecha_hold"
            "izquierda_main"
            "izquierda_hold"
            "trueque"
            "dinero"
            "kicker"
        ]

        for coil_name in coil_names:
            for pinball_hostname in self.pinball_hostnames:
                self.hosts.hostnames[pinball_hostname].cmd_pulse_coil(coil_name,12)
                time.sleep(1)


    def add_to_queue(self, topic, message, origin, destination):
        self.queue.put((topic, message, origin, destination))

    def run(self):
        while True:
            if self.active:
                try:
                    topic, message, origin, destination = self.queue.get(True,5)
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
                except queue.Empty:
                    if self.timer + self.timeout_duration < time.time(): # if timeout condition
                        self.set_current_mode(self.game_mode_names.ERROR)
                except AttributeError:
                    pass
            else:
                time.sleep(1)

