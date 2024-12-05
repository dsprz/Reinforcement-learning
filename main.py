import numpy as np
import random
from Grid import Grid_1D
from Agent import Agent
from Coordinates import Coordinates
from Action import Action
from Q_Table import Q_Table
from State import State


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

if __name__ == "__main__":
    print("")
    games_to_be_played = 500
    for game in range(games_to_be_played):
        
        continue_episode = True        
        
        while continue_episode:
            print("######")

            #Get the starting state information
            agent_position_before_moving = agent.get_position()
            starting_state_number = int(str(agent_position_before_moving.get_y()) + str(agent_position_before_moving.get_x()))
            print(f"starting state number = {starting_state_number}")
            
            #Choose a move to explore or to exploit
            epsilon = random.choice(range(1, 11))
            if epsilon > 2:
                #Pick a random move 80% of the time
                move = random.choice(action_list)
            else:
                #Pick the best move 20% of the time
                move = Q_table.get_best_action_for_state(state=State(starting_state_number), 
                                                         action_list=action_list)
            
            #The agent moves to another state
            agent.move(move)
            print(f"I move to the {move}")

            #Get destination state info (s_{t+1}) and update the Q table
            agent_position_after_moving = agent.get_position()
            Q_table.update_table(starting_state=State(starting_state_number),
                                action=move,
                                agent=agent,
                                discount_factor=gamma)

            #End the episode if the agent ends up in a reward!=0 cell 
            if agent_position_after_moving in grid1D_non_zero_rewards_coords:
                continue_episode = False
                print(f"I have now : {agent.get_rewards()}")
                print(Q_table)
                agent.reset_rewards()
    print("END")