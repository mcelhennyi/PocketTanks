import random

from agents import BaseAgent, ActionEnum, StateEnum
from sprites import X, Y


class DumbAgent(BaseAgent):
    def __init__(self):
        BaseAgent.__init__(self)

        self._first_shot = True
        self._last_shot_pwr = 0
        self._last_shot_ang = 0

        self._target_pwr = 0
        self._target_ang = 0

        self._distance_to_target = 1024
        self._last_impact = [0, 0]

        self._ready_to_fire = True

        self._exploration_value = 10

    def last_impact(self, location):
        self._last_impact[X] = location[X]
        self._last_impact[Y] = location[Y]

        # Lets decay our exploration value with shots
        self._exploration_value *= 0.9

        if self._exploration_value < 1:
            self._exploration_value = 1

    def act(self, state, target_offset=0):
        """

        :param state:
        :param target_offset: set to 5 to switch between active tank as self
        :return:
        """

        if self._first_shot:
            # If its our first shot, lets randomly guess at the location to shoot at
            self._target_pwr, self._target_ang = self._generate_first_shot([state[StateEnum.TANK1_LOCATION_X+target_offset], state[StateEnum.TANK1_LOCATION_Y+target_offset]])
        else:
            # This is second and onward shot, let slowly get closer to the target tank to increase the damage

            # Calculate the distance
            if not self._ready_to_fire:
                if self._last_impact[X] > state[StateEnum.TANK1_LOCATION_X+target_offset]:
                    # We impacted to the right, increase power and try again
                    self._target_pwr += 1 * random.randint(1, int(self._exploration_value))
                    self._ready_to_fire = True
                elif self._last_impact[X] < state[StateEnum.TANK1_LOCATION_X+target_offset]:
                    # We impacted to the right, increase power and try again
                    self._target_pwr -= 1 * random.randint(1, int(self._exploration_value))
                    self._ready_to_fire = True

        # Return an action - Adjust Power and angle to target values
        if state[StateEnum.TANK2_POWER-target_offset] > self._target_pwr:
            action = ActionEnum.DEC_PWR
        elif state[StateEnum.TANK2_POWER-target_offset] < self._target_pwr:
            action = ActionEnum.INC_PWR
        elif state[StateEnum.TANK2_ANGLE-target_offset] > self._target_ang:
            action = ActionEnum.DEC_ANG
        elif state[StateEnum.TANK2_ANGLE-target_offset] < self._target_ang:
            action = ActionEnum.INC_ANG
        else:
            action = ActionEnum.FIRE

        if action == ActionEnum.FIRE:
            self._first_shot = False
            self._last_shot_pwr = self._target_pwr
            self._last_shot_ang = self._target_ang
            self._ready_to_fire = False

        # print("Dumb Agent Act: " + str(action))

        return action

    def _generate_first_shot(self, enemy_location):
        pwr = 75
        ang = 135

        # Do random math

        return pwr, ang
