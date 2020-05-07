import arcade
import pymunk
import math
from heapq import heappop, heappush

from .constants import G_W, G_H, DIV

class UserMap:

    def __init__(self, div):
        # Lists for calculation and path finding
        self.spots = []
        self.open_set = []
        self.closed_set = []
        self.final_path = []
        self.obstacles = []

        # Lists for drawing
        self.path_shape_list = arcade.ShapeElementList()
        self.spots_shape_list = arcade.ShapeElementList()
        self.spots_list = [] # This list is required to avoid n ^ 2 list traversal
        
        # Start and Goal
        self.START = None
        self.GOAL = None

################### Map Update ###################

    # Main Update Function
    def update_map(self, goal_selected):
        current = None
        if goal_selected:
            if len(self.open_set) > 0:
                current = heappop(self.open_set)
                if current == self.GOAL:
                    self.final_path.insert(0, pymunk.Vec2d(current.x * G_W + G_W / 2, current.y * G_H + G_H / 2))
                    return {'status': True, 'path': self.final_path}
                
                self.closed_set.append(current)
                neighbours = self.__get_neighbours(current)
                for neigh in neighbours:
                    if neigh.is_not_wall() and neigh not in self.closed_set:
                        new_cost = current.g + self.__heuristic(neigh, current)
                        if new_cost < neigh.g or neigh not in self.open_set:
                            neigh.g = new_cost
                            neigh.h = self.__heuristic(neigh, self.GOAL)
                            neigh.parent = current

                            if neigh not in self.open_set:
                                heappush(self.open_set, neigh)
                        
    
        if goal_selected and not len(self.open_set) > 0:
            return {'status': False, 'path': None}


        self.calculate_and_draw_path(current)


################### Draw Functions ###################

    # Draw Functions
    def calculate_and_draw_path(self, current):
        self.path_shape_list = arcade.ShapeElementList()
        path = []
        points_list = []
        if current:
            temp = current
            point = pymunk.Vec2d(temp.x * G_W + G_W / 2, temp.y * G_H + G_H / 2)
            points_list.append((point.x, point.y))
            path.append(point)
            while temp.parent:
                temp = temp.parent
                point = pymunk.Vec2d(temp.x * G_W + G_W / 2, temp.y * G_H + G_H / 2)
                points_list.append((point.x, point.y))
                path.append(point)
        
            if len(points_list) > 2:
                line_strip = arcade.create_line_strip(points_list, arcade.color.BAKER_MILLER_PINK, 5)
                self.path_shape_list.append(line_strip)
            self.final_path = path.copy()
    
    def draw_pathfinder(self):
        self.path_shape_list.draw()
    
    def draw_grid(self):
        self.spots_shape_list.draw()


################### Grid Calculations ###################
    
    # Inital Grid Calculations
    def calculate_inital_grid(self):
        for col in self.spots:
            for spot in col:
                shape = arcade.create_rectangle_outline(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.BLACK)
                self.spots_list.append(shape)
        for shape in self.spots_list:
            self.spots_shape_list.append(shape)
        
    # Add data to UserMap
    def add_spots(self, spots):
        self.spots.append(spots)
                

################### Setters ###################

    # Set data to UserMap
    def set_wall(self, row, col):
        spot = self.spots[row][col]
        self.spots_list[row * DIV + col] = arcade.create_ellipse_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, 3, 3, arcade.color.RED)
        self.spots[row][col].set_wall()
        self.obstacles.append(pymunk.Vec2d(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2))
        self.__recalculate_grid()


    def set_start(self, row, col):
        spot = self.spots[row][col]
        if spot.is_not_wall():
            self.START = spot
            self.open_set.append(self.START)
            self.spots_list[row * DIV + col] = arcade.create_rectangle_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.BITTER_LEMON)
            self.__recalculate_grid()
            return self.START
        else:
            return None

    def set_goal(self, row, col):
        spot = self.spots[row][col]
        if spot.is_not_wall():
            self.GOAL = spot
            self.spots_list[row * DIV + col] = arcade.create_rectangle_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.AO)
            self.__recalculate_grid()
            return self.GOAL
        return None

    # Resets the goal and sets
    def reset_goal(self):        
        self.open_set = []
        self.closed_set = []
        self.open_set.append(self.START)
        spot = self.GOAL
        if spot:
            self.spots_list[spot.x * DIV + spot.y] = arcade.create_rectangle_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.RED)
            self.GOAL = None
        self.__recalculate_grid()
        
    
    def next_state(self):
        # Set goal as new start colour
        spot = self.GOAL
        self.spots_list[spot.x * DIV + spot.y] = arcade.create_rectangle_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.BITTER_LEMON)
        # Reset previous start colour
        spot = self.START
        self.spots_list[spot.x * DIV + spot.y] = arcade.create_rectangle_filled(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.WHITE)
        # Update changes
        self.__recalculate_grid()
        # Add new outline
        self.spots_list[spot.x * DIV + spot.y] = arcade.create_rectangle_outline(spot.x * G_W + G_W / 2, spot.y * G_H + G_H / 2, G_W, G_H, arcade.color.BLACK)
        # Set goal as new start
        self.START = self.GOAL
        self.START.reset()
        self.GOAL = None
        self.reset_goal()


    # Get data from UserMap
    def get_obstacles(self):
        return self.obstacles

################### Private Functions ###################

    # Private Functions
    def __recalculate_grid(self):
        self.spots_shape_list = arcade.ShapeElementList()
        for shape in self.spots_list:
            self.spots_shape_list.append(shape)

    def __heuristic(self, a, b):
        distance = math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
        return distance

    def __get_neighbours(self, spot):
        neighbours = []
        if spot.x < DIV - 1:
            neighbours.append(self.spots[spot.x + 1][spot.y])
        if spot.x > 0:
            neighbours.append(self.spots[spot.x - 1][spot.y])
        if spot.y < DIV - 1:
            neighbours.append(self.spots[spot.x][spot.y + 1])
        if spot.y > 0:
            neighbours.append(self.spots[spot.x][spot.y - 1])
        if spot.x > 0 and spot.y > 0:
            neighbours.append(self.spots[spot.x - 1][spot.y - 1])
        if spot.x < DIV - 1 and spot.y > 0:
            neighbours.append(self.spots[spot.x + 1][spot.y - 1])
        if spot.x > 0 and spot.y < DIV - 1:
            neighbours.append(self.spots[spot.x - 1][spot.y + 1])
        if spot.x < DIV - 1 and spot.y < DIV - 1:
            neighbours.append(self.spots[spot.x + 1][spot.y + 1])
        return neighbours
