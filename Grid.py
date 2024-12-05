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
class State:
    """
        Class to represent a state.
        A state has a number for easier access to the Q_table 
    """
    def __init__(self, 
                 number: int):
        self.number = number
    
    def get_number(self):
        return self.number

class Action:
    
    """
        Class that represents an action.
        An action has a name (e.g. 'right' or 'left') and a position change (e.g. 'right' means +1 on the x-axis, 'left' means -1 on the left axis)
        Position change can be changed to move more than 1 cell, but it should always be a positive int.
    """

    def __init__(self, 
                 name: str,
                 position_change: int):
        self.name = name
        self.position_change = position_change
    
    def get_name(self):
        return self.name

    def get_position_change(self):
        return self.position_change

    def __repr__(self):
        return self.name


    
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

        print(f"Cases with non zero rewards : {self.non_zero_rewards_coords}")

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

        print(f"At the beginning, I am at {self.position} and I have : {self.rewards}")
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
        print(f"I am now at {self.position}")
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

class Q_Table:

    """
        Class representing a Q_table.
    """

    actions_dict = {
        "right" : 0,
        "left" : 1
    }

    def __init__(self, 
                 nb_states: int, 
                 nb_actions: int, 
                 grid: Grid):
        self.nb_states = nb_states
        self.nb_actions = nb_actions
        self.grid = grid

        #initialize the Q_table to 0
        self.Q_table = np.zeros((nb_states, nb_actions))
        
        #self.Q_table[0][1] = 2
        #print(self.Q_table)
    
    def get_table(self) -> np.ndarray:
        return self.Q_table

    def update_table(self, 
                     starting_state: State, 
                     action: Action,
                     agent: Agent) -> None:
        
        """Update the Q_table using the Q_table update formula"""

        starting_state_number = starting_state.get_number()
        action_number = Q_Table.actions_dict[action.get_name()]
        
        agent_learning_rate = agent.get_learning_rate()
        
        #After executing the action action from the starting state s_{t}, 
        #the agent moves to a new position which is the destination state s_{t+1} and gets a reward
        agent_position = agent.get_position()
        reward = self.grid.get_reward(agent_position)
        
        destination_state_number = int(str(agent_position.get_y()) + str(agent_position.get_x()))
        print(f"destination state number = {destination_state_number}")
        

        old_Q_value = self.Q_table[starting_state_number][action_number]
        max_Q = max(self.Q_table[destination_state_number])

        print(f"maxQ in {self.Q_table[destination_state_number]} = {max_Q}")
        
        new_Q_value = old_Q_value + agent_learning_rate*(reward + gamma*max_Q - old_Q_value)
        self.Q_table[starting_state_number][action_number] = new_Q_value 


    def get_value(self, 
                  state: State, 
                  action: Action):
        """Get the value of Q(state, action)"""

        action_number = Q_Table.actions_dict[action.get_name()]
        state_number = state.get_number()
        return self.Q_table[state_number][action_number]

    def get_best_action_for_state(self, 
                                  state: State,
                                  action_list: list) -> Action: 
        state_number = state.get_number()
        max_action_number = np.argmax(self.Q_table[state_number])
        return action_list[max_action_number]

    def __repr__(self):
        """Print the Q_table"""

        res = ""
        #res += len("s0 |" + f"{self.Q_table[0][0]}")*" " 
        res += 15*" " 
        for i in range(self.nb_actions):
            if i == 0:
                res+= f"A{i} = right" + "|"
                res += 12*" " 
            elif i == 1:
                res+= f"A{i} = left" + "|"        
        res+="\n"

        for i in range(self.nb_states):
            res += f"s{i}" + " |" 
            for j in range(self.nb_actions):
                res += " " f"{self.Q_table[i][j]}" + " |"
            res += "\n"
        return res
    

grid1D = Grid_1D(reward, 
            discount_factor=gamma,
            cost=cost,
            nb_actions=nb_action,
            nb_states=nb_state)

starting_coords = Coordinates(2, 0)
agent = Agent(lr=alpha,
              starting_coords=starting_coords, 
              grid=grid1D)


action_right = Action("right", +1)
action_left = Action("left", -1)

Q_table = Q_Table(nb_state, 
                  nb_action, 
                  grid=grid1D)
print(f"Q_table test : {Q_table.get_value(State(0), action_left)}")

grid1D_non_zero_rewards_coords = grid1D.get_non_zero_rewards_coords()

action_list = [action_right, 
               action_left]

#If the agent is on a reward case other than 0 and decides do pick a move that does not allow to effectively move,
#the movement cost will still apply and the reward will still apply
if __name__ == "__main__":
    print("")
    for game in range(1, 1000):
        continue_episode = True
        
        while continue_episode:
            
            agent_position_before_moving = agent.get_position()
            starting_state_number = int(str(agent_position_before_moving.get_y()) + str(agent_position_before_moving.get_x()))
            print(f"starting state number = {starting_state_number}")
            
            epsilon = random.choice(range(1, 11))
            if epsilon > 2:
                move = random.choice(action_list)
            else:
                move = Q_table.get_best_action_for_state(state=State(starting_state_number), 
                                                         action_list=action_list)
            print("######")
            
            agent.move(move)
            print(f"I move to the {move}")
            agent_position_after_moving = agent.get_position()
            Q_table.update_table(State(starting_state_number),
                                move,
                                agent)

            if agent_position_after_moving in grid1D_non_zero_rewards_coords:
                #print(f"I reached a reward case diffrent from 0 in {i} actions !")
                continue_episode = False
                print(f"I have now : {agent.get_rewards()}")
                print(Q_table)
                agent.reset_rewards()
    print("END")