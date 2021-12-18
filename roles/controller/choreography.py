"""
This module coordinates the the carousels, matrix motors, and tubes
to pass balls between tubes and carousels
"""

# itertools.zip_longest is useful for handling the center carousel. 
# Ex: this pairs "coco" with "carouselcenter" after running out of fruit:
# zip_longest(FRUITS, CAROUSEL_HOSTNAMES, fillvalue="coco") 
import itertools
import time

# Constants
DEFAULT_TIMEOUT = 2.       # Default timeout for ball-handling elements

# Lookups
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
    def __init__(self, host_instance, matrix, 
                 tubes=[], 
                 timeout=DEFAULT_TIMEOUT):
        self.host_instance = host_instance
        self.matrix = matrix
        self.tubes = tubes
        self.timeout = timeout
        # Determine home parameters
        # zip_longest fills shortest list with fillvalue
        # In this case, that puts None with "carouselcenter"
        fruits_by_hostname = dict(
            itertools.zip_longest(CAROUSEL_HOSTNAMES, FRUITS))
        self.fruit = fruits_by_hostname[host_instance.hostname]
        self.target = self.fruit or "back"  # How others target this
        self.home_fruit = "coco"
        self.home_target = "back" if self.fruit else "coco"
        # Save reference to the appropriate motor
        motors_by_hostname = dict(
            itertools.zip_longest(
                CAROUSEL_HOSTNAMES, CAROUSEL_MOTOR_NAMES, fillvalue="coco"))
        self.motor_name = motors_by_hostname[host_instance.hostname]
        self.motor = matrix.motor_by_carousel_name[self.motor_name]
    
    def __getattr__(self, attribute):
        """ Anything not intercepted here gets passed to host_instance """
        return getattr(self.host_instance, attribute)
    
    @property
    def all_tubes(self):
        """ Return both child tubes as a list instead of a dict """
        return self.tubes.values()
        
    # TODO
    def get_nearest_available_fruit(self, neighbor):
        return "coco"

    # Motion ----------------------------------------------------------------
    def wait(self):
        """ Wait for carousel to finish moving """
        start_time = time.time()
        # self.motor.get_runtime_status_flags()
        while not self.motor["target_reached"][0]:
            # Took too long
            if time.time() - start_time > self.timeout:
                # HACK: always return True until I figure out how to make 
                # return False
                return True
            time.sleep(0.1)
            # self.motor.get_runtime_status_flags()
        return True
    
    # TODO: verify move
    def rotate_to_target(self, fruit, target, wait=True):
        """ Rotate fruit toward target and optionally wait to finish """
        # Abort if already moving
        if not self.motor["target_reached"]:
            # HACK: return True until we figure out how to detect this better
            return True

        # Get target name
        # # HACK: If target is an int, add backlash (debug)
        # backlash = 1024
        # if isinstance(target, int):
        #     target_name = target + backlash
        # If target is a string, assume that's the target
        elif isinstance(target, str):
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
        
        # HACK continued
        # if isinstance(target_name, int):
        #     self.matrix.cmd_rotate_carousel_to_target(self.motor_name, fruit, target_name-backlash)
        return self.wait()
    
    def home(self, wait=True):
        """ Return self to home orientation """
        return self.rotate_to_target(self.home_fruit, self.home_target, wait)

    # Queries ----------------------------------------------------------------
    def request_detect_balls(self):
        self.host_instance.request_carousel_detect_balls()
    
    def is_empty(self, update=True):
        if update:
            self.request_detect_balls()
        return not any(self.host_instance.balls_present.values())
        
    def is_full(self, update=True):
        if update:
            self.request_detect_balls()
        return all(self.host_instance.balls_present.values())

    def has_balls(self, update=True):
        """ Yep, that's what I'm calling it """
        return not self.is_empty(update)


