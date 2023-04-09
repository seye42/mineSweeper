from game import *
from player import *


g = Game(25, 50, 450, 4)
playRandomCell(g)
playRandomCell(g)
playRandomCell(g)
playRandomCell(g)
playRandomCell(g)
playRandomCell(g)
playRandomCell(g)
doAllDetermined(g)
g.display()


# # test case 0 -- winnable
# g = Game(8, 8, 10, 42)
# g = Game(8, 8, 10, 42)
# playRandomCell(g)
# doAllDetermined(g)
# playRandomCell(g)
# playRandomCell(g)

# # test case 1 -- winnable
# g = Game(40, 60, 150, 42)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# doAllDetermined(g)

# # test case 2 -- winnable
# g = Game(25, 50, 125, 4)
# playRandomCell(g)
# doAllDetermined(g)
# g.display()