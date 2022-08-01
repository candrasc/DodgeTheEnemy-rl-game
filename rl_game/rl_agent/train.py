from rl_game.game.environment.environment import Environment
from rl_game.rl_agent.perf_viz import gen_report
from rl_game.rl_agent.rl_agent import Agent
from rl_game.rl_agent import current_directory
import numpy as np
import pickle
import os
import keras


def main():

    env = Environment((700, 700))
    env.random_initialize(player_step_size_range=[3, 4],
                          player_size_range=[30, 31],
                          
                          num_enemies_range=[15, 16],
                          e_vel_range=[1, 3],
                          enemy_size_range=[30, 31],

                          num_rewards_range=[15, 16],
                          r_vel_range=[1, 2],
                          reward_size_range=[30, 31]
                          )

    epsilon = .95
    min_epsilon = 0.5

    trials = 10000
    trial_len = 500
    pos_reward = 200
    neg_reward = -200
    terminal_reward = 1000

    # Can load a previous model to speed up learning if you want
    model = keras.models.load_model('./rl_game/rl_agent/models/July31-0.001_LR-4-FR-2_obj_det-200r_-200p/trial-50')

    dqn_agent = Agent(env=env,
                      model = model,
                      epsilon=epsilon,
                      epsilon_min=min_epsilon)

    # This is for naming the folder
    learning_rate = dqn_agent.learning_rate
    num_obj_detected = dqn_agent.StateTrans.n_obj
    num_steps_per_move = dqn_agent.frames_per_step

    # Record sum of reward per trial for plotting
    results_dic = {}
    for trial in range(trials):
        results_dic[trial] = 0
        print('trial', trial)

        env.random_initialize(player_step_size_range=[3, 4],
                              player_size_range=[30, 31],
                              # Let's see if it can learn to avoid one enemy and collect rewards
                              num_enemies_range=[15, 16],
                              e_vel_range=[1, 3],
                              enemy_size_range=[30, 31],

                              num_rewards_range=[15, 16],
                              r_vel_range=[1, 2],
                              reward_size_range=[30, 31]
                              )

        player, enemies, goods = env.return_env_object_states()

        # Repeat same state 4 times to start to get right length of state vec
        cur_state = np.array([])
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
                new_state_mini, reward_mini, done_mini = dqn_agent.StateTrans.state_translation(collision,
                                                                                                goods_collected)
                new_state = np.append(new_state, new_state_mini)
                reward += reward_mini
                if done_mini == True:
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

            if step % 5 == 0:
                dqn_agent.replay()  # internally iterates default (prediction) model
                # iterates target model
                dqn_agent.target_train()

            if done:
                if trial % 50 == 0:

                    print(f'saving model at trial {trial}')
                    
                    direct = "./rl_game/rl_agent/models/July31-{learning_rate}_LR-{num_steps_per_move}-FR-{num_obj_detected}_obj_det-{pos_reward}r_{neg_reward}p"
                    dqn_agent.save_model(direct+f'/trial-{trial}')

                    with open(direct + "/results_dic.pkl", 'wb') as f:
                        pickle.dump(results_dic, f)

                if trial % 100 == 0:
                    # Reset the exploration every 100 trials
                    dqn_agent.epsilon = .50
                    dir_path = os.path.dirname(os.path.realpath(__file__))
                    lines = os.path.join(dir_path, direct)
                    gen_report(lines)
                break


if __name__ == "__main__":
    main()
