"""
This module coordinates the the carousels, matrix motors, and tubes
to pass balls between tubes and carousels
"""

# itertools.zip_longest is useful for handling the center carousel. 
# Ex: this pairs "coco" with "carouselcenter" after running out of fruit:
# zip_longest(FRUITS, CAROUSEL_HOSTNAMES, fillvalue="coco") 
import itertools
import time


# Empty function
NULLFUNC = lambda: None

# Lookup constants
CAROUSEL_CENTER_HOSTNAME = "carouselcenter"
CAROUSEL_HOSTNAMES = [
    "carousel1",
    "carousel2",
    "carousel3",
    "carousel4",
    "carousel5",
    "carouselcenter"]
CAROUSEL_MOTOR_NAMES = [
    "carousel_1",
    "carousel_2",
    "carousel_3",
    "carousel_4",
    "carousel_5",
    "carousel_center"]
FRUITS = ["coco", "naranja", "mango", "sandia", "pina"]
SIDES = ["left", "right"]
STATION_NAMES = [
    "pinball1game",
    "pinball2game",
    "pinball3game",
    "pinball4game",
    "pinball5game"]


class Carousel(object):
    """ hosts.Carousel wrapper that adds motion control and tube-awareness. """
    def __init__(self, host_instance, matrix, tubes=[], timeout=60.):
        self.host_instance = host_instance
        self.matrix = matrix
        self.tubes = tubes
        self.timeout = timeout
        # Determine home parameters
        # zip_longest puts "coco" with "carouselcenter"
        fruits_by_hostname = dict(
            itertools.zip_longest(CAROUSEL_HOSTNAMES, FRUITS, fillvalue="coco"))
        self.home_fruit = fruits_by_hostname[host_instance.hostname]       
        self.home_target = "back" if host_instance.hostname is not CAROUSEL_CENTER_HOSTNAME else "coco"
        # Save reference to the appropriate motor
        motors_by_hostname = dict(
            itertools.zip_longest(CAROUSEL_HOSTNAMES, CAROUSEL_MOTOR_NAMES, fillvalue="coco"))
        self.motor_name = motors_by_hostname[host_instance.hostname]
        self.motor = matrix.motor_by_carousel_name[self.motor_name]
    
    def __getattr__(self, attribute):
        """ Anything not intercepted here gets passed to host_instance """
        return getattr(self.host_instance, attribute)
        
    # TODO
    def get_nearest_available_fruit(self, neighbor):
        return "coco"

    # Motion ----------------------------------------------------------------
    def wait(self):
        """ Wait for carousel to finish moving """
        start_time = time.time()
        while not self.motor["target_reached"]:
            # Took too long
            if time.time() - start_time > TIMEOUT:
                return False
            time.sleep(0.1)
        return True
    
    def rotate_to_target(self, fruit, target, wait=True):
        """ Rotate fruit toward target and optionally wait to finish """
        # Abort if already moving
        if not self.motor["target_reached"]:
            return False

        # Get target name
        # If target is a string, assume that's the target
        if isinstance(target, str):
            target_name = target
        # If target is a Tube, then target_name is the side the tube is on
        # Trying to rotate to a remote tube would be weird, but it would work
        # by just assuming that you want to rotate like its parent carousel.
        elif isinstance(target, Tube):
            for side, tube in self.tubes.items():
                if tube is target:
                    target_name = side
        # If target is not a Tube or a string, then it's the center carousel
        else:
            target_name = "back"
            
        # Do move and optionally wait
        self.matrix.cmd_rotate_carousel_to_target(self.motor_name, fruit, target_name)        
        if not wait:
            return True
        return self.wait()
    
    def home(self, wait=True):
        """ Return self to home orientation """
        return self.rotate_to_target(self.home_fruit, self.home_target, wait)

    # Queries ----------------------------------------------------------------
    def is_empty(self, update=True):
        if update:
            self.request_detect_balls()
        return not any(self.host_instance.balls_present)
        
    def is_full(self, update=True):
        if update:
            self.request_detect_balls()
        return all(self.host_instance.balls_present)

    def has_balls(self, update=True):
        """ Yep, that's what I'm calling it """
        return not self.is_empty(update)


