import numpy as np
import random


class Win(Exception):
    pass


class Lose(Exception):
    pass


class Game:
    # constants
    MINE = np.uint8(255)
    STOP = np.uint8(9)  # normal cell cannot have more than 8 surrounding mines
    HIDE = np.uint8(0)
    SHOW = np.uint8(1)
    FLAG = np.uint8(2)


    def __init__(self, numRows, numCols, numMines, randSeed=None):

        # register the parameters
        self.numRows = numRows
        self.numCols = numCols
        self.numMines = numMines

        # seed the random number generator (for repeatable games)
        random.seed(randSeed)

        # allocate the basic arrays
        self.field = np.zeros((numRows + 2, numCols + 2), dtype=np.uint8)
        self.plays = np.zeros((numRows + 2, numCols + 2), dtype=np.uint8)
        self.displ = np.zeros((numRows + 2, numCols + 2), dtype=str)
            # add virtual borders to simplify neighborhood-based logic near the edges

        # populate the field's mines
        mineIdx = random.sample(xrange(self.numRows * self.numCols), numMines)
        for idx in mineIdx:
            r = idx / self.numCols + 1  # +1 for virtual borders
            c = idx % self.numCols + 1  # +1 for virtual borders
            self.field[r, c] = self.MINE

        # populate the field's numerical clues
        for r in xrange(1, self.numRows + 1):  # skip virtual borders
            for c in xrange(1, self.numCols + 1):  # skip virtual borders
                if self.field[r, c] != self.MINE:
                    self.field[r, c] = np.sum(self.getFieldNeighborhood(r, c) == self.MINE)

        # fill the virtual borders with a sentinal value to stop flood fill operations
        self.field[0,  :].fill(self.STOP)
        self.field[-1, :].fill(self.STOP)
        self.field[:,  0].fill(self.STOP)
        self.field[:, -1].fill(self.STOP)

        # initialize plays
        self.plays.fill(self.HIDE)
        self.plays[0,  :].fill(self.SHOW)
        self.plays[-1, :].fill(self.SHOW)
        self.plays[:,  0].fill(self.SHOW)
        self.plays[:, -1].fill(self.SHOW)

        # initialize the display array
        self.displ.fill('=')
        self.displ[0,  :].fill('-')
        self.displ[-1, :].fill('-')
        self.displ[:,  0].fill('|')
        self.displ[:, -1].fill('|')

        # initialize counters
        self.numFlagPlays = 0
        self.numShowPlays = 0


    def getFieldNeighborhood(self, r, c):
        return self.field[r - 1:r + 2, c - 1:c + 2]


    def getPlaysNeighborhood(self, r, c):
        return self.plays[r - 1:r + 2, c - 1:c + 2]


    def playFlag(self, r, c):
        if r < 1 or r > self.numRows + 1 or c < 1 or c > self.numCols + 1:
            print('WARNING: out-of-bounds cell (%d, %d)' % (r, c))
            return
        if self.plays[r, c] == self.SHOW:  # cell has already been shown
            print('WARNING: flag requested for shown cell (%d, %d)' % (r, c))
            return
        self.plays[r, c] = self.FLAG
        self.displ[r, c] = '?'
        self.numFlagPlays += 1
        self.checkVictoryConditions()


    def playShow(self, r, c):
        if r < 1 or r > self.numRows + 1 or c < 1 or c > self.numCols + 1:
            print('WARNING: out-of-bounds cell (%d, %d)' % (r, c))
            return
        if self.plays[r, c] == self.SHOW:  # cell has already been shown
            print('WARNING: duplicate show requested for cell (%d, %d)' % (r, c))
            return
        self.updateShow(r, c)
        if self.field[r, c] == 0:
            self.floodFillPlay(r, c)
        self.numShowPlays += 1
        self.checkVictoryConditions()


    def updateShow(self, r, c):
        self.plays[r, c] = self.SHOW
        if self.field[r, c] == self.MINE:  # game over
            self.displ[r, c] = 'x'
            raise Lose
        elif self.field[r, c] == 0:
            self.displ[r, c] = ' '
        elif self.field[r, c] != self.STOP:  # mine count of 1-8
            self.displ[r, c] = str(self.field[r, c])


    def floodFillPlay(self, r, c):
        cells = set([(r, c)])
        while len(cells):
            # get current cell's position and upper and lower rows
            (r, cBeg) = cells.pop()
            rU = r - 1
            rD = r + 1

            # build the list of column indices for the row, spreading from the current cell
            cL = cBeg - 1
            while self.field[r, cL] == 0:
                cL -= 1

            cR = cBeg + 1
            while self.field[r, cR] == 0:
                cR += 1
                # while loops are safe because of the self.STOP values in the first and last
                # columns of self.field
            cols = range(cL, cR + 1)

            # show the swept columns and add the cells above and below where needed
            for c in cols:
                self.updateShow(r, c)
                if self.field[r, c] == 0 and self.plays[rU, c] == self.HIDE:
                    cells.add((rU, c))
                if self.field[r, c] == 0 and self.plays[rD, c] == self.HIDE:
                    cells.add((rD, c))
                # first and last rows are safe because self.plays is initialized to self.SHOW


    def display(self):
        print('-'.join(self.displ[0, :].tostring()))
        for r in xrange(1, self.numRows + 1):  # skip virtual borders
            print(' '.join(self.displ[r, :].tostring()))
        print('-'.join(self.displ[-1, :].tostring()))


    def summarize(self):
        numCellShown = np.sum(self.plays == self.SHOW) - 2 * self.numCols - 2 * self.numRows - 4
            # correct for virtual borders
        numCellFlag = np.sum(self.plays == self.FLAG)
        numCellHidden = self.numRows * self.numCols - numCellShown
        return (numCellShown, numCellHidden, numCellFlag)

    def checkVictoryConditions(self):
        # check that all number cells are shown and all mines are flagged
        for r in xrange(1, self.numRows + 1):  # skip virtual borders
            for c in xrange(1, self.numCols + 1):  # skip virtual borders
                if (self.field[r, c] != self.MINE and self.plays[r, c] != self.SHOW) or \
                   (self.field[r, c] == self.MINE and self.plays[r, c] != self.FLAG):
                    return  # not done yet
        raise Win