class Tube(object):
    """ Convenience class to manage tubes via their hosts.Pinball staion 
        This version is aware of its parent carousel """
    def __init__(self, station, side, carousel, 
                 max_inventory=12,
                 timeout=DEFAULT_TIMEOUT):
        self.station = station
        self.side = side
        # HACK: should get this from fruit but whatever
        self.carousel = carousel
        self.max_inventory = max_inventory
        # Have to save references to a different set of commands based on side
        if side == "left":
            self.callbacks = {
                # "request_present": station.request_lefttube_present,
                # "set_present": station.set_lefttube_present,
                # "get_present": station.get_lefttube_present,
                # "clear_sensor": station.clear_tube_sensor_left,
                # "record_sensor": station.record_tube_sensor_left,
                # "get_sensor_events": station.get_count_tube_sensor_events_left,
                # "get_last_sensor_event": station.get_last_state_tube_sensor_events_left,
                # "launch": station.cmd_lefttube_launch,
                "set_inventory": station.set_left_stack_inventory,
                "get_inventory": station.get_left_stack_inventory,
                "event_history": station.left_tube_event_history,
                "request_detect_balls": station.get_left_stack_inventory,
                "request_eject_ball": station.cmd_lefttube_launch,
            }
        elif side == "right":
            self.callbacks = {
                "set_inventory": station.set_right_stack_inventory,
                "get_inventory": station.get_right_stack_inventory,
                "event_history": station.right_tube_event_history,
                "request_detect_balls": station.get_right_stack_inventory,
                "request_eject_ball": station.cmd_righttube_launch,
            }
        else:
            raise ValueError(f"Tube expected side right/left, got {side}")
    
    def __getattr__(self, attribute):
        """ Try to pass attribute requests to the right station attribute """
        return getattr(self.station, self.callbacks[attribute])
    
    # HACK: Takes a method that wraps a property and makes it a property again
    @property
    def inventory(self):
        return self.callbacks["get_inventory"]()
    
    @inventory.setter
    def inventory(self, value):
        self.callbacks["set_inventory"](value)
    
    def get_latest_event(self):
        """ Return last event in tube history if there are any """
        try:
            latest_event = self.callbacks["event_history"][-1]
        except IndexError:
            latest_event = [None, 0]
        return latest_event
    
    def request_detect_balls(self):
        """ Get inventory from parent station and save it.
            Inventory is also returned for convenience. """
        self.inventory = self.callbacks["get_inventory"]()
        return self.inventory

    def request_eject_ball(self, fruit=None, confirm=False):
        """ Accept and ignore if a fruit is passed in, for compatibility """
        # Try to eject
        self.callbacks["request_eject_ball"]()
        if not confirm:
            return True
        # Get last event for reference (before ball gets there)
        last_status, last_time = self.get_latest_event()
        # Wait for a new sensor_open event
        # HACK timeout should be a constant
        timeout = 2
        start_time = time.time()
        new_time = None
        while new_time == last_time or new_status == True:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.02)
            new_status, new_time = self.get_latest_event()
        # Verify that nothing else happens immediately afterward 
        # (ball doesn't immediately bounce back)
        time.sleep(0.2)
        return new_time == self.get_latest_event()[1] 
    
    def test_empty(self, sleep_time=1.):
        # First see if it's full -- doesn't take long
        if self.test_full(0.1):
            return False
        latest_time = self.get_latest_event()[1]
        # Try to shoot a ball, then wait
        self.request_eject_ball(confirm=False)
        time.sleep(sleep_time)
        # If nothing happened during that time, assume Tube is empty
        empty = latest_time == self.get_latest_event()[1] 
        if empty:
            self.inventory = 0
        return empty
    
    def test_full(self, sleep_time=1.):
        # Get latest event and elapsed time
        latest_status, latest_time = self.get_latest_event()
        time_elapsed = time.time() - latest_time
        # If beam is not broken, tube is not full
        if not latest_status:
            return False
        # If beam has been broken for a while, tube is full
        if time_elapsed > sleep_time:
            return True
        # If beam has only been broken recently, wait a little longer
        time.sleep(sleep_time - time_elapsed)
        # If beam is still broken, tube is full
        return self.get_latest_event()[0]
    
    def is_empty(self):
        if self.inventory is not None:
            return inventory < 1
        
    def is_full(self):
        if self.inventory is not None:
            return salf.inventory > self.max_inventory - 1
    
    def has_balls(self):
        if self.inventory is not None:
            return not self.is_empty()
    
    def get_nearest_available_fruit(self, neighbor=None):
        return self.carousel.get_nearest_available_fruit(self.side)
        

