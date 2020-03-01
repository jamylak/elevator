''' Controlls and handles MULTIPLE elevators '''
from constants import ElevatorDirection
from copy import deepcopy


class MultipleElevatorController(object):
    '''
    Controlls MULTIPLE elevators and summons the best one
    for the people in the buildings based off a simulation of which
    elevator will get there in the least steps
    '''

    def __init__(self, elevators=None):
        super().__init__()
        if elevators is None:
            elevators = []
        self.elevators = elevators

    def step_forward(self):
        for elevator in self.elevators:
            elevator.step_forward()

    def call_elevator(self, from_level:int, direction:ElevatorDirection):
        ''' Find the closest elevator either ALREADY on its way
        or not... based off how many STEPS it will take to REACH this level
        It can ONLY STOP and OPEN its doors for us if it is going in the
        SAME direction '''
        fastest_elevator = min(
            self.elevators,
            key=lambda e: MultipleElevatorController.steps_to_get_to_level(
                                        e, from_level, direction)
        )
        fastest_elevator.call_elevator(from_level, direction)
        return fastest_elevator

    @staticmethod
    def steps_to_get_to_level(elevator, from_level:int,
                              direction:ElevatorDirection):
        '''
        Calculate steps it would take to reach a level_no
        when summoning a lift to be able to compare lifts from a summoning
        perspective and know which one will be faster for us.

        Simulate each lift and see how long it would take in steps
        which include open / close door because that takes time too
        '''
        num_steps = 0
        elevator_copy = deepcopy(elevator)
        elevator_copy.call_elevator(from_level, direction)

        while True:
            if (elevator_copy.direction == direction and
                    elevator_copy.current_level == from_level):
                # we made it to our level! in simulated (num_steps)
                return num_steps
            num_steps += 1
            elevator_copy.step_forward()
