import sys, pygame, json
from environment import Environment
from objects.players import Player, Enemy

# Retrieve our game configs
with open("game_config.json", "rb") as f:
    config = json.load(f)

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


def run_app():
    # Set up game board and end screen
    pygame.init()
    clock = pygame.time.Clock()

    size = width, height = 700, 700
    screen = pygame.display.set_mode(size)
    black = (0,0,0)

    board = pygame.image.load('images/board.jpg').convert()
    board = pygame.transform.scale(board, size)
    boardrect = board.get_rect()

    game_over = pygame.image.load('images/game_over.png').convert()
    game_over = pygame.transform.scale(game_over, (600,300))

    victory_screen = pygame.image.load('images/victory_screen.gif').convert()
    victory_screen = pygame.transform.scale(victory_screen, (600, 600))

    # Initialize our game environment randomly with restraints
    Env = Environment(size)

    Env.random_initialize(player_step_size_range = player_step_size_range,
                         player_size_range = player_size_range,

                         num_enemies_range = num_enemies_range,
                         e_vel_range = enemy_velocity_range,
                         enemy_size_range = enemy_size_range,

                         num_rewards_range = num_rewards_range,
                         r_vel_range = reward_velocity_range,
                         reward_size_range = reward_size_range
                         )


    def update_objects_ingame(objects, enemies = True):
        """
        Need to refactor the enemy and reward class to have their display object
        use the same attribute name... can then pass either to this function
        and don't need the enemies=True param
        """
        if enemies:
            positions = [i.get_position() for i in objects]
            for i in objects:
                screen.blit(i.enemy, i.get_position())
        if not enemies:
            positions = [i.get_position() for i in objects]
            for i in objects:
                screen.blit(i.reward, i.get_position())

    # Start game loop
    collision_detected = False
    victory = False
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
        player, enemies, rewards, collision, rewards_collected = Env.env_take_step(move)

        screen.blit(board, boardrect)
        screen.blit(player.player, player.get_position())
        update_objects_ingame(enemies, enemies = True)
        update_objects_ingame(rewards, enemies = False)



        if collision == True:
            print('Press Space bar to play again')
            print('Press Q to randomly reset')
            screen.blit(game_over, (50,100))
            pygame.display.update()
            event = pygame.event.wait()
            key_input = pygame.key.get_pressed()
            if key_input[pygame.K_SPACE]:
                Env.env_reset()
                collision_detected = False

            if key_input[pygame.K_q]:
                Env.random_initialize(player_step_size_range = player_step_size_range,
                                     player_size_range = player_size_range,

                                     num_enemies_range = num_enemies_range,
                                     e_vel_range = enemy_velocity_range,
                                     enemy_size_range = enemy_size_range,

                                     num_rewards_range = num_rewards_range,
                                     r_vel_range = reward_velocity_range,
                                     reward_size_range = reward_size_range
                                     )

                collision_detected = False


        if len(rewards) == 0:
            screen.blit(victory_screen, (50,50))
            pygame.display.update()

            event = pygame.event.wait()
            key_input = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            if key_input[pygame.K_SPACE]:
                Env.env_reset()
                victory = False

            if key_input[pygame.K_q]:
                Env.random_initialize(player_step_size_range = player_step_size_range,
                                     player_size_range = player_size_range,

                                     num_enemies_range = num_enemies_range,
                                     e_vel_range = enemy_velocity_range,
                                     enemy_size_range = enemy_size_range,

                                     num_rewards_range = num_rewards_range,
                                     r_vel_range = reward_velocity_range,
                                     reward_size_range = reward_size_range
                                     )

                victory = False

        pygame.display.update()



if __name__ == '__main__':
    run_app()
