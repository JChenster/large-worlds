INT_INPUTS = ["N", "S", "E", "K", "phi", "num_periods", "i", "r", "num_trader_types", "rep_flag"]
FLOAT_INPUTS = ["alpha", "beta", "epsilon"]
BOOL_INPUTS = ["fix_num_states", "by_midpoint", "pick_agent_first", "is_custom", "use_backlog"]
STR_INPUTS = ["file_name"]

# Returns dictionary of parameters in input file
def obtainParameters(input_file: str) -> dict:
    p = {}
    # Store all of our parameters in a dictionary linking variable name to variable value
    with open(input_file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            left = line.split(":")[0]
            p[left] = line.split(":")[1].strip()
    
    # Use copy of dict to prevent mutating it while iterating through it
    # Converts each parameter to the correct data type
    for var_name, var in dict(p).items():
        if var_name in INT_INPUTS:
            p[var_name] = int(var)
        elif var_name in FLOAT_INPUTS:
            p[var_name] = float(var)
        elif var_name in BOOL_INPUTS:
            p[var_name] = (var == "True")
        elif var_name in STR_INPUTS:
            continue
        # Input is a list
        else:
            p[var_name] = list(map(float, var.split(",")))
            # Convert the key of dividend payoffs for a security numbers to integers
            try:
                p[int(var_name)] = p[var_name]
                del p[var_name]
            except: pass
    return p