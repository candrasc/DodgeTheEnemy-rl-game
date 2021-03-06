import sys, pygame, json
from environment import Environment
from objects.players import Player, Enemy

with open("game_config.json", "rb") as f:
    config = json.load(f)

p_con = config['player_configs']
e_con = config['enemy_configs']

player_size_range = p_con['player_size_range']
player_step_size_range = p_con['player_step_size_range']

num_enemies_range = e_con['num_enemies_range']
enemy_velocity_range = e_con['enemy_velocity_range']
enemy_size_range = e_con['enemy_size_range']



def run_app():
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


    Env = Environment(size)

    Env.random_initialize(player_step_size_range = player_step_size_range,
                         player_size_range = player_size_range,
                         num_enemies_range = num_enemies_range,
                         vel_range = enemy_velocity_range,
                         enemy_size_range = enemy_size_range)


    def update_enemies_ingame(enemies):
        positions = [enemy.get_position() for enemy in enemies]
        for enemy in enemies:
            screen.blit(enemy.enemy, enemy.get_position())

    # Start game loop
    collision_detected = False
    while collision_detected == False:
        # Clock locks framerate and prevents stuttering
        clock.tick(100)
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        key_input = pygame.key.get_pressed()
        move = Env.player.get_move(key_input)
        player, enemies, collision = Env.env_take_step(move)

        screen.blit(board, boardrect)
        screen.blit(player.player, player.get_position())
        update_enemies_ingame(enemies)

        if collision == True:
            print('Press Space bar to play again')
            print('Press Q to randomly reset')
            screen.blit(game_over, (50,100))
            pygame.display.update()
            event = pygame.event.wait()
            key_input = pygame.key.get_pressed()
            if key_input[pygame.K_SPACE]:
                Env.env_reset()
                collision_detected == False

            if key_input[pygame.K_q]:
                Env.random_initialize(player_step_size_range = player_step_size_range,
                                     player_size_range = player_size_range,
                                     num_enemies_range = num_enemies_range,
                                     vel_range = enemy_velocity_range,
                                     enemy_size_range = enemy_size_range)

                collision_detected == False

            else:
                collision_detected == True

        pygame.display.update()

    end_screen = True
    while end_screen == True:
        screen.blit(game_over, (50,100))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    run_app()
