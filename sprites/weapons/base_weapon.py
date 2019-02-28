import math

import pygame
from pygame.sprite import Sprite
from math import sin, cos
from sprites import InvalidMoveException, X, Y, BLUE, RED
from sprites.characters.projectile import BasicProjectileCharacter


GRAVITY = -9.8


class BaseWeapon(Sprite):
    def __init__(self, name, screen_dimensions, terrain, color, source_tank=None, target_tank=None):
        Sprite.__init__(self)

        # Game details
        self._dimension = screen_dimensions  # X, Y
        self._terrain = terrain
        self._target_tank = target_tank
        self._source_tank = source_tank

        # Weapon attributes
        self._location = (-1, -1)  # Locate all weapons off screen till used
        self._name = name
        self._color = color
        self._character = None

        # Firing attributes
        self._angle = 0
        self._power = 0
        self._last_y_power = 0
        self._start_location = [0, 0]
        self._elapsed_total_time = 0

        # Animation details
        self._is_animating = False
        self._fire = False
        self._impact = False
        self._done = False
        self._impact_callback = None

    def prepare(self, source_tank, target_tank):
        self._source_tank = source_tank
        self._target_tank = target_tank

    def draw(self, surface):
        if self._is_animating:
            self._character.draw(surface)

    def update(self, elapsed_time):
        # Animation
        if not self._done:
            if self._fire and not self._impact:
                if not self._hit_me() and not self._hit_enemy() and not self._hit_ground():
                    # We are flying, step it forward
                    self._step_flight(elapsed_time)
                    print("stepped")

                elif self._hit_me():
                    # OUCH! You shot yourself!!!!
                    self._impact = True
                    print("hit me")

                elif self._hit_enemy():
                    # We hit the ground
                    self._impact = True
                    print("hit enemy")

                elif self._hit_ground():
                    # BOOO you missed
                    self._impact = True
                    print("hit ground")

                else:
                    # what happened here????
                    print("unknown")

                    pass
            else:
                # Animate the impact
                self._done = True
                self._impact_callback()
        else:
            self._is_animating = False

    def fire(self, angle, power, from_location, impact_callback):
        if not self._is_animating:
            if not self._fire:
                print("fire!!!!!")
                # Initiate fire sequence
                self._fire = True
                self._is_animating = True

                # Save off fire angle and power
                self._power = power
                self._last_y_power = power * sin(angle)
                self._angle = angle
                self._start_location = from_location
                self._location = from_location

                # Save off the callback for an impact
                self._impact_callback = impact_callback

                # Init character
                self._character = BasicProjectileCharacter(
                    from_location,
                    color=self._color
                )
            else:
                raise InvalidMoveException("Cannot fire while weapon is already firing.")
        else:
            raise InvalidMoveException("Weapon already fired.")

    def is_available(self):
        return self._done

    def _hit_enemy(self):
        # TODO
        return False

    def _hit_me(self):
        # TODO
        return False

    def _hit_ground(self):
        return self._terrain.intersects_terrain(self._location)

    def _step_flight(self, elapsed_time):
        # TODO: Physics
        heading = 0

        # Save of the simulated distance
        self._elapsed_total_time += (elapsed_time / 100000.0)

        # velocities velocities
        ux = self._power * cos(self._angle*math.pi/180.0)  # X velocity doesnt change
        uy = self._power * sin(self._angle*math.pi/180.)  # get initial y for calculation
        vy = self._power * sin(self._angle*math.pi/180.) + GRAVITY*self._elapsed_total_time  # get current y vel

        # Total time of flight
        new_x = int(self._location[X] + ux * self._elapsed_total_time)
        new_y = int(self._location[Y] - (((vy + uy) / 2) * self._elapsed_total_time))

        print("Old location: " + str(self._start_location[X]) + ", " + str(self._start_location[Y]))
        print("New location: " + str(new_x) + ", " + str(new_y))

        # Move the character
        self._character.move(new_x=new_x, new_y=new_y, heading=heading)

        # Save off new locations
        self._location = [new_x, new_y]

        # Save off y velocity
        self._last_y_power = vy
