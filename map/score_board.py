from pygame.sprite import Sprite
import pygame
from sprites import X, Y, RED, GREEN, BLUE

HEIGHT = 100


class ScoreBoard(Sprite):
    def __init__(self, screen_dimensions, terrain, tank1, tank2):
        Sprite.__init__(self)

        # init stuff
        pygame.font.init()
        self._font = pygame.font.SysFont('Comic Sans MS', 20)

        # Passed in args
        self._dimensions = screen_dimensions
        self._terrain = terrain
        self._tank1 = tank1
        self._tank2 = tank2

        # Score board polygons
        self._scoreboard_outline = []
        self._ = []

        # Scoreboard text
        self._weapon_label = self._font.render('Weapon Type: ', False, RED)
        self._weapon_label_location = [0, 0]
        self._tank1_health = self._font.render('Tank 1 Health: ', False, BLUE)
        self._tank1_health_location = [0, 0]
        self._tank2_health = self._font.render('Tank 2 Health: ', False, RED)
        self._tank2_health_location = [0, 0]

        # Init the polygons and locations
        self._init_scoreboard()

    def update(self):
        pass

    def draw(self, surface):
        # Draw the outline
        pygame.draw.polygon(
            surface,
            GREEN,
            self._scoreboard_outline,
            2
        )

        # Draw label
        surface.blit(self._weapon_label, self._weapon_label_location)

    def _init_scoreboard(self):

        # Draw the scoreboard
        self._scoreboard_outline = [
            [0, 0],  # UL
            [self._dimensions[X]-1, 0],  # UR
            [self._dimensions[X]-1, HEIGHT],  # LR
            [0, HEIGHT],  # LL
            [0, 0],  # UL - repeat first point to close the polygon
        ]