class Tube(object):
    """ Convenience class to manage tubes via their hosts.Pinball staion 
        This version is aware of its parent carousel """
    def __init__(self, station, side, carousel, max_inventory=6):
        self.station = station
        self.side = side
        # HACK: should get this from fruit but whatever
        self.carousel = carousel
        self.max_inventory = max_inventory
        self.inventory = -1
        # Have to save references to a different set of commands based on side
        if side == "left":
            self.callbacks = {
                "request_detect_balls": station.get_left_stack_inventory,
                "request_eject_ball": station.cmd_lefttube_launch
            }
        elif side == "right":
            self.callbacks = {
                "request_detect_balls": station.get_right_stack_inventory,
                "request_eject_ball": station.cmd_righttube_launch          
            }
        else:
            raise ValueError(f"Tube expected side right/left, got {side}")
                
    def request_detect_balls(self):
        """ Get inventory from parent station and save it.
            Inventory is also returned for convenience. """
        self.inventory = self.callbacks["request_detect_balls"]()
        return self.inventory
    
    def request_eject_ball(self, fruit=None):
        return self.callbacks["request_eject_ball"]()
        
    def is_empty(self):
        return self.request_detect_balls() < 1
        
    def is_full(self):
        return self.request_detect_balls() > self.max_inventory - 1
    
    def has_balls(self):
        return not self.is_empty()
    
    # TODO
    def get_nearest_available_fruit(self, neighbor):
        return True
        

