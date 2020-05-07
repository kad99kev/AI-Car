class Spot:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.parent = None
        self.wall = False
    
    def __lt__(self, other):
        if self.get_f() == other.get_f():
            return self.h < other.h
        return self.get_f() < other.get_f()

    def __repr__(self):
        return f"x: {self.x} | y: {self.y} | f: {self.get_f()} | g: {self.g} | h: {self.h}\n"

    def get_f(self):
        return self.h + self.g
    
    def is_not_wall(self):
        return not self.wall
    
    def set_wall(self):
        if not self.wall: 
            # This will prevent a wall from being declassified as not a wall
            # if the user by mistake clicks on the wall again
            self.wall = True

    def reset(self):
        self.g = 0
        self.h = 0
        self.parent = None

            