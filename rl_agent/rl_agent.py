import os, sys, pickle
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import random
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam

from collections import deque
from rl_agent.state_translator import StateTranslator
from rl_agent.perf_viz import gen_report

class Agent:
    """
    Given an environment state, choose an action, and learn from the reward
    https://towardsdatascience.com/reinforcement-learning-w-keras-openai-dqns-1eed3a5338c

    https://towardsdatascience.com/deep-q-learning-tutorial-mindqn-2a4c855abffc

    https://www.researchgate.net/post/What-are-possible-reasons-why-Q-loss-is-not-converging-in-Deep-Q-Learning-algorithm

    """

    def __init__(self, env, model=None, epsilon = 1.0, epsilon_min = 0.05, frames_per_step=4):
        self.env = env
        self.StateTrans = StateTranslator(env, n_objects_in_state = 2)
        self.board = np.zeros(env.board)
        self.env     = env
        self.frames_per_step = frames_per_step
        self.state_shape  = self.StateTrans.state_shape*4
        print('my state shape is:', self.state_shape)
        self.memory  = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = 0.950
        self.learning_rate = 0.001
        self.tau = .125

        if model == None:
            self.model = self.create_model()
        else:
            self.model = model
        self.target_model = self.create_model()

    def create_model(self):
        model   = Sequential()
        model.add(Dense(2000, input_dim=self.state_shape, activation="relu"))
        model.add(Dense(1000, activation="relu"))
        model.add(Dense(500, activation="relu"))
        model.add(Dense(1000, activation="relu"))
        model.add(Dense(500, activation="relu"))
        model.add(Dense(100, activation="relu"))
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
        ########################
        # This can be sped up significantly, but processing all samples in batch rather than 1 at a time
        ####################
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



from environment.environment import Environment

def main():
    """
    Script to train Agent
    Currently combine every 4 steps into one state and take an action for 4
    steps

    Trials are not ended when the agent ends the game... they are just there to
    help save the agent improvement over time

    Instead the trial will continue, but the environment will random reset
    """

    env = Environment((700,700))

    epsilon = .95
    min_epsilon = 0.05

    trials  = 10000
    trial_len = 500
    pos_reward = 200
    neg_reward = -250


    # Can load a previous model to speed up learning if you want
   # model = keras.models.load_model('April21-0.001_LR-3_HL-2_obj_det-250r_-200p/trial-350_200_reward')

    dqn_agent = Agent(env=env,
                      #model = model,
                      epsilon = epsilon,
                      epsilon_min = min_epsilon)

    # This is for naming the folder
    learning_rate = dqn_agent.learning_rate
    num_hidden_layers = 3
    num_obj_detected = dqn_agent.StateTrans.n_obj

    num_steps_per_move = dqn_agent.frames_per_step
    steps = []

    # Record sum of reward per trial for plotting
    results_dic = {}
    for trial in range(trials):
        results_dic[trial] = 0
        print('trial', trial)

        env.random_initialize(player_step_size_range = [3, 4],
                             player_size_range = [30, 31],
                            # Let's see if it can learn to avoid one enemy and collect rewards
                             num_enemies_range = [8, 9],
                             e_vel_range = [1, 3],
                             enemy_size_range = [30, 31],

                             num_rewards_range = [8, 9],
                             r_vel_range = [1,2],
                             reward_size_range = [30, 31]
                             )

        player, enemies, goods = env.return_cur_env()

        # Repeat same state 4 times to start to get right length of state vec
        cur_state = np.array([])
        action_start = np.random.randint(0, 4)
        for i in range(num_steps_per_move):

            dqn_agent.StateTrans.set_objects(player, enemies, goods)
            cur_state_mini = dqn_agent.StateTrans.get_state()
            cur_state = np.append(cur_state, cur_state_mini)


        print('state_shape1', len(cur_state))
        for step in range(trial_len):
            if step % 50 == 0:
                print('step: ', step)

            # Given an action, move 4 steps in that direction and record all vectors
            #####################
            action = dqn_agent.act(cur_state)
            new_state = np.array([])
            reward = 0
            done = False
            for i in range(num_steps_per_move):
                new_player, new_enemies, new_goods, \
                collision, goods_collected = env.env_take_step(action)

                dqn_agent.StateTrans.set_objects(new_player, new_enemies, goods)
                new_state_mini, reward_mini, done_mini = dqn_agent.StateTrans.state_translation(collision, goods_collected)
                new_state = np.append(new_state, new_state_mini)
                reward += reward_mini
                if done_mini == True:
                    done = True

            # Ensure rewards are consistent
            if reward>=5:
                reward = pos_reward
                print('reward collected')
            # Make it slightly worse to die... staying alive is more important
            # than collecting rewards
            elif reward<=-5:
                reward = neg_reward
            # If in 4 frames, the agent dies and collects rewards, or doesn't
            # collect anything we will not return any type of feedback
            elif reward > -5 and reward <5:
                reward = -1

            results_dic[trial] += reward
            dqn_agent.remember(cur_state, action, reward, new_state, done)

            cur_state = new_state

            if step % 5 == 0:
                dqn_agent.replay()       # internally iterates default (prediction) model
                # iterates target model
                dqn_agent.target_train()

            if done:
                if trial%50 == 0:
                    print('done', reward)
                    direct = f"April21-{learning_rate}_LR-{num_hidden_layers}_HL-{num_obj_detected}_obj_det-{pos_reward}r_{neg_reward}p"
                    dqn_agent.save_model(direct + f"/trial-{trial+350}_200_reward")
                    with open(direct + "/results_dic.pkl", 'wb') as f:
                        pickle.dump(results_dic, f)
                if trial%100 == 0:
                    gen_report(direct)

                break


if __name__ == "__main__":
    main()
