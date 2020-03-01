import unittest
import elevator
from constants import (ElevatorCommand, ElevatorStatus, ElevatorDoorStatus,
                       ElevatorDirection)
from exceptions import ElevatorOutOfBoundsException
from multiple_elevator_controller import MultipleElevatorController


class TestElevatorSelections(unittest.TestCase):

    def test_elevator_go_below_ground_floor(self):
        '''
        If ground floor is the lowest we cannot go lower
        Make sure it raises appropriate ElevatorOutOfBoundsException
        '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        with self.assertRaises(ElevatorOutOfBoundsException):
            elevator1.select_level(-1)

    def test_elevator_go_above_roof(self):
        '''
        Try to go above roof and make sure it
        raises appropriate ElevatorOutOfBoundsException
        '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        elevator1.select_level(4)
        with self.assertRaises(ElevatorOutOfBoundsException):
            elevator1.select_level(5)

    def test_elevator_go_up_down(self):
        ''' Test some basic UP and DOWN commands '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        # go to level 3
        elevator1.select_level(3)
        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.UP, ElevatorCommand.UP, ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR, ElevatorCommand.CLOSE_DOOR],
        )

        elevator1.step_forward()
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.MOVING_UP)

        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.UP, ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR, ElevatorCommand.CLOSE_DOOR],
        )

        elevator1.step_forward()
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.MOVING_UP)

        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR, ElevatorCommand.CLOSE_DOOR],
        )

        elevator1.step_forward()
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.MOVING_UP)

        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.OPEN_DOOR, ElevatorCommand.CLOSE_DOOR],
        )

        elevator1.step_forward()
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.OPEN)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)

        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.CLOSE_DOOR],
        )

        # We finished getting to level 3, nothing left to do
        elevator1.step_forward()
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(list(elevator1.generate_commands()), [])
        self.assertEqual(elevator1.current_level, 3)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        # Now test GOING DOWN
        elevator1.select_level(0)
        self.assertEqual(
            list(elevator1.generate_commands()),
            [ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR, ElevatorCommand.CLOSE_DOOR],
        )
        self.assertEqual(elevator1.direction, ElevatorDirection.DOWN)

    def test_elevator_same_direction_out_of_sequence(self):
        ''' Test multiple people select floors in
        same direction out of sequence '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        elevator1.select_level(4)
        elevator1.select_level(3)
        elevator1.select_level(2)
        elevator1.select_level(1)
        # this is our current level, should have no affect
        elevator1.select_level(0)
        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP, # go to level 1
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP, # go to level 2
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP, # go to level 3
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP, # go to level 4
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

    def test_elevator_opposite_direction(self):
        ''' Test multiple people select floors in opposite direction '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        # first go straight to level 2 from ground
        elevator1.select_level(2)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )
        elevator1.step_forward()
        elevator1.step_forward()
        elevator1.step_forward()
        elevator1.step_forward()

        # Make sure we are on level 2
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.current_level, 2)
        self.assertEqual(list(elevator1.generate_commands()), [])

        # Now let's select level 4,
        # THEN level 1, and make sure it works correctly
        elevator1.select_level(4)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # select level 1
        elevator1.select_level(1)
        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # Now STEP FORWARD to LEVEL 4 and see if elevator DIRECTION is changed
        elevator1.step_forward()
        elevator1.step_forward()
        elevator1.step_forward() # open door on level 4
        elevator1.step_forward() # close door on level 4
        elevator1.step_forward()
        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )
        self.assertEqual(elevator1.direction, ElevatorDirection.DOWN)

    def test_elevator_same_direction_individually(self):
        ''' Test multiple people select floors in same
        direction individually '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        # first go straight to level 2 from ground
        elevator1.select_level(2)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # now let's select level 1
        elevator1.select_level(1)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )


        # now select level 3
        elevator1.select_level(3)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

    def test_elevator_same_floor(self):
        ''' test selecting the same floor  '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.door_status, ElevatorDoorStatus.CLOSED)
        self.assertEqual(elevator1.status, ElevatorStatus.IDLE)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

        # first go straight to level 2 from ground
        elevator1.select_level(2)
        elevator1.select_level(2)
        elevator1.select_level(2)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        self.assertEqual(elevator1.direction, ElevatorDirection.UP)


class TestElevatorCalls(unittest.TestCase):

    def test_call_elevator_at_floor_3_from_ground(self):
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        elevator1.call_elevator(3, ElevatorDirection.UP)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        self.assertEqual(elevator1.direction, ElevatorDirection.UP)

    def test_multiple_people_dif_floors_same_direction(self):
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        elevator1.call_elevator(3, ElevatorDirection.UP)
        elevator1.call_elevator(1, ElevatorDirection.UP)
        elevator1.call_elevator(2, ElevatorDirection.UP)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # Go up
        elevator1.step_forward()

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # open door
        elevator1.step_forward()

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        # close door
        elevator1.step_forward()

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

        self.assertEqual(elevator1.direction, ElevatorDirection.UP)
        self.assertEqual(elevator1.current_level, 1)

        for i in range(6):
            elevator1.step_forward()

        # finish the sequence
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)
        self.assertEqual(elevator1.current_level, 3)

    def test_call_outside_and_inside_same_direction(self):
        ''' multiple people both calling outside and
        selecting stop inside to go same direction '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        elevator1.call_elevator(3, ElevatorDirection.UP)
        elevator1.call_elevator(1, ElevatorDirection.UP)
        elevator1.select_level(2)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )

    def test_multiple_people_diff_floors_opposite_direction(self):
        ''' multiple people both calling outside and
        selecting stop inside to go same direction '''
        elevator1 = elevator.Elevator("G 1 2 3 4".split())
        self.assertEqual(elevator1.direction, ElevatorDirection.UP)
        # Call the elevator
        elevator1.call_elevator(3, ElevatorDirection.UP)
        elevator1.call_elevator(1, ElevatorDirection.UP)
        elevator1.call_elevator(1, ElevatorDirection.DOWN)
        # select a level from inisde
        elevator1.select_level(2)

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )
        for i in range(8):
            # get to level 3
            elevator1.step_forward()

        self.assertEqual(elevator1.direction, ElevatorDirection.DOWN)

        elevator1.call_elevator(0, ElevatorDirection.UP)
        elevator1.call_elevator(4, ElevatorDirection.DOWN)

        # Now we have to go down to level 1 from that
        # guy above who's been waiting since the start
        # then we go to Ground to service the new guy who clicked up
        # and all the way to 4 to for the new guy who clicked down

        self.assertEqual(list(elevator1.generate_commands()),
            [
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.DOWN,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.DOWN,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.UP,
             ElevatorCommand.OPEN_DOOR,
             ElevatorCommand.CLOSE_DOOR,
            ],
        )
        for i in range(14):
            elevator1.step_forward()

        self.assertEqual(elevator1.direction, ElevatorDirection.DOWN)
        self.assertEqual(elevator1.current_level, 4)


