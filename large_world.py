import random
import sqlite3
from small_world import SmallWorld
from market_table import MarketTable
from agent_intelligence import dividendFirstOrderAdaptive
import database_manager as dm

class LargeWorld:
    # Attributes:
    # N: int                                        number of small worlds
    # S: int                                        number of states in L
    # E: float                                      endowment of each security in each small world
    # L: List[int]                                  union of states in small worlds
    # small_worlds: dict{agent_num:SmallWorld}      dictionary of key agent numbers and value SmallWorld objects
    # market_table: MarketTable                     our market making mechanism
    # by_midpoint: bool                             whether or not transaction prices should be the midpoint of the bid-ask spread
    #                                               if False we use the price of the earlier order
    # con: Connection                               connection to database object
    # cur: Cursor                                   Cursor object to execute database commands

    # Parameters
    # N: int                    number of small worlds
    # S: states                 number of states in large world
    # E: float                  endowment that each small world has for each of its states
    # K: int                    can have one of two meanings, must be <= S if fix_num_states or  <= N if fix_num_worlds
    # fix_num_states: bool      if True, each small world gets K states. If false, each state is assigned to K small worlds
    # by_midpoint: bool         whether or not transaction prices should be the midpoint of the bid-ask spread
    #                           if False we use the price of the earlier order
    # pick_agent_first: bool    if True, we randomly pick an agent then a state in an iteration.
    #                           if False, we randomly pick a state then an agent
    # file_name: str            what file names for this large world will be called
    def __init__(self, N: int, S: int, E: int, K: int, fix_num_states: bool, by_midpoint: bool, pick_agent_first: bool, file_name: str):
        # Make sure our inputs are valid
        if fix_num_states and K > S:
            raise ValueError("Number of states in large world must be greater than number of states in small world")
        if not fix_num_states and K > N:
            raise ValueError("Number of small worlds must be greater than number of small worlds each state is in")
        
        self.N, self.S, self.E = N, S, E
        self.by_midpoint = by_midpoint
        self.pick_agent_first = pick_agent_first
        self.small_worlds = dict()

        # Each world get K states
        if fix_num_states:
            self.agents = range(N)
            # We put all the states that are in our large world in L 
            d = dict()
            for agent_num in range(N):
                agent = SmallWorld(agent_num, random.sample(range(S), K), self.E)
                for state_num in agent.states.keys():
                    if not d.get(state_num):
                        d[state_num] = True
                self.small_worlds[agent_num] = agent
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
                # There is a possibility that an agent gets assigned no states
                # In this case, it is excluded from the large world
                if states_list[agent_num]:
                    agent = SmallWorld(agent_num, states_list[agent_num], self.E)
                    self.small_worlds[agent_num] = agent
        # Set up our database
        self.con = sqlite3.connect(file_name + ".db")
        self.cur = self.con.cursor()
        # Set up our market
        # We only include the states that are owned by some agents in our marketplace
        self.market_table = MarketTable(self.L, self.small_worlds, self.by_midpoint, self.cur)

    # String representation of large world and the small worlds and state within it
    def __str__(self) -> str:
        ans = f"This large world contains {self.N} agents with {len(self.L)} states\n"
        for small_world in self.small_worlds.values():
            ans += str(small_world)
        return ans

    def giveMinimalIntelligence(self, R) -> None:
        # Iterate through each agent:
        for small_world in self.small_worlds.values():
            states = list(small_world.states.keys())
            not_realized_states = list(filter(lambda s: s not in R, states))
            # Initialize not_info by randomly choosing half of the agent's states not included in R 
            not_info = random.sample(not_realized_states, len(not_realized_states) // 2)
            small_world.giveNotInfo(not_info)

    # Initialize aspiration level of our small worlds based on R
    def initalizeAspiration(self) -> None:
        # Iterate through each agent:
        for small_world in self.small_worlds.values():
            not_info = small_world.not_info
            # Agent updates aspiration level of states in not_info to 0
            for state in not_info:
                small_world.states[state].updateAspiration(0)
            # Set aspiration levels for states with unknown payoff
            C = small_world.num_states - len(not_info)
            for state_num, state in small_world.states.items():
                if state_num not in not_info:
                    state.updateAspiration(1/C)

    # Re-endow all small worlds at the beginning of a period if it is not the first
    def resetSmallWorlds(self) -> None:
        for small_world in self.small_worlds.values():
            small_world.balanceReset()
            for state in small_world.states.values():
                state.amountAdd(self.E)

    # Called at the end of a period to pay out all dividends as appropriate
    # We log how much of each security each agent has at the end of a period in our security_balances table
    def realizePeriod(self, R, period_num: int) -> None:
        for small_world in self.small_worlds.values():
            for state_num, state in small_world.states.items():
                is_realized = 1 if state_num in R else 0
                self.cur.execute("INSERT INTO security_balances VALUES (?, ?, ?, ?, ?, ?)",
                                [period_num, small_world.agent_num, state_num, state.amount, is_realized, is_realized * state.amount]
                )
                if state.amount > 0:
                    if is_realized:
                        small_world.balanceAdd(state.amount)
                        state.updateAspiration(dividendFirstOrderAdaptive(state.aspiration, 1))
                    else:
                        state.updateAspiration(dividendFirstOrderAdaptive(state.aspiration, 0))
                    state.amountReset()
    
    # Parameters:
    # period_num: int       what period it is 
    # i: int                number of market making iterations
    # r: int                number of states that will be realized, must be <= S
    def period(self, period_num: int, i: int, r: int) -> None:
        if r > self.S:
            raise ValueError("r must be <= number of states in large world")
        # We make the model choice that states not in any small worlds may still be realized
        # Initialize R by choosing r random states in the large world with equal probability to be realized 
        R = random.sample(range(self.S), r)
        dm.updateRealizationsTable(self.cur, period_num, self.S, R)
        self.giveMinimalIntelligence(R)
        if period_num == 0:
            self.initalizeAspiration()
        else:
            self.resetSmallWorlds()
        # Conduct each market making iteration using a single processor 
        for j in range(i):
            if self.pick_agent_first:
                rand_agent = random.choice(list(self.small_worlds.values()))
                rand_state = random.choice(list(rand_agent.states.values()))
            else:
                rand_state_num = random.choice(self.L)
                rand_state = random.choice(self.market_table.table[rand_state_num].reserve)
            rand_action = random.choice(["bid", "ask"])

            if rand_action == "bid":
                bid = random.uniform(0, rand_state.aspiration)
                self.market_table.updateBidder(bid, rand_state, j)
            else:
                ask = random.uniform(rand_state.aspiration, 1)
                self.market_table.updateAsker(ask, rand_state, j)    
        # Finish the period
        self.market_table.tableReset()
        self.realizePeriod(R, period_num)
        dm.updateAgentsTable(self.cur, period_num, self.small_worlds.values())

    # parameters
    # num_periods: int      number of periods to run the simulation for
    # i: int                number of market making iterations
    # r: int                number of states that will be realized, must be <= S
    def simulate(self, num_periods: int, i: int, r: int):
        dm.createTransactionsTable(self.cur)
        dm.createAgentsTable(self.cur)
        dm.createRealizationsTable(self.cur)
        dm.createSecurityBalancesTable(self.cur)
        for period in range(num_periods):
            self.period(period, i, r)
        # Save and close database connection
        self.con.commit()
        self.con.close()