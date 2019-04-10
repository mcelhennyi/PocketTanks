import json
import os
import time
import matplotlib.pyplot as plt
import numpy as np


class DataLogger:
    def __init__(self, n_episodes, save_period, batch_size, state_size, action_size):
        self._file_name = "logs/data_" + time.strftime("%Y%m%d-%H%M%S") + ".json"

        # Open dir
        if not os.path.isdir('logs'):
            os.mkdir('logs')

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
            json.dump(self._output, f)

    def show_graphs(self):

        # Show First player graph
        x = []
        y = {

        }
        epsilon = []
        index = 0
        for game in self._output['output']['games']:
            # make the X for the graph (games played)
            x.append(index)
            index += 1

            # Make the y for each graph
            if game['winner'] not in y:
                y[game['winner']] = [1]
            else:
                y[game['winner']] = np.max(y[game['winner']]) + 1

            # Save off epsilon
            epsilon.append(game['epsilon'])

        # Draw both plots
        for i, key in enumerate(y):
            plt.subplot(3, 1, 1 + i)
            plt.plot(x, y[key], 'o-')
            plt.title(key + " wins.")
            plt.ylabel('Win Amount')

        plt.subplot(3, 1, 3)
        plt.plot(x, epsilon, 'o-')
        plt.title("Epsilon over time.")
        plt.ylabel('Epsilon')
        plt.xlabel('Game Number')

        plt.show()
