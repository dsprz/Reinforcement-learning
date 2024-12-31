from Rogue import Hero, Game, Coord
import numpy as np
import random

#To deep copy a value
import copy

#To store a dictionary in a file
import pickle

"""
    Simple Q-learning
    No mobs, no items, only the hero, some cliffs and a destination to reach
    State storing is made using the hero coordinates since there is no other state defining elements, like mob coords, item coords, mob health etc.
"""

#Set a seed
random.seed(4)

# ----------------Initialization of the game and the hero which will act as the agent -------------------
hero = Hero()
game = Game(hero=hero)

#For states
coords_to_be_added = Coord(0,0)

#--------------- Initialize the q_table in dict form -------------------

#The storing syntax is : 
#   (hero.x, hero.y) : [Q(s[k], a[1]), Q(s[k], a[2]), ... , Q(s[k], a[N])]
#   where [Q(s, a1), Q(s, a2), ... , Q(s, aN)] is initialized to [0, 0, ..., 0]
q_table = {
    
}

# --------------- Initialization of some constants -------------------
X_LENGTH = len(game.floor.get_mat())
Y_LENGTH = len(game.floor.get_mat()[0])
GAMMA = 1 #discount factor
LEARNING_RATE = 0.99
hero.set_learning_rate(LEARNING_RATE)
REWARDS = np.array(game.get_map().get_rewards_map())
MOVE_COST = 1 #Tous les pas sont similaires et négatifs
STAIRS_COORDS = game.floor.stairs_coordinates
MAX_TRAINING_GAMES = 400

#End state i.e. the stairs
TERMINAL_STATE = STAIRS_COORDS.x, STAIRS_COORDS.y
q_table[TERMINAL_STATE] = [0 for action in range(len(Hero.ACTIONS))]


#Get the coords of the hero and store them in the q_table 
hero_coord = game.get_hero_coords()
state_tuple = (hero_coord.x, hero_coord.y)
q_table[state_tuple] = [0 for action in range (len(Hero.ACTIONS))]

# ------------------- Play simulation ------------------------
print(" ---------------------------- START GAMING ----------------------------------------")
    
continue_episode = True


#Epsilon
choose_at_move_at_random_threshold = 0.2

#Variable to store last state to detect if the agent is going backwards
last_state = hero_coord.x, hero_coord.y

#Variable to detect if the agent keeps hitting a wall
same_state = hero_coord.x, hero_coord.y


#Number of moves used to get to terminal state
moves_used = 0

