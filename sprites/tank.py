import pygame
from pygame.sprite import Sprite
from sprites import X, Y, InvalidMoveException, BLUE, Character

MOVE_DISTANCE = 10
MOVE_COUNT_MAX = 5

MAX_ANGLE = 180
MIN_ANGLE = 0
MAX_POWER = 100
MIN_POWER = 0

LEFT = 0
RIGHT = 1

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

    def draw(self, surface):
        # Draw the body - 0
        pygame.draw.polygon(surface,
                            self._color,
                            self._polygon,
                            LINE_WIDTH)

        # Draw the turret
        self._turret.draw(surface)


class Tank(Sprite):
    def __init__(self, screen_dimensions, location, weapons_list, terrain, color=BLUE):
        Sprite.__init__(self)

        # Game details
        self._dimension = screen_dimensions  # x, y
        self._terrain = terrain

        # Tank attributes
        self._location = location
        self._move_count = MOVE_COUNT_MAX
        self._move_amt = 0
        self._tank_character = TankCharacter(location, color)

        # Gun attributes
        self._gun_angle = MAX_ANGLE/2
        self._gun_power = MAX_POWER/2

        # Weapons
        self._weapons = weapons_list
        self._weapon_selected = 0

        # Animation tracking
        self._is_animating = False

    # Render functions for animations
    def update(self):
        # self._is_animating = True
        # Will used to animate

        # Update/Move the tank
        self._tank_character.set_cannon_angle(self._gun_angle)
        self._tank_character.move(
            self._location[X],
            self._location[Y],
            0
        )

    def draw(self, surface):
        self._tank_character.draw(surface)

    # --------------------- #
    # Change to next weapon #
    # --------------------- #
    def load_next_weapon(self):
        if not self._is_animating:
            if self._weapon_selected < len(self._weapons) - 1:
                self._weapon_selected += 1
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # ------------------------- #
    # Change to previous weapon #
    # ------------------------- #
    def load_previous_weapon(self):
        if not self._is_animating:
            if self._weapon_selected > 0:
                self._weapon_selected -= 1
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # ---------- #
    # Move Right #
    # ---------- #
    def move_right(self):
        if not self._is_animating:
            self._move(RIGHT)
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # --------- #
    # Move Left #
    # --------- #
    def move_left(self):
        if not self._is_animating:
            self._move(LEFT)
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # -------------- #
    # Increase angle #
    # -------------- #
    def increase_angle(self):
        if not self._is_animating:
            if self._gun_angle < MAX_ANGLE:
                self._gun_angle += 1
            else:
                # invalid move
                raise InvalidMoveException("Cannot Increase angle past " + str(MAX_ANGLE))
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # -------------- #
    # Decrease angle #
    # -------------- #
    def decrease_angle(self):
        if not self._is_animating:
            if self._gun_angle > MIN_ANGLE:
                self._gun_angle -= 1
            else:
                # invalid move
                raise InvalidMoveException("Cannot decrease angle past " + str(MIN_ANGLE))
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # -------------- #
    # Increase power #
    # -------------- #
    def increase_power(self):
        if not self._is_animating:
            if self._gun_power < MAX_POWER:
                self._gun_power += 1
            else:
                # invalid move
                raise InvalidMoveException("Cannot Increase power past " + str(MAX_POWER))
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # -------------- #
    # Decrease power #
    # -------------- #
    def decrease_power(self):
        if not self._is_animating:
            if self._gun_power > MIN_POWER:
                self._gun_power -= 1
            else:
                # invalid move
                raise InvalidMoveException("Cannot decrease power past " + str(MIN_POWER))
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    # ------------------ #
    # ---- PRIVATES ---- #
    # ------------------ #
    # Move Function
    def _move(self, direction):
        if not self._is_animating:
            if self._move_count != 0:
                self._move_count -= 1
                self._location[X] += MOVE_DISTANCE if direction == RIGHT else - MOVE_DISTANCE
                self._location[Y] = self._terrain.height_at_point(self._location[X])
            else:
                # Invalid move
                raise InvalidMoveException("Cannot move the tank anymore, maximum moves used: " +
                                           str(MOVE_COUNT_MAX) + " .")
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    def _step_animation(self):
        pass