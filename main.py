from large_world import LargeWorld
from simulation_statistics import obtainParameters, runStatistics
import time

DEFAULT_ALPHA = .05
DEFAULT_BETA = .15

# Given an input file, it runs a round of the simulation
def runInputFile(input_file):
    p = obtainParameters(input_file)
    start = time.time()
    L = LargeWorld(p["N"], p["S"], p["E"], p["K"], p["fix_num_states"], p["pick_agent_first"], p["by_midpoint"], p["alpha"], p["beta"], p["file_name"])
    L.simulate(p["num_periods"], p["i"], p["r"])
    end = time.time()
    db_name = input_file[:-3] + ".db"
    print(f"Successfully ran simulation! This simulation took {round(end - start, 1)} seconds to run. Results can be found in {db_name}")
    runStatistics(db_name)

# Creates an input file based on what the user enters and runs a round of the simulation with it
def handleInput():
    print("-" * 75)
    # try:
    print("Inpute the following parameters")
    N = int(input("Number of small worlds: "))
    S = int(input("Number of states in large world: "))
    E = int(input("Endowment of each security: "))
    fix_flag = input("Type 'states' to fix the number of number of states in each small world or 'worlds' to fix the number of small worlds assigned to each state: ").strip().lower()
    if fix_flag == "states":
        fix_num_states = True
        K = int(input("States in each small world: "))
    elif fix_flag == "worlds":
        fix_num_states = False
        K = int(input("Number of small worlds each state is assigned to: "))
    else:
        raise ValueError()
    trade_flag = input("How trade prices are calculated? Type 'midpoint' for the midpoint of the bid and ask or 'time' for the earlier offer: ").strip().lower()
    if trade_flag == "midpoint":
        by_midpoint = True
    elif trade_flag == "time":
        by_midpoint = False
    else:
        raise ValueError()
    rand_flag = input("In each iteration, should we pick 'agent' or 'state' first? ").strip().lower()
    if rand_flag == "agent":
        pick_agent_first = True
    elif rand_flag == "state":
        pick_agent_first = False
    else:
        raise ValueError() 
    num_periods = int(input("Number of periods: "))
    i = int(input("Trading iterations in each period: "))
    r = int(input("States realized during each period: "))
    greeks_flag = input(f"Do you want to input custom values of alpha/beta or leave them at {DEFAULT_ALPHA} and {DEFAULT_BETA} respectively? (Yes/No) ").strip().lower()
    if greeks_flag == "yes":
        alpha = float(input("Alpha: "))
        beta = float(input("Beta: "))
    elif greeks_flag == "no":
        alpha, beta = DEFAULT_ALPHA, DEFAULT_BETA
    else:
        raise ValueError()
    file_name = input("Prefix to name files of this simulation: ")

    # Constants
    PARAMETERS = [N, S, E, K, fix_num_states, by_midpoint, pick_agent_first, alpha, beta, num_periods, i, r, file_name]
    PARAMETER_NAMES = ["N", "S", "E", "K", "fix_num_states", "by_midpoint", "pick_agent_first", "alpha", "beta", "num_periods", "i", "r", "file_name"]

    # Create an input file logging our inputs
    f = open(file_name + ".in", "w")
    for i in range(len(PARAMETERS)):
        f.write(f"{PARAMETER_NAMES[i]}:{PARAMETERS[i]}\n")
    f.close()

    runInputFile(file_name + ".in")
    # except:
    #     print("Your input was invalid, start over!")
    #     handleInput()

# Displays menu of options and enables user to choose what to do
def menu():
    print("-" * 75)
    print("'input': input parameters and run a round of the simulation")
    print("'run': run an already existing input file")
    print("'stats' to run statistics for an already existing database")
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
    elif i == "stats":
        db = input("Enter database file name: ")
        print("-" * 75)
        runStatistics(db)
    else:
        print("That's not a valid option, try again")
    menu()

def main():
    print("-" * 75)
    print("Welcome to the Large Worlds simulation!")
    menu()

if __name__ == "__main__":
    main()