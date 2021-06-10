from largeworld import LargeWorld
from simulation_statistics import obtainParameters, runStatistics

def runInputFile(input_file):
    p = obtainParameters(input_file)
    L = LargeWorld(p["N"], p["S"], p["E"], p["K"], p["fix_num_states"], p["by_midpoint"], p["file_name"])
    L.simulate(p["num_periods"], p["i"], p["r"])
    print(f"Successfully ran simulation! Results can be found in {input_file[:-3]}.db")

# Creates an input file based on what the user enters and runs a round of the simulation with it
def handleInput():
    print("-" * 75)
    # try:
    N = int(input("Enter how many small worlds you want: "))
    S = int(input("Enter number of states you want in the large world: "))
    E = int(input("Enter the endowment of each state you want each small world to have: "))
    fix_flag = input("What do you want to fix? Type 'states' to fix the number of number of states in each small world or 'worlds' to fix the number of small worlds assigned to each state: ").strip().lower()
    if fix_flag == "states":
        fix_num_states = True
        K = int(input("Enter number of states you want each small world to have: "))
    elif fix_flag == "worlds":
        fix_num_states = False
        K = int(input("Enter number of small worlds you want each state to be assigned to: "))
    else:
        raise ValueError()
    trade_flag = input("How should trade prices be calculated? Type 'midpoint' for the midpoint of the bid and ask or 'time' for the earlier offer: ").strip().lower()
    if trade_flag == "midpoint":
        by_midpoint = True
    elif trade_flag == "time":
        by_midpoint = False
    else:
        raise ValueError()
    file_name = input("Enter what the files for this simulation should be named: ")
    num_periods = int(input("Enter how many periods you want: "))
    i = int(input("Enter how many trading iterations you want each period to have: "))
    r = int(input("Enter how many states you want to be realized during each period: "))

    # Create an input file logging our inputs
    f = open(file_name + ".in", "w")
    parameters = [N, S, E, K, fix_num_states, by_midpoint, file_name, num_periods, i, r]
    parameter_names = ["N", "S", "E", "K", "fix_num_states", "by_midpoint", "file_name", "num_periods", "i", "r"]
    for i in range(len(parameters)):
        f.write(f"{parameter_names[i]}:{parameters[i]}\n")
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
    i = input("Enter your choice here: ").strip().lower()
    if i == "input":
        handleInput()
    elif i == "run":
        input_file = input("Enter input file name: ")
        # try:
        runInputFile(input_file)
        # except:
        #     print("That's an invalid input file, try again")
        #     menu()
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