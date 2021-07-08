from large_world import LargeWorld
from simulation_statistics import runStatistics
import time
from parse_input import obtainParameters

DEFAULT_ALPHA = .05
DEFAULT_BETA = .15
DEFAULT_PHI = 3
DEFAULT_EPSILON = .05

# Given an input file, it runs a round of the simulation
def runInputFile(input_file):
    p = obtainParameters(input_file)
    start = time.time()
    # New input parameters must be called here
    L = LargeWorld(p)
    print("Currently running simulation! This could take a few minutes...")
    L.simulate(p["num_periods"], p["i"], p["r"])
    end = time.time()
    db_name = input_file[:-3] + ".db"
    print(f"Successfully ran simulation! This simulation took {round(end - start, 1)} seconds to run. Results can be found in {db_name}")
    runStatistics(db_name)

# Creates an input file based on what the user enters and runs a round of the simulation with it
# If at any point, an invalid parameter is entered, a Value Exception is raised
def handleInput():
    print("-" * 75)
    # try:
    p = {}
    print("Inpute the following p")
    
    # Numerical large world attributes
    p["N"], p["S"], p["E"] = -1, -1, -1
    while p["N"] < 0:
        try: p["N"] = int(input("N, Number of small worlds aka. agents: "))
        except: pass

    while p["S"] < 0:
        try: p["S"] = int(input("S, Number of states in large world: "))
        except: pass

    while p["E"] < 0:
        try: p["E"] = int(input("E, Endowment of each security: "))
        except: pass

    # Boolean attributes
    fix_flag = ""
    while fix_flag not in ["states", "worlds"]:
        fix_flag = input("Type 'states' to fix the number of number of states in each small world or 'worlds' to fix the number of small worlds assigned to each state: ").strip().lower()
    p["fix_num_states"] = (fix_flag == "states")

    p["K"] = -1
    while p["K"] < 0:
        fix_num_states_prompt = "K, States in each small world: "
        fix_num_worlds_prompt = "K, Number of small worlds each state is assigned to: "
        try: p["K"] = int(input(fix_num_states_prompt if p["fix_num_states"] else fix_num_worlds_prompt))
        except: pass

    trade_flag = ""
    while trade_flag not in ["midpoint", "time"]:
        trade_flag = input("How trade prices are calculated? Type 'midpoint' for the midpoint of the bid and ask or 'time' for the earlier offer: ").strip().lower()
    p["by_midpoint"] = (trade_flag == "midpoint")

    rand_flag = ""
    while rand_flag not in ["agent", "state"]:
        rand_flag = input("In each iteration, should we pick 'agent' or 'state' first? ").strip().lower()
    p["pick_agent_first"] = (rand_flag == "agent")

    backlog_flag = ""
    while backlog_flag not in ["yes", "no"]:
        backlog_flag = input("Do you want to use a backlog when giving agents intelligence? (Yes/No) ")
    p["use_backlog"] = (backlog_flag == "yes")

    p["rep_flag"] = ""
    while p["rep_flag"] not in ["1", "2"]:
        p["rep_flag"] = input("Do you want to use representativeness module '1' or '2'? ")

    # Simulation mechanism-specific numerical attributes
    p["num_periods"], p["i"], p["r"] = -1, -1, -1

    while p["num_periods"] < 0:
        try: p["num_periods"] = int(input("Number of periods: "))
        except: pass

    while p["i"] < 0:
        try: p["i"] = int(input("i, Trading iterations in each period: "))
        except: pass

    while p["r"] < 0:
        try: p["r"] = int(input("r, States realized during each period: "))
        except: pass

    greeks_flag = ""
    while greeks_flag not in ["yes", "no"]:
        greeks_flag = input(f"Do you want to input custom values of alpha/beta/phi/epsilon or leave them at {DEFAULT_ALPHA}/{DEFAULT_BETA}/{DEFAULT_PHI}/{DEFAULT_EPSILON} respectively? (Yes/No) ").strip().lower()
    if greeks_flag == "yes":
        p["alpha"], p["beta"], p["phi"], p["epsilon"] = -1, -1, -1, -1
        while p["alpha"] < 0:
            p["alpha"] = float(input("Alpha: "))
        while p["beta"] < 0:
            p["beta"] = float(input("Beta: "))
        while p["phi"] < 0:
            p["phi"] = float(input("Phi: "))
        while p["epsilon"] < 0: 
            p["epsilon"] = float(input("Epsilon: "))
    else:
        p["alpha"], p["beta"], p["phi"], p["epsilon"] = DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_PHI, DEFAULT_EPSILON

    # Handle custom dividends    
    is_custom = ""
    while is_custom not in ["yes", "no"]:
        is_custom = input("Do you want to enter custom dividends? (Yes/No) ").strip().lower()
    p["is_custom"] = is_custom == "yes"

    # We want to have different dividend payoffs for different types of traders
    if p["is_custom"]:
        # Receive input of number of traders
        p["num_trader_types"] = None
        while p["num_trader_types"] is None or p["num_trader_types"] <= 0:
            try: p["num_trader_types"] = int(input("Number of trader types: "))
            except: pass

        # Matrix where matrix[i][j] represents the payoff for dividend for security j for traders of type i
        dividends = [[0] * p["S"] for _ in range(p["num_trader_types"])]
        # This is an array where the i'th element represents how many traders are of type i
        num_traders_by_type = [0 for _ in range(p["num_trader_types"])]

        # We have to know the dividend payoff for each state for a trader of each type
        for i in range(p["num_trader_types"]):
            
            print(f"Trader type {i}")
            while num_traders_by_type[i] <= 0 or sum(num_traders_by_type) > p["N"]:
                try: num_traders_by_type[i] = int(input(f"\tNumber of agents that should be of type {i}: "))
                except: pass
            
            for state_num in range(p["S"]):
                # Obtain dividend input for a state 
                dividend = None
                while dividend is None:
                    try: dividend = float(input(f"\tDividend of security {state_num}: "))
                    except: pass
                dividends[i][state_num] = dividend

        if sum(num_traders_by_type) != p["N"]:
            raise ValueError("The sum of the traders of each type does not equal number of agents in large world")
    
        p["num_traders_by_type"] = ",".join(map(str, num_traders_by_type))
        for i in range(len(dividends)):
            p[i] = ",".join(map(str, dividends[i]))

    p["file_name"] = input("Prefix to name files of this simulation: ")

    # Create an input file logging our inputs
    with open(p["file_name"] + ".in", "w") as f:
        for var_name, var in p.items():
            f.write(f"{var_name}:{var}\n")

    runInputFile(p["file_name"] + ".in")
    # except:
    #     print("Your input was invalid, start over!")
    #     handleInput()

# Displays menu of options and enables user to choose what to do
def menu():
    print("-" * 75)
    print("'input': input p and run a round of the simulation")
    print("'run': run an already existing input file")
    print("'q' to quit")
    i = input("Enter your choice here: ").strip().lower()
    if i == "q":
        return
    if i == "input":
        handleInput()
    elif i == "run":
        input_file = input("Enter input file name: ")
        # try:
        runInputFile(input_file)
        # except:
        #     print("That's an invalid input file, try again")
    else:
        print("That's not a valid option, try again")
    menu()

def main():
    print("-" * 75)
    print("Welcome to the Large Worlds simulation!")
    menu()

if __name__ == "__main__":
    main()