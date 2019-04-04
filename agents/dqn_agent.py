import os
import random

from agents import BaseAgent

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np


class DqnAgent(BaseAgent):
    def __init__(self, state_size, action_size, load_weights=False):
        BaseAgent.__init__(self)

        self._state_size = state_size
        self._action_size  = action_size

        self._gamma = 0.95
        self._epsilon = 1.0
        self._epsilon_decay = 0.995
        self._epsilon_min = 0.01

        self._learning_rate = 0.001
        self._model = None

        self._build_model()

        # Load up known weights
        max_file_number = ''
        if load_weights:
            for file in os.listdir('/models'):
                file_without_ending = file.split('.')[0]
                file_number = file_without_ending.split('_')[1]
                if int(file_number) > int(max_file_number):
                    max_file_number = file_number
            self.load(os.path.join('models', 'weights_' + max_file_number + '.hdf5'))

    def _build_model(self):
        # neural net to approximate Q-value function:
        self._model = Sequential()

        # Hidden Layers
        self._model.add(Dense(24, input_dim=self._state_size, activation='relu'))  # 1st hidden layer; states as input
        self._model.add(Dense(24, activation='relu'))  # 2nd hidden layer

        # Output layer
        self._model.add(Dense(self._action_size, activation='linear'))

        # Compile the model
        self._model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))

    def get_epsilon(self):
        return self._epsilon

    def get_memory(self):
        return self._memory

    def act(self, state):
        if np.random.rand() <= self._epsilon:
            # Explore
            return random.randrange(self._action_size)

        # Exploit
        act_values = self._model.predict(state)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        # Sample randomly from memory
        minibatch = random.sample(self._memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            # For each memory
            target = reward  # if done (boolean whether game ended or not, i.e., whether final state or not), then target = reward
            if not done:
                # if not done, then predict future discounted reward
                target = (reward + self._gamma *  # (target) = reward + (discount rate gamma) *
                          np.amax(self._model.predict(next_state)[0]))  # (maximum target Q based on future action a')

            target_f = self._model.predict(state)  # approximately map current state to future discounted reward
            target_f[0][action] = target

            # single epoch of training with x=state, y=target_f; fit decreases loss btwn target_f and y_hat
            self._model.fit(state, target_f, epochs=1, verbose=0)

        # Decay the epsilon value to increase exploitation
        if self._epsilon > self._epsilon_min:
            self._epsilon *= self._epsilon_decay

    def load(self, name):
        self._model.load_weights(name)

    def save(self, name):
        self._model.save_weights(name)
