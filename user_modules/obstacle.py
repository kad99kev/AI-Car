import arcade
import pymunk

class Obstacle:
    def __init__(self, position):
        self.radius = 3
        self.colour = arcade.color.RED
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, self.radius)

    def return_shape(self):
        return self.shape

    def get_obstacle(self):
        return arcade.create_ellipse_filled(self.body.position.x, self.body.position.y, self.radius, self.radius, self.colour)