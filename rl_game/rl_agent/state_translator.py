import numpy as np
import datetime

class StateTranslator:
    """WOW. What a fucking mess. Need to refactor.

    Used to translate the environment's object positions, sizes, speeds etc into a fixed size
    vector that can be passed to the RL agent
    """

    def __init__(self, env, n_objects_in_state=2):
        self.env = env
        self.board = np.zeros(env.board)
        self.n_obj = n_objects_in_state
        self.goods_in_game = len(env.rewards)
        self.state_shape = 54  #num enemies remaining
        # Factors to divide state attributes by so they are less than 1
        self.size_scale = 100  # max object size
        self.position_scale = env.board[0]  # max board dimension
        self.velocity_scale = 5  # max velocity

    def set_objects(self, player, enemies, goods):
        """
        """
        self.player = player
        self.enemies = np.array(enemies)
        self.goods = np.array(goods)

    def __translate_velocities(self, velocity):
        """
        Given a velocity param that includes an x and y velocity,
        translate it into a 6d vec (One hote encoding for x a y up or down (4 total), then abs value)

        We can't just do 1 up 0, down as having 0 will occur when we have no object in that position
        to return a velocity, which will confuse the neural net
        """
        x_vel = velocity[0]
        y_vel = velocity[1]

        vel_vec = np.zeros(4)

        if x_vel >= 0:
            vel_vec[0] = 1

        if y_vel >= 0:
            vel_vec[1] = 1


        vel_vec[2] = abs(x_vel)
        vel_vec[3] = abs(y_vel)

        return vel_vec

    def _get_object_attributes(self):

        def __get_velocity_position_size(units):
            if len(units)>0:
                unit_positions = []
                unit_sizes = []
                unit_velocities = []
                for unit in units:
                    vel = self.__translate_velocities(unit.get_velocity())
                    unit_velocities.append(vel) 
                    unit_sizes.append(unit.size)
                    unit_positions.append(unit.get_position())
                return unit_velocities, unit_positions, unit_sizes
            else:
                return [0], [0], [0]


        player_pos = np.array(self.player.get_position())
        player_size = np.array(self.player.size)
        player_step_size = np.array(self.player.step_size)

        enemy_velocities, enemy_positions, enemy_sizes = __get_velocity_position_size(self.enemies)

        good_velocities, good_positions, good_sizes = __get_velocity_position_size(self.goods)

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

    def _get_n_closest_objects(self, player_pos, player_size, obj_pos, obj_sizes, n_obj):
        """
        For now, we will just get the closest objects based on their position
        and radius... even though they are squares, this is good enough
        (the sizes will be inputs into the NN so it will be figured out then)
        """

        distances = np.array([])
        for i in range(len(obj_sizes)):
            dist = self._calc_distance(player_pos, obj_pos[i])
            dist_true = abs(dist - player_size - obj_sizes[i])
            distances = np.append(distances, dist_true)

        idx = np.argpartition(distances, range(n_obj))
        n_smallest_indicies = idx[:n_obj]

        return n_smallest_indicies

    def _get_distance_to_object(self, object):
        """
        Return vector that includes x distance, y distance, then one-hot vector of size 4
        for if the enemy is above, below, left, or right
        """
        position1 = self.player.get_position()
        position2 = object.get_position()

        player_size = self.player.size
        object_size = object.size

        player_rad = player_size / 2
        object_rad = object_size / 2

        p_x = position1[0] + player_rad
        p_y = position1[1] + player_rad

        e_x = position2[0] + object_rad
        e_y = position2[1] + object_rad

        dx = max((abs(e_x - p_x) - (player_rad + object_rad)) / self.position_scale, 0)
        dy = max((abs(e_y - p_y) - (player_rad + object_rad)) / self.position_scale, 0)

        pos_vec = np.zeros(4)
        if e_y >= p_y:
            pos_vec[0] = 1
        else:
            pos_vec[1] = 1

        if e_x >= p_x:
            pos_vec[2] = 1
        else:
            pos_vec[3] = 1

        final_vec = np.append(np.array([dx, dy]), pos_vec)
        return final_vec.flatten()

    def _get_distance_to_walls(self):
        x_wall1 = 0
        y_wall1 = 0
        x_wall2 = self.env.board[0]
        y_wall2 = self.env.board[0]
        player_pos = self.player.get_position()
        player_size = self.player.size

        hit_wall = False
        # Note player position starts at the top left of the shape... not center
        d_x1 = player_pos[0] - x_wall1
        d_x2 = x_wall2 - (player_pos[0] + player_size)
        d_y1 = player_pos[1] - y_wall1
        d_y2 = y_wall2 - (player_pos[1] + player_size)

        distance_array = np.array([d_x1, d_x2, d_y1, d_y2])

        if len(distance_array[distance_array <= 0]):
            # print(distance_array)
            # print(np.argwhere(distance_array<=0).flatten())
            hit_wall = True

        return distance_array, hit_wall

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

        distances_to_walls, _ = self._get_distance_to_walls()

        if n_obj_enemies > 0:
            n_smallest_enemy_indicies = self._get_n_closest_objects(player_pos,
                                                                    player_size,
                                                                    enemy_positions,
                                                                    enemy_sizes,
                                                                    n_obj_enemies)
            
            close_enemies = self.enemies[n_smallest_enemy_indicies]

            enemy_distances = np.array([])
            for e in close_enemies:
                e_dist_vec = self._get_distance_to_object(e)
                enemy_distances = np.append(enemy_distances, e_dist_vec)

            enemy_distances = self.__fill_end_of_array(enemy_distances, self.n_obj * 6).flatten()

            ev = self.__fill_end_of_array(enemy_velocities[n_smallest_enemy_indicies].flatten(),
                                          self.n_obj * 6)

        else:
            # ep = np.zeros(self.n_obj * 2)
            # es = np.zeros(self.n_obj)
            enemy_distances = np.zeros(self.n_obj * 6)
            ev = np.zeros(self.n_obj * 6)

        if n_obj_goods > 0:
            n_smallest_good_indicies = self._get_n_closest_objects(player_pos,
                                                                   player_size,
                                                                   good_positions,
                                                                   good_sizes,
                                                                   n_obj_goods)
            close_goods = self.goods[n_smallest_good_indicies]
            goods_distances = np.array([])
            for g in close_goods:
                g_dist_vec = self._get_distance_to_object(g)
                goods_distances = np.append(goods_distances, g_dist_vec)

            goods_distances = self.__fill_end_of_array(goods_distances, self.n_obj * 6).flatten()

            gv = self.__fill_end_of_array(good_velocities[n_smallest_good_indicies].flatten(),
                                          self.n_obj * 6)

        else:

            goods_distances = np.zeros(self.n_obj * 6)
            gv = np.zeros(self.n_obj * 6)

        state = np.array([])

        state = np.append(state, n_obj_goods/self.goods_in_game)

        state = np.append(state,
                          [distances_to_walls / self.position_scale,
                           player_step_size / self.velocity_scale
                           ])

        state = np.append(state,
                          [enemy_distances,
                           ev / self.velocity_scale])

        state = np.append(state,
                          [goods_distances,
                           gv / self.velocity_scale])

        state = np.hstack(state)
        return state.flatten()

    def state_translation(self, collision, goods_collected):
        """Used to translate state into format similar to OpenAi gym
        which we will pass to our RL agent
        """

        Done = False
        Reward = -1
        state = self.get_state()
        distances_to_walls, hit_wall = self._get_distance_to_walls()

        if collision:
            Done = True
            Reward = -50

        elif goods_collected:
            Done = False
            Reward = +50

        # elif hit_wall:
        #     print('hitwall')
        #     Done = False
        #     Reward = -50

        elif len(self.goods) == 0:
            Done = True
            Reward = +10 ** 6

        return state, Reward, Done
