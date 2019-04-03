import math
from math import atan2

import pygame
from pygame.sprite import Sprite
from math import sin, cos

from map.terrain import OutOfMapException
from sprites import InvalidMoveException, X, Y, BLUE, RED
from sprites.characters.projectile import BasicProjectileCharacter
from sprites.tank import Tank

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
        self._super_old_location = [0,0]
        self._super_old_count = 0
        self._name = name
        self._color = color
        self._character = None
        self._damage_radius = 40
        self._damage_multiplier = 0.5  # This means, that at most, there can be 20 pts damage

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

    def get_name(self):
        return self._name

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
                try:
                    if not self._hit_source() and not self._hit_enemy() and not self._hit_ground():
                        # We are flying, step it forward
                        self._step_flight(elapsed_time)
                        # print("stepped")

                    elif self._hit_source():
                        # OUCH! You shot yourself!!!!
                        self._impact = True
                        # print("hit source")
                        distance = self._distance(self._source_tank.get_location())
                        damage = (self._damage_radius - distance) * self._damage_multiplier
                        self._source_tank.damage(damage)
                        print("hit yourself, damage: " + str(damage))

                    elif self._hit_enemy():
                        # We hit the ground
                        self._impact = True
                        distance = self._distance(self._target_tank.get_location())
                        damage = (self._damage_radius - distance) * self._damage_multiplier
                        self._target_tank.damage(damage)
                        print("hit enemy, damage: " + str(damage))

                    elif self._hit_ground():
                        # BOOO you missed
                        self._impact = True
                        # print("hit ground")

                    else:
                        # what happened here????
                        # print("unknown")

                        pass
                except OutOfMapException:
                    # We flew out of the map, no reasom to do any more
                    self._impact = True
            else:
                # Animate the impact
                self._done = True
                self._impact_callback(self._location)
        else:
            self._is_animating = False

    def fire(self, angle, power, from_location, impact_callback):
        if not self._is_animating:
            if not self._fire:
                # print("fire!!!!!")
                # Initiate fire sequence
                self._fire = True
                self._is_animating = True

                # Save off fire angle and power
                self._power = power
                self._last_y_power = power * sin(angle)
                self._angle = angle
                self._start_location[X] = from_location[X]
                self._start_location[Y] = from_location[Y]
                self._super_old_location[X] = from_location[X]
                self._super_old_location[Y] = from_location[Y]
                self._super_old_count = 0
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
        return not self._done

    def _hit_enemy(self):
        try:
            if self._hit_ground():
                # If the projectile hits the ground, lets check if it hit the enemy
                distance = self._distance(self._target_tank.get_location())
                if distance <= self._damage_radius:
                    return True
        except OutOfMapException:
            # We flew out of the map, no reasom to do any more
            pass

        return False

    def _hit_source(self):
        try:
            if self._hit_ground():
                # If the projectile hits the ground, lets check if it hit the source
                distance = self._distance(self._source_tank.get_location())
                if distance <= self._damage_radius:
                    return True
        except OutOfMapException:
            # We flew out of the map, no reasom to do any more
            pass

        return False

    def _distance(self, location):
        x_target = location[X]
        y_target = location[Y]
        # print(x_target)
        # print(y_target)
        # print(self._location)
        return math.sqrt((x_target - self._location[X])**2 + (y_target - self._location[Y])**2)

    def _hit_ground(self):
        return self._terrain.intersects_terrain(self._location)

    def _step_flight(self, elapsed_time):
        # Adjust all the times to scale it back
        ts = 0.00001

        # Save of the simulated distance
        self._elapsed_total_time += (elapsed_time / 1000000.0)  # Elapsed comes in millis

        # velocities velocities
        ux = self._power * cos(self._angle*math.pi/180.0)  # X velocity doesnt change
        uy = self._power * sin(self._angle*math.pi/180.0)  # get initial y for calculation

        # Total time of flight
        # x = x0 + v0t
        new_x = int(self._start_location[X] +
                    ux * self._elapsed_total_time
                    )
        # y = y0 + v0t + 1/2(at^2)
        new_y = int(self._start_location[Y] +
                    - (uy * self._elapsed_total_time +
                    (0.5 * GRAVITY * self._elapsed_total_time**2))
                    )

        # print("Old location: " + str(self._start_location[X]) + ", " + str(self._start_location[Y]))
        # print("New location: " + str(new_x) + ", " + str(new_y))
        #
        # print("Delta x: " + str(self._location[X] - new_x))

        # Calculate projectile heading
        heading = - (360 + ((atan2((self._super_old_location[Y] - new_y), (self._super_old_location[X] - new_x)) * 180.0 / math.pi) - 180))
        # print("**HEADING :" + str(heading))

        # Move the character
        self._character.move(new_x=new_x, new_y=new_y, heading=heading)

        # Save off new locations
        self._location = [new_x, new_y]

        # Save off a super old location every 5 steps
        if self._super_old_count == 5:
            self._super_old_location[X] = new_x
            self._super_old_location[Y] = new_y
            self._super_old_count = 5

        # Save off y velocity
        # self._last_y_power = vy

        self._super_old_count += 1  # Increment the count to smooth the slope calculation
