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