import os, sys
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from collections import deque
from .state_translator import StateTranslator


class Agent:
    """
    Given an environment state, choose an action, and learn from the reward
    https://towardsdatascience.com/reinforcement-learning-w-keras-openai-dqns-1eed3a5338c

    https://towardsdatascience.com/deep-q-learning-tutorial-mindqn-2a4c855abffc

    https://www.researchgate.net/post/What-are-possible-reasons-why-Q-loss-is-not-converging-in-Deep-Q-Learning-algorithm

    """

    def __init__(self, env, model=None, epsilon=1.0, epsilon_min=0.10, frames_per_step=4):
        self.env = env
        self.StateTrans = StateTranslator(env, n_objects_in_state=2)
        self.board = np.zeros(env.board)
        self.frames_per_step = frames_per_step
        self.state_shape = self.StateTrans.state_shape * frames_per_step
        print('my state shape is:', self.state_shape)
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = 0.99
        self.learning_rate = 0.001
        self.tau = .125

        if model == None:
            self.model = self.create_model()
        else:
            self.model = model
        self.target_model = self.create_model()

    def create_model(self):
        model = Sequential()
        model.add(Dense(50, input_dim=self.state_shape, activation="relu"))
        model.add(Dense(4))
        model.compile(loss="MSE",
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return random.choice(self.env.action_space)

        action_values = self.model.predict(state.reshape(-1, self.state_shape))[0]
        action = np.argmax(action_values)

        return action

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 256
        if len(self.memory) < batch_size:
            return

        samples = random.sample(self.memory, batch_size)

        states = np.array([])
        actions = np.array([])
        rewards = []
        dones = []
        new_states = np.array([])

        for sample in samples:
            state, action, reward, new_state, done = sample

            states = np.append(states, state)
            actions = np.append(actions, action)
            rewards.append(reward)
            new_states = np.append(new_states, new_state)
            dones.append(done)

        new_states = new_states.reshape(batch_size, self.state_shape)
        targets = self.target_model.predict(states.reshape(batch_size, self.state_shape))
        targets = targets.reshape(batch_size, 4)
        for i in range(batch_size):
            if dones[i]:
                targets[i][int(actions[i])] = rewards[i]

            else:
                Q_future = max(self.target_model.predict(new_states[i].reshape(-1, self.state_shape))[0])
                #                 print('targets i', targets[i])
                #                 print('actions[i]', actions[i])
                targets[i][int(actions[i])] = rewards[i] + Q_future * self.gamma

        self.model.fit(states.reshape(batch_size, self.state_shape), targets,
                       epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)
