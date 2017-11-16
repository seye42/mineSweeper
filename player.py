import numpy as np
import random
import game


def main():
    # parameters
    numRows = 8
    numCols = 8
    numMines = 10

    # make a game
    g = game.Game(numRows, numCols, numMines, 3)

    # make the initial play
    playRandomCell(g)
    g.display()

    g.playFlag(2,5)
    g.playFlag(5,3)
    g.playFlag(5,5)
    g.playFlag(5,6)
    g.playFlag(6,8)

    # play determined cells
    playDeterminedCells(g)
    # TODO: need to fix up when one play in PDC opens up another
    playDeterminedCells(g)
    g.display()

    '''
    TODO: Think about what auxiliary lists make sense to build in to Game so that so much looping
    isn't required here. Maybe that's shown and flagged lists or something similar. Also need to
    make a determined flagger for the cases where the unshown + flagged around a cell equal it's
    number. May also want to have play* functions return when they did something so that the higher
    level logic in the outer loops can branch as needed for strats.
    '''

    return


def playRandomCell(g):
    '''
    Find and play a single cell using a completely naive random selection where all unshown and
    non-flagged cells are equally likely
    '''

    # find all playable cells
    playable = []
    for r in xrange(1, g.numRows + 1):
        for c in xrange(1, g.numCols + 1):
            if g.plays[r, c] != g.SHOW and g.displ[r, c] != g.FLAG:
                playable.append((r, c))

    # select on randomly
    (r, c) = random.choice(playable)

    # play it
    g.playShow(r, c)
    return


def playDeterminedCells(g):
    '''
    Find and play all cells whose mines are already completely determined (and showing the
    remaining neighbors is therefore safe)
    '''

    # find all determined cells
    playable = []
    for r in xrange(1, g.numRows + 1):
        for c in xrange(1, g.numCols + 1):
            if g.plays[r, c] == g.SHOW:
                numFlags = np.sum(g.getPlaysNeighborhood(r, c) == g.FLAG)
                if g.field[r, c] == numFlags:
                    playable.append((r, c))

    # play the remaining neighbors of each determined cell
    for (rCent, cCent) in playable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if g.plays[r, c] != g.FLAG and g.plays[r, c] != g.SHOW:
                    g.playShow(r, c)
    return