def play():
    global last_state, continue_episode, same_state, moves_used

    moves_used+=1
    # The hero starts at some coordinates
    hero_coord = game.get_hero_coords()
    print(f"The hero starts at {hero_coord.x, hero_coord.y}")
    starting_state = (hero_coord.x, hero_coord.y)

    #Make a move to another state
    print("Preparing to move...")

    #Pick a move at random 80% of the time
    if random.random() > choose_at_move_at_random_threshold:
        move_number = random.choice([0, 3])

    else:
        #Pick the best move 80% of the time
        move_number = np.argmax(q_table[starting_state])
        print(f"The best move at {starting_state} is move {move_number} because it has Q(s,a) = {max(q_table[starting_state])}")
    
    if move_number == 0:
        print("move left")
        cliff = hero.move_left(game)
        coords_to_be_added = Coord(-1, 0)
    elif move_number == 1:
        print("move right")
        cliff = hero.move_right(game)
        coords_to_be_added = Coord(1, 0)

    elif move_number == 2:
        print("move up")
        cliff = hero.move_up(game)
        coords_to_be_added = Coord(0, 1)

    elif move_number == 3:
        print("move down")
        cliff = hero.move_down(game)
        coords_to_be_added = Coord(0, -1)
    
    
    #The hero can get out of map by pure chance, handle the case
    hero_is_out_of_map_x = starting_state[0] + coords_to_be_added.x > X_LENGTH-1 or starting_state[0] + coords_to_be_added.x < 0
    hero_is_out_of_map_y = starting_state[1] + coords_to_be_added.y > Y_LENGTH-1 or starting_state[1] + coords_to_be_added.y < 0
    hero_is_out_of_map = hero_is_out_of_map_x or hero_is_out_of_map_y

    if hero_is_out_of_map:
        destination_state = starting_state
    else:
        #The hero has already been resetted to its starting position if the encountered a cliff
        #Getting the new coordinates directly now would be getting the coordinates of its starting location

        if cliff:
            destination_state = (starting_state[0] + coords_to_be_added.x, starting_state[1] + coords_to_be_added.y)
        else:
        #Get the new coordinates of the hero
            hero_coord = game.get_hero_coords()
            destination_state = (hero_coord.x, hero_coord.y)

    print(f"destination state : {destination_state}")

    #Add the destination state to the q table if it does not exist
    q_table.setdefault(destination_state, [0 for action in range (len(Hero.ACTIONS))])
    
    
    destination_state_x = destination_state[0]
    destination_state_y = destination_state[1]
    # Get the reward
    if hero_is_out_of_map:
        reward = -999
    else:
        reward = REWARDS[destination_state_y][destination_state_x] - MOVE_COST
    

    #Avoiding going back by setting a malus  
    print(f"Comparing last_state : {last_state} to destination state : {destination_state}")
    print(f"Comparing last_destination : {same_state} to destination state : {destination_state}")
    if destination_state == last_state or destination_state == same_state:
        reward -= 2

    print(f"reward : {reward}")

    #Update Q_table with the reward
    #Convert to float to avoid displaying "np.float64(value)"" in print statements
    q_table[starting_state][move_number] += float(LEARNING_RATE*(reward + GAMMA*max(q_table[destination_state]) - q_table[starting_state][move_number]))

    #Break the loop if the hero attains the stairs
    if destination_state == TERMINAL_STATE:
        print("End of the episode because stairs reached")
        game.get_map().reset_hero()
        continue_episode = False
        return 


    #Store the starting state to use for the next iteration to avoid going back
    #Store the current state to avoid staying in place
    last_state = copy.deepcopy(starting_state)
    same_state = copy.deepcopy(destination_state)

    if cliff :
        print("End of episode because cliff")
        continue_episode = False



try:
    #Load an already exisitng Q_table, if it does not exist then train
    with open("Q_table.pkl", "rb") as file:
        q_table = pickle.load(file)

except FileNotFoundError:
    #Train if the Q_table file does not exist
    for tryout in range(MAX_TRAINING_GAMES):
        continue_episode = True

        #At 60% of games, start to use the best moves while still exploring
        if tryout>0.6*MAX_TRAINING_GAMES:
            choose_at_move_at_random_threshold = 0.8
        while continue_episode:
            play()
        print("############")



# Reset hero coords after training
game.get_map().reset_hero()



#Make it so the agent always chooses the best action according to the Q-values
choose_at_move_at_random_threshold = 1


#Store the results in a dict
results = {

}

#Gaming with the Q-table

for i in range(10):
    game.get_map().reset_hero()
    continue_episode = True
    moves_used = 0
    print(f"-------------------------------------- GAME NUMBER {i} ----------------------------------------")
    while continue_episode:
        play()
    print(f"Finished in {moves_used} moves")
    print("############")
    results[f"Game {i}"] = f"{moves_used} moves"



def print_dict_nicely(dict: dict, dict_name: str):
    """ 
        Print a dictionary nicely
        For clean display in the terminal
    """

    max_key_length = max(len(key) for key in dict)
    max_value_length = max(len(str(value)) for value in dict.values())
                
    print(f"{dict_name} = ", "{")
    for key, value in dict.items():
        print(f"   {str(key):{max_key_length}} : {str(value):{max_value_length}},")

    print("}")


#Sort the Q-table by values for easier reading
q_table = dict(sorted(q_table.items(), key=lambda x :(x[0][0], x[0][1])))
print_dict_nicely(q_table, "Q_table")

import pandas as pd
df = pd.DataFrame(REWARDS)
print(df)

print(f"Hero starting coords : {hero_coord}")
print(f"STAIRS COORDS : {STAIRS_COORDS}")
print_dict_nicely(results, "Results")


#Store the dictionary as JSON
with open("Q_table.pkl", "wb") as file:
    pickle.dump(q_table, file)

if __name__ == "__main__":
    pass
#Donner des indices à l'agent pour qu'il arrive à trouver l'escalier pendant son training
#Ex un malus s'il retourne sur ses pas, ça peut aider à apprendre les zones sans issues