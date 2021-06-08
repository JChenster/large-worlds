from state import State

class SmallWorld:
    # Attributes:
    # agent_num: int                    the number of this small world in large world
    # num_states: int                   number of states in this small world
    # balance: float                    cash balance
    # not_info: List[int]               list of the state numbers the agent knows are not realized
    # states: dict{state_num: State}    dictionary of states in this small world with key state number and value State object
    # C: int                            number of states for whom the outcome is uncertain

    # Intialize a small world with its agent_number (number of the small world in a large world),
    # a list of states that will be endowed with E each, as well as a cash balanace which is 0 by default
    def __init__(self, agent_num: int, states_list, E: int, balance = 0):
        self.agent_num = agent_num
        self.num_states = len(states_list)
        self.balance = balance
        self.not_info = []
        self.states = dict()
        for state in states_list:
            s = State(self, state, E)
            self.states[state] = s
    
    def __str__(self) -> str:
        ans = f"Small world {self.agent_num} contains {self.num_states} states and ${self.balance}\n"
        ans += f"\tIt knows states {self.not_info} are not realized\n"
        for state in self.states.values():
            ans += f"\t\t{str(state)}\n"
        return ans

    def balanceAdd(self, amount) -> None:
        self.balance += amount
    
    def balanceReset(self) -> None:
        self.balance = 0

    def giveNotInfo(self, not_info) -> None:
        self.not_info = not_info
        self.C = self.num_states - len(self.not_info)