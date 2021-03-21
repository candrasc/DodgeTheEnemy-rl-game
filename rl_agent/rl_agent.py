import os, sys
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import random
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam

from collections import deque
from rl_agent.state_translator import StateTranslator

class Agent:
    """
    Given an environment state, choose an action, and learn from the reward
    https://towardsdatascience.com/reinforcement-learning-w-keras-openai-dqns-1eed3a5338c

    https://towardsdatascience.com/deep-q-learning-tutorial-mindqn-2a4c855abffc

    https://www.researchgate.net/post/What-are-possible-reasons-why-Q-loss-is-not-converging-in-Deep-Q-Learning-algorithm

    """

    def __init__(self, env, model=None, epsilon = 1.0, epsilon_min = 0.05):
        self.env = env
        self.StateTrans = StateTranslator(env, n_objects_in_state = 4)
        self.board = np.zeros(env.board)
        self.env     = env
        self.memory  = deque(maxlen=2000)
        self.gamma = 0.85
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = 0.990
        self.learning_rate = 0.005
        self.tau = .125

        if model == None:
            self.model = self.create_model()
        else:
            self.model = model
        self.target_model = self.create_model()

    def create_model(self):
        model   = Sequential()
        state_shape  = self.StateTrans.state_shape
        model.add(Dense(48, input_dim=state_shape, activation="relu"))
        model.add(Dense(24, activation="relu"))
        model.add(Dense(12, activation="relu"))
        model.add(Dense(len(self.env.action_space)))
        model.compile(loss=keras.losses.Huber(),
            optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self, state):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return random.choice(self.env.action_space)

        action = np.argmax(self.model.predict(state.reshape(-1, self.StateTrans.state_shape))[0])
        #print(self.model.predict(state.reshape(-1, self.StateTrans.state_shape))[0])
        return action

    def remember(self, state, action, reward, new_state, done):
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 32
        if len(self.memory) < batch_size:
            return

        samples = random.sample(self.memory, batch_size)
        ########################
        # This can be sped up significantly, but processing all samples in batch rather than 1 at a time
        ####################
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state.reshape(-1, self.StateTrans.state_shape))
            if done:
                target[0][action] = reward
            else:
                Q_future = max(self.target_model.predict(new_state.reshape(-1, self.StateTrans.state_shape))[0])
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(state.reshape(-1, self.StateTrans.state_shape), target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)

"""
Try a state that includes distances to objects from player instead of the carinal positions
"""

from environment.environment import Environment

def main():

    env = Environment((700,700))

    epsilon = .95
    min_epsilon = 0.10
    min_epsilon
    # We random reset the env after every finish... trials are just for model saving
    # checkpoint purposes
    trials  = 50
    trial_len = 10000
    #model = keras.models.load_model('trial-2.model')
    # updateTargetNetwork = 1000
    dqn_agent = Agent(env=env,
                      epsilon = epsilon,
                      min_epsilon = min_epsilon)
    steps = []
    for trial in range(trials):
        print('trial', trial)
        env.random_initialize(player_step_size_range = [10, 11],
                             player_size_range = [30, 31],
                            # Let's see if it can learn to avoid one enemy and collect rewards
                             num_enemies_range = [5, 6],
                             e_vel_range = [1, 4],
                             enemy_size_range = [30, 31],

                             num_rewards_range = [5, 6],
                             r_vel_range = [1,2],
                             reward_size_range = [30, 31]
                             )

        player, enemies, goods = env.return_cur_env()

        dqn_agent.StateTrans.set_objects(player, enemies, goods)

        cur_state = dqn_agent.StateTrans.get_state()
        # Reset exploration at the start of each new random state
        dqn_agent.epsilon = 1

        for step in range(trial_len):
            if step % 100 == 0:
                print('step: ', step)


            action = dqn_agent.act(cur_state)
            new_player, new_enemies, new_goods, \
            collision, goods_collected = env.env_take_step(action)

            dqn_agent.StateTrans.set_objects(new_player, new_enemies, goods)
            new_state, reward, done = dqn_agent.StateTrans.state_translation(collision, goods_collected)


            dqn_agent.remember(cur_state, action, reward, new_state, done)

            cur_state = new_state

            if step % 100 == 0:
                dqn_agent.replay()       # internally iterates default (prediction) model
                # iterates target model
            if step % 1000 == 0:
                dqn_agent.target_train()

            if done:
                print('done')
                # break
                env.random_initialize(player_step_size_range = [10, 11],
                                     player_size_range = [30, 31],
                                    # Let's see if it can learn to avoid one enemy and collect rewards
                                     num_enemies_range = [5, 6],
                                     e_vel_range = [1, 4],
                                     enemy_size_range = [30, 31],

                                     num_rewards_range = [5, 6],
                                     r_vel_range = [1,2],
                                     reward_size_range = [30, 31]
                                     )

                player, enemies, goods = env.return_cur_env()

                dqn_agent.StateTrans.set_objects(player, enemies, goods)

                cur_state = dqn_agent.StateTrans.get_state()

            if step >= 100:

                if step % 100 == 0:

                    dqn_agent.save_model("trial-{}_model_100_replay_1000_retrain".format(trial))


    dqn_agent.save_model("training_over.model")

if __name__ == "__main__":
    main()
