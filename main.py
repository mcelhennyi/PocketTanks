import random

import pygame

from agents import ActionEnum
from agents.dumb_agent import DumbAgent
from map.score_board import ScoreBoard
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

        self._score_board = None

        self._game_over = False

        self._player_1_active = True

        self._player_2 = None

        self._restart = False

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self._restart = False

        # Generate terrain
        self._terrain = Terrain(self.size, color=GREEN)

        # Generate a list of weapons
        weapons1 = []
        for i in range(0, 100):
            weapons1.append(BaseWeapon('BASIC_'+str(i), self.size, self._terrain, BLUE))

        weapons2 = []
        for i in range(0, 100):
            weapons2.append(BaseWeapon('BASIC_'+str(i), self.size, self._terrain, RED))

        # Setup two tanks
        tank1_location_x = random.randint(0, int(self.width/3.0))
        tank2_location_x = random.randint(int(2*self.width/3.0), self.width - 1)
        self._tank1 = Tank(screen_dimensions=self.size,
                           location=[tank1_location_x, self._terrain.height_at_point(tank1_location_x)],
                           weapons_list=weapons1,
                           color=BLUE,
                           terrain=self._terrain,
                           name="Player 1 (You)",
                           switch_player_callback=self._switch_player,
                           damage_callback=self._show_damage
                           )
        self._tank2 = Tank(screen_dimensions=self.size,
                           location=[tank2_location_x, self._terrain.height_at_point(tank2_location_x)],
                           weapons_list=weapons2,
                           color=RED,
                           terrain=self._terrain,
                           name="Player 2 (CPU)",
                           switch_player_callback=self._switch_player,
                           damage_callback=self._show_damage
                           )

        self._tank1.set_target(self._tank2)
        self._tank2.set_target(self._tank1)

        self._score_board = ScoreBoard(self.size, self._terrain, self._tank1, self._tank2)
        self._score_board.switch_active_player(self._tank1)

        self._player_2 = DumbAgent()

        return True

    def on_event(self, event):
        try:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                self._running = False
                print("Game over, you pressed quit.")

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self._restart = True
                self._running = False
                print("Game restarted.")

            else:
                if not self._game_over:

                    if self._player_1_active:
                        # --------------- #
                        # Player 1's turn #
                        # --------------- #
                        if event.type == pygame.KEYDOWN:
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

                            # Increase weapon choice
                            elif event.key == pygame.K_PERIOD:
                                self._tank1.load_next_weapon()

                            # Decrease weapon choice
                            elif event.key == pygame.K_COMMA:
                                self._tank1.load_previous_weapon()

                            else:
                                # print("You pressed: " + str(event.key))
                                pass

        except InvalidMoveException as e:
            print('Whoops!')
            print(e)
        except OutOfMapException as e:
            print('Whoops!')
            print(e)

    def _handle_agents(self):

        """
            - Tank 1 location
            - Tank 1 health
            - Tank 1 Power
            - Tank 1 Angle
            - Tank 2 location
            - Tank 2 health
            - Tank 2 Power
            - Tank 2 Angle
        """

        state = [
            # Tank 1
            self._tank1.get_location(),
            self._tank1.get_health(),
            self._tank1.get_power(),
            self._tank1.get_angle(),

            # Tank 2
            self._tank2.get_location(),
            self._tank2.get_health(),
            self._tank2.get_power(),
            self._tank2.get_angle(),
        ]

        if not self._player_1_active:
            if not self._tank2.is_animating():
                # --------------- #
                # Player 2's turn #
                # --------------- #
                action = self._player_2.act(state)
                if action == ActionEnum.LEFT:
                    print("Player 2: Moves Left.")
                    self._tank2.move_left()
                elif action == ActionEnum.RIGHT:
                    print("Player 2: Moves Right.")
                    self._tank2.move_right()
                elif action == ActionEnum.INC_PWR:
                    print("Player 2: Increases gun power.")
                    self._tank2.increase_power()
                elif action == ActionEnum.DEC_PWR:
                    print("Player 2: Decreases gun power.")
                    self._tank2.decrease_power()
                elif action == ActionEnum.INC_ANG:
                    print("Player 2: Increases gun angle.")
                    self._tank2.increase_angle()
                elif action == ActionEnum.DEC_ANG:
                    print("Player 2: Decreases gun angle.")
                    self._tank2.decrease_angle()
                elif action == ActionEnum.FIRE:
                    print("Player 2: Fires!")
                    self._tank2.fire()

    def _show_damage(self, damaged_name, damage_amount):
        self._score_board.damage_display(damaged_name, damage_amount)

    def _switch_player(self, impact_location):
        if not self._player_1_active:
            # Tell the person who shot, where the impact landed
            self._player_2.last_impact(impact_location)

        self._player_1_active = not self._player_1_active
        self._score_board.switch_active_player(self._tank1 if self._player_1_active else self._tank2)

    def on_loop(self, elapsed_time):
        if not self._game_over:
            # Update Tank1
            self._tank1.update(elapsed_time)

            # update tank2
            self._tank2.update(elapsed_time)
        else:
            # send signal to display result
            self._score_board.end_game(self._tank1 if self._tank1.is_alive() else self._tank2)

        # Update Scoreboard
        self._score_board.update()

        # Print out game status
        if not self._tank1.is_alive() or not self._tank2.is_alive():
            self._game_over = True

    def on_render(self):
        # Reset screen to black
        self._display_surf.fill(BLACK)

        # Draw the terrain
        self._terrain.draw(self._display_surf)

        # Draw player 1
        self._tank1.draw(self._display_surf)

        # Draw player 2
        self._tank2.draw(self._display_surf)

        # Draw Scoreboard
        self._score_board.draw(self._display_surf)

        pygame.display.update()

    def on_cleanup(self):
        # pygame.quit()
        pass

    def on_execute(self):
        # Allow a game to restart
        while True:
            if not self.on_init():
                self._running = False

            # Run the main game loop
            last_time = pygame.time.get_ticks()
            while self._running:
                elapsed_time = pygame.time.get_ticks() - last_time
                for event in pygame.event.get():
                    self.on_event(event)
                self._handle_agents()
                self.on_loop(elapsed_time)
                self.on_render()
            self.on_cleanup()

            if not self._restart:
                pygame.quit()
                break


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
