import arcade
import pymunk
import math

from .constants import G_H, G_W

class Car:

    def __init__(self):
        self.mass = 10
        self.max_speed = 100
        self.turn_rate = 50
        self.sight = 10

        self.width = 5
        self.height = 10
        moment = pymunk.moment_for_box(self.mass, (self.width, self.height))
        self.body = pymunk.Body(self.mass, moment, body_type=pymunk.Body.DYNAMIC)
        self.body.position = (0, 0)

        self.shape = pymunk.Poly.create_box(self.body, (self.width, self.height))
        self.colour = arcade.color.LIGHT_BLUE

        pos = self.body.position
        self.car = arcade.ShapeElementList()
        self.car.append(arcade.create_rectangle_filled(pos.x, pos.y, self.width, self.height, self.colour, 0))
        self.car.append(arcade.create_rectangle_filled(pos.x, pos.y + self.height // 2, 4, 2, arcade.color.DARK_IMPERIAL_BLUE, 0))
        self.debug = arcade.ShapeElementList()

        # Path following
        self.goal = None
        self.following_path = True
        self.path_index = 0
        self.path = None
        self.boundaries = None

################### Draw ###################

    def draw_car(self, debug):
        self.car.center_x, self.car.center_y = self.body.position
        self.car.angle = self.body.angle
        if debug:
            self.__draw_debug()
        self.car.draw()



################### Setters ###################

    def set_start(self, start):
        self.body.position = pymunk.Vec2d(start.x * G_W + G_W / 2, start.y * G_H + G_H / 2)

    def set_goal(self, goal):
        self.goal = pymunk.Vec2d(goal.x * G_W + G_W / 2, goal.y * G_H + G_H / 2)

    def set_path(self, path, boundaries):
        # Ignore start point
        self.boundaries = boundaries[1:]
        self.path = path[1:]
        pos = self.body.position
        angle = (pos - self.path[0]).normalized()
        self.body.angle = angle.get_angle()


################### Update and Follow ###################

    def update(self):
        # self.body.apply_impulse_at_local_point(pymunk.Vec2d(0, 0))
        if self.body.velocity.length > 0:
            self.body.angle = self.body.velocity.get_angle_degrees() - 90

    def follow_path(self):
        if self.following_path:
            if self.boundaries[self.path_index].has_crossed_line(self.body.position):
                if self.path[self.path_index] == self.goal:
                    target = self.path[self.path_index]
                    self.__slow_down(target)
                else:
                    self.path_index += 1
            if self.following_path:
                target = self.path[self.path_index]
                self.__seek(target)
                self.debug.append(arcade.create_ellipse_filled(target.x, target.y, 4, 4, arcade.color.BANGLADESH_GREEN))
        return self.following_path

    def next_state(self):
        self.goal = None
        self.following_path = True
        self.path_index = 0
        self.path = None
        self.boundaries = None


################### Debug ###################

    def __draw_debug(self):
        self.debug.draw()
        self.debug = arcade.ShapeElementList()


################### Private Functions ###################

    def __limit(self, vector, limit):
        if vector.get_length() > limit:
            vector.length = limit
        return vector
    
    def __slow_down(self, target):
        target_offset = target - self.body.position
        distance = target_offset.length
        
        # To bring to gradual halt
        ramped_speed = self.max_speed * (distance / 1e5)
        clipped_speed = min(ramped_speed, self.max_speed)
        desired = (clipped_speed / distance) * target_offset

        steer = (desired - self.body.velocity).rotated(-self.body.angle)
        steer = self.__limit(steer, self.turn_rate)
        self.body.apply_impulse_at_local_point(steer)
        self.body.velocity = self.__limit(self.body.velocity, self.max_speed)

        if distance < 5:
            self.following_path = False
            self.body.velocity -= self.body.velocity

    def __seek(self, target):
        # Apply steering forces based on arrival
        target_offset = target - self.body.position
        distance = target_offset.length
        ramped_speed = self.max_speed * (distance / 10)
        clipped_speed = min(ramped_speed, self.max_speed)
        desired = (clipped_speed / distance) * target_offset
        
        steer = (desired - self.body.velocity).rotated(-self.body.angle)
        steer = self.__limit(steer, self.turn_rate)
        self.body.apply_impulse_at_local_point(steer)
        self.body.velocity = self.__limit(self.body.velocity, self.max_speed)
        
 
    def __copy_vect(self, vector):
        return pymunk.Vec2d(vector.x, vector.y)




