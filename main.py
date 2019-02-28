import random

import pygame

from sprites import BLUE, RED, GREEN, InvalidMoveException, BLACK
from sprites.tank import Tank
from map.terrain import Terrain, OutOfMapException
from sprites.weapons.base_weapon import BaseWeapon


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

        # Generate a list of weapons
        weapons1 = []
        for i in range(0, 10):
            weapons1.append(BaseWeapon('BASIC', self.size, self._terrain, BLUE))

        weapons2 = []
        for i in range(0, 10):
            weapons2.append(BaseWeapon('BASIC', self.size, self._terrain, RED))

        # Setup two tanks
        tank1_location_x = random.randint(0, int(self.width/3.0))
        tank2_location_x = random.randint(int(2*self.width/3.0), self.width - 1)
        self._tank1 = Tank(screen_dimensions=self.size,
                           location=[tank1_location_x, self._terrain.height_at_point(tank1_location_x)],
                           weapons_list=weapons1,
                           color=BLUE,
                           terrain=self._terrain,
                           )
        self._tank2 = Tank(screen_dimensions=self.size,
                           location=[tank2_location_x, self._terrain.height_at_point(tank2_location_x)],
                           weapons_list=weapons2,
                           color=RED,
                           terrain=self._terrain,
                           )

        self._tank1.set_target(self._tank2)
        self._tank2.set_target(self._tank1)

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

                # MOVE power UP
                elif event.key == pygame.K_EQUALS:
                    self._tank1.increase_power()

                # MOVE power DOWN
                elif event.key == pygame.K_MINUS:
                    self._tank1.decrease_power()

                # Fire
                elif event.key == pygame.K_f:
                    self._tank1.fire()

                else:
                    print("You pressed: " + str(event.key))
        except InvalidMoveException as e:
            print('Whoops!')
            print(e)
        except OutOfMapException as e:
            print('Whoops!')
            print(e)

    def on_loop(self, elapsed_time):
        # Update Tank1
        self._tank1.update(elapsed_time)

        # update tank2
        self._tank2.update(elapsed_time)

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

        last_time = pygame.time.get_ticks()
        while self._running:
            elapsed_time = pygame.time.get_ticks() - last_time
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop(elapsed_time)
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
