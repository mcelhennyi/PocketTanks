import pygame

from sprites import Y, X
from sprites.characters import Character

TANK_WIDTH = 31
TANK_HEIGHT = 13

TURRET_WIDTH = 13
TURRET_HEIGHT = 9

CANNON_WIDTH = 3  # When the cannon is pointing to 90 degrees
CANNON_HEIGHT = 21  # When cannon is pointing to 90 degrees

LINE_WIDTH = 3


class CannonCharacter(Character):
    def __init__(self, vertex, color):
        Character.__init__(self, vertex=vertex, color=color)

    def get_tip(self):
        pt = [self._vertex[X], self._vertex[Y] + CANNON_HEIGHT]
        return self._rotate_point(pt)

    def draw(self, surface):
        pygame.draw.polygon(surface,
                            self._color,
                            self._polygon,
                            LINE_WIDTH)

    def move(self, new_x, new_y, heading=0):
        Character.move(self, new_x, new_y, heading)

        # Cannon of the tank - we will assume 0 degrees is to the right, and center the vertex of the cannon at
        #  the middle of the turret
        self._polygon = [
            [new_x, new_y+0.5*CANNON_WIDTH],  # LL
            [new_x, new_y-CANNON_WIDTH],  # UL
            [new_x+CANNON_HEIGHT, new_y-CANNON_WIDTH],  # UR
            [new_x+CANNON_HEIGHT, new_y+0.5*CANNON_WIDTH],  # LR
            [new_x, new_y+0.5*CANNON_WIDTH],  # LL - repeat first to close poly
        ]

        # Adjust the cannon's heading
        self._rotate_polygon()


class TurretCharacter(Character):
    def __init__(self, vertex, color):
        Character.__init__(self, vertex=vertex, color=color)
        # Setup the cannon
        self._cannon = CannonCharacter(
            [
                # Set vertex to middle of turret
                vertex[X],
                vertex[Y] - 0.5*TURRET_HEIGHT
            ],
            color
        )
        self._cannon_angle = 0

    def set_cannon_angle(self, ang):
        self._cannon_angle = ang

    def get_cannon_tip(self):
        return self._cannon.get_tip()

    def move(self, new_x, new_y, heading=0):
        Character.move(self, new_x, new_y, heading)

        # Move the turret poly
        self._polygon = [
            [new_x-0.5*TURRET_WIDTH, new_y],  # LL
            [new_x-0.5*TURRET_WIDTH, new_y-TURRET_HEIGHT],  # UL
            [new_x+0.5*TURRET_WIDTH, new_y-TURRET_HEIGHT],  # UR
            [new_x+0.5*TURRET_WIDTH, new_y],  # LR
            [new_x-0.5*TURRET_WIDTH, new_y],  # LL - repeat first to close the shape
        ]

        # Move and rotate cannon
        self._cannon.move(new_x,
                          new_y - 0.5*TURRET_HEIGHT,
                          self._cannon_angle)  # Pass in the angle of the cannon to the 'heading' param

        # Rotate to match terrain
        self._rotate_polygon()

    def draw(self, surface):
        # Draw the turret
        pygame.draw.polygon(surface,
                            self._color,
                            self._polygon,
                            LINE_WIDTH)

        # Draw the cannon
        self._cannon.draw(surface)


class TankCharacter(Character):
    def __init__(self, vertex, color):
        Character.__init__(self, vertex=vertex, color=color)

        # Setup the turret
        self._turret = TurretCharacter(
            [
                vertex[X],
                vertex[Y]-TANK_HEIGHT  # The turrets base/vertex is the base where it meets the body
            ],
            color
        )

        # Set initial Location of tank
        self.move(new_x=vertex[X], new_y=vertex[Y], heading=0)

    def set_cannon_angle(self, ang):
        self._turret.set_cannon_angle(ang)

    def get_cannon_tip(self):
        return self._turret.get_cannon_tip()

    def move(self, new_x, new_y, heading=0):
        Character.move(self, new_x, new_y, heading)

        # Body of tank - bottom part
        self._polygon = [
            [new_x-0.5*TANK_WIDTH, new_y],  # LL
            [new_x-0.5*TANK_WIDTH, new_y-TANK_HEIGHT],  # UL
            [new_x+0.5*TANK_WIDTH, new_y-TANK_HEIGHT],  # UR
            [new_x+0.5*TANK_WIDTH, new_y],  # LR
            [new_x-0.5*TANK_WIDTH, new_y],  # LL - repeat first to close the shape
        ]

        # Move turret
        self._turret.move(new_x,
                          new_y-TANK_HEIGHT,
                          self._heading)

        # Rotate to match terrain
        self._rotate_polygon()

    def draw(self, surface):
        # Draw the body - 0
        pygame.draw.polygon(surface,
                            self._color,
                            self._polygon,
                            LINE_WIDTH)

        # Draw the turret
        self._turret.draw(surface)
