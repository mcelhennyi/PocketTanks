import json
import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np


class DataLogger:
    def __init__(self, n_episodes=0, save_period=0, batch_size=0, state_size=0, action_size=0, load_file=None):
        self._file_name = "logs/data_" + time.strftime("%Y%m%d-%H%M%S") + ".json"

        if not load_file:
            # Open dir
            if not os.path.isdir('logs'):
                os.mkdir('logs')

            assert n_episodes != 0
            assert save_period != 0
            assert batch_size != 0
            assert state_size != 0
            assert action_size != 0

            # Write header/open file
            self._output = {
                "config": {
                    "n_episodes": n_episodes,
                    "save_period": save_period,
                    "batch_size": batch_size,
                    "state_size": state_size,
                    "action_size": action_size,
                },
                "output": {
                    #
                    "steps": [],
                    "games": [],
                }
            }

            # Create the file
            self.write_object_to_file()
        else:
            self._output = {}
            with open(os.path.join('logs', load_file), mode='r') as f:
                file_data = f.read()
                self._output = json.loads(file_data)

    def add_step(self, data):
        self._output['output']['steps'].append(data)

    def add_game(self, data):
        self._output['output']['games'].append(data)
        #
        # if len(self._output['output']['games']) % 50 == 0:
        #     with open(self._file_name, mode='w') as f:
        #         json.dump(self._output, f)

    def add_any(self, key, value):
        self._output['output'][key] = value

    def write_object_to_file(self):
        with open(self._file_name, mode='w') as f:
            json.dump(self._output, f, default=self._default, indent=3)

    def _default(self, obj):
        if type(obj).__module__ == np.__name__:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj.item()
        raise TypeError('Unknown type:', type(obj))

    def show_graphs(self):

        # Show First player graph
        x = []
        y = {
            "Player 1": [],
            "Player 2": [],
        }
        epsilon = []
        player_health = {
            "player_1_health": [],
            "player_2_health": [],
        }
        index = 0
        for game in self._output['output']['games']:
            # make the X for the graph (games played)
            x.append(index)

            # Make the y for each graph
            if len(y["Player 1"]) == 0:
                y["Player 1"].append(1 if game['winner'] == 'Player 1' else 0)
            else:
                y["Player 1"].append(np.max(y["Player 1"]) + 1 if game['winner'] == 'Player 1' else np.max(y["Player 1"]))

            if len(y["Player 2"]) == 0:
                y["Player 2"].append(1 if game['winner'] == 'Player 2' else 0)
            else:
                y["Player 2"].append(np.max(y["Player 2"]) + 1 if game['winner'] == 'Player 2' else np.max(y["Player 2"]))

            # Save off epsilon
            epsilon.append(game['epsilon'])

            # Mark health
            player_health['player_2_health'].append(game['player_2_health'])

            index += 1

        # Draw both plots
        for i, key in enumerate(y):
            plt.subplot(4, 1, 1 + i)
            plt.plot(x, y[key], 'o-')
            plt.title(key + " wins.")
            plt.ylabel('Win Amount')

        plt.subplot(4, 1, 3)
        plt.plot(x, epsilon, 'o-')
        plt.title("Epsilon over time.")
        plt.ylabel('Epsilon')

        plt.subplot(4, 1, 4)
        plt.plot(x, player_health['player_2_health'], 'o-')
        plt.title("Player 2 health at end")
        plt.ylabel('Health')
        plt.xlabel('Game Number')

        plt.subplots_adjust(hspace=0.5)

        plt.show()


if __name__ == '__main__':
    filename = sys.argv[1]
    dl = DataLogger(load_file=filename)
    dl.show_graphs()
