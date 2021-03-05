from objects.position import PositionSetter
from objects.players import Player, Enemy
import numpy as np

class Environment:
    def __init__(self, board_dimensions = (720, 720)):
        self.board = board_dimensions
        self.enemies = []
        self.pos_setter = PositionSetter(board_dimensions)
        # Create class attributes to keep track of the starting postions
        # So that we can reset the game after an end_state
        self.initial_enemies = []
        self.initial_player = None
        self.player = None

    def add_player(self, player):
        """
        In the future, can just pass Player object in... this was just nice
        to see the attributes
        """
        self.player = player
        self.initial_player = self.player.copy()

    def get_player(self):
        return self.player

    def move_player(self, direction):
        position = self.pos_setter

        position.set_object(self.player.size,
                            self.player.get_position())

        step = self.player.step_size

        if direction==0:
            position.set_width(-step)
        if direction==1:
            position.set_height(-step)
        if direction==2:
            position.set_width(step)
        if direction==3:
            position.set_height(step)


        new_pos = position.get_position()
        self.player.set_position(new_pos)

        return self.player


    def add_enemy(self, enemy):
        self.enemies.append(enemy)
        self.initial_enemies.append(enemy.copy())

    def add_enemies(self, enemies):
        for i in enemies:
            self.add_enemy(i)

    def move_enemy(self, enemy):
        enemy_size = enemy.size
        enemy_position = enemy.get_position()

        x = enemy.get_velocity()[0]
        y = enemy.get_velocity()[1]

        position = self.pos_setter
        position.set_object(enemy_size,
                            enemy_position)

        position.set_width(x)
        position.set_height(y)

        cur_pos = position.get_position()

        # Cause ball to change directions in one dimension if at edge of board
        if cur_pos[0] == position.max_width or cur_pos[0] == 0:
            enemy.set_velocity(x = -x)
        elif cur_pos[1] == position.max_height or cur_pos[1] == 0:
            enemy.set_velocity(y = -y)

        enemy.set_position(cur_pos)
        return enemy

    def move_all_enemies(self):
        updated_enemies = [self.move_enemy(enemy) for enemy in self.enemies]
        self.enemies = updated_enemies
        [enemy.get_position() for enemy in updated_enemies]
        return updated_enemies

    def env_take_step(self, player_move):
        """
        Move enemies and the player in the environment for a single step_size

        Return player and enemy positions
        """

        new_player = self.move_player(player_move)
        new_enemies = self.move_all_enemies()
        collision = self.check_collisions()

        return new_player, new_enemies, collision

    def _contact_made(self, player_pos, enemy_pos, player_size, enemy_size):
        # print(player_size)
        player_rad = player_size/2 - 3
        enemy_rad = enemy_size/2
        w1 = player_pos[0] + player_rad
        h1 = player_pos[1] + player_rad
        w2 = enemy_pos[0] + enemy_rad
        h2 = enemy_pos[1] + enemy_rad

        if abs(w1 - w2) < (player_rad + enemy_rad) and abs(h1 - h2) < (player_rad + enemy_rad):
            return True

        else:
            return False

    def check_collisions(self):

        player_pos = self.player.get_position()
        player_size = self.player.size
        enemy_positions = [enemy.get_position() for enemy in self.enemies]
        enemy_sizes = [enemy.size for enemy in self.enemies]

        collisions = False
        for i in range(len(self.enemies)):
            if self._contact_made(player_pos, enemy_positions[i], player_size, enemy_sizes[i]) == True:
                collisions = True

        return collisions

    def env_reset(self):
        """
        Return the environment to its starting state
        """
        self.player = self.initial_player.copy()
        self.enemies = [enemy.copy() for enemy in self.initial_enemies]

    def env_random_reset(self,
                     player_step_size_range = (1, 5),
                     player_size_range = (10,40),
                     num_enemies_range = 10,
                     vel_range = (0, 5),
                     enemy_size_range = (10,100)):
        """
        Reset the game, but all positions and enemy velocities are randomized.
        Useful for RL training where you want to expose the agent to many states
        """
        def _rand_int(start, end):
            return np.random.randint(start, end)

        self.player = None
        self.enemies = []
        pos_range = (0, self.board[0])
        player = Player(player_number = 1,
                        player_size = _rand_int(player_size_range[0],
                                                player_size_range[1],
                                                ),

                        step_size = _rand_int(player_step_size_range[0],
                                              player_step_size_range[1],
                                              ),

                        position = (_rand_int(pos_range[0],
                                             pos_range[1]),
                                    _rand_int(pos_range[0],
                                              pos_range[1])))

        self.add_player(player)

        for i in range(_rand_int(1, num_enemies_range)):
            enemy = Enemy(size = _rand_int(enemy_size_range[0],
                                                       enemy_size_range[1]),

                          starting_pos = (_rand_int(vel_range[0],
                                               pos_range[1]),
                                          _rand_int(pos_range[0],
                                                pos_range[1])),

                          velocity = (_rand_int(vel_range[0],
                                               vel_range[1]),
                                      _rand_int(vel_range[0],
                                                vel_range[1])))
            self.add_enemy(enemy)
