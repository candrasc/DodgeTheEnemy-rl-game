import json
import os

import keras
import numpy as np
from rl_game.game.environment.environment import Environment
from rl_game.rl_agent import current_directory
from rl_game.rl_agent.perf_viz import gen_report
from rl_game.rl_agent.rl_agent import Agent

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

def main():

    epsilon = .95
    min_epsilon = 0.5
    steps_to_train = 20

    trials = 1000
    trial_len = 1000
    pos_reward = 200
    neg_reward = -200
    terminal_reward = 1000


    env_config = {
                'player_step_size_range':[3, 4],
                'player_size_range' : [30, 31],

                'num_enemies_range' : [20, 21],
                'e_vel_range' : [1, 3],
                'enemy_size_range' : [30, 31],

                'num_rewards_range' : [20, 21],
                'r_vel_range' : [1, 2],
                'reward_size_range' : [30, 31]
                }

    env = Environment((700, 700))
    env.random_initialize(**env_config)


    # model_name = 'Aug1-0.001_LR-4-FR-2_obj_det-200r_-200p/trial-850'
    # model_path = os.path.join(FILE_PATH, 'models', model_name)
    # model = keras.models.load_model(model_path)

    dqn_agent = Agent(env=env,
                     # model = model,
                      epsilon=epsilon,
                      epsilon_min=min_epsilon)

    # This is for naming the folder
    learning_rate = dqn_agent.learning_rate
    num_obj_detected = dqn_agent.StateTrans.n_obj
    num_steps_per_move = dqn_agent.frames_per_step

    # Record sum of reward per trial for plotting
    results_dic = {}
    for trial in range(trials+1):
        results_dic[trial] = 0
        print('trial', trial)

        env.random_initialize(**env_config)

        player, enemies, goods = env.return_env_object_states()

        # Repeat same state 4 times to start to get right length of state vec
        cur_state = np.array([])
        for _ in range(num_steps_per_move):
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
            for _ in range(num_steps_per_move):
                new_player, new_enemies, new_goods, \
                collision, goods_collected = env.env_take_step(action)

                dqn_agent.StateTrans.set_objects(new_player, new_enemies, goods)
                new_state_mini, reward_mini, done_mini = dqn_agent.StateTrans.state_translation(collision,
                                                                                                goods_collected)
                new_state = np.append(new_state, new_state_mini)
                reward += reward_mini
                if done_mini:
                    done = True

            # Ensure rewards are consistent
            if reward >= 20:
                reward = pos_reward
                print('reward collected')

            elif reward >10*5:
                reward = terminal_reward
                print('we won!')

            elif reward <= -20:
                reward = neg_reward
                if done:
                    print('collision')
                else:
                    print('wall')
            # If in 4 frames, the agent dies and collects rewards, or doesn't
            # collect anything we will not return any type of feedback
            elif reward > -20 and reward < 20:
                reward = -1

            results_dic[trial] += reward
            dqn_agent.remember(cur_state, action, reward, new_state, done)

            cur_state = new_state

            if step % steps_to_train == 0:
                dqn_agent.replay()  # internally iterates default (prediction) model
                # iterates target model
                dqn_agent.target_train()

            if done:
                if trial % 50 == 0:

                    print(f'saving model at trial {trial}')
                    
                    relative_path = f"models/Aug2-wide-nowallpen"
                    trial_path = f'trial-{trial}'
                    full_save_path = os.path.join(FILE_PATH, relative_path, trial_path)
                    dqn_agent.save_model(full_save_path)

                    with open(os.path.join(FILE_PATH, relative_path, "results_dic.json"), 'w') as f:
                        json.dump(results_dic, f)
                    
                    lines = os.path.join(FILE_PATH, relative_path)
                    gen_report(lines)

                if trial % 100 == 0:
                    # Reset the exploration every 100 trials
                    dqn_agent.epsilon = .50

                break


if __name__ == "__main__":
    main()
