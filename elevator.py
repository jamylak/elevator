#!/usr/bin/python3
from collections import defaultdict
from constants import (ElevatorCommand, ElevatorStatus, ElevatorDirection,
                       ElevatorDoorStatus)
from exceptions import ElevatorOutOfBoundsException
from itertools import tee

# Helper function from https://docs.python.org/3/library/itertools.html
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Elevator(object):
    '''
    A class representating an Elevator

    Attributes:
      levels (list): eg. ["P3", "P2", "P1", "G", "1", "2"]
             Internally these will be referenced by index eg. 0, 1, 2, 3, ..
      current_level (int): integer repreenting current level.
             0 = Ground. 1,2,3 etc
             Below Ground (if exists) = -1, -2, -3 etc
      levels_to_visit (dict):  Dictionary of levels to visit.
             eg. {level_no: {DIRECTION_UP, DIRECTION_DOWN}}
             We want to visit this level 1 time on the way up
             and once on the way down...
      door_status (ElevatorDoorStatus): .OPEN or .CLOSED
      direction (ElevatorDirection): .UP or .DOWN
      current_command (ElevatorCommand): Represents the current command in use
    '''

    def __init__(self, levels:list, current_level:int=0,
                 door_status:ElevatorDoorStatus=ElevatorDoorStatus.CLOSED,
                 direction:ElevatorDirection=ElevatorDirection.UP):
        if len(levels) <= 1:
            raise ValueError("You neeed at least 2 levels "
                             "otherwise why do you even have a lift?")
        super().__init__()

        self.levels = levels
        self.current_level = current_level
        self.levels_to_visit = defaultdict(set)
        self.door_status = door_status
        self.direction = direction
        self.current_command = None

    @property
    def is_going_up(self):
        return self.direction == ElevatorDirection.UP

    @property
    def num_levels(self):
        return len(self.levels)

    @property
    def status(self):
        ''' Whether lift is going up ie. True or down ie. False '''
        if self.current_command in (None,
                                    ElevatorCommand.OPEN_DOOR,
                                    ElevatorCommand.CLOSE_DOOR):
            return ElevatorStatus.IDLE
        elif self.is_going_up:
            return ElevatorStatus.MOVING_UP
        else:
            return ElevatorStatus.MOVING_DOWN

    def gen_commands_lvl_to_lvl(self, start_level, target_level):
        '''
        Connect these start_level <-> target_level with commands and
        OPEN_DOOR & CLOSE_DOOR at the end

        eg. start_level = 0, target_level = 3
        Returns: [UP_1, UP_1, UP_1, OPEN_DOOR, CLOSE_DOOR]
        '''
        if start_level == target_level:
            return
        if start_level < target_level:
            for i in range(start_level, target_level):
                yield ElevatorCommand.UP
        else:
            for i in range(start_level, target_level, -1):
                yield ElevatorCommand.DOWN

        yield ElevatorCommand.OPEN_DOOR
        yield ElevatorCommand.CLOSE_DOOR

    def generate_commands(self):
        '''
        Generates commands for the LIFT system to execute

        eg. elevator at level 0, 1 person inside select to stop on 3,
        Returns: [UP_1, UP_1, UP_1,OPEN_DOOR, CLOSE_DOOR].
        '''
        if self.direction in self.levels_to_visit[self.current_level]:
            # If we are due to visit this level we are currently on
            yield ElevatorCommand.OPEN_DOOR
            yield ElevatorCommand.CLOSE_DOOR
        elif self.door_status == ElevatorDoorStatus.OPEN:
            # Our doors are open because we are leaving this current level
            yield ElevatorCommand.CLOSE_DOOR

        # 1. First lets find ALL levels in the current direction we
        # are going in order. Then lets remove any we aren't visiting
        # in our current direction.
        # eg. if we are going up, go as FAR up as possible
        if self.is_going_up:
            current_dir_all_levels = range(self.current_level,
                                           self.num_levels)
        else:
            current_dir_all_levels = range(self.current_level, -1, -1)
        # now filter out levels we aren't visiting in our current direction
        current_dir_visit_levels = [lvl for lvl in current_dir_all_levels
                            if self.direction in self.levels_to_visit[lvl]]

        # 2. Now let's find all levels we'd visit on the way BACK
        # eg. if we are going up, we just went as FAR UP as we can,
        # now go all the way DOWN
        if self.is_going_up:
            reverse_dir_all_levels = range(self.num_levels - 1, -1, -1)
        else:
            reverse_dir_all_levels = range(0, self.num_levels)
        reverse_dir_visit_levels = [lvl for lvl in reverse_dir_all_levels
          if ElevatorDirection(-self.direction) in self.levels_to_visit[lvl]]

        # 3. NOW let's find all levels if we flipped around AGAIN
        # and came back to out current level, after doing #1 and #2
        if self.is_going_up:
            passed_current_dir_all_levels = range(0, self.current_level)
        else:
            passed_current_dir_all_levels = range(self.num_levels,
                                                  self.current_level, -1)
        final_return_visit_levels = [
            lvl for lvl in passed_current_dir_all_levels
            if self.direction in self.levels_to_visit[lvl]
        ]

        # Now lets put all the levels we want to visit IN ORDER together
        levels = ([self.current_level] + current_dir_visit_levels +
                  reverse_dir_visit_levels + final_return_visit_levels)

        # Now lets connect all the commands joining all these visits
        for level1, level2 in pairwise(levels):
            yield from self.gen_commands_lvl_to_lvl(level1, level2)

    def add_level(self, level_no:int, direction):
        '''
        This selects levels WITHOUT moving yet... and then
        we return the STEPS eg.
        e.g. elevator at level 0, 1 person inside select to stop on 3
        [UP_1, UP_1, UP_1, OPEN_DOOR, CLOSE_DOOR]
        '''
        if level_no < 0 or level_no >= self.num_levels:
            raise ElevatorOutOfBoundsException("This level can't be reached!")

        # Don't add in our current levele in our current direction
        if not (level_no == self.current_level and
                self.direction == direction):
            self.levels_to_visit[level_no].add(direction)

    def select_level(self, level_no:int, direction=None):
        ''' Select a level to visit and specify in which direction
        we want to visit it in '''
        if direction is None:
            # If there is no direction specified,
            # It means someone inside the lift is selecting a level
            # So choose the most convenient direction

            # Level 0 and MAX LEVEL can only be UP / DOWN respectively
            if level_no == 0:
                direction = ElevatorDirection.UP
            elif level_no == self.num_levels - 1:
                direction = ElevatorDirection.DOWN
            # Choose our current direction if we will pass this level
            # on our current trajectory, else choose our return direction
            elif (self.is_going_up and self.current_level < level_no
                or not self.is_going_up and self.current_level > level_no):
                # this could add impossible directions if they are at TOP or 0
                direction = self.direction
            else:
                direction = ElevatorDirection(-self.direction)
        self.add_level(level_no, direction)
        # We may need to reverse our direction to reach this level
        self.reset_direction()

    def call_elevator(self, from_level:int, direction:ElevatorDirection):
        '''
        Summon (call) the lift. Follow this algorithm
        eg. going up go as far up high as you can then as far low as you can
        and then back up again (or inversed)
        '''
        assert 0 <= from_level  < self.num_levels
        if (from_level == self.num_levels - 1
            and direction == ElevatorDirection.UP or
            from_level == 0 and direction == ElevatorDirection.DOWN):
            # We can't go Down from 0 or UP from the MAX LEVEL
            raise ElevatorOutOfBoundsException("Impossible Action")
        self.select_level(from_level, direction)

    def reset_direction(self):
        ''' Check if there are no levels left in our direction
        if so then let's reverse direction '''
        if not any(self.levels_to_visit.values()):
            return
        max_level = max(lvl for lvl in self.levels_to_visit
                        if self.levels_to_visit[lvl])
        min_level = min(lvl for lvl in self.levels_to_visit
                        if self.levels_to_visit[lvl])

        # If we are going up and above the max level we need to visit
        # or we are going down and lower than the min level we need to visit
        # reverse our direction as long as we aren't currently stopping
        # at a level we need to visit
        if ((self.is_going_up and self.current_level >= max_level or
             not self.is_going_up and self.current_level <= min_level)
            and self.direction not in
                self.levels_to_visit[self.current_level]):
            self.direction = ElevatorDirection(-self.direction)

    def step_forward(self):
        ''' Step forward our elevator through and run its
        next command '''
        try:
            self.current_command = next(self.generate_commands())
            if self.current_command == ElevatorCommand.UP:
                self.current_level += 1
            elif self.current_command == ElevatorCommand.DOWN:
                self.current_level -= 1
            elif self.current_command == ElevatorCommand.OPEN_DOOR:
                self.door_status = ElevatorDoorStatus.OPEN
                # weve now visited this level in out current direction
                self.levels_to_visit[self.current_level].discard(
                                                      self.direction)
            elif self.current_command == ElevatorCommand.CLOSE_DOOR:
                self.door_status = ElevatorDoorStatus.CLOSED
            self.reset_direction()
        except StopIteration:
            # Nothing to do right now
            pass
