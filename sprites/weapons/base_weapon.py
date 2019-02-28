import pygame
from pygame.sprite import Sprite

from sprites import InvalidMoveException, X, Y, BLUE, RED, Character

PROJECTILE_WIDTH = 3
PROJECTILE_HEIGHT = 7
LINE_WIDTH = 1


class ProjectileCharacter(Character):
    def __init__(self, point, heading, color):
        Character.__init__(self, vertex=point, color=color)

        # Build the body
        self._body = []  # list of points, of form [[x, y] ... ]
        self._point = point
        self._color = color
        self._heading = heading

        # Set initial Location of tank
        self.move(new_x=point[X], new_y=point[Y], heading=self._heading)

    def move(self, new_x, new_y, heading=0):
        """
        These param describe the center of this projectile

        :param new_x:
        :param new_y:
        :param heading:
        :return:
        """

        # Save location centroid
        self._point[X] = new_x
        self._point[Y] = new_y

        # Save off new heading
        self._heading = heading

        self._body = [
            [new_x - PROJECTILE_WIDTH/2, new_y + PROJECTILE_HEIGHT/2],  # LL
            [new_x - PROJECTILE_WIDTH/2, new_y - PROJECTILE_HEIGHT/2],  # UL
            [new_x + PROJECTILE_WIDTH/2, new_y - PROJECTILE_HEIGHT/2],  # UR
            [new_x + PROJECTILE_WIDTH/2, new_y + PROJECTILE_HEIGHT/2],  # LR
            [new_x - PROJECTILE_WIDTH / 2, new_y + PROJECTILE_HEIGHT / 2],  # LL - repeat first to close the shape
        ]

        # Rotate the body for the heading
        self._body = self._rotate_polygon(self._body, heading)

    def draw(self, surface):
        pygame.draw.polygon(surface,
                            self._color,
                            self._body,
                            LINE_WIDTH)


class BaseWeapon(Sprite):
    def __init__(self, name, screen_dimensions, terrain, me, enemy):
        Sprite.__init__(self)

        # Game details
        self._dimension = screen_dimensions  # X, Y
        self._terrain = terrain
        self._enemy_tank = enemy
        self._my_tank = me

        # Weapon attributes
        self._location = (-1, -1)  # Locate all weapons off screen till used
        self._name = name
        self._character = None

        # Firing attributes
        self._angle = 0
        self._power = 0
        self._starting_location = None

        # Animation details
        self._is_animating = False
        self._fire = False
        self._impact = False
        self._done = False

    def update(self, *args):
        # Animation
        if not self._done:
            if self._fire and not self._impact:
                if not self._hit_me() and not self._hit_enemy() and not self._hit_ground():
                    # We are flying, step it forward
                    self._step_flight()

                elif self._hit_me():
                    # OUCH! You shot yourself!!!!
                    self._impact = True

                elif self._hit_enemy():
                    # We hit the ground
                    self._impact = True

                elif self._hit_ground():
                    # BOOO you missed
                    self._impact = True

                else:
                    # what happened here????
                    pass
            else:
                # Animate the impact
                self._done = True
        else:
            self._is_animating = False

    def fire(self, angle, power, from_location):
        if not self._is_animating:
            if not self._fire:
                # Initiate fire sequence
                self._fire = True
                self._is_animating = True

                # Save off fire angle and power
                self._power = power
                self._angle = angle
                self._starting_location = from_location
                self._character = ProjectileCharacter(location=from_location,
                                                      heading=angle,
                                                      color=RED)
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

    def _step_flight(self):
        # TODO: Physics
        new_x = 0
        new_y = 0
        heading = 0

        # Move the character
        self._character.move_projectile(new_x=new_x, new_y=new_y, heading=heading)

        # Save off new locations
        self._location = [new_x, new_y]
