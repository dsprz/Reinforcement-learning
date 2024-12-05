import numpy as np
from abc import ABC, abstractmethod
import random

# we have 2 actions : move left and move right
nb_action = 2
nb_state = 6

# the tab with the representation of the 6 states (-1 for the bad end, 1 for the good end, and 0 for other states)
reward = [-1,0,0,0,0,1]

# cost of one move
cost = 0.01

# learning rate - should not be too high, e.g. between .5 and .9
alpha = 0.9

# discount factor that shows how much you care about future (remember 0 for myopic)
gamma = 0.5

class QTable:

    def __init__(self, nb_states, nb_actions):
        self.nb_states = nb_states
        self.nb_actions = nb_actions
        self.Q_table = np.zeros((nb_states, nb_actions))
    
    def get_table(self):
        return self.Q_table

    def update_table(self):
        pass

    def __repr__(self):
        res = ""
        for i in range(self.nb_states):
            pass

class Grid(ABC):
    pass

    @abstractmethod
    def get_cost(self):
        pass

    @abstractmethod
    def get_grid_length(self):
        pass


class Grid_1D(Grid):
    
    def __init__(self, 
                 reward_list: list, 
                 discount_factor: float,
                 cost: float,
                 nb_actions: int,
                 nb_states: int,
                 ):
        self.input_list = reward_list
        self.grid = np.array(reward_list)
        self.discount_factor = discount_factor
        self.cost = cost
        self.nb_actions = nb_actions
        self.nb_states = nb_states
        self.Q_table = QTable(self.nb_states, self.nb_actions)

        #self.negative_reward_coords = [Coordinates(reward_list.index(i), 0) for i in reward_list if i < 0]
        #self.positive_reward_coords = [Coordinates(reward_list.index(i), 0) for i in reward_list if i > 0]
        self.non_zero_rewards_coords = [Coordinates(reward_list.index(i), 0) for i in reward_list if i != 0]

        print(self.non_zero_rewards_coords)

    def get_grid(self):
        return self.grid

    def get_grid_length(self):
        return len(self.grid)

    def get_reward(self, coordinates):
        x = coordinates.get_x()
        return self.input_list[x]

    def get_cost(self):
        return self.cost
    
    def get_non_zero_rewards_coords(self):
        return self.non_zero_rewards_coords 


class Coordinates:

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

class Agent:

    def __init__(self, 
                 lr: float, 
                 starting_coords: Coordinates,
                 grid: Grid):
        self.grid = grid
        self.rewards = 0
        self.learning_rate = lr
        self.position = starting_coords

        self.rewards += self.grid.get_reward(self.position)
        print(f"At the beginning, I am at {self.position} and I have : {self.rewards}")
        self.actions = {
            "right" : 1,
            "left": 1,
            "up" : 0,
            "down" : 0 
        }
    
    def move(self, 
             action: str):
        
        movement_cost = self.grid.get_cost()

        x = self.position.get_x()
        y = self.position.get_y()
        grid_length = self.grid.get_grid_length()

        if action == "right" and x < grid_length - 1:
            x += self.actions[action]
        elif action == "left" and x > 0:
            x -= self.actions[action]
        elif action == "up":
            y += self.actions[action]
        elif action == "down":
            y -= self.actions[action]
        
        self.position = Coordinates(x, y)
        print(self.position)
        self.rewards -= movement_cost
        self.rewards += self.grid.get_reward(self.position)
    
    def get_rewards(self):
        return self.rewards

    def get_position(self):
        return self.position
    
grid1D = Grid_1D(reward, 
            discount_factor=gamma,
            cost=cost,
            nb_actions=nb_action,
            nb_states=nb_state 
            )

starting_coords = Coordinates(1, 0)
agent = Agent(lr=alpha,
              starting_coords=starting_coords, 
              grid=grid1D)


#If the agent is on a reward case other than 0 and decides do pick a move that does not allow to effectively move,
#the movement cost will still apply and the reward will still apply

action_list = ["right", "left"]
if __name__ == "__main__":

    for i in range(10):
        move = random.choice(action_list)
        print(f"I move to the {move}")
        agent.move(move)
        agent_position = agent.get_position()
        if agent_position in grid1D.get_non_zero_rewards_coords():
            print(f"J'ai atteint une case reward différente de 0 en {i} actions !")
            break

    print(f"I have now : {agent.get_rewards()}")
