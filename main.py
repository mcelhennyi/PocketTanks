import random
import threading
import time

import pygame

from agents import ActionEnum
from agents.dumb_agent import DumbAgent
from map.score_board import ScoreBoard
from sprites import BLUE, RED, GREEN, InvalidMoveException, BLACK, X, Y
from sprites.tank import Tank
from map.terrain import Terrain, OutOfMapException
from sprites.weapons.base_weapon import BaseWeapon


NOMINAL_REWARD = 100


class App:
    def __init__(self, training_mode=False, ml_step_callback=None):
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

        # Stuff to separtate/allow the ml to train vs user to play
        self._training_mode = training_mode
        self._ml_step_callback = ml_step_callback
        self._ml_next_action = None
        self._step_simulation = False
        self._action_taken = False
        self._reward_from_ml_shot = 0
        self.start_time = time.time()

        self._lock = threading.Lock()

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self._restart = False
        self._game_over = False
        self._player_1_active = True

        # Generate terrain
        self._terrain = Terrain(self.size, color=GREEN)

        # Generate a list of weapons
        weapons1 = []
        for i in range(0, 500):
            weapons1.append(BaseWeapon('BASIC_'+str(i), self.size, self._terrain, BLUE))

        weapons2 = []
        for i in range(0, 500):
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

        # Init ML stuff
        self._ml_next_action = None
        self._step_simulation = False
        self._action_taken = False
        self._reward_from_ml_shot = 0

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

                    # Make sure its player 1's turn
                    if self._player_1_active:
                        # Dont allow the user to intervene when the ML is playinh
                        if not self._training_mode:
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

    def get_game_state(self):
        """
           - Tank 1 location x
           - y
           - Tank 1 health
           - Tank 1 Power
           - Tank 1 Angle
           - Tank 2 location
           - y
           - Tank 2 health
           - Tank 2 Power
           - Tank 2 Angle
        """

        return [
            # Tank 1
            self._tank1.get_location()[X],
            self._tank1.get_location()[Y],
            self._tank1.get_health(),
            self._tank1.get_power(),
            self._tank1.get_angle(),

            # Tank 2
            self._tank2.get_location()[X],
            self._tank2.get_location()[Y],
            self._tank2.get_health(),
            self._tank2.get_power(),
            self._tank2.get_angle(),
        ]

    # Called before on_loop
    def _handle_agents(self):

        # Get the current state
        state = self.get_game_state()

        # if time.time() > self.start_time + 10:
        #     print("HANLDE AGENTSSSSSSSS")
        #     print(self._player_1_active)
        #     print(self._training_mode)
        #     print( self._step_simulation)

        if not self._player_1_active:
            if not self._tank2.is_animating():
                try:
                    # --------------- #
                    # Player 2's turn #
                    # --------------- #
                    action = self._player_2.act(state)
                    if action == ActionEnum.LEFT:
                        # print("Player 2: Moves Left.")
                        self._tank2.move_left()

                    elif action == ActionEnum.RIGHT:
                        # print("Player 2: Moves Right.")
                        self._tank2.move_right()

                    elif action == ActionEnum.INC_PWR:
                        # print("Player 2: Increases gun power.")
                        self._tank2.increase_power()

                    elif action == ActionEnum.DEC_PWR:
                        # print("Player 2: Decreases gun power.")
                        self._tank2.decrease_power()

                    elif action == ActionEnum.INC_ANG:
                        # print("Player 2: Increases gun angle.")
                        self._tank2.increase_angle()

                    elif action == ActionEnum.DEC_ANG:
                        # print("Player 2: Decreases gun angle.")
                        self._tank2.decrease_angle()

                    elif action == ActionEnum.FIRE:
                        print("Player 2: Fires!")
                        self._tank2.fire()
                except InvalidMoveException as e:
                    print('Whoops! Invalid move: ' + str(e))

        # ML's turn
        else:

            # If we are in ML playing mode, lets check for its next command
            if self._training_mode:

                # Marks beginning of a "Step" to the trainer
                if self._step_simulation:
                    if not self._tank1.is_animating():

                        try:
                            # Make sure there are no game commands
                            if self._ml_next_action == -1:
                                self._restart = True
                                self._running = False
                            elif self._ml_next_action == -2:
                                self._restart = False
                                self._running = False

                            # No game commands, check for the next move
                            else:
                                # Check for the ML's move
                                if self._ml_next_action == ActionEnum.LEFT:
                                    # print("Q-Learning Agent: Moves Left.")
                                    self._tank1.move_left()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.RIGHT:
                                    # print("Q-Learning Agent: Moves Right.")
                                    self._tank1.move_right()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.INC_PWR:
                                    # print("Q-Learning Agent: Increases gun power.")
                                    self._tank1.increase_power()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.DEC_PWR:
                                    # print("Q-Learning Agent: Decreases gun power.")
                                    self._tank1.decrease_power()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.INC_ANG:
                                    # print("Q-Learning Agent: Increases gun angle.")
                                    self._tank1.increase_angle()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.DEC_ANG:
                                    # print("Q-Learning Agent: Decreases gun angle.")
                                    self._tank1.decrease_angle()
                                    self._action_taken = True
                                    self._step_simulation = False

                                elif self._ml_next_action == ActionEnum.FIRE:
                                    print("Q-Learning Agent: Fires!")
                                    self._tank1.fire()
                                    self._step_simulation = False
                                    self._action_taken = False  # Tells the action taken callback to not fire beciase an impact callback will fire
                                else:
                                    print("Unknown action: " + str(self._ml_next_action))

                        except InvalidMoveException as e:
                            print('Whoops! Invalid move: ' + str(e))
                            # Send notification of this to AI
                            self._handle_action_taken(True)

    def queue_ml_action(self, action):
        """
        Send -1 for a restart and a -2 to quit

        :param action:
        :return:
        """
        with self._lock:
            self._ml_next_action = action
            self._step_simulation = True
            self._action_taken = False

    # def step(self):
    #     self._step_simulation = True

    def _show_damage(self, damaged_name, damage_amount):
        self._score_board.damage_display(damaged_name, damage_amount)

    def _calculate_reward(self, damage, distance, is_enemy=False):
        reward = NOMINAL_REWARD

        # Calculate self damage reward
        if damage < 0:
            reward = 0.1

        else:
            # Damage is either nothing (we missed) or we have some damage, create a reward
            reward += damage  # Max damage is currently 20 pts

        # Therefore max reward at this point is 100 + 20  (We may need to equalize the width of the screen and damage)

        # Multiply the reward by the inverse of the distance normalized, so the closer we get the more reward we give
        distance_normalized = float(distance) / float(self.size[X])
        # print(distance)

        # limit of this calculation is the width of the game screen times the max reward so 1024 * 120
        if is_enemy:
            # If its the enemy's shot, we only care if we get hit...give reward for damage
            reward = - damage

        else:
            # if its our shot, we want a gradient of damage from target to landing
            reward *= 1 - distance_normalized

        return reward

    def _switch_player(self, impact_location, damage, distance):
        # Make sure to mark the state of the game before sending a ml step callback reponse
        if not self._tank1.is_alive() or not self._tank2.is_alive():
            self._game_over = True

        if not self._player_1_active:
            # Tell the person who shot, where the impact landed
            self._player_2.last_impact(impact_location)

            # Our ML Went, then Player 2 went, now lets tell the ML what ended up happening
            # if self._training_mode:
            state_now = self.get_game_state()
            # TODO: For now, we will only let the model train off of its own actions. Since it cant move
            # reward = self._calculate_reward(damage, distance, is_enemy=True)
            # reward += self._reward_from_ml_shot
            reward = self._reward_from_ml_shot
            print("REWARD: " + str(reward))
            if self._training_mode:
                # print("Player two fired, handle callback")
                self._ml_step_callback(state_now, reward, self._game_over)
            self._reward_from_ml_shot = 0  # Reset this for consistentcy
        else:
            # Calculate the reward from ML' sshot
            self._reward_from_ml_shot = self._calculate_reward(damage, distance)

        self._player_1_active = not self._player_1_active
        self._score_board.switch_active_player(self._tank1 if self._player_1_active else self._tank2)

        self._tank1.stop_animating()
        self._tank2.stop_animating()

    # Called after handle agents
    def on_loop(self, elapsed_time):
        # Update Tank1
        self._tank1.update(elapsed_time)

        # update tank2
        self._tank2.update(elapsed_time)

        if self._game_over:
            # send signal to display result
            self._score_board.end_game(self._tank1 if self._tank1.is_alive() else self._tank2)

        # Update Scoreboard
        self._score_board.update()

        # Print out game status - Note this is done again to catch
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

    def _handle_action_taken(self, no_reward=False):
        # Generate the state, note that here a NON firing action was taken, so reward will be None(?)
        reward = NOMINAL_REWARD/4  # A nominal reward amount

        if no_reward:
            # print("NO REWARD")
            reward = 0

        state_now = self.get_game_state()
        if self._training_mode:
            # print("HANDLE ACTION TAKEN")
            print("REWARD: " + str(reward))
            self._ml_step_callback(state_now, reward, self._game_over)
        self._action_taken = False

    def on_cleanup(self):
        # pygame.quit()
        pass

    def on_execute(self):
        # Allow a game to restart
        while True:
            if not self.on_init():
                self._running = False
                break
            else:
                # successful init
                self._handle_action_taken()

            # Run the main game loop
            last_time = pygame.time.get_ticks()
            while self._running:
                with self._lock:
                    if self._action_taken:
                        # print("loop handle")
                        self._handle_action_taken()

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
