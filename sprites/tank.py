import pygame
from pygame.sprite import Sprite
from pygame import Rect
from sprites import X, Y, InvalidMoveException, BLUE

MOVE_DISTANCE = 10
MOVE_COUNT_MAX = 5

MAX_ANGLE = 180
MIN_ANGLE = 0
MAX_POWER = 100
MIN_POWER = 0

LEFT = 0
RIGHT = 1

TANK_WIDTH = 21
TANK_HEIGHT = 9

TURRET_WIDTH = 15
TURRET_HEIGHT = 5

LINE_WIDTH = 3


class TankCharacter:
    def __init__(self, location, color):

        # Build the body
        self._body_rect = None
        self._turret = None
        self._location = location
        self._color = color

        # Set initial Location of tank
        self.move_tank(new_x=location[X], new_y=location[Y], init=True)

    def _init_tank(self, new_x, new_y, ):
        self._body_rect = Rect(new_x-0.5*TANK_WIDTH, new_y-TANK_HEIGHT,
                               TANK_WIDTH, TANK_HEIGHT)
        self._turret = Rect(new_x-0.5*TURRET_WIDTH, new_y-TANK_HEIGHT-TURRET_HEIGHT,
                            TURRET_WIDTH, TURRET_HEIGHT)

    def move_tank(self, new_x, new_y, init=False):
        """

        :param new_x: The center of the tank from left to right
        :param new_y: The base of the body of the tank
        :param init:
        :return:
        """
        # Init the tank
        if init:
            self._init_tank(new_x, new_y)

        # The Y coordinate will be the bottom of the tank body and X coordinate will be the center of the tank body
        self._body_rect.centerx = new_x
        self._body_rect.centery = new_y - 0.5*TANK_HEIGHT

        # Build the turret
        self._turret.centerx = new_x
        self._turret.centery = new_y - (TANK_HEIGHT + 0.5*TURRET_HEIGHT)

        # Save location
        self._location[X] = new_x
        self._location[Y] = new_y

    def draw(self, surface):
        pygame.draw.rect(surface,
                         self._color,
                         self._body_rect,
                         LINE_WIDTH)
        pygame.draw.rect(surface,
                         self._color,
                         self._turret,
                         LINE_WIDTH)


class Tank(Sprite):
    def __init__(self, screen_dimensions, location, weapons_list, color=BLUE):
        Sprite.__init__(self)

        # Game details
        self._dimension = screen_dimensions  # x, y

        # Tank attributes
        self._location = location
        self._move_count = MOVE_COUNT_MAX
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
    def update(self, direction):
        self._is_animating = True
        # Will used to animate
        pass

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
            else:
                # Invalid move
                raise InvalidMoveException("Cannot move the tank anymore, maximum moves used: " +
                                           str(MOVE_COUNT_MAX) + " .")
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    def _step_animation(self):
        pass