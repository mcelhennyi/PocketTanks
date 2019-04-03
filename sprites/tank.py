import pygame
from pygame.sprite import Sprite
from sprites import X, Y, InvalidMoveException, BLUE
from sprites.characters.tank import TankCharacter, TANK_WIDTH

MOVE_DISTANCE = 10
MOVE_COUNT_MAX = 100

MAX_ANGLE = 180
MIN_ANGLE = 0
MAX_POWER = 100
MIN_POWER = 0

LEFT = 0
RIGHT = 1


class Tank(Sprite):
    def __init__(self, screen_dimensions, location, weapons_list, terrain, color=BLUE, name='Name', switch_player_callback=None, damage_callback=None):
        Sprite.__init__(self)

        # Game details
        self._dimension = screen_dimensions  # x, y
        self._terrain = terrain
        self._enemy = None
        self._switch_player_callback = switch_player_callback
        self._damage_callback = damage_callback

        # Tank attributes
        self._location = location
        self._move_count = MOVE_COUNT_MAX
        self._move_amt = 0
        self._color = color
        self._tank_character = TankCharacter(location, color)
        self._health = 100
        self._name = name

        # Gun attributes
        self._gun_angle = MAX_ANGLE/4 if color == BLUE else MAX_ANGLE * 3/4
        self._gun_power = MAX_POWER/2

        # Weapons
        self._weapons = weapons_list
        self._weapon_selected = 0

        # Animation tracking
        self._is_animating = False

    def is_animating(self):
        return self._is_animating

    def get_location(self):
        return self._location

    def set_target(self, tank):
        self._enemy = tank

    def is_alive(self):
        return self._health > 0

    def get_name(self):
        return self._name

    def get_health(self):
        return self._health

    def get_color(self):
        return self._color

    def get_power(self):
        return self._gun_power

    def get_angle(self):
        return self._gun_angle

    def get_move_count(self):
        return self._move_count

    def get_current_weapon_name(self):
        return self._weapons[self._weapon_selected].get_name()

    def damage(self, damage_value):
        damage_value = int(damage_value)
        if self._health >= damage_value:
            self._health -= damage_value

            self._damage_callback(self._name, damage_value)
        else:
            self._health = 0

        print(self._name + ": Ouch!, I've been damaged by " + str(damage_value) + ", my new health is: " + str(self._health))

    # Render functions for animations
    def update(self, elapsed_time):
        # self._is_animating = True
        # Will used to animate

        # Update/Move the tank
        if self._is_animating:
            self._step_animation(elapsed_time)
            self._weapons[self._weapon_selected].update(elapsed_time)

        self._tank_character.set_cannon_angle(self._gun_angle)
        self._tank_character.move(
            self._location[X],
            self._location[Y],
            self._terrain.grade_at_point(self._location[X], TANK_WIDTH)
        )

    def draw(self, surface):
        self._tank_character.draw(surface)
        if self._is_animating:
            self._weapons[self._weapon_selected].draw(surface)

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
                # print("more- power: " + str(self._gun_power))
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
                # print("less power: " + str(self._gun_power))
                self._gun_power -= 1
            else:
                # invalid move
                raise InvalidMoveException("Cannot decrease power past " + str(MIN_POWER))
        else:
            raise InvalidMoveException("Cannot play while game is animating.")

    def _get_cannon_tip(self):  # returns location [x, y]
        return self._tank_character.get_cannon_tip()

    def fire(self):
        # Setup the weapon
        weapon = self._weapons[self._weapon_selected]
        weapon.prepare(self, self._enemy)

        # FIRE!!!!
        weapon.fire(self._gun_angle, self._gun_power, self._get_cannon_tip(), self._impact_callback)

        # Enable animation
        self._is_animating = True

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

    def _step_animation(self, elapsed_time):
        pass

    def _impact_callback(self, impact_location):
        self._is_animating = False
        self.load_next_weapon()
        self._switch_player_callback(impact_location)
