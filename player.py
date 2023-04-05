import numpy as np
import random


'''
TODO: Think about what auxiliary lists make sense to build in to Game so that so much looping
isn't required here. Maybe that's shown and flagged lists or something similar.
'''


def playRandomCell(g):
    '''
    Find and play a single cell using a completely naive random selection where all unshown and
    non-flagged cells are equally likely
    '''

    # find all playable cells
    playable = []
    for r in range(1, g.numRows + 1):
        for c in range(1, g.numCols + 1):
            if g.plays[r, c] != g.SHOW and g.displ[r, c] != g.FLAG:
                playable.append((r, c))

    # select on randomly
    (r, c) = random.choice(playable)

    # play it
    g.playShow(r, c)
    return


def doAllDetermined(g):
    updated = True
    while updated:
        flagRet = flagDeterminedCells(g)
        playRet = playDeterminedCells(g)
        updated = playRet or flagRet

    return


def playDeterminedCells(g):
    '''
    Find and play all cells whose mines are already completely determined (and showing the
    remaining neighbors is therefore safe)
    '''

    # find all determined cells
    playable = []
    for r in range(1, g.numRows + 1):
        for c in range(1, g.numCols + 1):
            if g.plays[r, c] == g.SHOW:
                neigh = g.getPlaysNeighborhood(r, c)
                numFlags = np.sum(neigh == g.FLAG)
                numHidden = np.sum(neigh == g.HIDE)
                if g.field[r, c] == numFlags and numHidden > 0:
                    playable.append((r, c))

    # play the remaining neighbors of each determined cell
    for (rCent, cCent) in playable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if g.plays[r, c] != g.FLAG and g.plays[r, c] != g.SHOW:
                    g.playShow(r, c)

    return len(playable) > 0


def flagDeterminedCells(g):
    '''
    Find and flag all cells that are completely determined mines (and are therefore safe)
    '''

    # find all determined cells
    flaggable = []
    for r in range(1, g.numRows + 1):
        for c in range(1, g.numCols + 1):
            if g.plays[r, c] == g.SHOW:
                neigh = g.getPlaysNeighborhood(r, c)
                numFlags = np.sum(neigh == g.FLAG)
                numHidden = np.sum(neigh == g.HIDE)
                if g.field[r, c] == numFlags + numHidden and numHidden > 0:
                    flaggable.append((r, c))

    # play the remaining neighbors of each determined cell
    for (rCent, cCent) in flaggable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if g.plays[r, c] == g.HIDE:
                    g.playFlag(r, c)

    return len(flaggable) > 0
