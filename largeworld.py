import random
from typing import List
from smallworld import SmallWorld
from markettable import MarketTable
import marketmaker

class LargeWorld:
    # Attributes:
    # N: int                                number of small worlds
    # S: int                                number of states in L
    # L: List[int]                          union of states in small worlds
    # agents: List[int]                     list of agents in large world
    # small_worlds: List[SmallWorld]        list of SmallWorld objects    

    # Parameters
    # N: int                    number of small worlds
    # S: states                 number of states in large world
    # E: float                  endowment that each small world has for each of its states
    # K: int                    can have one of two meanings, must be <= S if fix_num_states or  <= N if fix_num_worlds
    # fix_num_states: bool        optional, configured as True by default in which each small world gets K states
    # fix_num_worlds: bool        optional, configured as False by default, when True each state is assigned to K worlds
    def __init__(self, N: int, S: int, E: int, K: int, fix_num_states = True, fix_num_worlds = False):
        # Make sure our inputs are valid
        if fix_num_states and fix_num_worlds or not(fix_num_states or fix_num_worlds):
            raise ValueError("Exactly one of fix_num_states or fix_num_worlds must be configured")
        if fix_num_states and K > S:
            raise ValueError("Number of states in large world must be greater than number of states in small world")
        if fix_num_worlds and K > N:
            raise ValueError("Number of small worlds must be greater than number of small worlds each state is in")
        
        self.N, self.S = N, S
        self.small_worlds, self.agents = [], []

        # Each world get K states
        if fix_num_states:
            self.agents = range(N)
            # We put all the states that are in our large world in L 
            d = dict()
            for agent_num in range(N):
                agent = SmallWorld(agent_num, random.sample(range(S), K), E)
                for state_num in agent.states.keys():
                    if not d.get(state_num):
                        d[state_num] = True
                self.small_worlds.append(agent)
            self.L = list(d.keys())
        # Each state is placed in K worlds
        else:
            # states_list represents an array with the states in each of the N agents
            self.L = range(S)
            states_list = []
            [states_list.append([]) for i in range(N)]
            for state in range(S):
                random_small_worlds = random.sample(range(N), K)
                [states_list[i].append(state) for i in random_small_worlds]
            for agent_num in range(N):
                # We make sure that our agent actually has states within it
                if states_list[agent_num]:
                    self.agents.append(agent_num)
                    agent = SmallWorld(agent_num, states_list[agent_num], E)
                    self.small_worlds.append(agent)

    # String representation of large world and the small worlds and state within it
    def __str__(self) -> str:
        ans = f"This large world contains {self.N} agents with {len(self.L)} states\n"
        for small_world in self.small_worlds:
            ans += str(small_world)
        return ans

    # Initialize aspiration level of our small worlds based on R
    def initalizeAspiration(self, R: List[int]) -> None:
        # Iterate through each agent:
        for small_world in self.small_worlds:
            states = list(small_world.states.keys())
            not_realized_states = list(filter(lambda s: s not in R, states))
            # Initialize not_info by randomly choosing half of the agent's states not included in R 
            not_info = random.sample(not_realized_states, len(not_realized_states) // 2)
            
            # Agent updates aspiration level of states in not_info to 0
            for state in not_info:
                small_world.states[state].updateAspiration(0)
            # Set aspiration levels for states with unknown payoff
            C = small_world.num_states - len(not_info)
            for state in states:
                if state not in not_info:
                    small_world.states[state].updateAspiration(1/C)
    
    # Parameters:
    # period_num: int       what period it is 
    # i: int                number of market making iterations
    # r: int                number of states that will be realized, must be <= S
    def period(self, period_num: int, i: int, r: int) -> None:
        if r > len(self.S):
            raise ValueError("r must be <= number of states in large world")

        bid_table = MarketTable(self.small_worlds, "bid")
        ask_table = MarketTable(self.small_worlds, "ask")

        # We make the model choice that states not in any small worlds may still be realized
        # Initialize R by choosing r random states in the large world with equal probability to be realized 
        R = random.sample(len(self.L), r)

        if period_num == 0:
            self.initalizeAspiration(R)
        # implement first order adaptive updating of aspiration based on previous period's dividends
        else:
            pass

        # Conduct each market making iteration using a single processor 
        for j in range(i):
            rand_agent = random.choice(self.small_worlds.values())
            rand_state = rand_agent[random.choice(rand_agent.states.keys())]
            rand_action = random.choice(["bid", "ask"])

            if rand_action == "bid":
                bid = random.uniform(0, rand_state.aspiration)
                rand_state.updateBid(bid)
            else:
                # Only submit the ask if the agent has amount > 0
                ask = random.uniform(rand_state.aspiration, 1)
                rand_state.updateAsk(ask)
