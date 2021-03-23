import json
from environment.game import run_game, run_game_with_agent, initialize_env, create_static_images, \
                 play_victory_screen, play_game_over_screen, restart_game
from rl_agent.rl_agent import Agent
import pygame
import keras


with open("game_config.json", "rb") as f:
    config = json.load(f)

if __name__ == '__main__':


    screen, board, game_over, victory_screen, clock = create_static_images()
    Env = initialize_env(config)
    model = keras.models.load_model('rl_agent/trial-4_model_higher_penalty_transfer_learning_from_good_perf')
    print('model_loaded')
    Agent = Agent(Env,
                  model=model,
                  epsilon = 0,
                  epsilon_min = 0)

    while True:
        victory, collision = run_game_with_agent(Agent, Env, board, screen, clock)

        play_victory_screen(screen, victory_screen, victory)

        play_game_over_screen(screen, game_over, collision)

        reset_same, random_reset = restart_game()

        # Depending on key press, we restart the same game or a random new one
        if reset_same == True:
            Env.env_reset()

        elif random_reset == True:
            Env = initialize_env(config)
