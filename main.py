import random

import pygame

from sprites import BLUE, RED, GREEN, InvalidMoveException, BLACK
from sprites.tank import Tank
from map.terrain import Terrain


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
        tank1_location_x = random.randint(0, int(self.width/3.0))
        tank2_location_x = random.randint(int(2*self.width/3.0), self.width - 1)
        self._tank1 = Tank(screen_dimensions=self.size,
                           location=[tank1_location_x, self._terrain.height_at_point(tank1_location_x)],
                           weapons_list=[],
                           color=BLUE,
                           terrain=self._terrain,
                           )
        self._tank2 = Tank(screen_dimensions=self.size,
                           location=[tank2_location_x, self._terrain.height_at_point(tank2_location_x)],
                           weapons_list=[],
                           color=RED,
                           terrain=self._terrain,
                           )

        return True

    def on_event(self, event):
        try:
            if event.type == pygame.QUIT:
                self._running = False

            elif event.type == pygame.KEYDOWN:
                # MOVE TANK LEFT
                if event.key == pygame.K_LEFT:
                    self._tank1.move_left()

                # MOVE TANK RIGHT
                elif event.key == pygame.K_RIGHT:
                    self._tank1.move_right()

                # MOVE Turret UP
                elif event.key == pygame.K_UP:
                    self._tank1.increase_angle()

                # MOVE Turret DOWN
                elif event.key == pygame.K_DOWN:
                    self._tank1.decrease_angle()
                else:
                    print("You pressed: " + str(event.key))
        except InvalidMoveException as e:
            print('Whoops!')
            print(e)

    def on_loop(self):
        # Update Tank1
        self._tank1.update()

        # update tank2
        self._tank2.update()

    def on_render(self):
        # Reset screen to black
        self._display_surf.fill(BLACK)

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
        if not self.on_init():
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
