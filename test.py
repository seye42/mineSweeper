from game import *
from player import *


testNum = 2

if testNum == 0:
    # small, winnable
    g = Game(8, 8, 10, 50, True)
    basicPlayer(g)
elif testNum == 1:
    # medium winnable
    g = Game(40, 60, 150, 42, True)
    basicPlayer(g)
elif testNum == 2:
    # medium, winnable
    g = Game(25, 50, 125, 4, True)
    basicPlayer(g)
elif testNum == 3:
    # first play is a mine, incomplete game
    g = Game(6, 10, 22, 0)
    print(g.field)
    g.playCell(1, 3)
    print(g.field)
    g.display()
elif testNum == 4:
    # basic player loses
    g = Game(25, 50, 250, 6, True)
    basicPlayer(g)
else:
    pass