"""
This file stores the main functions that our main.py will use to run the game
"""
from rl_game.game.environment.environment import Environment
import pygame, sys
from rl_game.rl_agent.state_translator import StateTranslator
import numpy as np


def initialize_env(config, board_size = (700, 700)):

    p_con = config['player_configs']
    e_con = config['enemy_configs']
    r_con = config['reward_configs']

    player_size_range = p_con['player_size_range']
    player_step_size_range = p_con['player_step_size_range']

    num_enemies_range = e_con['num_enemies_range']
    enemy_velocity_range = e_con['enemy_velocity_range']
    enemy_size_range = e_con['enemy_size_range']

    num_rewards_range = r_con['num_rewards_range']
    reward_velocity_range = r_con['reward_velocity_range']
    reward_size_range = r_con['reward_size_range']

    Env = Environment(board_size)

    Env.random_initialize(player_step_size_range = player_step_size_range,
                         player_size_range = player_size_range,

                         num_enemies_range = num_enemies_range,
                         e_vel_range = enemy_velocity_range,
                         enemy_size_range = enemy_size_range,

                         num_rewards_range = num_rewards_range,
                         r_vel_range = reward_velocity_range,
                         reward_size_range = reward_size_range
                         )
    return Env


def create_static_images(board_size = (700, 700)):

    size = board_size
    screen = pygame.display.set_mode(size)

    board = pygame.image.load('rl_game/game/environment/images/board.jpg').convert()
    board = pygame.transform.scale(board, size)

    game_over = pygame.image.load('rl_game/game/environment/images/you_lose.jpg').convert()
    game_over = pygame.transform.scale(game_over, (600,600))

    victory_screen = pygame.image.load('rl_game/game/environment/images/victory.jpg').convert()
    victory_screen = pygame.transform.scale(victory_screen, (600, 600))

    clock = pygame.time.Clock()

    return screen, board, game_over, victory_screen, clock


def update_objects_ingame(screen, objects, enemies=True):
    """
    Need to refactor the enemy and reward class to have their display object
    use the same attribute name... can then pass either to this function
    and don't need the enemies=True param
    """
    if enemies:
        for i in objects:
            screen.blit(i.enemy, i.get_position())
    if not enemies:
        for i in objects:
            screen.blit(i.reward, i.get_position())


def run_game(Env, board, screen, clock):
    black = (0,0,0)
    boardrect = board.get_rect()

    collision_detected = False
    victory = False

    state_trans = StateTranslator(Env, 2)
    while collision_detected == False and victory == False:
        # Clock locks framerate and prevents stuttering
        clock.tick(100)
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        key_input = pygame.key.get_pressed()
        move = Env.player.get_move(key_input)


        """
        Return the player class, list of enemy classes, uncollected rewards,
        collision and rewards collected are boolean
        """
        # before_step = datetime.datetime.now()
        player, enemies, rewards, collision, rewards_collected = Env.env_take_step(move)
        state_trans.set_objects(player, enemies, rewards)
        state_translated, reward, _ = state_trans.state_translation(collision, rewards_collected)
        print('state ', state_translated)
        #print('reward', reward)

        screen.blit(board, boardrect)
        screen.blit(player.player, player.get_position())
        update_objects_ingame(screen, enemies, enemies = True)
        update_objects_ingame(screen, rewards, enemies = False)
        pygame.display.update()

        if len(rewards) == 0:
            victory = True
            return victory, collision_detected

        if collision == True:
            collision_detected = True
            return victory, collision_detected


def run_game_with_agent(agent, env, board, screen, clock):
    black = (0,0,0)
    boardrect = board.get_rect()

    collision_detected = False
    victory = False
    num_steps_per_move = agent.frames_per_step

    # Create a state that is 4 frames to start as that is what we train with
    action = 1
    cur_state = np.array([])
    for _ in range(num_steps_per_move):
        new_player, new_enemies, new_goods, \
        collision_mini, goods_collected = env.env_take_step(action)

        agent.StateTrans.set_objects(new_player, new_enemies, new_goods)
        new_state_mini, reward_mini, done_mini = agent.StateTrans.state_translation(collision_mini, goods_collected)
        cur_state = np.append(cur_state, new_state_mini)

    step_count = 0
    while collision_detected == False and victory == False:
        # Clock locks framerate and prevents stuttering
        step_count += 1
        print(step_count)

        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        """
        Return the player class, list of enemy classes, uncollected rewards,
        collision and rewards collected are boolean
        """


        # Make an action with our state
        action = agent.act(cur_state)
        # Create an empty state to popualate with our last action
        cur_state = np.array([])
        collision = False

        # Perform action x amount of times as we train with... ie one state is 4 frames
        for _ in range(num_steps_per_move):
            clock.tick(400)
            new_player, new_enemies, new_goods, \
            collision_mini, goods_collected = env.env_take_step(action)

            agent.StateTrans.set_objects(new_player, new_enemies, new_goods)
            new_state_mini, reward_mini, done_mini = agent.StateTrans.state_translation(collision_mini, goods_collected)
            # print(reward_mini)
            cur_state = np.append(cur_state, new_state_mini)

            if collision_mini:
                collision = True

            rewards = new_goods

            screen.blit(board, boardrect)
            screen.blit(new_player.player, new_player.get_position())
            update_objects_ingame(screen, new_enemies, enemies = True)
            update_objects_ingame(screen, new_goods, enemies = False)
            pygame.display.update()



        if len(rewards) == 0:
            victory = True
            return victory, collision_detected

        if collision == True:
            collision_detected = True
            return victory, collision_detected


def restart_game():
    wait = True
    while wait:
        reset_same, reset_random = False, False
        #pygame.event.set_allowed([pygame.K_SPACE, pygame.K_q])
        event = pygame.event.wait()
        key_input = pygame.key.get_pressed()

        if key_input[pygame.K_q]:
            reset_random = True
            wait = False

        if key_input[pygame.K_SPACE]:
            reset_same = True
            wait = False

    return reset_same, reset_random


def play_victory_screen(screen, victory_screen, victory):
    black = (0,0,0)
    while victory == True:

        screen.fill(black)
        screen.blit(victory_screen, (50,50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_SPACE] or key_input[pygame.K_q]:
            victory = False
            return

def play_game_over_screen(screen, game_over, collision):
    black = (0,0,0)
    while collision == True:
        screen.fill(black)
        screen.blit(game_over, (50,50))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        key_input = pygame.key.get_pressed()
        if key_input[pygame.K_SPACE] or key_input[pygame.K_q]:
            collision = False
            return
