from game import *
from player import *

# g = Game(25, 50, 450, 4)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# playRandomCell(g)
# doAllDetermined(g)
# g.display()

testNum = 0

if testNum == 0:
    # small, winnable
    g = Game(8, 8, 10, 42)
    playRandomCell(g)
    doAllDetermined(g)
    playRandomCell(g)
    playRandomCell(g)
elif testNum == 1:
    # medium winnable
    g = Game(40, 60, 150, 42)
    playRandomCell(g)
    playRandomCell(g)
    playRandomCell(g)
    doAllDetermined(g)
elif testNum == 2:
    # medium, winnable
    g = Game(25, 50, 125, 4)
    playRandomCell(g)
    doAllDetermined(g)
elif testNum == 3:
    # first play is a mine
    g = Game(6, 10, 22, 0)
    print(g.field)
    g.playCell(1, 3)
    print(g.field)
    g.display()
else:
    pass