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
        self.pinball_names = ["pinball1game","pinball2game","pinball3game","pinball4game","pinball5game"]
        self.carousel_names = [
            "carousel1",
            "carousel2",
            "carousel3",
            "carousel4",
            "carousel5",
            "carouselcenter",
        ]
        self.motor_names = [
            "carousel_1",
            "carousel_2",
            "carousel_3",
            "carousel_4",
            "carousel_5",
            "carousel_center",
        ]
        self.fruit_names = [
            "coco",
            "naranja",
            "mango",
            "sandia",
            "pina",
        ]
        self.active_games = [1] # this is a short hack for excluding certain stations 
        self.game_mode_names = settings.Game_Modes
        self.timer = time.time()
        self.timeout_duration = 120 #seconds
        self.maximum_carousel_position_discrepancy = 100
        self.phase = self.PHASE_ZERO
        self.start()
        # self.hosts["pinballmatrix"].request_amt203_zeroed()
        # bypass inventory
        #self.set_current_mode(self.game_mode_names.ATTRACTION)

    def rotate_carousel_to_position(
        self, 
        carousel_name, 
        fruit_name, 
        position_name, 
        timeout_duration=20):
        start_time = time.time()
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target(carousel_name, fruit_name, position_name)
        while not self.hosts.pinballmatrix.get_destination_reached(carousel_name)[0]:
            time.sleep(.25)
            if time.time() - timeout_duration > start_time:
                break
        discrepancy = self.hosts.pinballmatrix.get_discrepancy(carousel_name)

        if abs(discrepancy) > self.maximum_carousel_position_discrepancy:
            return [self.hosts.pinballmatrix.get_destination_reached(carousel_name),discrepancy]
        else:
            return [self.hosts.pinballmatrix.get_destination_reached(carousel_name)[0],discrepancy]

    def eject_ball_to_tube(
        self, 
        carousel_name, 
        fruit_name, 
        pinball_name, 
        tube_left_right, 
        retries=5):
        # THIS FUNCTION DOES NOT ENSURE THAT THE CAROUSEL IS IN POSITION 
        # is there a ball in the pocket?
        carousel_balls_detected = self.hosts.hostnames[carousel_name].get_carousel_ball_detected()
        if carousel_balls_detected[fruit_name] == False:
            return [False,"no ball"]

        #is tube full?
        if tube_left_right == "left":
            if self.hosts.hostnames[pinball_name].request_lefttube_full(True):
                return [False,"full"]
        else:
            if self.hosts.hostnames[pinball_name].request_righttube_full(True):
                return [False,"full"]
        # eject
        for i in range(retries):
            self.hosts.hostnames[carousel_name].request_eject_ball(fruit_name)
            time.sleep(0.4)
            carousel_balls_detected = self.hosts.hostnames[carousel_name].get_carousel_ball_detected()
            if carousel_balls_detected[fruit_name] == False:
                if tube_left_right == "left":
                    if self.hosts.hostnames[pinball_name].get_count_tube_sensor_events_left(2) > 0:
                        return [True,""]
                else:
                    if self.hosts.hostnames[pinball_name].get_count_tube_sensor_events_right(2) > 0:
                        return [True,""]
        return [False,None]

    def launch_ball_to_carousel(
        self, 
        carousel_name, 
        fruit_name, 
        pinball_name, 
        tube_left_right, 
        retries=5):
        # is carousel in position?

        # is carousel pocket empty?
        carousel_balls_detected = self.hosts.hostnames[carousel_name].get_carousel_ball_detected()
        if carousel_balls_detected[fruit_name]: 
            return [False,"carousel pocket full"]
        # is tube ball count > 0? -1 denotes ball count before inventory
        if tube_left_right == "left":
            if self.hosts.hostnames[pinball_name].get_left_stack_inventory() == 0: # -1 denotes ball count before inventory
                return [False,"inventory zero"]
        else:
            if self.hosts.hostnames[pinball_name].get_right_stack_inventory() == 0: # -1 denotes ball count before inventory
                return [False,"inventory zero"]
        # launch tube 
        for i in range(retries):
            if tube_left_right == "left":
                self.hosts.pinball1game.cmd_lefttube_launch()
            else:
                self.hosts.pinball1game.cmd_righttube_launch()
            time.sleep(1)
            carousel_balls_detected = self.hosts.hostnames[carousel_name].get_carousel_ball_detected()
            print("...............",carousel_balls_detected,fruit_name,carousel_balls_detected[fruit_name])
            if carousel_balls_detected[fruit_name]: 
                return [True,""]
            else:
                time.sleep(0.75)
                self.hosts.hostnames[carousel_name].request_eject_ball(fruit_name)
                time.sleep(1)
                if tube_left_right == "left":
                    if self.hosts.hostnames[pinball_name].get_count_tube_sensor_events_left(2) == 0:
                        return [False,"tube_empty"]
                else:
                    if self.hosts.hostnames[pinball_name].get_count_tube_sensor_events_right(2) == 0:
                        return [True,"tube_empty"]
        return [False,"ball_stuck"]

    def pass_ball_between_adjacent_carousels(
            origin_carousel_name,
            origin_fruit_name,
            destination_carousel_name,
            destination_fruit_name,
            retries = 5
        ):
        # is one carousel the carouselcenter?
        if origin_carousel_name == "carouselcenter" or destination_carousel_name == "carouselcenter":
            # does origin_fruit_name pocket have a ball?
            carousel_balls_detected = self.hosts.hostnames[origin_carousel_name].get_carousel_ball_detected()
            if not carousel_balls_detected[origin_fruit_name]:
                return [False,"no ball in origin"]
            # is destination_fruit_name empty?
            carousel_balls_detected = self.hosts.hostnames[destination_carousel_name].get_carousel_ball_detected()
            if carousel_balls_detected[destination_fruit_name]:
                return [False,"ball in destination"]
            for i in range(retries):
                self.hosts.hostnames[origin_carousel_name].request_eject_ball(origin_fruit_name)
                time.sleep(1)
                carousel_balls_detected = self.hosts.hostnames[destination_carousel_name].get_carousel_ball_detected()
                if carousel_balls_detected[destination_fruit_name]:
                    return [True,""] 
            return [False,"transfer failed"]

    ##########################################################

    def move_balls_from_edge_carousels_to_tubes(self, active_games):
        for active_game_int in active_games:
            active_motor = self.motor_names[active_game_int]
            active_carousel = self.carousel_names[active_game_int]
            active_pinball = self.pinball_names[active_game_int]
            balls_detected = self.hosts.hostnames[active_carousel].get_carousel_ball_detected()
            if any(value == True for value in balls_detected.values()):
                for fruit_name in self.fruit_names:
                    if balls_detected[fruit_name]: 
                        success, reason = self.rotate_carousel_to_position(active_carousel, fruit_name, "left")
                        if success:
                            self.eject_ball_to_tube(active_carousel, fruit_name, active_pinball, "left")
                        else:
                            print("move_balls_from_edge_carousels_to_tubes",success, reason)
                            return ["move_balls_from_edge_carousels_to_tubes",success, reason]

    def move_balls_from_center_carousel_to_tubes(self, active_games):
        success, reason = self.rotate_carousel_to_position("carousel_center", "coco", "coco")
        if not success:
            print("move_balls_from_center_carousel_to_tubes", "rotate_carousel_to_position", success, reason)
            return ["move_balls_from_center_carousel_to_tubes", "rotate_carousel_to_position", success, reason]
        for active_game_int in active_games:
            active_motor = self.motor_names[active_game_int]
            active_carousel = self.carousel_names[active_game_int]
            active_pinball = self.pinball_names[active_game_int]
            active_fruit = self.self.fruit_names[active_game_int]
            success, reason = self.rotate_carousel_to_position(active_carousel, active_fruit, "back")
            if not success:
                print("move_balls_from_center_carousel_to_tubes","rotate_carousel_to_position",success, reason)
                return ["move_balls_from_center_carousel_to_tubes","rotate_carousel_to_position",success, reason]
            success, reason = self.pass_ball_between_adjacent_carousels("carousel_center",active_fruit,active_carousel,active_fruit)
            if not success:
                print("move_balls_from_center_carousel_to_tubes","pass_ball_between_adjacent_carousels",success, reason)
                return ["move_balls_from_center_carousel_to_tubes","pass_ball_between_adjacent_carousels",success, reason]

    def shuffle_all_balls_between_tubes_in_same_station(self, active_games, origin_tube, destination_tube):
        game_and_count = []
        for active_game_int in active_games:
            active_motor = self.motor_names[active_game_int]
            active_carousel = self.carousel_names[active_game_int]
            active_pinball = self.pinball_names[active_game_int]
            active_fruit = self.self.fruit_names[active_game_int]
            number_of_balls_transfered = 0
            while True:
                # move carousel pocket to origin tube
                success, reason = self.rotate_carousel_to_position(active_motor, active_fruit, origin_tube)
                if not success:
                    print("shuffle_all_balls_between_tubes_in_same_station", "rotate_carousel_to_position", success, reason)
                    return ["shuffle_all_balls_between_tubes_in_same_station", "rotate_carousel_to_position", success, reason]
                # launch ball from origin tube
                success, reason = self.launch_ball_to_carousel(
                    active_carousel, 
                    active_fruit, 
                    active_pinball, 
                    origin_tube)
                if not success:
                    # detect empty tube and break while loop
                    if reason == "tube_empty":
                        break
                    else:
                        print("shuffle_all_balls_between_tubes_in_same_station", "launch_ball_to_carousel", success, reason)
                        return ["shuffle_all_balls_between_tubes_in_same_station", "launch_ball_to_carousel", success, reason]
                # move carousel pocket to destination_tube
                success, reason = self.rotate_carousel_to_position(active_motor, active_fruit, destination_tube)
                if not success:
                    print("shuffle_all_balls_between_tubes_in_same_station", "rotate_carousel_to_position", success, reason)
                    return ["shuffle_all_balls_between_tubes_in_same_station", "rotate_carousel_to_position", success, reason]

                # eject ball from carousel pocket
                success, reason = self.eject_ball_to_tube(active_carousel, active_fruit, active_pinball, destination_tube)
                if not success:
                    print("shuffle_all_balls_between_tubes_in_same_station", "eject_ball_to_tube", success, reason)
                    return ["shuffle_all_balls_between_tubes_in_same_station", "eject_ball_to_tube", success, reason]

                number_of_balls_transfered +=1
            game_and_count.append([active_game,number_of_balls_transfered])
        return game_and_count


    def inventory(self):
        choreo = self.choreography
        self.active = True
        
        # Zeroing
        pass
        
        # Get flat list of all Tubes (instead of dicts)
        tubes_all = choreo.all_tubes
        # Check for any tubes that already know they're full
        tubes_known = []
        tubes_unknown = []
        for tube in tubes_known:
            if tube.test_full():
                # test_full can set tube.inventory = tube.max_inventory
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
        #self.set_current_mode(self.game_mode_names.ATTRACTION)

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
                    pass
                    #if self.timer + self.timeout_duration < time.time(): # if timeout condition
                    #    self.set_current_mode(self.game_mode_names.ERROR)
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