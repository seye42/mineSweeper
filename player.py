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

    # get all playable cells (non-shown, non-flagged, and non-virtual border cells)
    playable = g.getPlayable()

    # select on randomly
    (r, c) = random.choice(playable)

    # play it
    g.playCell(r, c)
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
            if g.isShown(g.field[r, c]):
                neigh = g.getFieldNeighborhood(r, c)
                numFlagged = np.sum(g.isFlagged(neigh))
                numHidden = np.sum(~g.isShown(neigh))
                if g.getNumber(g.field[r, c]) == numFlagged and numHidden > 0:
                    playable.append((r, c))

    # play the remaining neighbors of each determined cell
    played = False
    for (rCent, cCent) in playable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if not g.isFlagged(g.field[r, c]) and not g.isShown(g.field[r, c]):
                    played = True
                    g.playCell(r, c)

    return played


def flagDeterminedCells(g):
    '''
    Find and flag all cells that are completely determined mines (and are therefore safe)
    '''

    # find all determined cells
    flaggable = []
    for r in range(1, g.numRows + 1):
        for c in range(1, g.numCols + 1):
            if g.isShown(g.field[r, c]):
                neigh = g.getFieldNeighborhood(r, c)
                numFlagged = np.sum(g.isFlagged(neigh))
                numHidden = np.sum(~g.isShown(neigh) & ~g.isFlagged(neigh))
                if g.getNumber(g.field[r, c]) == numFlagged + numHidden and numHidden > 0:
                    flaggable.append((r, c))

    # play the remaining neighbors of each determined cell
    flagged = False
    for (rCent, cCent) in flaggable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if not g.isFlagged(g.field[r, c]) and not g.isShown(g.field[r, c]):
                    flagged = True
                    g.flagCell(r, c)

    return flagged