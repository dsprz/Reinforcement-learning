from Coordinates import Coordinates
from Grid import Grid
from Action import Action

class Agent:

    def __init__(self, 
                 lr: float, 
                 starting_coords: Coordinates,
                 grid: Grid):
        
        self.grid = grid
        self.rewards = 0
        self.learning_rate = lr
        self.position = starting_coords

        #Just get the reward on spawn (most likely to be 0).
        self.rewards += self.grid.get_reward(self.position)

        #print(f"At the beginning, I am at {self.position} and I have : {self.rewards}")
        self.actions = {
            "right" : 1,
            "left": 1,
            "up" : 0,
            "down" : 0 
        }
    
    def move(self, 
             action: Action):
        """
            Make the agent move after using the Action action.
            The movement cost penalty is applied for every action.
        """
        movement_cost = self.grid.get_cost()

        x = self.position.get_x()
        y = self.position.get_y()
        grid_length = self.grid.get_grid_length()
        action_name = action.get_name()
        position_change = action.get_position_change()

        if action_name == "right" and x < grid_length - 1:
            x += position_change
        elif action_name == "left" and x > 0:
            x += position_change
        elif action_name == "up":
            y += position_change
        elif action_name == "down":
            y += position_change
        
        self.position = Coordinates(x, y)
        #print(f"I am now at {self.position}")
        self.rewards -= movement_cost
        self.rewards += self.grid.get_reward(self.position)
    
    def get_rewards(self):
        return self.rewards

    def get_position(self):
        return self.position

    def get_learning_rate(self):
        return self.learning_rate
    
    def reset_rewards(self):
        self.rewards = 0
