import os
import queue
import threading
import time

class Mode_Reset(threading.Thread):
    """
    In RESET mode, the controller returns all balls to starting state.
        balls are exchanged via carousels to equalize total number of balls per gamestation
        in final state
            left stack is empty
            right stack has pre-defined max number of balls
            all carousels pockets are filled
        all carousels are in correct positions

    """
    def __init__(self,tb, host_states):
        threading.Thread.__init__(self)
        self.tb = tb 
        self.host_states = host_states
        self.queue = queue.Queue()
    def calculate_steps(self):
        """
        How to represent the steps?
            topic + message would be good because it's not an intermediate system
        Where do movements get verified?  
            Should be in a whole-matrix-exchange system including the matrix, carousels, and stacks.
        Phase 1: 
            fill all carousels 
        Phase 2: 
            fill the right stack until full or until all gamestation balls are used
        Phase 3: 
            move excess balls in left tubes through matrix to unfilled right tubes of other gamestations
            what is the algorithm?
        """

    def request_current_sensor_nominal(self, message, origin, destination)
        # TODO: Make the ACTUAL test here.
        return True
        
    def add_to_queue(self, topic, message, origin, destination):
        """
        receives messages about stacks, carousels, matrix
        """
        self.queue.put((topic, message, origin, destination))
    def run(self):
        while True:
            try:
                topic, message, origin, destination = self.queue.get(True) #we may not need these values. Just the event is may be important.
                # if any system tests return False, stop Safety_Enable, cutting higher power, write to log
                # if any tests do not return before timestamp, stop Safety_Enable, cutting higher power, write to log
                # if all tests return True before timestamp, 
                    # if inventory_complete == True
                        # transition to settings.Game_Modes.RESET
                    # else
                        # transition to settings.Game_Modes.INVENTORY
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print(e, repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))
