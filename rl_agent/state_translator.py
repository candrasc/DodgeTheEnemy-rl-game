"""
Get closest non zero in array https://stackoverflow.com/questions/30368632/calculate-distance-on-a-grid-between-2-points

Will do similar to above for state value
1) Given the position of the player and positions of all enemies, find the distance from player to all enemies
given player and enemy radius (This isn't perfect for diagnols, but it is good enough...)

2) State vector will be a fixed size to accomdate x enemies. Features will include
    - Distance from each edge of the board (4)
    - Player position, player step size: (2 + 1)
    - For each enemy in x enemies: position, velocity: ,distance of its closest point to the player 4*(2 + 2 + 1)
"""
import numpy as np

class StateTranslator:
    """
    Used to translate the environment's object positions, sizes, speeds etc into a fixed size
    vector that can be passed to the RL agent
    """

    def __init__(self, env, n_objects_in_state = 4):
        self.env = env
        self.board = np.zeros(env.board)
        self.n_obj = n_objects_in_state
        self.state_shape = (2*( 2*self.n_obj + self.n_obj + 2*self.n_obj) + # enemy and goods
                            (2 + 1 + 1)) # player attributes
        # Factors to divide state attributes by so they are less than 1
        self.size_scale = 100 # max object size
        self.position_scale = env.board[0] # max board dimension
        self.velocity_scale = 10 # max velocity

    def _get_x_y_coord(self, position):
        """
        Given a tuple, return the x and y coordinates
        """
        return position[0], position[1]

    def set_objects(self, player, enemies, goods):
        """
        """
        self.player = player
        self.enemies = np.array(enemies)
        self.goods = np.array(goods)


    def _get_object_attributes(self):

        player_pos = np.array(self.player.get_position())
        player_size = np.array(self.player.size)
        player_step_size = np.array(self.player.step_size)

        if len(self.enemies) > 0:
            enemy_positions, enemy_sizes, enemy_velocities = zip(*((enemy.get_position(),
                                                                   enemy.size,
                                                                   enemy.get_velocity())
                                                                   for enemy in self.enemies))
        else:
            enemy_positions, enemy_sizes, enemy_velocities = [0],[0],[0]

        if len(self.goods)>0:
            good_positions, good_sizes, good_velocities = zip(*((good.get_position(),
                                                                 good.size,
                                                                 good.get_velocity())
                                                                 for good in self.goods))
        else:
            good_positions, good_sizes, good_velocities = [0],[0],[0]

        enemy_positions = np.array(enemy_positions)
        enemy_sizes = np.array(enemy_sizes)
        enemy_velocities = np.array(enemy_velocities)

        good_positions = np.array(good_positions)
        good_sizes = np.array(good_sizes)
        good_velocities = np.array(good_velocities)

        return (player_pos, player_size, player_step_size,
                enemy_positions, enemy_sizes, enemy_velocities,
                good_positions, good_sizes, good_velocities)

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

    def _get_n_closest_objects(self, player_pos, player_size, obj_poss, obj_sizes, n_obj):
        """
        For now, we will just get the closest objects based on their position
        and radius... even though they are squares, this is good enough
        (the sizes will be inputs into the NN so it will be figured out then)
        """

        if len(obj_sizes)<=n_obj:
            n_smallest_indicies = [i for i in range(len(obj_sizes))]

        else:
            distances = np.array([])
            for i in range(len(obj_sizes)):
                dist = self._calc_distance(player_pos, obj_poss[i])
                dist_true = abs(dist - player_size - obj_sizes[i])
                distances = np.append(distances, dist_true)

            idx = np.argpartition(distances, n_obj)
            n_smallest_indicies = idx[:n_obj]

        return n_smallest_indicies

    def __fill_end_of_array(self, array, desired_length):
        """When their are less objects than our maxmimum amount (n_obj),
        we fill the end of the array with zeros so that the state size is
        always the same
        """

        if len(array) < desired_length:
            num_to_add = desired_length - len(array)
            array = np.append(array, np.zeros(num_to_add))

        return array

    def get_state(self):
        """
        Create the final np vector that will be passed to the RL agent
        """
        n_obj_goods = min(self.n_obj, len(self.goods))
        n_obj_enemies = min(self.n_obj, len(self.enemies))

        player_pos, player_size, player_step_size, \
        enemy_positions, enemy_sizes, enemy_velocities, \
        good_positions, good_sizes, good_velocities = self._get_object_attributes()

        if n_obj_enemies>0:
            n_smallest_enemy_indicies = self._get_n_closest_objects(player_pos,
                                                                   player_size,
                                                                   enemy_positions,
                                                                   enemy_sizes,
                                                                   n_obj_enemies)

            ep = self.__fill_end_of_array(enemy_positions[n_smallest_enemy_indicies].flatten(),
                                   self.n_obj * 2)

            es = self.__fill_end_of_array(enemy_sizes[n_smallest_enemy_indicies].flatten(),
                                   self.n_obj)

            ev = self.__fill_end_of_array(enemy_velocities[n_smallest_enemy_indicies].flatten(),
                                   self.n_obj * 2)

        else:
            ep = np.zeros(self.n_obj * 2)
            es = np.zeros(self.n_obj)
            ev = np.zeros(self.n_obj * 2)

        if n_obj_goods>0:
            n_smallest_good_indicies = self._get_n_closest_objects(player_pos,
                                                                    player_size,
                                                                    good_positions,
                                                                    good_sizes,
                                                                    n_obj_goods)

            gp = self.__fill_end_of_array(good_positions[n_smallest_good_indicies].flatten(),
                                   self.n_obj * 2)

            gs = self.__fill_end_of_array(good_sizes[n_smallest_good_indicies].flatten(),
                                   self.n_obj)

            gv = self.__fill_end_of_array(good_velocities[n_smallest_good_indicies].flatten(),
                                   self.n_obj * 2)

        else:
            gp = np.zeros(self.n_obj * 2)
            gs = np.zeros(self.n_obj)
            gv = np.zeros(self.n_obj * 2)


        state = np.array([])

        state = np.append(state,
                         [player_pos/self.position_scale,
                          player_size/self.size_scale,
                          player_step_size/self.velocity_scale])

        state = np.append(state,
                         [ep/self.position_scale,
                          es/self.size_scale,
                          ev/self.velocity_scale])

        state = np.append(state,
                         [gp/self.position_scale,
                          gs/self.size_scale,
                          gv/self.velocity_scale])

        state = np.hstack(state)
        return state.flatten()


    def state_translation(self, collision, goods_collected):
        """Used to translate state into format similar to OpenAi gym
        allow agent to train
        """

        Done = False
        Reward = -1
        state = self.get_state()

        if collision:
            Done = True
            Reward = -100

        if goods_collected:
            Done = True
            Reward = +100

        return state, Reward, Done
