from game import *
from player import *

# parameters
numGames = 1000
numRows = 16
numCols = 30
numMines = 99
    # https://minesweepergame.com/ranking-rules.php

won = np.zeros((numGames, 1), dtype=bool)
elapsedTime = np.zeros((numGames, 1))

for seed in range(0, numGames):
    g = Game(8, 8, 10, seed, False)
    try:
        basicPlayer(g)
    except GameOver as e:
        d = e.args[0]
        won[seed] = d['won']
        elapsedTime[seed] = d['elapsedTime']