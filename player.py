import numpy as np
import random


def brutePlayer(g):
    while True:
        playRandomCell(g)


def basicPlayer(g):
    while True:
        playRandomCell(g)
        doAllDetermined(g)


def patternPlayer(g):
    while True:
        playRandomCell(g)
        doAllDetermined(g)

        # 1-2-x pattern
        # 1-1-x pattern


def playRandomCell(g):
    '''
    Find and play a single cell using a completely naive random selection where all unshown and
    non-flagged cells are equally likely
    '''

    # get all playable cells (non-shown, non-flagged, and non-virtual border cells)
    plays = g.getValidPlays()

    # select one randomly
    (r, c) = random.choice(tuple(plays))

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
    shownCells = g.getShownCells()
    playable = []
    for (r, c) in shownCells:
        neigh = g.getFieldNeighborhood(r, c)
        numFlagged = np.sum(g.isFlagged(neigh))
        numHidden = np.sum(~g.isShown(neigh))
        if g.getNumber(g.field[r, c]) == numFlagged and numHidden > 0:
            playable.append((r, c))

    # play the remaining neighbors of each determined cell
    played = False
    validPlays = g.getValidPlays()
    for (rCent, cCent) in playable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if (r, c) in validPlays:  # TODO: replace with some sort of isValidPlay(r, c)?
                    played = True
                    g.playCell(r, c)

    return played


def flagDeterminedCells(g):
    '''
    Find and flag all cells that are completely determined mines (and are therefore safe)
    '''

    # find all determined cells
    shownCells = g.getShownCells()
    flaggable = []
    for (r, c) in shownCells:
        neigh = g.getFieldNeighborhood(r, c)
        numFlagged = np.sum(g.isFlagged(neigh))
        numHidden = np.sum(~g.isShown(neigh) & ~g.isFlagged(neigh))
        if g.getNumber(g.field[r, c]) == numFlagged + numHidden and numHidden > 0:
            flaggable.append((r, c))

    # flag the remaining neighbors of each determined cell
    flagged = False
    validPlays = g.getValidPlays()
    for (rCent, cCent) in flaggable:
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                if (r, c) in validPlays:
                    flagged = True
                    g.flagCell(r, c)

    return flagged