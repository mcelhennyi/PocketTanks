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
    LEFT = 0
    RIGHT = 1
    INC_ANG = 2
    DEC_ANG = 3
    INC_PWR = 4
    DEC_PWR = 5
    FIRE = 6


class StateEnum:

    TANK1_LOCATION = 0
    TANK1_HEALTH = 1
    TANK1_POWER = 2
    TANK1_ANGLE = 3

    TANK2_LOCATION = 4
    TANK2_HEALTH = 5
    TANK2_POWER = 6
    TANK2_ANGLE = 7


class BaseAgent:
    def __init__(self):

        self.memory = deque(maxlen=2000)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        pass

    def replay(self, batch_size):
        pass

    def load(self, name):
        pass

    def save(self, name):
        pass
