from rl_game.game.environment import game_runner as GR
from rl_game.rl_agent.rl_agent import Agent
import keras



def main_rl(config: dict) -> None:
    screen, board, game_over, victory_screen, clock = GR.create_static_images()
    env = GR.initialize_env(config)
    model = keras.models.load_model('rl_game/rl_agent/models/July31-0.001_LR-4-FR-2_obj_det-200r_-200p/trial-800')
    print('model_loaded')
    agent = Agent(env,
                  model=model,
                  epsilon=0,
                  epsilon_min=0)

    while True:
        victory, collision = GR.run_game_with_agent(agent, env, board, screen, clock)

        GR.play_victory_screen(screen, victory_screen, victory)

        GR.play_game_over_screen(screen, game_over, collision)

        reset_same, random_reset = GR.restart_game()

        # Depending on key press, we restart the same game or a random new one
        if reset_same == True:
            env.env_reset()

        elif random_reset == True:
            env = GR.initialize_env(config)

def main_person(config: dict) -> None:
    screen, board, game_over, victory_screen, clock = GR.create_static_images()
    env = GR.initialize_env(config)

    while True:
        victory, collision = GR.run_game(env, board, screen, clock)

        GR.play_victory_screen(screen, victory_screen, victory)

        GR.play_game_over_screen(screen, game_over, collision)

        reset_same, random_reset = GR.restart_game()

        # Depending on key press, we restart the same game or a random new one
        if reset_same == True:
            env.env_reset()

        elif random_reset == True:
            env = GR.initialize_env(config)


