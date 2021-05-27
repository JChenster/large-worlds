from state import State

class SmallWorld:
    def __init__(self, agent_num: int, states_list, E: int, balance = 0):
        self.agent_num = agent_num
        self.states = dict()
        self.num_states = len(states_list)
        self.balance = balance
        for state in states_list:
            s = State(state, E)
            self.states[state] = s
    
    def __str__(self):
        ans = f"Small world {self.agent_num} contains {self.num_states} states and ${self.balance}\n"
        for state in self.states.keys():
            ans += f"\t{str(self.states[state])}\n"
        return ans        
