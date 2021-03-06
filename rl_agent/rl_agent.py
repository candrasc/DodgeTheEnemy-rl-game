import numpy as np


class Agent:
    """
    Given an environment state, choose an action, and learn from the reward
    """

    def __init__(self, env):
        self.env = environment
        self.board = np.zeros(env.board)
        # What values will represent the player and the enemies in our state
        # We will pass an np matrix of zeros, ones, and twos as inputs...
        # If that doesn't work we can describe the state space as the closest 4 enemies
        # their positions, and their velocities
        self.player_vals = 1
        self.enemy_vals = 2

    def _get_x_y_coord(self, position):
        """
        Given a tuple, return the x and y coordinates
        """
        return position[0], position[1]

    def _set_board_positions(self, players, enemies):
        """
        set the x y cooridnates of the objects on the board without setting
        their sizes
        """
        # Get player center coordinates
        board = self.board.copy()
        player_position = player.get_position()
        player_x, player_y = self._get_x_y_coord(player_position)

        # Get size of our player
        player_size = player.player_size
        board[player_y][player_x] = 1


        for enemy in enemies:
            enemy_position = enemy.get_position()
            enemy_x, enemy_y = self._get_x_y_coord(enemy_position)
            board[enemy_x][enemy_y] = 2

        return board

    def _set_full_board(self, players, enemies):
        pass

    def agent_move(self, player_position, enemy_positions):
        pass
