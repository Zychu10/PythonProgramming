import random


class Sheep:
    def __init__(self, x=0.0, y=0.0, number=0, status='alive'):
        self.x = x
        self.y = y
        self.number = number
        self.status = status

    def get_position(self):
        return self.x, self.y

    def move(self, sheep_move_dist):
        direction = random.randint(0, 3)  # 0 means north, 1 means south, 2 means east, 3 means west
        if direction == 0:
            self.y += sheep_move_dist
        if direction == 1:
            self.y -= sheep_move_dist
        if direction == 2:
            self.x += sheep_move_dist
        if direction == 3:
            self.x -= sheep_move_dist
