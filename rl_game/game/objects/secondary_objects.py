import os
import copy
import pygame
from rl_game.game.objects import current_directory


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
        return self.velocity

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
        enemy_path = os.path.join(current_directory, "object_images/enemy.png")
 
        enemy = pygame.image.load(enemy_path).convert()
        self.enemy = pygame.transform.scale(enemy,(self.size, self.size))



class Reward(NonPlayerBase):
    """
    Items the player is trying to collect for points
    """
    def __init__(self, reward_value = 10, size = 30, step_size = 0.3, starting_pos = (1,1), velocity=(1,1)):
        super().__init__(size, step_size, starting_pos, velocity)
        reward_path = os.path.join(current_directory, "object_images/reward_one.png")

        reward = pygame.image.load(reward_path).convert()
        self.reward = pygame.transform.scale(reward, (self.size, self.size))
        self.reward_value = reward_value