''' These represent useful constants that keep track or
represent the Elevator Status'''
from enum import Enum, IntEnum


class ElevatorCommand(Enum):
    ''' Represents a COMMAND to the Elevator system to go
    Up, Down, Open Door or Close the door'''
    UP = "UP_1"
    DOWN = "DOWN_1"
    OPEN_DOOR = "OPEN_DOOR"
    CLOSE_DOOR = "CLOSE_DOOR"


class ElevatorStatus(Enum):
    ''' Represents the status of the elevator. It can only be
    one of 3, Going Down, Idle, or Going Up'''
    MOVING_DOWN = "moving down"
    IDLE = "idle"
    MOVING_UP = "moving up"


class ElevatorDoorStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


class ElevatorDirection(IntEnum):
    ''' Whether the lift is going up or down. Used to summon the lift '''
    UP = 1
    DOWN = -1
