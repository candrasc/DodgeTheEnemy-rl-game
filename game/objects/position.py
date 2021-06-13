
class PositionSetter:
    """
    Used in game objects to set their position within legal limits
    """
    def __init__(self, board_dimensions):
        self.board = board_dimensions

    def set_object(self, player_size, current_pos = (1,1)):
        self.max_width = self.board[0] - player_size
        self.max_height = self.board[1] - player_size
        self.current_width = current_pos[0]
        self.current_height = current_pos[1]


    def get_width(self):
        return self.current_width

    def set_width(self, step):
        self.current_width += step
        self.current_width = max(0,
                                min(self.current_width, self.max_width))

    def get_height(self):
        return self.current_height

    def set_height(self, step):
        self.current_height += step
        self.current_height= max(0,
                                min(self.current_height, self.max_height))

    def get_position(self):
        return self.current_width, self.current_height