class Choreography(): 
    """ This does the things """

    def __init__(self, tb, hosts, total_balls=None, timeout=DEFAULT_TIMEOUT):
        self.tb = tb
        self.hosts = hosts
        self.total_balls = total_balls
        self.timeout = timeout
        
        # Save reference to pinballmatrix for carousel rotation
        self.matrix = hosts.pinballmatrix        
        # Create dicts of ball-handling elements for easy access
        # The Carousel and Tube objects here are aware of their neighbors
        # self.carousels = {fruit: Carousel}, ex: carousels["coco"]
        # self.tubes = {fruit: {side: Tube}}, ex: tubes["coco"]["left"]
        self.carousels = {"center": Carousel(hosts.carouselcenter,
                                             self.matrix,
                                             timeout=self.timeout)}     
        self.tubes = {}         
        carousel_names = dict(zip(FRUITS, CAROUSEL_HOSTNAMES))
        station_names = dict(zip(FRUITS, STATION_NAMES))
        for fruit in FRUITS:
            carousel = Carousel(
                hosts.hostnames[carousel_names[fruit]],
                self.matrix,
                timeout=self.timeout)
            self.carousels[fruit] = carousel
            self.tubes[fruit] = {}
            station = hosts.hostnames[station_names[fruit]]
            for side in SIDES:
                tube = Tube(station, side, carousel, timeout=self.timeout)
                self.tubes[fruit][side] = tube
                carousel.tubes.append(tube)

        # Also make flat lists available
        self.all_carousels = list(self.carousels.values())
        self.all_tubes = []
        for pair in self.tubes.values():
            self.all_tubes += [pair["left"], pair["right"]]
        self.all_vehicles = self.all_carousels + self.all_tubes
        targets = [c.target for c in self.all_carousels]
        targets += [t.side for t in self.all_tubes]
        self.targets_by_vehicle = dict(zip(self.all_vehicles, targets))

        # Empty function, makes conditional callbacks easier
        self.nullfunc = lambda: None
        
    # Helpers ----------------------------------------------------------------
    
    def process_carousels(self, carousels=None) -> list:
        """ Helper function to make carousel input more versatile
        Can specify carousels by instance, name, or None (all) """
        # If None, assume we want all carousels
        carousels = carousels or self.all_carousels
        # If given only one item, ensure that it's a list
        if not isinstance(carousels, (list, tuple)):
            carousels = [carousels]
        # Remove any Tubes
        for carousel in carousels:
            if isinstance(carousel, Tube):
                carousels.remove(carousel)
        # Turn strings into Carousels assuming they're fruit names
        for i in range(len(carousels)):
            potential_name = carousels[i]
            if isinstance(potential_name, str):
                carousels[i] = self.carousels[potential_name]
        return carousels

    # Multi-carousel movements -----------------------------------------------

    def wait_carousels(self, carousels=None) -> bool:
        """ Wait for list of carousels to finish moving.
            Checks all carousels by default. """
        # Ensure carousels is a list of Carousel instances
        carousels = self.process_carousels(carousels)
        # Start waiting
        done = False
        start_time = time.time()
        while not done:
            # Timeout
            if time.time() - start_time > self.timeout:
                # HACK: return True anyway
                return True
            time.sleep(0.1)
            # Refresh motor statuses
            for carousel in carousels:
                # motor.get_runtime_status_flags()
                done &= carousel.motor["target_reached"][0]
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
        return self.wait_carousels(carousels)    

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
        return self.wait_carousels(carousels)      

    def align_pockets(self, vehicles, fruits, wait=True) -> bool:
        """ Align pockets between two vehicles. Tubes are ignored. """
        # Figure out what's going where
        carousels, fruits_out, targets = [], [], []
        for i, vehicle in enumerate(vehicles):
            if isinstance(vehicle, Carousel):
                carousels.append(vehicle)
                fruits_out.append(fruits[i])
                targets.append(self.targets_by_vehicle[vehicles[1-i]])
        # Make it so
        return self.rotate_carousels_to_targets(carousels, fruits_out, targets, wait)
    
    # Single transfer between neighbors --------------------------------------
    
    def handoff(self, sender, receiver, send_fruit, 
                receive_fruit=None,
                fanfare_start=None,
                fanfare_end=None) -> bool:
        # Easier to use empty fanfare funcs than a bunch of conditionals
        fanfare_start = fanfare_start or self.nullfunc
        fanfare_end = fanfare_end or self.nullfunc 
        # Determine receive fruit
        receive_fruit = receive_fruit or receiver.get_nearest_available_fruit(sender) 
        # Verify that sender and receiver are ready
        # HACK: Bypass prep verification
        # if isinstance(sender, Tube) and sender.is_empty():
        #     return False 
        # if isinstance(receiver, Tube) and receiver.is_full():
        #     return False
        # if isinstance(sender, Carousel) and not sender.balls_present[send_fruit]:
        #     return False
        # if isinstance(receiver, Carousel) and receiver.balls_present[receive_fruit]:
        #     return False 
        # Prep any carousels involved and wait for them to finish
        # Fanfare starts when the movement starts
        fanfare_start()
        if not self.align_pockets([sender, receiver], [send_fruit, receive_fruit]):
            fanfare_end()
            return False
        # HACK: Bypass send verification
        sender.request_eject_ball(send_fruit)
        # # Get starting inventory of receiver, for reference
        # if isinstance(receiver, Tube):
        #     start_inventory = receiver.request_update_balls()
        # Try to launch a few times
        n = 0
        while True:
            # Launch!
            sender.request_eject_ball(send_fruit)
            # TODO: poll sooner than this
            time.sleep(1.)
            # See if the receiver has indeed gotten the ball
            receiver.request_detect_balls()
            # HACK: bypass check for Tubes -- should just look for an event
            if isinstance(receiver, Tube): # and receiver.inventory > start_inventory:
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
        # Let caller know where the ball is now, in case of autoselect
        return receive_fruit
    
    # Single transfer along a path -------------------------------------------
    
    def generate_path(self, sender, receiver) -> list:
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
        if current_carousel.hostname is not CAROUSEL_CENTER_HOSTNAME: 
            # ...a child tube, then that's next
            if isinstance(receiver, Tube) and receiver.carousel == current_carousel:
                path.append(receiver)     
            # ...anything else, then we have to get there via the center
            else: 
                path.append(self.carousels["center"])
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
    
    def do_path(self, path, send_fruit=None, xfer_fruit=None, fanfare=None):
        """ Run ball through a given path with optional fanfare """
        # Start from beginning of path   
        current_vehicle, current_fruit = path.pop(0), send_fruit
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
            current_fruit = self.handoff(
                current_vehicle, 
                next_vehicle,
                current_fruit, 
                xfer_fruit, 
                next_fanfare,
                next_fanfare_end)
            # Abort if handoff failed
            if not current_fruit:
                return False
            # Now we're somewhere new
            current_vehicle = next_vehicle
        return True

    def transfer(self, sender, receiver,
                 send_fruit=None,
                 xfer_fruit=None,
                 fanfare=None) -> bool:
        """ Transfer one ball from sender to receiver. """
        # If given a send carousel but no fruit, try to find an occupied pocket
        if send_fruit is None and isinstance(sender, Carousel):
            sender.request_detect_balls()
            for fruit, occupied in sender.balls_present.items():
                if occupied:
                    send_fruit = fruit
                    break
            else:
                return False
        # Generate and run path from sender to receiver
        # Path is fruit-agnostic
        path = self.generate_path(sender, receiver)
        return self.do_path(path, send_fruit, xfer_fruit, fanfare)        

    # Multiple transfers -----------------------------------------------------
    
    def transfer_all(self, sender, receivers,
                     fanfare_start=None,
                     fanfare_end=None) -> int:
        """ Move all balls from one vehicle to a list of receivers 
            Returns total transferred, might be useful for inventory """
        # Easier to use empty fanfare funcs than a bunch of conditionals
        fanfare_start = fanfare_start or self.nullfunc
        fanfare_end = fanfare_end or self.nullfunc 
        # If only one receiver is given, turn it into a list
        if not isinstance(receiver, (list, tuple)):
            receivers = [receivers]
        # Get first receiver
        receiver = receivers.pop(0)
        # Keep sending balls until sender is empty
        total_transferred = 0
        fanfare_start()
        while sender.has_balls():
            # If transfer fails for any reason (like receiver full)...
            if not self.transfer(sender, receiver):
                # ...return False if no receivers left. Sender is not empty.
                if not receivers:
                    fanfare_end()
                    return total_transferred
                # Otherwise, move to next receiver
                receiver = receivers.pop(0)
            total_transferred += 1
        # We did it, sender is empty!
        fanfare_end()
        return total_transferred
    
    # TODO: Optimize dump order
    def purge_vehicle(self, vehicle) -> bool:
        """ Fast-ish purge of a specified vehicle.
            - Center carousel will dump to edge carousels 
            - Edge carousels will dump to tubes 
            - Tubes will dump to other tubes """
        # Determine potential receivers
        # Note that the sender itself is removed from receivers later
        receivers = []
        # If vehicle is a string, assume it's a fruit name for a Carousel
        if isinstance(vehicle, str):
            vehicle = self.carousels[vehicle]
        # If emptying center carousel, dump into edge carousels
        if vehicle is self.carousels["center"]:
            receivers = self.all_carousels
        # If emptying another carousel, dump into local tubes first then others
        elif isinstance(vehicle, Carousel):
            receivers = vehicle.all_tubes
            for tube in self.all_tubes:
                if tube not in receivers:
                    receivers.append(tube)
        # If emptying a tube, dump into other local tube and then remote ones
        elif isinstance(vehicle, Tube):
            receivers = vehicle.carousel.all_tubes
            for tube in self.all_tubes:
                if tube not in receivers:
                    receivers.append(tube)
        # Don't send anything to self or to center carousel
        for bad_receiver in (vehicle, self.carousels["center"]):
            if bad_receiver in receivers:
                receivers.remove[bad_receiver]
        # Dump into one receiver until full, then move to next
        return self.transfer_all(vehicle, receivers)

    def equalize_tubes(self, tubes=None) -> bool:
        """ Equalize inventory between a list of tubes as best as possible
            Equalizes all tubes by default """
        tubes = tubes or self.all_tubes
        # Equalize routine
        while True:
            # Sort tubes from emptiest to fullest
            tubes.sort(key=lambda tube: tube.request_detect_balls())
            # Find transfer amount to (try to) equalize max and min tubes
            max_tube, min_tube = tubes[-1], tubes[0]
            to_transfer = floor((max_tube.inventory - min_tube.inventory) / 2)
            # If nothing left to transfer, we're done
            if not to_transfer:
                return True
            # Do transfers, abort if any don't work
            for i in range(to_transfer):
                if not self.transfer(max_tube, min_tube):
                    return False
    
    def distribute_to_tubes(self, senders=None, receivers=None, equalize=False) -> bool:
        """ Distribute balls from senders into given tubes """
        # If receivers not specified, assume it's all tubes
        receivers = receivers or self.all_tubes
        # If senders not specified, get list of everything that's not a sender
        if not senders:
            senders = self.all_carousels + self.all_tubes
            for receiver in receivers:
                if receiver in senders:
                    senders.remove(receiver)
        # Transfer balls from all senders into emptiest receiver tubes
        for sender in senders:
            while sender.has_balls():
                receiver = min(receiver_tubes, key=lambda t: t.inventory)
                if not self.transfer(sender, receiver):
                    return False
        # Optionally, equalize receiver tubes afterward
        if not equalize:
            return True
        return self.equalize_tubes(receiver_tubes)
            