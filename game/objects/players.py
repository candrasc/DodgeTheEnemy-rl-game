import pygame
import copy
import os, inspect

current_directory = os.path.dirname(
                    os.path.abspath(inspect.stack()[0][1]))

class Player:
    def __init__(self, player_number=1, player_size = 30, step_size = 0.3, position = (1,1)):

        player_path = os.sep.join([current_directory, 'object_images/player_one.png '])
        try:
            self.player = pygame.image.load(player_path).convert()
            self.player = pygame.transform.scale(self.player,(player_size, player_size))
        except:
            pass

        self.player_number = player_number
        self.size = player_size
        self.step_size = step_size

        self.position = position


    def get_move(self, key_input):

        if key_input[pygame.K_LEFT]:
            return 0
        if key_input[pygame.K_UP]:
            return 1
        if key_input[pygame.K_RIGHT]:
            return 2
        if key_input[pygame.K_DOWN]:
            return 3


    def set_position(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def copy(self):
        copyobj = Player()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

class NonPlayerBase:
    """
    Base class for all objects that are not a player (rewards and enemies)
    """
    def __init__(self, size = 30, step_size = 0.3, starting_pos = (1,1), velocity=(1,1)):

        self.size = size
        self.step_size = step_size
        self.position = starting_pos
        self.velocity = velocity

    def move(self):
        return velocity

    def set_velocity(self, x=None, y=None):
        cur_x = self.velocity[0]
        cur_y = self.velocity[1]
        if x == None:
            self.velocity = (cur_x, y)
        elif y == None:
            self.velocity = (x, cur_y)

    def get_velocity(self):
        return self.velocity

    def set_position(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def copy(self):
        copyobj = Enemy()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj

class Enemy(NonPlayerBase):
    """
    Object to avoid in game
    """
    def __init__(self,  size = 30, step_size = 0.3, starting_pos = (1,1), velocity=(1,1)):
        super().__init__(size, step_size, starting_pos, velocity)
        enemy_path = os.sep.join([current_directory, "object_images/enemy.png"])
        try:
            self.enemy = pygame.image.load(enemy_path).convert()
            self.enemy = pygame.transform.scale(self.enemy,(self.size, self.size))
        except:
            pass

class Reward(NonPlayerBase):
    """
    Items the player is trying to collect for points
    """
    def __init__(self, reward_value = 10, size = 30, step_size = 0.3, starting_pos = (1,1), velocity=(1,1)):
        super().__init__(size, step_size, starting_pos, velocity)
        reward_path = os.sep.join([current_directory, "object_images/reward_one.png"])
        try:
            self.reward = pygame.image.load(reward_path).convert()
            self.reward = pygame.transform.scale(self.reward, (self.size, self.size))
        except:
            pass
        self.reward_value = reward_value
