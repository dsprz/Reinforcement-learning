from Grid import Grid
from Action import Action
from State import State
from Agent import Agent
import numpy as np


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

        #Initialize the Q_table to 0
        self.Q_table = np.zeros((nb_states, nb_actions))
            
    def get_table(self) -> np.ndarray:
        return self.Q_table

    def update_table(self, 
                     starting_state: State, 
                     action: Action,
                     agent: Agent,
                     discount_factor: float) -> None:
        
        """Update the Q_table using the Q_table update formula"""

        starting_state_number = starting_state.get_number()
        action_number = Q_Table.actions_dict[action.get_name()]
        
        agent_learning_rate = agent.get_learning_rate()
        
        #After executing the action action from the starting state s_{t}, 
        #the agent moves to a new position which is the destination state s_{t+1} and gets a reward
        agent_position = agent.get_position()
        reward = self.grid.get_reward(agent_position)
        
        destination_state_number = int(str(agent_position.get_y()) + str(agent_position.get_x()))
        #print(f"destination state number = {destination_state_number}")
        

        old_Q_value = self.Q_table[starting_state_number][action_number]
        max_Q = max(self.Q_table[destination_state_number])

        #print(f"maxQ in {self.Q_table[destination_state_number]} = {max_Q}")
        
        new_Q_value = old_Q_value + agent_learning_rate*(reward + discount_factor*max_Q - old_Q_value)
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

        """Return the best action for the state""" 
        state_number = state.get_number()
        max_action_number = np.argmax(self.Q_table[state_number])
        return action_list[max_action_number]

    def __repr__(self):
        """
            Print out the Q_table in the command line.
            Not the nicest implementation but it is good enough for me.
        """

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