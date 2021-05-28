from state import State
from typing import List

class SmallWorld:
    # Attributes:
    # agent_num: int (the number of this small world in large world)
    # num_states: int (number of states in this small world)
    # balance: float (cash balance)
    # states: dict(state_num: State) (dictionary of states in this small world with key state number and value State object)

    # Intialize a small world with its agent_number (number of the small world in a large world),
    # a list of states that will be endowed with E each, as well as a cash balanace which is 0 by default
    def __init__(self, agent_num: int, states_list: List[int], E: int, balance = 0):
        self.agent_num = agent_num
        self.num_states = len(states_list)
        self.balance = balance
        self.states = dict()
        for state in states_list:
            s = State(state, E)
            self.states[state] = s
    
    def __str__(self):
        ans = f"Small world {self.agent_num} contains {self.num_states} states and ${self.balance}\n"
        for state in self.states.keys():
            ans += f"\t{str(self.states[state])}\n"
        return ans        
