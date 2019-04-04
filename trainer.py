import os
import threading
import time
import numpy as np

from threading import Thread

from agents.dqn_agent import DqnAgent
from main import App


# Number of games to play
n_episodes = 200
save_period = 50  # Saves off every n episodes' model
batch_size = 32  # multiples of 2

state_size = 8
action_size = 7

output_dir = 'models/'


class Handler:
    def __init__(self):
        self.lock = threading.Lock()
        self.callback_triggered = False

        self.next_state = None
        self.reward = None
        self.game_over = None

    def callback(self, next_state, reward, game_over):
        with self.lock:
            print("SET TRUE")
            self.callback_triggered = True

            self.next_state = next_state
            self.reward = reward
            self.game_over = game_over

    def wait_for_callback(self,):
        while True:
            with self.lock:
                if self.callback_triggered:
                    print("Next State received!")
                    self.callback_triggered = False
                    break

            time.sleep(0.0001)

        return self.next_state, self.reward, self.game_over


# Setup our output dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a game environment
handler = Handler()
game = App(training_mode=True, ml_step_callback=handler.callback)
thread = Thread(target=game.on_execute)
thread.start()

# Create the agent
agent = DqnAgent(state_size, action_size)

# Let the game start up
time.sleep(5)

# Play n_episodes count games
for e in range(n_episodes): # iterate over new episodes of the game
    # Reset the state of the game with a restart, wait for it to take
    print("Resetting game state...")
    game.queue_ml_action(-1)  # -1 restarts, -2 quits
    _ = handler.wait_for_callback()
    state = np.reshape(game.get_game_state(), [1, state_size])
    game_over = False
    print("Reset. Starting game " + str(e))

    while not game_over:

        print("**********************************************")
        print("****************** NEW ROUND *****************")
        print("**********************************************")
        # Make our agent act
        action = agent.act(state)
        print("queue action: " + str(action))
        game.queue_ml_action(action)  # Sends the 'step' commanad

        # Get the next state, etc from the action
        print("wait for next state")
        next_state, reward, game_over = handler.wait_for_callback()
        print("handle next state")

        # Remember the action
        next_state = np.reshape(next_state, [1, state_size])
        agent.remember(state, action, reward, next_state, game_over)

        # Save the state as next state
        state = next_state

        if game_over:
            print("GAME OVER!!!!!!")

    print("episode: {}/{}, score: {}, e: {:.2}"  # print the episode's score and agent's epsilon
          .format(e, n_episodes, time, agent.get_epsilon()))

    # Train the agent off the game we just played
    if len(agent.get_memory()) > batch_size:
        agent.replay(batch_size)

    # Save off every 50 episodes
    if e % save_period == 0:
        agent.save(output_dir + "weights_" + '{:04d}'.format(e) + ".hdf5")
