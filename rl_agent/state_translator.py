"""
Get closest non zero in array https://stackoverflow.com/questions/30368632/calculate-distance-on-a-grid-between-2-points

Will do similar to above for state value
1) Given the position of the player and positions of all enemies, find the distance from player to all enemies
given player and enemy radius (This isn't perfect for diagnols, but it is good enough...)
    - For each object, calculate 8 points for each (4 corners and midpoints for each side). Find distance for each
    point on A to each point on B and use the shortest as the distance value (8*8 checks (64) per object pair)

2) State vector will be a fixed size to accomdate x enemies. Features will include
    - Distance from each edge of the board (4)
    - Player position, player step size: (2 + 1)
    - For each enemy in x enemies: position, velocity: ,distance of its closest point to the player 4*(2 + 2 + 1)
"""

class StateTranslator:
    """
    Used to translate the environment's object positions, sizes, speeds etc into a fixed size
    vector that can be passed to the RL agent
    """

    def __init__(self, env):
        self.env = environment
        self.board = np.zeros(env.board)

    def _get_x_y_coord(self, position):
        """
        Given a tuple, return the x and y coordinates
        """
        return position[0], position[1]

    def set_objects(self, player, enemies, goods):
        """
        """
        self.player = player
        self.enemies = enemies
        self.goods = goods

    def _get_all_positions(self):
        """
        get the center of each object which will help with our distance calculations
        """
        player_pos = player.get_position()

        enemy_positions = []
        for enemy in self.enemies:
            enemy_positions.append(enemy.get_position())

        good_positions = []
        for good in self.goods:
            good_positions.append(good.get_position())

        return player_pos, enemy_positions, good_positions

    def _calc_distance(self, position1, position2):
        """
        Given the x, y coordinates of two points, find the distance
        """

        p_x = position1[0]
        p_y = position1[1]

        e_x = position2[0]
        e_y = position2[1]

        dx = abs(e_x - p_x)
        dy = abs(e_y - p_y)

        mini = min(dx, dy)
        maxi = max(dx, dy)

        diagonalSteps = mini
        straightSteps = maxi - mini

        distance = np.sqrt(2) * diagonalSteps + straightSteps

        return distance
