import arcade
import pymunk

from .line import Line

class Path:

    def __init__(self):
        self.turn_dist = 10
        self.thickness = 16
        self.points = None
        self.turn_boundaries = []
        self.road_back = arcade.ShapeElementList()
        self.road_front = arcade.ShapeElementList()
        self.draw_points = arcade.ShapeElementList()
        self.draw_boundaries = arcade.ShapeElementList()

    def add_spots(self, points):
        self.points = points
        self.points.reverse()
        
        previous_point = self.points[0]
        for point in self.points:
            dir_to_current_point = (point - previous_point).normalized()
            turn_boundary_point = point - dir_to_current_point * self.turn_dist * 2.5 if point == self.points[-1] else point - dir_to_current_point * self.turn_dist
            self.turn_boundaries.append(Line(turn_boundary_point, previous_point - dir_to_current_point * self.turn_dist))
            previous_point = turn_boundary_point

        self.__setup_draw()
        

    def get_points_and_boundaries(self):
        return self.points, self.turn_boundaries

    def draw_path(self, debug):
        self.road_back.draw()
        self.road_front.draw()
        if debug:
            self.draw_points.draw()
            self.draw_boundaries.draw()

    def __setup_draw(self):
        self.road_back.append(arcade.create_line_strip(self.points, arcade.color.DARK_GRAY, self.thickness))
        self.road_front.append(arcade.create_line_strip(self.points, arcade.color.BLACK, 1))
        
        for e in self.points:
            self.draw_points.append(arcade.create_ellipse(e.x, e.y, 1, 1, arcade.color.YELLOW))
        
        for b in self.turn_boundaries:
            self.draw_boundaries.append(b.draw_line(20))
        