class Choreography(): 
    """ This does the things """

    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
        
        # Save reference to pinballmatrix for carousel rotation
        self.matrix = hosts.pinballmatrix        
        # Create dicts of ball-handling elements for easy access
        # The Carousel and Tube objects here are aware of their neighbors
        # self.carousels = {fruit: Carousel}, ex: carousels["coco"]
        # self.tubes = {fruit: {side: Tube}}, ex: tubes["coco"]["left"]
        self.carousels = {"center": Carousel(hosts.carouselcenter, self.matrix)}     
        self.tubes = {}         
        carousel_names = dict(zip(FRUITS, CAROUSEL_HOSTNAMES))
        station_names = dict(zip(FRUITS, STATION_NAMES))
        for fruit in FRUITS:
            carousel = Carousel(hosts.hostnames[carousel_names[fruit]], self.matrix)
            self.carousels[fruit] = carousel
            self.tubes[fruit] = {}
            station = hosts.hostnames[station_names[fruit]]
            for side in SIDES:
                tube = Tube(station, side, carousel)
                self.tubes[fruit][side] = tube
                carousel.tubes.append(tube)

    # Multi-carousel movements -----------------------------------------------

    def process_carousels(self, carousels=None) -> list:
        """ Helper function to make carousel input more versatile
            Can specify carousels by instance, name, or None (all) """
        # If None, assume we want all carousels
        carousels = carousels or self.carousels
        # If given only one item, ensure that it's a list
        if not isinstance(carousels, (list, tuple)):
            carousels = [carousels]
        # If any are strings, assume they're fruit names for carousels
        for i in range(len(carousels)):
            if isinstance(carousels[i], str):
                carousels[i] = self.carousels[carousel]
        return carousels

    def wait_carousels(self, carousels=None) -> bool:
        """ Wait for list of carousels to finish moving.
            Checks all carousels by default. """
        # Ensure carousels is a list of Carousel instances
        carousels = self.process_carousels(carousels)
        # Start waiting
        done = [False]
        start_time = time.time()
        while not all(done):
            # Took too long
            if time.time() - start_time > TIMEOUT:
                return False
            time.sleep(0.1)
            # Refresh motor statuses
            done = [carousel.motor["target_reached"] for carousel in carousels]
        return True

    def rotate_carousels_to_targets(self, carousels, fruits, targets, wait=True) -> bool:
        """ Concurrent carousel movements """
        # Verify that each carousel has a fruit and a target
        if not len(carousels) == len(fruits) == len(targets):
            return False
        # Ensure carousels is a list of Carousel instances
        carousels = self.process_carousels(carousels)
        # Start all the moves
        for carousel, fruit, target in zip(carousels, fruits, targets):
            if not carousel.rotate_to_target(fruit, target, wait=False):
                return False
        # Optionally, wait for moves to finish
        if not wait:
            return True 
        return wait_carousels(carousels)    

    def home_carousels(self, carousels=None, wait=True) -> bool:
        """ Send a list of carousels back to their home position.
            If no carousels specified, will home them all. """
        # Ensure carousels is a list of Carousel instances
        carousels = self.process_carousels(carousels)
        # Start all carousels homing at once
        for carousel in carousels:
            if not carousel.home(wait=False):
                return False
        # Optionally, wait for moves to finish
        if not wait:
            return True
        return wait_carousels(carousels)      

    def align_pockets(self, vehicle1, fruit1, vehicle2, fruit2, wait=True) -> bool:
        """ Align pockets between two vehicles. Tubes are ignored. """
        vehicles = (vehicle1, vehicle2)
        fruits = (fruit1, fruit2)
        # Figure out what's going where
        # Kind of silly to have a loop but I like it
        carousels, fruits, targets = [], [], []
        for i in range(vehicles):
            if isinstance(vehicle, Carousel):
                carousels.append(vehicles[i])
                fruits.append(fruits[i])
                targets.append(vehicles[1-i])
        # Make it so
        return self.rotate_carousels_to_targets(carousels, fruits, targets, wait)
    
    # Single transfer between neighbors --------------------------------------
    
    def handoff(sender, send_fruit, receiver, 
                fanfare_start=None,
                fanfare_end=None,
                preserve_fruit=False) -> bool:
        # Easier to use empty fanfare funcs than a bunch of conditionals
        fanfare_start = fanfare_start or NULLFUNC
        fanfare_end = fanfare_end or NULLFUNC 
        # Determine receive fruit
        receive_fruit = preserve_fruit or receiver.get_nearest_available_fruit(sender) 
        # Verify that sender and receiver are ready
        if isinstance(sender, Tube) and sender.is_empty():
            return False 
        if isinstance(receiver, Tube) and receiver.is_full():
            return False
        if isinstance(sender, Carousel) and not sender.balls_present[send_fruit]:
            return False
        if isinstance(receiver, Carousel) and receiver.balls_present[receive_fruit]:
            return False 
        # Prep any carousels involved and wait for them to finish
        # Fanfare starts when the movement starts
        fanfare_start()
        if not align_pockets(sender, send_fruit, receiver, receive_fruit):
            fanfare_end()
            return False
        # Get starting inventory of receiver, for reference
        if isinstance(receiver, Tube):
            start_inventory = receiver.request_update_balls()
        # Try to launch a few times
        n = 0
        while True:
            # Launch!
            sender.request_eject_ball(send_fruit)
            time.sleep(1.)
            # See if the receiver has indeed gotten the ball
            receiver.request_detect_balls()
            if isinstance(receiver, Tube) and receiver.inventory > start_inventory:
                break
            if isinstance(receiver, Carousel) and receiver.balls_present[receive_fruit]:
                break
            # Don't try forever
            if n > 9:
                fanfare_end()
                return False
            n += 1
        # We did it!
        fanfare_end()
        # Let caller know where the ball is in case of autoselect
        return receive_fruit
    
    # Single transfer along a path -------------------------------------------
    
    def generate_path(sender, receiver) -> list:
        ''' Given vehicles "sender" and "receiver", find a path from sender to 
            receiver and return it as a list of vehicles used to get there. 
            This path does not care which fruit is used on carousels. '''      
        # Start from sender
        path = [sender]

        # Helper, returns whether path is finished yet 
        def path_complete() -> bool:
            return path[-1] == receiver
        
        # If sender and receiver are the same, then what are we doing here
        if path_complete():
            return path
        # If starting from a Tube, next step is always its parent carousel
        if isinstance(sender, Tube):
            path.append(sender.carousel)
            # Maybe that's the end?
            if path_complete():
                return path
        
        # Now we're in a carousel no matter what.
        current_carousel = path[-1]
        # If it's an edge carousel and the destination is...
        if current_carousel is not CENTER_CAROUSEL: 
            # ...a child tube, then that's next
            if isinstance(receiver, Tube) and receiver.carousel == current_carousel:
                path.append[receiver]     
            # ...anything else, then we have to get there via the center
            else: 
                path.append[center_carousel]
        # Is that the end?
        if path_complete():
            return path
        
        # Okay, we're at the center carousel. From here it's easy: 
        # Either directly to the destination carousel...
        if isinstance(receiver, Carousel):
            path.append(receiver)        
        # ...or to a tube via its parent carousel.
        else:
            path.append(receiver.carousel)
            path.append(receiver)
        # Don't need to verify, path is complete.
        return path
    
    def do_path(path, start_fruit=None, fanfare=None, preserve_fruit=None):
        """ Implement a given path, with optional fanfare """
        # Start from beginning of path   
        current_vehicle, current_fruit = path.pop(0), start_fruit
        # For each path step...
        for next_vehicle in path:
            # Get optional fanfare
            if fanfare:
                next_fanfare = fanfare.pop(0)
                # If it's a tuple, split it into start and end commands
                if isinstance(fanfare, (list, tuple)):
                    next_fanfare, next_fanfare_end = fanfare
                else:
                    next_fanfare_end = None
            # Do the handoff and save the new pocket (in case of autoselect)
            current_fruit = handoff(
                current_vehicle, 
                current_fruit, 
                next_vehicle, 
                next_fanfare,
                next_fanfare_end,
                preserve_fruit)
            # Abort if handoff failed
            if not current_fruit:
                return False
            # Now we're somewhere new
            current_vehicle = next_vehicle
        return True

    def transfer(self, sender, receiver,
                 send_fruit=None,
                 fanfare=None,
                 preserve_fruit=False) -> bool:
        """ Transfer one ball from sender to receiver. """
        # Can't send from a carousel without knowing which pocket to send from
        if isinstance(sender, Carousel) and send_fruit is None:
            return False
        # Generate and run path from sender to receiver
        # Path is fruit-agnostic
        path = self.generate_path(sender, receiver)
        return self.do_path(path, start_fruit, fanfare, preserve_fruit)        

    # Multiple transfers -----------------------------------------------------
    
    def transfer_all(self, sender, receivers,
                     fanfare_start=None,
                     fanfare_end=None) -> bool:
        """ Move all balls from one vehicle to a list of receivers """
        # Easier to use empty fanfare funcs than a bunch of conditionals
        fanfare_start = fanfare_start or NULLFUNC
        fanfare_end = fanfare_end or NULLFUNC 
        # If only one receiver is given, turn it into a list
        if not isinstance(receiver, (list, tuple)):
            receivers = [receivers]
        # Get first receiver
        receiver = receivers.pop(0)
        # Keep sending balls until sender is empty
        fanfare_start()
        while sender.has_balls():
            # If transfer fails for any reason (like receiver full)...
            if not transfer(sender, receiver):
                # ...return False if no receivers left. Sender is not empty.
                if not receivers:
                    fanfare_end()
                    return False
                # Otherwise, move to next receiver
                receiver = receivers.pop(0)
        # We did it, sender is empty!
        fanfare_end()
        return True
    
    def purge_vehicle(self, vehicle) -> bool:
        """ Fast purge of a specified vehicle.
            - Center carousel will dump to edge carousels 
            - Edge carousels will dump to tubes 
            - Tubes will dump to other tubes """
        # List of potential receivers
        receivers = []
        # TODO: Optimize dump order
        # If emptying center carousel, dump into edge carousels
        if vehicle is self.carousels["center"]:
            receivers = self.carousels
        # If emptying a tube, dump into other local tube and then remote ones
        if isinstance(vehicle, Carousel):
            carousel = vehicle.carousel
        # If emptying edge carousel, dump into local tubes first then others'
        else:
            receivers = carousel.tubes.values()
            for potential_receiver in self.carousels:
                receivers += potential_receiver.tubes.values()
        # Don't send anything to self or to center carousel
        for bad_receiver in (vehicle, self.carousels["center"]):
            if bad_receiver in receivers:
                receivers.remove[bad_receiver]
        
        # Dump into one receiver until full, then move to next
        for fruit, occupied in carousel.balls_present.items():
            if not occupied:
                continue
            if not self.transfer(carousel, receiver, fruit):
                receivers.pop(0)
                if len(receivers) == 0:
                    return False
        return True

    def equalize_tubes(self, tubes=None) -> bool:
        """ Equalize inventory between a list of tubes as best as possible
            Equalizes all tubes by default """
        tubes = tubes or self.tubes
        # Equalize routine
        while True:
            # Sort tubes from fullest to emptiest
            tubes.sort(key=lambda tube: tube.request_detect_balls(), reverse=True)
            # Find transfer amount to bring max and min inventory within 1
            max_tube, min_tube = tubes[0], tubes[-1]
            to_transfer = floor((max_tube.inventory - min_tube.inventory) / 2)
            # If nothing left to transfer, we're done
            if not to_transfer:
                return True
            # Do transfers, abort if any don't work
            for i in range(to_transfer):
                if not self.transfer(max_tube, min_tube):
                    return False