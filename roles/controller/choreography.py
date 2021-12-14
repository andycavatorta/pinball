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
class Fruit_Names():
    COCO = "coco"
    MANGO = "mango"
    SANDIA = "sandia"
    NARANJA = "naranja"
    PINA = "pina"
    ANY = "any"

class Tube_Names():
    TRUEQUE = "trueque"
    DINARO = "dinero"

class Choreography(): 
    """
    

    """
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
        self.expected = {} # a list of expected return values

    def home(self):
        self.expected = {
            "carousel_1":[b"event_destination_reached",None],
            "carousel_2":[b"event_destination_reached",None],
            "carousel_3":[b"event_destination_reached",None],
            "carousel_4":[b"event_destination_reached",None],
            "carousel_5":[b"event_destination_reached",None],
            "carousel_center":[b"event_destination_reached",None],
        }
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_5","pina","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_4","sandia","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_3","mango","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_2","naranja","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_1","coco","back")
        self.hosts.pinballmatrix.cmd_rotate_carousel_to_target("carousel_center","coco","coco")
 
    def transfer(self, batch):
        pass

#############################################
###  C H E C K S  A N D  R E M E D I E S  ###
#############################################

def check_if_tube_is_empty(station_fruit_name, tube_name):
    pass

def check_if_tube_is_full(station_fruit_name, tube_name):
    pass

def check_if_pocket_has_ball(carousel_name, fruit_name):
    pass

def check_if_carousel_position_is_within_tolerance(carousel_name):
    pass

def check_if_tube_ball_bounced():
    pass

def check_if_tube_ball_stuck():
    pass

def ():
    pass

########################
###  E L E M E N T S ###
########################

class Transfer_Ball_From_Tube_To_Edge_Carousel():
    def __init__(self, tb, hosts):
        """
        steps:
        check if ball in tube
        check if edge carousel pocket is empty
        rotate edge carousel to tube
        check if carousel position is precise enough
        launch tube
        sleep x ms
        check if ball detected in pocket
            remedy: tube ball not detected in pocket
        report success 
        """
        self.hosts = hosts
        self.tb = tb
        self.steps = []
    def begin(self, 
            callback, 
            station_fruit_name, 
            tube_name, 
            pocket_fruit_name, 
            fanfare=None):
        pass
        """
        """

class Transfer_Ball_From_Edge_Carousel_To_Tube():
    def __init__(self, tb, hosts):
        """
        steps:
        check if tube has capacity
        check if edge carousel pocket has ball
        rotate edge carousel pocket to tube
        check if carousel position is precise enough
        eject ball
        check if ball motion detected in tube
        report success 
        """
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            station_fruit_name, 
            tube_name, 
            pocket_fruit_name, 
            fanfare=None):
        pass

class Transfer_Ball_From_Edge_Carousel_To_Center_Carousel():
    def __init__(self, tb, hosts):
        """
        steps:
        check if edge carousel pocket has ball
        check if center carousel pocket is empty
        rotate edge carousel pocket to center
        rotate center carousel pocket to edge carousel
        eject ball
        check if edge carousel pocket has no ball
        check if center carousel pocket has ball
        report
        """
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            station_fruit_name, 
            edge_pocket_fruit_name, 
            center_pocket_fruit_name, 
            fanfare=None):
        pass

class Transfer_Ball_From_Center_Carousel_To_Edge_Carousel():
    def __init__(self, tb, hosts):
        """
        steps:
        check if edge carousel pocket has no ball
        check if center carousel pocket has ball
        rotate edge carousel pocket to center
        rotate center carousel pocket to edge carousel
        eject ball
        check if edge carousel pocket has no ball
        check if center carousel pocket has ball
        report
        """
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            station_fruit_name, 
            edge_pocket_fruit_name=None, 
            center_pocket_fruit_name=None, 
            fanfare=None):
            edge_pocket_fruit_name = edge_pocket_fruit_name or station_fruit_name 
            center_pocket_fruit_name = center_pocket_fruit_name or station_fruit_name

        pass

##########################
###  C O M P O U N D S ###
##########################

class Transfer_Ball_From_Local_Carousel_To_Remote_Carousel():
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
        self.steps = []
    def begin(self, 
            callback, 
            origin_station_fruit_name, 
            origin_pocket_fruit_name, 
            center_pocket_fruit_name, 
            destination_station_fruit_name, 
            destination_pocket_fruit_name, 
            fanfare=None):
        pass
        """
        Transfer_Ball_From_Edge_Carousel_To_Center_Carousel
        Transfer_Ball_From_Center_Carousel_To_Edge_Carousel
        """

class Transfer_Ball_From_Local_Tube_To_Remote_Carousel():
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            origin_tube_name,
            origin_station_fruit_name, 
            origin_pocket_fruit_name, 
            center_pocket_fruit_name, 
            destination_station_fruit_name, 
            destination_pocket_fruit_name, 
            fanfare=None):
        pass
        """
        Transfer_Ball_From_Tube_To_Edge_Carousel
        Transfer_Ball_From_Edge_Carousel_To_Center_Carousel
        Transfer_Ball_From_Center_Carousel_To_Edge_Carousel
        """

class Transfer_Ball_From_Local_Carousel_To_Remote_Tube():
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            origin_station_fruit_name, 
            origin_pocket_fruit_name, 
            center_pocket_fruit_name, 
            destination_station_fruit_name, 
            destination_pocket_fruit_name,
            remote_tube_name, 
            fanfare=None):
        pass
        """
        Transfer_Ball_From_Edge_Carousel_To_Center_Carousel
        Transfer_Ball_From_Center_Carousel_To_Edge_Carousel
        Transfer_Ball_From_Edge_Carousel_To_Tube
        """

class Transfer_Ball_From_Local_Tube_To_Remote_Tube():
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback,
            origin_tube_name,
            origin_station_fruit_name, 
            origin_pocket_fruit_name, 
            center_pocket_fruit_name, 
            destination_station_fruit_name, 
            destination_pocket_fruit_name, 
            remote_tube_name, 
            fanfare=None):
        pass
        """
        Transfer_Ball_From_Tube_To_Edge_Carousel
        Transfer_Ball_From_Edge_Carousel_To_Center_Carousel
        Transfer_Ball_From_Center_Carousel_To_Edge_Carousel
        Transfer_Ball_From_Edge_Carousel_To_Tube
        """

class Transfer_Ball_From_Local_Tube_To_Local_Tube():
    def __init__(self, tb, hosts):
        self.hosts = hosts
        self.tb = tb
    def begin(self, 
            callback, 
            origin_station_fruit_name, 
            origin_tube_name, 
            center_pocket_fruit_name, 
            destination_tube_name, 
            fanfare=None):
        pass
        """
        Transfer_Ball_From_Tube_To_Edge_Carousel
        Transfer_Ball_From_Edge_Carousel_To_Tube

        """

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

    #def dispatch(self, ): #wreceives commands and feedback info












