import json
from rl_game.game.environment.game_runner import run_game_with_agent, initialize_env, create_static_images, \
                 play_victory_screen, play_game_over_screen, restart_game
from rl_game.rl_agent.rl_agent import Agent
import keras


with open("game_config.json", "rb") as f:
    config = json.load(f)

if __name__ == '__main__':

    screen, board, game_over, victory_screen, clock = create_static_images()
    Env = initialize_env(config)
    model = keras.models.load_model('rl_game/rl_agent/July7-0.001_LR-4-FR-2_obj_det-200r_-200p/trial-500')
    print('model_loaded')
    Agent = Agent(Env,
                  model=model,
                  epsilon=0,
                  epsilon_min=0)

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
