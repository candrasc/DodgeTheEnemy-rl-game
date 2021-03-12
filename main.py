import json
from environment.game import run_game, initialize_env, create_static_images, \
                 play_victory_screen, play_game_over_screen, restart_game
                 
import pygame

with open("game_config.json", "rb") as f:
    config = json.load(f)

if __name__ == '__main__':

    screen, board, game_over, victory_screen, clock = create_static_images()
    Env = initialize_env(config)

    while True:
        victory, collision = run_game(Env, board, screen, clock)

        play_victory_screen(screen, victory_screen, victory)

        play_game_over_screen(screen, game_over, collision)

        reset_same, random_reset = restart_game()

        # Depending on key press, we restart the same game or a random new one
        if reset_same == True:
            Env.env_reset()

        elif random_reset == True:
            Env = initialize_env(config)
