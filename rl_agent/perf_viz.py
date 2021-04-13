"""
Create a visualization of reward per trial for a trained agent
"""

import pickle, os
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import pandas as pd

def gen_report(directory):

    directory = directory
    filename = "results_dic.pkl"
    file_path = os.sep.join([directory, filename])

    with open(file_path, 'rb') as f:
        results = pickle.load(f)

    df = pd.DataFrame.from_dict(results, orient='index', columns = ['reward'])


    df['rolling_5'] = df['reward'].rolling(5).mean()
    df['rolling_10'] = df['reward'].rolling(10).mean()
    df['rolling_20'] = df['reward'].rolling(20).mean()
    df['rolling_50'] = df['reward'].rolling(50).mean()

    plt.figure(figsize = (12, 7))
    #plt.plot(df['reward'], label = 'True rewards')
    #plt.plot(df['rolling_5'], label = '5 trial rolling ave')
    plt.plot(df['rolling_10'], label = '10 trial rolling ave', color = 'blue', linewidth = 3)
    plt.plot(df['rolling_20'], label = '20 trial rolling ave', color = 'red', linewidth = 3)
    plt.plot(df['rolling_50'], label = '50 trial rolling ave', color = 'green', linewidth = 3)
    plt.title("Agent Reward Per Trial: 200 Reward, 250 Penalty")
    plt.xlabel('Trial')
    plt.ylabel('Total Reward')
    plt.legend()
    plt.savefig(os.sep.join([directory, 'reward_per_trial.png']))

if __name__ == "__main__":
    gen_report('0.001_LR-3_HL-1_obj_det-250r_-200p')
