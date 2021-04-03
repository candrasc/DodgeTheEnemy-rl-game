# rl_game_dodge_the_enemy
I created a game from scratch with the purpose of teaching a reinforcement learning agent to play it. The core of the game is the environment class that sets what is possible within its boundries and allows the objects within it to act in a certain way. I also created object classes which interact within the environment (Players, Enemeis, Rewards). Its mostly a lot of numpy and rendered with Pygame! 

This game can be played by a player or an reinforcement learning agent. You can choose main.py to play yourself, and main_rl.py to watch an rl agent play.

The RL agent has been able to succesfully win an easier version of the game you can see below. In the near future, I will write an article about the methodology and "tricks" I used to get the agent to learn the game. This agent is far from perfect and will be updated to more advanced algorithms such as actor-critic.

## Game Objectives:
1) Collect all the rewards (multi-color bouncing squares)
2) Dodge the enemies (red bouncing squares)

## See it in action! ##
### Below is the RL agent beating a simplified version of the game where all objects are the same size 

![alt text](https://github.com/candrasc/rl_game_dodge_the_enemy/blob/main/read_me_images/ezgif-2-b3433a7c00d1.gif "RL Agent Victory")

## Try it out yourself
1) Clone the repo
2) Create a conda environment to run the game with: "conda create --name <env> --file requirements.txt"
3) Edit the game config to have your desired params such as range of: enemy velocities, num enemies, enemy size (and the same for rewards to collect)
4) Run "main_rl.py" from the console and you can watch the AI play the game! Feel free to try and load different models I have trained and saved with various results in the rl_agent/previously_trained_agents directory
5) To restart the game in the same environment, double tap "space". To restart in a new random environment, double tap "q"

If you want to play the game yourself, just run "main.py"