class TestMultipleElevators(unittest.TestCase):
    ''' Test our multiple elevator controller  '''

    def test_multiple_elevators_basic(self):
        ''' Test 2 elevators and make sure it chooses the right one '''
        LEVELS = "G 1 2 3 4 5 6 7 8 9".split()
        elevator1 = elevator.Elevator(LEVELS)
        elevator2 = elevator.Elevator(LEVELS)

        controller = MultipleElevatorController([elevator1, elevator2])

        self.assertEqual(elevator1.direction, ElevatorDirection.UP)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator2.direction, ElevatorDirection.UP)
        self.assertEqual(elevator2.current_level, 0)

        # Let's move elevator1 to level 8 so they are far away
        elevator1.select_level(8)
        while next(elevator1.generate_commands(), None):
            elevator1.step_forward()

        self.assertEqual(elevator1.current_level, 8)

        # Now elevator1 has reached level 8
        # So let's summon an elevator to go to level 2
        # it should pick elevator2
        self.assertEqual(controller.call_elevator(2, ElevatorDirection.UP),
                         elevator2)

    def test_multiple_elevators_advanced(self):
        ''' Test 3 elevators and make sure it chooses the right one '''
        LEVELS = "G 1 2 3 4 5 6 7 8 9 10 11".split()
        elevator1 = elevator.Elevator(LEVELS)
        elevator2 = elevator.Elevator(LEVELS)
        elevator3 = elevator.Elevator(LEVELS)
        self.assertEqual(elevator1.current_level, 0)
        self.assertEqual(elevator2.current_level, 0)
        self.assertEqual(elevator3.current_level, 0)

        controller = MultipleElevatorController([
            elevator1, elevator2, elevator3])

        # Let's move elevator1 to level 10 so they are far away
        elevator1.select_level(10)
        while next(elevator1.generate_commands(), None):
            elevator1.step_forward()
        self.assertEqual(elevator1.current_level, 10)

        # Let's move elevator2 to level 6 so they are far away
        elevator2.select_level(6)
        while next(elevator2.generate_commands(), None):
            elevator2.step_forward()
        self.assertEqual(elevator2.current_level, 6)

        # Now let's summon a lift to go DOWN at level 5
        # it should be lift 2
        self.assertEqual(controller.call_elevator(5, ElevatorDirection.DOWN),
                         elevator2)

        # Now let's summon a lift to go UP at level 2
        # it should be lift 3
        self.assertEqual(controller.call_elevator(2, ElevatorDirection.UP),
                         elevator3)

        # Now let's summon a lift to go DOWN to level 9
        # it should be lift 1
        self.assertEqual(controller.call_elevator(9, ElevatorDirection.DOWN),
                         elevator1)


if __name__ == '__main__':
    unittest.main()
