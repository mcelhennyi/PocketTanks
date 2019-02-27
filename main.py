import random

import pygame

from sprites import BLUE, RED, GREEN
from sprites.tank import Tank
from terrain import Terrain


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 512

        self._tank1 = None
        self._tank2 = None

        self._terrain = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        # Generate terrain
        self._terrain = Terrain(self.size, color=GREEN)

        # Setup two tanks
        tank1_location_x = random.randint(0, self.width/2)
        tank2_location_x = random.randint(self.width/2, self.width - 1)
        self._tank1 = Tank(screen_dimensions=self.size,
                           location=[tank1_location_x, self._terrain.height_at_point(tank1_location_x)],
                           weapons_list=[],
                           color=BLUE)
        self._tank2 = Tank(screen_dimensions=self.size,
                           location=[tank2_location_x, self._terrain.height_at_point(tank2_location_x)],
                           weapons_list=[],
                           color=RED)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        # Update Tank1
        # self._tank1.update()
        pass

    def on_render(self):
        # Draw the terrain
        self._terrain.draw(self._display_surf)

        # Draw player 1
        self._tank1.draw(self._display_surf)

        # Draw player 2
        self._tank2.draw(self._display_surf)

        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
