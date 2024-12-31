class Coordinates:

    """A class to hold the coordinates of the agent in a grid"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def set_x(self, x):
        self.x = x
    
    def set_y(self, y):
        self.y = y
    
    def __repr__(self):
        return f"<{self.x}, {self.y}>"

    def __eq__(self, other_coords):
        other_coords_x = other_coords.get_x()
        other_coords_y = other_coords.get_y()
        return self.x == other_coords_x and self.y == other_coords_y