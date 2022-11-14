from typing import Tuple, List

from rl_game.game.objects.position_utils import PositionSetter
from rl_game.game.objects.player import Player
from rl_game.game.objects.secondary_objects import Enemy, Reward
import numpy as np
import random


class Environment:
    ACTION_SPACE = [0, 1, 2, 3]

    def __init__(self, board_dimensions=(700, 700)):
        self.board = board_dimensions
        self.pos_setter = PositionSetter(board_dimensions)
        # Create class attributes to keep track of the starting postions
        # So that we can reset the game after an end_state
        self.enemies = []
        self.player = None
        self.rewards = []
        self.initial_enemies = []
        self.initial_player = None
        self.initial_rewards = []
        self.score = None

    def add_player(self, player: Player):
        """ Add a player to the environment and record its initial state

        Args:
            player: Instatiated Player class

        """
        self.player = player
        self.initial_player = self.player.copy()

    def get_player(self) -> Player:
        return self.player

    def move_player(self, direction: int) -> Player:
        """ Translates an int from 1 to 3 into a direction to move and updates player position

        Args:
            direction: integer representing left, right, up or down

        Returns: the player with the updated position based on their direction

        """

        position = self.pos_setter

        position.set_object(self.player.size,
                            self.player.get_position())

        step = self.player.step_size

        if direction == 0:
            position.set_x_coord(-step)
        if direction == 1:
            position.set_y_coord(-step)
        if direction == 2:
            position.set_x_coord(step)
        if direction == 3:
            position.set_y_coord(step)

        new_pos = position.get_position()
        self.player.set_position(new_pos)

        return self.player

    ################################
    # This block of code can be refactored as it is going to be almost exactly
    # The same as for rewards
    def add_enemy(self, enemy: Enemy) -> None:
        """ Add enemy to environment and record initial state

        Args:
            enemy: Instatiated Enemy class

        Returns:

        """
        self.enemies.append(enemy)
        self.initial_enemies.append(enemy.copy())

    def add_enemies(self, enemies: List[Enemy]) -> None:
        """ add many enemies

        Args:
            enemies: list of enemy class

        Returns:

        """
        for i in enemies:
            self.add_enemy(i)

    def move_enemy(self, enemy: Enemy) -> Enemy:
        """ Move an enemy based on their predefined velocity

        Args:
            enemy:

        Returns: Enemy with updated position

        """
        enemy_size = enemy.size
        enemy_position = enemy.get_position()

        x = enemy.get_velocity()[0]
        y = enemy.get_velocity()[1]

        position = self.pos_setter
        position.set_object(enemy_size,
                            enemy_position)

        position.set_x_coord(x)
        position.set_y_coord(y)

        cur_pos = position.get_position()

        # Cause ball to change directions in one dimension if at edge of board
        if cur_pos[0] == position.max_width or cur_pos[0] == 0:
            enemy.set_velocity(x=-x)
        elif cur_pos[1] == position.max_height or cur_pos[1] == 0:
            enemy.set_velocity(y=-y)

        enemy.set_position(cur_pos)
        return enemy

    def move_all_enemies(self) -> List[Enemy]:
        updated_enemies = [self.move_enemy(enemy) for enemy in self.enemies]
        self.enemies = updated_enemies
        return updated_enemies

    ################################
    # This is literally the same as enemy functions above...
    def add_reward(self, reward: Reward) -> None:
        self.rewards.append(reward)
        self.initial_rewards.append(reward.copy())

    def add_rewards(self, rewards):
        for i in rewards:
            self.add_reward(i)

    def move_reward(self, reward):
        reward_size = reward.size
        reward_position = reward.get_position()

        x = reward.get_velocity()[0]
        y = reward.get_velocity()[1]

        position = self.pos_setter
        position.set_object(reward_size,
                            reward_position)

        position.set_x_coord(x)
        position.set_y_coord(y)

        cur_pos = position.get_position()

        # Cause ball to change directions in one dimension if at edge of board
        if cur_pos[0] == position.max_width or cur_pos[0] == 0:
            reward.set_velocity(x=-x)
        elif cur_pos[1] == position.max_height or cur_pos[1] == 0:
            reward.set_velocity(y=-y)

        reward.set_position(cur_pos)
        return reward

    def move_all_rewards(self):
        updated_rewards = [self.move_reward(reward) for reward in self.rewards]
        self.rewards = updated_rewards
        [reward.get_position() for reward in updated_rewards]
        return updated_rewards

    ################################

    def env_take_step(self, player_move: int) -> Tuple[Player, list, list, bool, bool]:
        """ Cause entire environment to take a step. All players, enemies, and rewards make one movement.
        Also checks if any rewards or collisions have occured.

        Args:
            player_move: int represeting up, down, left or right

        Returns: All players, enemies, and rewards. If any rewards or collisions have occured.

        """

        new_player = self.move_player(player_move)
        if len(self.enemies) > 0:
            new_enemies = self.move_all_enemies()
        else:
            new_enemies = []
        new_rewards = self.move_all_rewards()

        # There is a very rare bug with check collisions trying to pop rewards and failing

        collision, rewards_collected = self.check_collisions()

        return new_player, new_enemies, new_rewards, collision, rewards_collected

    def return_env_object_states(self):
        """
        Returns: all objects active in the environment
        """
        return self.player, self.enemies, self.rewards

    def _contact_made(self, player_pos, object_pos, player_size, object_size) -> bool:
        """

        Args:
            player_pos:
            object_pos:
            player_size:
            object_size:

        Returns: If contact has been made between the player and a given object

        """
        # print(player_size)
        player_rad = player_size / 2
        enemy_rad = object_size / 2
        w1 = player_pos[0] + player_rad
        h1 = player_pos[1] + player_rad
        w2 = object_pos[0] + enemy_rad
        h2 = object_pos[1] + enemy_rad

        if abs(w1 - w2) < (player_rad + enemy_rad) and abs(h1 - h2) < (player_rad + enemy_rad):
            return True

        else:
            return False

    def check_collisions(self) -> Tuple[bool, bool]:
        """ Check for any collisions between the player and rewards and enemies

        Returns:

        """

        player_pos = self.player.get_position()
        player_size = self.player.size

        collisions = False
        if len(self.enemies) > 0:
            enemy_positions, enemy_sizes = zip(*((enemy.get_position(), enemy.size)
                                                 for enemy in self.enemies))

            for i in range(len(self.enemies)):
                if self._contact_made(player_pos, enemy_positions[i], player_size, enemy_sizes[i]):
                    collisions = True

        rewards_collected = False
        if len(self.rewards) > 0:
            reward_positions, reward_sizes = zip(*((reward.get_position(), reward.size)
                                                   for reward in self.rewards))

            for i in range(len(self.rewards)):
                if self._contact_made(player_pos, reward_positions[i], player_size, reward_sizes[i]):
                    try:
                        if len(self.rewards) > 0:
                            self.rewards.pop(i)
                        rewards_collected = True
                    except Exception as e:
                        print("Its me the rarest exceptione ever which I'm sure will get fixed..", e)

        return collisions, rewards_collected

    def env_reset(self):
        """
        Return the environment to its starting state
        """
        self.player = self.initial_player.copy()
        self.enemies = [enemy.copy() for enemy in self.initial_enemies]
        self.rewards = [reward.copy() for reward in self.initial_rewards]

        return self

    def random_initialize(self,
                          player_step_size_range=(1, 5),
                          player_size_range=(10, 40),

                          num_enemies_range=(3, 10),
                          e_vel_range=(0, 5),
                          enemy_size_range=(10, 100),

                          num_rewards_range=(10, 11),
                          r_vel_range=(0, 2),
                          reward_size_range=(10, 11)):
        """ Reset the game, but all positions and enemy velocities are randomized.
        Useful for RL training where you want to expose the agent to many states

        Args:
            player_step_size_range:
            player_size_range:
            num_enemies_range:
            e_vel_range:
            enemy_size_range:
            num_rewards_range:
            r_vel_range:
            reward_size_range:

        Returns:

        """

        def _rand_int(start, end):
            return np.random.randint(start, end)

        # First clear out all player and enemy attributes
        self.player = None
        self.initial_player = None
        self.enemies = []
        self.initial_enemies = []
        self.rewards = []
        self.initial_rewards = []

        pos_range = (0, self.board[0])
        player = Player(player_size=_rand_int(player_size_range[0],
                                              player_size_range[1],
                                              ),

                        step_size=_rand_int(player_step_size_range[0],
                                            player_step_size_range[1],
                                            ),

                        position=(_rand_int(pos_range[0],
                                            pos_range[1]),
                                  _rand_int(pos_range[0],
                                            pos_range[1])))

        self.add_player(player)

        player_pos = player.get_position()
        avoid_squares_x = list(range(player_pos[0] - 50, player_pos[0] + 50))

        avoid_squares_y = list(range(player_pos[1] - 50, player_pos[1] + 50))

        for i in range(_rand_int(num_enemies_range[0], num_enemies_range[1])):
            e_pos_x = random.choice(list(set(range(pos_range[0], pos_range[1])) - set(avoid_squares_x)))
            e_pos_y = random.choice(list(set(range(pos_range[0], pos_range[1])) - set(avoid_squares_y)))

            enemy = Enemy(size=_rand_int(enemy_size_range[0],
                                         enemy_size_range[1]),

                          starting_pos=(e_pos_x,
                                        e_pos_y),

                          velocity=(_rand_int(e_vel_range[0],
                                              e_vel_range[1]),
                                    _rand_int(e_vel_range[0],
                                              e_vel_range[1])))
            self.add_enemy(enemy)

        for _ in range(_rand_int(num_rewards_range[0], num_rewards_range[1])):
            reward = Reward(size=_rand_int(reward_size_range[0],
                                           reward_size_range[1]),

                            starting_pos=(_rand_int(r_vel_range[0],
                                                    pos_range[1]),
                                          _rand_int(pos_range[0],
                                                    pos_range[1])),

                            velocity=(_rand_int(r_vel_range[0],
                                                r_vel_range[1]),
                                      _rand_int(r_vel_range[0],
                                                r_vel_range[1])))
            self.add_reward(reward)

        return self
