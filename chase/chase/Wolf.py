import logging
import math


class Wolf:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x, self.y

    def move(self, wolf_move_dist, flock):
        number = 1
        max_range = math.inf
        for sheep in flock:
            if sheep.status == 'alive':
                distance = round(math.sqrt((self.x - sheep.x) ** 2 + (self.y - sheep.y) ** 2), 3)
                if max_range > distance:
                    max_range = distance
                    number = sheep.number
        if max_range <= wolf_move_dist:
            self.x = flock[number - 1].x
            self.y = flock[number - 1].y
            flock[number - 1].status = "eaten"
            print(f"Sheep number {number} is eaten")
            logging.info(f"Sheep number {number} is eaten")
        if max_range > wolf_move_dist:
            x_move = wolf_move_dist * ((flock[number - 1].x - self.x) / max_range)
            y_move = wolf_move_dist * ((flock[number - 1].y - self.y) / max_range)
            self.x = round(self.x + x_move, 3)
            self.y = round(self.y + y_move, 3)
            print(f"Wolf is chasing sheep number {number}")
            logging.info(f"Wolf is chasing sheep number {number}")
