import arcade
import pymunk

from .constants import VERTICAL_LINE_GRADIENT

class Line(object):

    def __init__(self, point_on_line, point_perpendicular_to_line):
        dx = point_on_line.x - point_perpendicular_to_line.x
        dy = point_on_line.y - point_perpendicular_to_line.y

        self.slope_perpendicular = VERTICAL_LINE_GRADIENT if dx == 0 else dy / dx
        self.slope = VERTICAL_LINE_GRADIENT if self.slope_perpendicular == 0 else -1 / self.slope_perpendicular

        self.y_intercept = point_on_line.y - self.slope * point_on_line.x
        self.point_on_line1 = point_on_line
        self.point_on_line2 = point_on_line + pymunk.Vec2d(1, self.slope)

        self.approach_side = self.__get_side(point_perpendicular_to_line)

    def has_crossed_line(self, p):
        return self.__get_side(p) != self.approach_side
    
    def __get_side(self, p):
        return (p.x - self.point_on_line1.x) * (self.point_on_line2.y - self.point_on_line1.y) > (p.y - self.point_on_line1.y) * (self.point_on_line2.x - self.point_on_line1.x)

    def draw_line(self, length):
        line_dir = pymunk.Vec2d(1, self.slope).normalized()
        line_centre = self.point_on_line1
        return arcade.create_line_strip((line_centre - line_dir * length / 2, line_centre + line_dir * length / 2), arcade.color.BAKER_MILLER_PINK)
