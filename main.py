import sys, pygame
from game import Environment
from objects.players import Player, Enemy


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


def update_enemies_ingame(enemies, enemy_positions):
    lst = list(zip(enemies, enemy_positions))
    for i in lst:
        screen.blit(i[0].enemy, i[1])

collision = False
while collision == False:
    # Clock locks framerate and prevents stuttering
    clock.tick(100)
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    key_input = pygame.key.get_pressed()
    move = PlayerOne.get_move(key_input)
    player_pos, enemy_positions = Env.env_take_step(move)

    screen.blit(board, boardrect)
    screen.blit(PlayerOne.player, player_pos)
    update_enemies_ingame(enemies, enemy_positions)

    collisions = Env.check_collisions()
    if True in collisions:
        collision = True

    pygame.display.update()

while True:
    screen.blit(game_over, (50,100))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
