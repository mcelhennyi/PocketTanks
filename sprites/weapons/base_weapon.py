from pygame.sprite import Sprite

from sprites import InvalidMoveException, X


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

        # Animation details
        self._is_animating = False
        self._fire = False
        self._impact = False
        self._done = False

    def update(self, *args):
        # Animation
        if not self._done:
            if self._fire and not self._impact:
                if  not self._hit_me() and not self._hit_enemy() and not self._hit_ground():
                    # We are flying, step it forward
                    self._animate_flight()

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

    def fire(self):
        if not self._is_animating:
            if not self._fire:
                self._fire = True
                self._is_animating = True
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

    def _animate_flight(self):
        # TODO
        pass
