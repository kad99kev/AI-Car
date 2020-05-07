import arcade
import pymunk
import os

from user_modules import Spot
from user_modules import UserMap
from user_modules import Car
from user_modules import Path
from user_modules import Obstacle
from user_modules import TextButton

from user_modules import SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_TITLE, DIV, DT, G_W, G_H


class AICar(arcade.Window):

    def __init__(self, width, height, title):

        super().__init__(width, height, title)
        # Related to Map
        self.PATH = None
        self.MAP = None
        self.CAR = None
        self.obstacle_button = None
        self.reset_button = None
        self.debug_button = None
        self.obstacles = None
        self.text_state = "Click and Drag your mouse over the grid to place obstacles"
        self.extra_text = " "
        self.status = None
        arcade.set_background_color(arcade.color.WHITE)

        # Related to Physics
        self.space = None

    def setup(self):
        # Setup Space
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)


        self.status = {'start_selected': False, 'goal_selected': False, 'found_path': False, 'draw_obstacles': True, 'debug': False}
        self.extra_text = " "

        # Setting up Map
        self.MAP = UserMap(DIV)
        for i in range(DIV):
            spots = []
            for j in range(DIV):
                spots.append(Spot(i, j))
            self.MAP.add_spots(spots)
        self.MAP.calculate_inital_grid()

        # Setting up GUI
        self.obstacle_button = TextButton(110, SCREEN_HEIGHT - 20, 200, 30, "Finish Drawing")
        self.reset_button = TextButton(360, SCREEN_HEIGHT - 20, 80, 30, "Reset")
        self.debug_button = TextButton(450, SCREEN_HEIGHT - 20, 80, 30, "Debug")
        print("Setup Finished")

        # Setting up Space
        self.CAR = Car()
        self.space.add(self.CAR.body, self.CAR.shape)

        # Setting up Path
        self.PATH = Path()

        # Setting Obstacles
        self.obstacles_shape_list = arcade.ShapeElementList()


    def next_state(self):
        self.status['goal_selected'] = False
        self.status['found_path'] = False
        self.MAP.next_state()
        self.CAR.next_state()
        self.PATH = Path()
        

    def on_draw(self):

        arcade.start_render()
        
        if not self.status['found_path']:
            self.MAP.draw_grid()
            self.MAP.draw_pathfinder()
        else:
            self.PATH.draw_path(self.status['debug'])
            self.obstacles_shape_list.draw()
            self.CAR.draw_car(self.status['debug'])

        self.obstacle_button.draw()
        self.reset_button.draw()
        self.debug_button.draw()
        arcade.draw_text(self.text_state, 5, SCREEN_HEIGHT - 50, arcade.color.BLACK, 14, anchor_x="left", anchor_y="top")
        arcade.draw_text(self.extra_text, 5, SCREEN_HEIGHT - 75, arcade.color.BLACK, 14, anchor_x="left", anchor_y="top")

    def on_update(self, delta_time):
        if not self.status['found_path']:
            result = self.MAP.update_map(self.status['goal_selected'])
            if result is not None:
                self.status['found_path'] = result['status']
                if self.status['found_path']:
                    self.PATH.add_spots(result['path'])
                    obstacles = self.MAP.get_obstacles()
                    for o in obstacles:
                        obs = Obstacle(o)
                        self.space.add(obs.return_shape())
                        self.obstacles_shape_list.append(obs.get_obstacle())
                    points, boundaries = self.PATH.get_points_and_boundaries()
                    self.CAR.set_path(points, boundaries)
                else:
                    self.extra_text = "No Path Found! Select New Path"
                    self.status['goal_selected'] = False
                    self.MAP.reset_goal()
        else:
            moving = self.CAR.follow_path()
            self.CAR.update()
            if not moving:
                self.next_state()
            self.space.step(DT)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        row = x // G_W
        column = y // G_H
        if self.status['draw_obstacles']:
            self.MAP.set_wall(row, column)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.obstacle_button.clicked(x, y):
            self.status['draw_obstacles'] = not self.status['draw_obstacles']
            if not self.status['draw_obstacles']:
                self.text_state = "Select two end points, first for the start then for the end."
                self.obstacle_button.change_text("Draw Obstacles")
            else:
                self.obstacle_button.change_text("Finish Drawing")
                self.text_state = "Click and Drag your mouse over the grid to place obstacles"

        elif self.reset_button.clicked(x, y):
            self.setup()

        elif self.debug_button.clicked(x, y):
            self.status['debug'] = not self.status['debug']

        else:
            if not self.status['draw_obstacles']:
                row = x // G_W
                column = y // G_H
                if not self.status['start_selected']:
                    start = self.MAP.set_start(row, column)
                    if start is not None:
                        self.status['start_selected'] = True
                        self.CAR.set_start(start)
                    else:
                        self.extra_text = "You cannot start on a wall!"

                else:
                    if not self.status['goal_selected']:
                        goal = self.MAP.set_goal(row, column)
                        if goal is not None:
                            self.status['goal_selected'] = True
                            self.CAR.set_goal(goal)
                        else:
                            self.extra_text = "Goal cannot be set over an obstacle!"

def main():
    window = AICar(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
