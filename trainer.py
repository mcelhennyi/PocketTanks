import os
import threading
import time
from collections import deque

import numpy as np

from threading import Thread

from agents.dqn_agent import DqnAgent
from main import App


# Number of games to play
from utils.logger import DataLogger

n_episodes = 10000
save_period = 50  # Saves off every n episodes' model
batch_size = 32  # multiples of 2

state_size = 10
action_size = 5  # 7 if we want to move, not doing that for now

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
            # print("SET TRUE")
            self.callback_triggered = True

            self.next_state = next_state
            self.reward = reward
            self.game_over = game_over

    def wait_for_callback(self,):
        while True:
            with self.lock:
                if self.callback_triggered:
                    # print("Next State received!")
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

# Create a data logger
logger = DataLogger(
    n_episodes,
    save_period,
    batch_size,
    state_size,
    action_size
)

# Let the game start up
time.sleep(5)

# Track some times
last_play_time = 0
last_train_time = 0

# Sliding window so we can check the winning rate, and see if its increasing
winners_window = []
window_size = int(n_episodes*0.1)
p1_win_ratio = 0
p2_win_ratio = 0

# Track winner count
winners = {}

# Play n_episodes count games
for e in range(n_episodes): # iterate over new episodes of the game
    try:
        # Reset the state of the game with a restart, wait for it to take
        print("Resetting game state...")
        game.queue_ml_action(-1)  # -1 restarts, -2 quits
        _ = handler.wait_for_callback()
        state = np.reshape(game.get_game_state(), [1, state_size])
        game_over = False
        print("Reset. Starting game " + str(e))

        time_start = time.time()
        msg = "Game " + str(e + 1) + " of " + str(n_episodes) + ",  LPT: " + \
              str(last_play_time) + ", LTT: " + str(last_train_time) + ", epsilon: " + str(agent.get_epsilon())
        game.show_message(msg)
        print(msg)

        for winner in winners:
            print(winner + " has " + str(winners[winner]) + " wins so far.")

        while not game_over:

            # print("**********************************************")
            # print("****************** NEW ROUND *****************")
            # print("**********************************************")
            # Make our agent act
            action = agent.act(state)
            # print("queue action: " + str(action))
            game.queue_ml_action(action)  # Sends the 'step' commanad

            # Get the next state, etc from the action
            # print("wait for next state")
            next_state, reward, game_over = handler.wait_for_callback()
            # print("handle next state")

            # Remember the action
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, game_over)

            # Save off this round
            #logger.add_step({
            #    "state": state,
            #    "action": action,
            #    "reward": reward,
            #    "next_state": next_state,
            #    "game_over": game_over
            #})

            # Save the state as next state
            state = next_state

            if game_over:
                print("GAME OVER: " + game.get_winner().get_name() + " wins!")
                if game.get_winner().get_name() not in winners:
                    winners[game.get_winner().get_name()] = 1
                else:
                    winners[game.get_winner().get_name()] += 1

                winners_window.append(game.get_winner().get_name())

        print("episode: {}/{}, e: {:.2}"  # print the episode's score and agent's epsilon
              .format(e, n_episodes, agent.get_epsilon()))

        game_end = time.time()

        # Train the agent off the game we just played
        if len(agent.get_memory()) > batch_size:
            agent.replay(batch_size)

        train_end = time.time()

        last_play_time = (int((game_end-time_start) / 60 * 10000)) / 10000
        last_train_time = (int((train_end-game_end) / 60 * 10000)) / 10000

        print("Playing took: " + str(last_play_time) + " minutes.")
        print("Training took: " + str(last_train_time) + " minutes.")

        if len(winners_window) == window_size:
            win_count_1 = winners_window.count(game.get_player_1().get_name())
            win_count_2 = winners_window.count(game.get_player_2().get_name())
            p1_win_ratio = win_count_1/window_size
            p2_win_ratio = win_count_2/window_size
            winners_window = []

        print("Player 1 win ratio: " + str(p1_win_ratio))
        print("Player 2 win ratio: " + str(p2_win_ratio))

        logger.add_game({
            "winner": "Player 1" if game.get_winner() == game.get_player_1() else "Player 2",
            "play_time": last_play_time,
            "train_time": last_train_time,
            "epsilon": agent.get_epsilon(),
            "player_1_health": game.get_player_1().get_health(),
            "player_2_health": game.get_player_2().get_health(),
            "p1_win_ratio": p1_win_ratio,
            "p2_win_ratio": p2_win_ratio
        })

        # Save off every 50 episodes
        if e % save_period == 0:
            agent.save(output_dir + "weights_" + '{:04d}'.format(e) + ".hdf5")
            logger.write_object_to_file()

        logger.add_any('winners', winners)
    except KeyboardInterrupt:
        break


# End game
print("Ending game...")
game.queue_ml_action(-2)
print("Ended.")


print("Writing out log file...")
logger.write_object_to_file()
print("Log written")


print("Showing win graphs...")
logger.show_graphs()
print("Graphs closed.")
