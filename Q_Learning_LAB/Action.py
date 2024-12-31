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