from abc import ABC, abstractmethod
from Coordinates import Coordinates
import numpy as np

class Grid(ABC):

    """An abstract class representing any grid"""

    @abstractmethod
    def get_cost(self):
        pass

    @abstractmethod
    def get_grid_length(self):
        pass
    
    @abstractmethod
    def get_reward(self):
        pass

class Grid_1D(Grid):

    """A class representing a 1-D grid"""

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
        #self.Q_table = Q_Table(self.nb_states, self.nb_actions)

        self.non_zero_rewards_coords = [Coordinates(reward_list.index(i), 0) for i in reward_list if i != 0]

        #print(f"Cases with non zero rewards : {self.non_zero_rewards_coords}")

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