import pygame

from sprites import Y, X
from sprites.characters import Character

BASIC_PROJECTILE_WIDTH = 3
BASIC_PROJECTILE_HEIGHT = 7

LINE_WIDTH = 2


class BasicProjectileCharacter(Character):
    def __init__(self, vertex, color):
        Character.__init__(self, vertex=vertex, color=color)

    def draw(self, surface):
        if self._ready:
            pygame.draw.polygon(surface,
                                self._color,
                                self._polygon,
                                LINE_WIDTH)
            # print("Drawing: " + str(self._polygon))

    def move(self, new_x, new_y, heading=0):
        Character.move(self, new_x, new_y, heading)

        # print("Animating: " + str(new_x) + ", " + str(new_y))

        # Cannon of the tank - we will assume 0 degrees is to the right, and center the vertex of the cannon at
        #  the middle of the turret
        self._polygon = [
            [new_x, new_y+0.5*BASIC_PROJECTILE_WIDTH],  # LL
            [new_x, new_y-BASIC_PROJECTILE_WIDTH],  # UL
            [new_x+BASIC_PROJECTILE_HEIGHT, new_y-BASIC_PROJECTILE_WIDTH],  # UR
            [new_x+BASIC_PROJECTILE_HEIGHT, new_y+0.5*BASIC_PROJECTILE_WIDTH],  # LR
            [new_x, new_y+0.5*BASIC_PROJECTILE_WIDTH],  # LL - repeat first to close poly
        ]

        # Adjust the cannon's heading
        self._rotate_polygon()

        self._ready = True
