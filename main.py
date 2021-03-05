import sys, pygame
from environment import Environment
from objects.players import Player, Enemy


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

    PlayerOne = Player(player_number = 1,
                       player_size = 30,
                       step_size = 3,
                       position = (1,1))

    Env.add_player(PlayerOne)

    EnemyOne = Enemy(size = 100,
                     starting_pos=(500, 400),
                     velocity = (1, 1))

    EnemyTwo = Enemy(size = 50,
                     starting_pos=(300, 300),
                     velocity = (2, 2))

    EnemyThree = Enemy(size = 30,
                     starting_pos=(100, 300),
                     velocity = (4, 3))

    enemies = [EnemyOne, EnemyTwo, EnemyThree]

    Env.add_enemies(enemies)


    def update_enemies_ingame(enemies):
        positions = [enemy.get_position() for enemy in enemies]
        for enemy in enemies:
            screen.blit(enemy.enemy, enemy.get_position())

    collision_detected = False
    while collision_detected == False:
        # Clock locks framerate and prevents stuttering
        clock.tick(100)
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        key_input = pygame.key.get_pressed()
        move = PlayerOne.get_move(key_input)
        player, enemies, collision = Env.env_take_step(move)

        screen.blit(board, boardrect)
        screen.blit(player.player, player.get_position())
        update_enemies_ingame(enemies)

        if collision == True:
            print('Press Space bar to play again')
            print('Press Q to randomly reset')
            event = pygame.event.wait()
            key_input = pygame.key.get_pressed()
            if key_input[pygame.K_SPACE]:
                Env.env_reset()
                collision_detected == False

            if key_input[pygame.K_q]:
                Env.env_random_reset()
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
