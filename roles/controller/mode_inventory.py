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
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.phase = self.PHASE_ZERO
        self.start()
        # self.hosts["pinballmatrix"].request_amt203_zeroed()
        # bypass inventory
        #self.set_current_mode(self.game_mode_names.ATTRACTION)

    def inventory(self):
        choreo = self.choreography
        self.active = True
        
        # Zeroing
        pass
        
        # Inventory 
        total_balls = 0
        # Get flat list of all Tubes (instead of dicts)
        tubes_all = []
        for pair in choreo.tubes:
            tubes_all += [pair["left"], pair["right"]]
        # Check for any tubes that already know they're full
        tubes_known = []
        tubes_unknown = []
        for tube in tubes_known:
            if tube.test_full():
                # is_full will set tube.inventory = tube.max_inventory
                tubes_known.append(tube)
            else:
                tubes_unknown.append(tube)
        # Check for empty tubes by shooting non-full tubes once
        # TODO: move carousels to blocking positions?
        tubes_empty = []
        for tube in tubes_unknown:
            if tube.test_empty():
                tube.inventory = 0
                tubes_empty.append(tube)
                tubes_unknown.remove(tube)
        # Dump carousels into unknown tubes, hoping to fill them
        for tube in tubes_unknown:
            for carousel in choreo.carousels:
                choreo.transfer_all(carousel, tube)
                if tube.is_full():
                    tubes_unknown.remove(tube)
                    tubes_known.append(tube)
                    break
        # Fill remaining unknown tubes until all are known
        while tubes_unknown:
            # Using pop() because tube will become known
            tube_unknown = tubes_unknown.pop()
            for tube_known in tubes_known:
                choreo.transfer_all(tube_known, tube_unknown)
                if tube_unknown.is_full():
                    tubes_known.append(tube_unknown)

        # Distribute balls equally and finish
        return choreo.equalize_tubes()
    
    # TODO: Just stuffed everything in here for now, slowly getting more concrete
    def begin(self):
        #self.timer = time.time()
        self.active = True
        self.set_current_mode(self.game_mode_names.ATTRACTION)

    def end(self):
        self.active = False

    def set_amt203_zeroed(self,amt203_zeroed):
        if all(amt203_zeroed): # when all report finished.
            self.phase = self.PHASE_INVENTORY
            # start inventory

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

"""
inventory
    empty center carousel
        for each occupied center pocket
            find closest available outer pocket
                element: center carousel to outer carousel
    empty outer carousels
        for each outer carousel
            for occupied pocket
                if dinero tube not full
                    element: carousel to adjacent tube
                    continue
                if trueque tube not full
                    element: carousel to adjacent tube
                    continue
                find closest nonadjacent tube not full
                    element: local carousel to remote carousel
                    element: carousel to adjacent tube
    empty each tube to establish zero-based counting
        for origin_tube in tubes
            destination_tube =  closest nonfull tube
            try
                if is_adjacent(origin_tube, destination_tube)
                    local tube to local tube
                else
                    local tube to remote tube
            except donor_tube.motion_not_detected
                record zero value                        
                break
            except donor_tube.carousel.ball_not_received
                record zero value                        
                break

trueque mode setup
    equally distribute balls among games, with dinero tube as destination
    transfer all balls in trueque tube to dinero tube
local tube to local tube
local tube to remote tube
2x (local tube to remote tube)
dinero mode set up 
    equally distribute balls among games, with dinero tube as destination
    transfer all balls in trueque tube to dinero tube
local tube to local tube
local tube to remote tube
2x (local tube to remote tube)
"""