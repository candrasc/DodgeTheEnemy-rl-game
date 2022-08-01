import json
import argparse
from rl_game import run_game

MODEL_NAME = 'Aug1-0.001_LR-4-FR-2_obj_det-200r_-200p/trial-300'

def run():

    parser = argparse.ArgumentParser()
    # Do you want to play or watch AI
    parser.add_argument('--mode', '-m',
                        help="Enter 'play' or 'ai'")
    # Do you want dybamic or static game config
    parser.add_argument('--config', '-c',
                        help="Enter 'test' or 'game'")
    args = parser.parse_args()

    with open("game_config.json", "rb") as f:
        config = json.load(f)
    
    if args.config == 'game':
        conf = config['play']
    elif args.config == 'test':
        conf = config['test']
    else:
        raise ValueError("config must be 'game' or 'test'")
    
    if args.mode == 'ai':
        run_game.main_rl(conf, MODEL_NAME)
    elif args.mode == 'play':
        run_game.main_person(conf)
    else:
        raise ValueError("mode must be 'ai' or 'play'")

    
if __name__=='__main__':
    run()
