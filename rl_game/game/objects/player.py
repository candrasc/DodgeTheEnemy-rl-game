import pygame
import copy
import os, inspect

from typing import Tuple

from rl_game.game.objects import current_directory


class Player:

    def __init__(self, player_number=1, player_size=30, step_size=0.3, position=(1,1)):

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

    def get_move(self, key_input)-> int:

        if key_input[pygame.K_LEFT]:
            return 0
        if key_input[pygame.K_UP]:
            return 1
        if key_input[pygame.K_RIGHT]:
            return 2
        if key_input[pygame.K_DOWN]:
            return 3

    def set_position(self, position: Tuple[int]):
        self.position = position

    def get_position(self) -> Tuple[int]:
        return self.position

    def copy(self):
        copyobj = Player()
        for name, attr in self.__dict__.items():
            if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
                copyobj.__dict__[name] = attr.copy()
            else:
                copyobj.__dict__[name] = copy.deepcopy(attr)
        return copyobj


