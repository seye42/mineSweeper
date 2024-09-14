from game import *
from player import *


testNum = 0

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
elif testNum == 5:
    # official beginner
    # https://minesweepergame.com/ranking-rules.php
    g = Game(8, 8, 10, 3, True)
    basicPlayer(g)
elif testNum == 6:
    # official intermediate
    # https://minesweepergame.com/ranking-rules.php
    g = Game(16, 16, 40, 2, True)
    basicPlayer(g)
elif testNum == 7:
    # official expert
    # https://minesweepergame.com/ranking-rules.php
    g = Game(16, 30, 99, 5, True)
    basicPlayer(g)
else:
    pass