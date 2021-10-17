"""
This module coordinates the the carousels, matrix motors, and tubes
to pass balls between tubes and carousels


the elements of the motions:

move all carousels into game-start positions

move carousel fruit to positon (front, back, left, right)

launch ball to carousel

verify 

"""
"""
tubes = [
    station[4].tubes[1],
    station[4].tubes[0],
    station[3].tubes[1],
    station[3].tubes[0],
    station[2].tubes[1],
    station[2].tubes[0],
    station[1].tubes[1],
    station[1].tubes[0],
    station[0].tubes[1],
    station[0].tubes[0],
]


ball_homes = {
    coco:[tube_left,tube_right,coco,sandia,pina,naranja,mango],
    sandia:[tube_left,tube_right,coco,sandia,pina,naranja,mango],
    pina:[tube_left,tube_right,coco,sandia,pina,naranja,mango],
    naranja:[tube_left,tube_right,coco,sandia,pina,naranja,mango],
    mango:[tube_left,tube_right,coco,sandia,pina,naranja,mango]
}

transfer( # returns values and throws exceptions
    (
        (coco.tube_left, mango.mango)# origin, destination
    ),# batch of transfer
)
"""
"""

local abstractions for tubes, carousels, motors, etc

transfer function
    automatically updates local abstractions

routines - 
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
class Routine_Home():
    """
    set all carousels to their home positions
    """
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_5","pina","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_4","sandia","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_3","mango","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_2","naranja","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_1","coco","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","coco","coco")




class Choreography(): 
    """
    Is Choreography threaded?
    the transfer function should return values synchronously
    """
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb

    def transfer(self, batch):
        """
        basic algorithms
            



        cases for double transfer:

        cases for single transfer:
            local tube to local carousel
                tube to adjacent carousel
            local tube to remote carousel
                tube to adjacent carousel
                local carousel to remote carousel
            local tube to local tube
                tube to adjacent carousel
                carousel to adjacent tube
            local tube to remote tube
                tube to adjacent carousel
                local carousel to remote carousel
                (remote) carousel to adjacent tube
            local carousel to local tube
                carousel to adjacent tube
            local carousel to remote carousel
                local carousel to remote carousel
            local carousel to remote tube
                local carousel to remote carousel
                (remote) carousel to adjacent tube

        elements of transfer:
            tube to adjacent carousel
                confirm pocket is empty
                confirm ball count in tube is > 0
                rotate_carousel_to_position
                    confirm position reached
                fire tube solenoid
                    confirm ball sensed in pocket
                        if not, confirm motion detected in tube
                            if not error state
                        fire again? how many tries?
                ? rotate carousel to end position?

            carousel to adjacent tube
                confirm pocket is not empty
                confirm tube is not full
                rotate_carousel_to_position
                    confirm position reached
                eject ball from pocket
                    confirm poocket empty
                    confirm motion detected in tube
                ? rotate carousel to end position?
                
            center carousel to outer carousel # used for clearing carousels after error shutdown
                confirm center carousel pocket is not empty
                confirm outer carousel pocket is empty
                rotate center_carousel_to_position
                    confirm position reached
                rotate outer_carousel_to_position
                    confirm position reached
                eject ball from center pocket
                    confirm center pocket vacant
                    confirm outer pocket occupied
                    
            local carousel to remote carousel (through center)
                confirm local pocket is not empty
                confirm remote pocket is empty
                confirm center pocket is empty
                rotate center carousel to position
                    confirm position reached
                rotate remote carousel to position
                    confirm position reached
                rotate local carousel to position
                    confirm position reached
                eject ball from local pocket
                    confirm local pocket empty
                    confirm center pocket not empty
                rotate center carousel to position
                    confirm position reached
                eject ball from center pocket
                    confirm center pocket empty
                    confirm remote pocket not empty
                ? rotate carousels to end position?



        """
        # work on single-transfer case first
        transaction = batch[0]
        origin, destination = transaction















