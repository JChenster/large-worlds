from largeworld import LargeWorld
from smallworld import SmallWorld

L1 = LargeWorld(50, 50, 1, 5)
L2 = LargeWorld(50, 50, 1, 5, fixNumStates = False, fixNumWorlds = True)
print(str(L1))
print(str(L2))