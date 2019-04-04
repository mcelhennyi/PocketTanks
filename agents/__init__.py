from collections import deque
from enum import Enum

"""
States:
    - Tank 1 location
    - Tank 1 health
    - Tank 1 Power
    - Tank 1 Angle
    - Tank 2 location
    - Tank 2 health
    - Tank 2 Power
    - Tank 2 Angle
    
Available Actions:
    - Move left
    - move right
    - increase power
    - decrease power
    - increase angle
    - decrease angle
    - fire

"""


class ActionEnum:
    INC_ANG = 0
    DEC_ANG = 1
    INC_PWR = 2
    DEC_PWR = 3
    FIRE = 4

    # Hidden from AI for now
    LEFT = 5
    RIGHT = 6


class StateEnum:

    TANK1_LOCATION_X = 0
    TANK1_LOCATION_Y = 1
    TANK1_HEALTH = 2
    TANK1_POWER = 3
    TANK1_ANGLE = 4

    TANK2_LOCATION_X = 5
    TANK2_LOCATION_Y = 6
    TANK2_HEALTH = 7
    TANK2_POWER = 8
    TANK2_ANGLE = 9


class BaseAgent:
    def __init__(self):

        self._memory = deque(maxlen=2000)

    def remember(self, state, action, reward, next_state, done):
        self._memory.append((state, action, reward, next_state, done))

    def act(self, state):
        pass

    def replay(self, batch_size):
        pass

    def load(self, name):
        pass

    def save(self, name):
        pass
