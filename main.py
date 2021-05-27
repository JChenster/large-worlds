from largeworld import LargeWorld
from smallworld import SmallWorld

# Large world where each small world has 5 states each
L1 = LargeWorld(50, 50, 1, 5)
print(str(L1))

# Large world where each state is placed in 5 small worlds each
L2 = LargeWorld(50, 50, 1, 5, fixNumStates = False, fixNumWorlds = True)
print(str(L2))