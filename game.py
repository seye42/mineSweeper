import numpy as np
import random
import time


class GameOver(Exception):
    pass


class DisplaySymbols:
    # see https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

    # basic symbol set
    BLOCK = '\033[38;2;64;64;64m' + chr(888)
    FLAG  = '\033[38;2;204;0;0m' + chr(182)
    MINE  = '\033[38;2;255;178;102m' + 'X'
    NUMERALS = [' ',
                '\033[38;2;0;128;255m'   + '1',
                '\033[38;2;0;204;0m'     + '2',
                '\033[38;2;204;0;0m'     + '3',
                '\033[38;2;51;51;255m'   + '4',
                '\033[38;2;128;0;0m'     + '5',
                '\033[38;2;0;204;204m'   + '6',
                '\033[38;2;0;102;0m'     + '7',
                '\033[38;2;192;192;192m' + '8']

    # last play background highlight toggles
    PLAY  = '\033[48;2;110;110;110m'
    RESET = '\033[0m'


    def showSymbols(self):
        string = self.BLOCK + self.FLAG + self.MINE
        for n in self.NUMERALS:
            string += n
        print('Basic symbol set:')
        print(string + self.RESET)
        print('\nSymbols with last play background highlights:')
        print(self.PLAY + string + self.RESET)
        print('\nExample with single last play symbol:')
        print(self.MINE + self.PLAY + self.FLAG + self.RESET + self.NUMERALS[8])


class Game:
    # masks and constants
    NUM_MASK  = np.uint8(0x0F)
    MINE_MASK = np.uint8(0x10)
    FLAG_MASK = np.uint8(0x20)
    PLAY_MASK = np.uint8(0x40)
    SHOW_MASK = np.uint8(0x80)
    BORDER = np.uint8(9)  # normal cells cannot have more than 8 surrounding mines


    def __init__(self, numRows, numCols, numMines, randSeed=None, printSummary=False):
        # check that parameters are reasonable
        if numRows < 1 or numCols < 1:
            raise ValueError('invalid game size')
        if numMines < 0:
            raise ValueError('number of mines must be non-negative')
        if numMines > (numRows - 1) * (numCols - 1):
            # see https://minesweepergame.com/ranking-rules.php, this also guarantees that the first-play mine
            # relocation logic can find a non-mine space
            raise ValueError('too many mines (maximum is %d for this game size)' % (numRows - 1) * (numCols - 1))

        # register the parameters
        self.numRows = numRows
        self.numCols = numCols
        self.numMines = numMines
        self.randSeed = randSeed
        self.printSummary = printSummary
        self.startTime = time.time()

        # seed the random number generator (for repeatable games)
        random.seed(randSeed)

        # allocate the basic arrays
        self.field = np.zeros((numRows + 2, numCols + 2), dtype=np.uint8)
            # add virtual borders to simplify neighborhood-based logic near the edges

        # populate the field's mines
        mineIdx = random.sample(range(numRows * numCols), numMines)
        for idx in mineIdx:
            r = (idx // numCols) + 1  # +1 for virtual borders
            c = (idx %  numCols) + 1  # +1 for virtual borders
            self.setMine(r, c)

        # populate the field's numerical clues
        for r in range(1, numRows + 1):  # skip virtual borders
            for c in range(1, numCols + 1):  # skip virtual borders
                self.setNumber(r, c)

        # fill the virtual borders with a sentinal value to stop flood fill operations
        value = np.bitwise_or(self.BORDER, self.SHOW_MASK)
        self.field[0,  :].fill(value)
        self.field[-1, :].fill(value)
        self.field[:,  0].fill(value)
        self.field[:, -1].fill(value)

        # initialize counters and last play history
        self.numFlagPlays = 0
        self.numShowPlays = 0
        self.lastPlay = (0, 0)
        self.won = False

        # initialize cell sets
        self.validPlays = set()
        for r in range(1, numRows + 1):  # skip virtual borders
            for c in range(1, numCols + 1):  # skip virtual borders
                self.validPlays.add((r, c))
        self.shownCells = set()
        self.flaggedCells = set()


    def isMine(self, field):
        return np.bitwise_and(field, self.MINE_MASK).astype(bool)


    def setMine(self, r, c):
        self.field[r, c] = np.bitwise_and(self.field[r, c], ~self.NUM_MASK)
        self.field[r, c] = np.bitwise_or(self.field[r, c], self.MINE_MASK)


    def unsetMine(self, r, c):
        self.field[r, c] = np.bitwise_and(self.field[r, c], ~self.MINE_MASK)


    def isFlagged(self, field):
        return np.bitwise_and(field, self.FLAG_MASK).astype(bool)


    def setFlagged(self, r, c):
        self.field[r, c] = np.bitwise_or(self.field[r, c], self.FLAG_MASK)
        self.flaggedCells.add((r, c))


    def isPlayed(self, field):
        return np.bitwise_and(field, self.PLAY_MASK).astype(bool)


    def setPlayed(self, r, c):
        self.field[r, c] = np.bitwise_or(self.field[r, c], self.PLAY_MASK)


    def isShown(self, field):
        return np.bitwise_and(field, self.SHOW_MASK).astype(bool)


    def setShown(self, r, c):
        self.field[r, c] = np.bitwise_or(self.field[r, c], self.SHOW_MASK)
        self.shownCells.add((r, c))


    def isBorder(self, r, c):
        return np.bitwise_and(self.field[r, c], self.NUM_MASK) == self.BORDER


    def getNumber(self, field):
        return np.bitwise_and(field, self.NUM_MASK)


    def setNumber(self, r, c):
        if not self.isMine(self.field[r, c]) and not self.isBorder(r, c):
            # preserve the upper nibble in case flags have already been set
            upper = np.bitwise_and(self.field[r, c], ~self.NUM_MASK)

            # determine lower nibble based on neighborhood
            if r == 0 or r == self.numRows + 1 or c == 0 or c == self.numCols + 1:
                # part of virtual border
                lower = self.BORDER
            else:
                lower = np.sum(self.isMine(self.getFieldNeighborhood(r, c)))

            # combine
            self.field[r, c] = np.bitwise_or(upper, lower)


    def setNumberNeighborhood(self, rCent, cCent):
        for r in range(rCent - 1, rCent + 2):
            for c in range(cCent - 1, cCent + 2):
                self.setNumber(r, c)


    def getFieldNeighborhood(self, r, c):
        return self.field[r - 1:r + 2, c - 1:c + 2]


    def getFirstNonMineCell(self):
        # find the first non-mine cell in the raster sequence
        row = 0
        for r in range(1, self.numRows + 1):  # skip virtual borders
            for c in range(1, self.numCols + 1):  # skip virtual borders
                if not self.isMine(self.field[r, c]):
                    row = r
                    col = c
                    break
                    # this is guaranteed to occur to because Game's constructor checks that at
                    # least one mine-free space always exists
            if row > 0:
                break
        return (row, col)


    def getValidPlays(self):
        return self.validPlays


    def getFlaggedCells(self):
        return self.flaggedCells


    def getShownCells(self):
        return self.shownCells


    def flagCell(self, r, c):
        if r < 1 or r > self.numRows + 1 or c < 1 or c > self.numCols + 1:
            print('WARNING: out-of-bounds cell (%d, %d)' % (r, c))
            return
        if self.isFlagged(self.field[r, c]):  # cell has already been flagged
            print('WARNING: duplicate flag requested for already-flagged cell (%d, %d)' % (r, c))
            return
        if self.isPlayed(self.field[r, c]):  # cell has already been played (and shown)
            print('WARNING: flag requested for played/shown cell (%d, %d)' % (r, c))
            return
        self.numFlagPlays += 1
        self.setFlagged(r, c)
        self.validPlays.discard((r, c))
        self.checkVictoryConditions()


    def playCell(self, r, c):
        if r < 1 or r > self.numRows + 1 or c < 1 or c > self.numCols + 1:
            print('WARNING: out-of-bounds cell (%d, %d)' % (r, c))
            return
        if self.isPlayed(self.field[r, c]):  # cell has already been played
            print('WARNING: duplicate play requested for already-played cell (%d, %d)' % (r, c))
            return
        if self.isShown(self.field[r, c]):  # cell has already been shown
            print('WARNING: play requested for shown cell (%d, %d)' % (r, c))
            return
        self.lastPlay = (r, c)
        self.numShowPlays += 1
        self.setPlayed(r, c)
        self.setShown(r, c)
        self.validPlays.discard((r, c))
        if self.isMine(self.field[r, c]):
            if self.numShowPlays == 1:  # special case of cannot lose on first play
                # see https://web.archive.org/web/20180618103640/http://www.techuser.net/mineclick.html

                # determine the first free cell the mine will be relocated to
                (rRelo, cRelo) = self.getFirstNonMineCell()

                # update the mine flags
                self.unsetMine(r, c)
                self.setMine(rRelo, cRelo)

                # update the adjacency numbers in both the original and relocated neighborhoods
                self.setNumberNeighborhood(r, c)
                self.setNumberNeighborhood(rRelo, cRelo)
            else:  # not first play: selected a mine -> game over
                self.stopTime = time.time()
                self.elapsedTime = self.stopTime - self.startTime
                if self.printSummary:
                    self.printOutSummary()
                self.won = False
                raise GameOver(self.summarize())
        if self.getNumber(self.field[r, c]) == 0:  # empty cell -- expand
            self.floodFillPlay(r, c)
        self.checkVictoryConditions()


    def floodFillPlay(self, r, c):
        cells = set([(r, c)])
        while len(cells):
            # get current cell's position and upper and lower rows
            (r, cBeg) = cells.pop()
            rU = r - 1
            rD = r + 1

            # build the list of column indices for the row, spreading from the current cell
            cL = cBeg - 1
            while self.getNumber(self.field[r, cL]) == 0:
                cL -= 1

            cR = cBeg + 1
            while self.getNumber(self.field[r, cR]) == 0:
                cR += 1
                # while loops are safe because of the self.BORDER values in the first and last
                # columns of self.field
            cols = range(cL, cR + 1)

            # show the swept columns and add the cells above and below where needed
            for c in cols:
                self.setShown(r, c)
                self.validPlays.discard((r, c))
                num = self.getNumber(self.field[r, c])
                if num == 0 and not self.isShown(self.field[rU, c]):
                    cells.add((rU, c))
                if num == 0 and not self.isShown(self.field[rD, c]):
                    cells.add((rD, c))
                # first and last rows are safe because self.field is initialized to show the border


    def display(self):
        print('')
        s = DisplaySymbols()
        for r in range(1, self.numRows + 1):  # skip virtual borders
            string = ''
            for c in range(1, self.numCols + 1):  # skip virtual borders
                # define pre- and postfix strings for background highlighting of the last play
                if r == self.lastPlay[0] and c == self.lastPlay[1]:
                    prefix  = s.PLAY
                    postfix = s.RESET
                else:
                    prefix  = ''
                    postfix = ''

                # decode the field into the display symbol
                if self.isShown(self.field[r, c]):
                    if self.isMine(self.field[r,c]):
                        symbol = s.MINE
                    else:
                        symbol = s.NUMERALS[self.getNumber(self.field[r, c])]
                elif self.isFlagged(self.field[r, c]):
                    symbol = s.FLAG
                else:  # not shown
                    symbol = s.BLOCK
                string += prefix + symbol + postfix
            print(string + s.RESET)  # reset formatting for other stdout users


    def checkVictoryConditions(self):
        # check that all number cells are shown and all mines are flagged
        if len(self.validPlays) > 0:
            # still valid plays remaining
            return
        for r in range(1, self.numRows + 1):  # skip virtual borders
            for c in range(1, self.numCols + 1):  # skip virtual borders
                # TODO: drop the first clause of the compound?
                if (not self.isMine(self.field[r, c]) and not self.isShown(self.field[r, c])) or \
                   (self.isMine(self.field[r, c]) and not self.isFlagged(self.field[r, c])):
                    return  # not yet done
        self.stopTime = time.time()
        self.elapsedTime = self.stopTime - self.startTime
        if self.printSummary:
            self.printOutSummary()
        self.won = True
        raise GameOver(self.summarize())


    def summarize(self):
        d = {}
        d['numRows']      = self.numRows
        d['numCols']      = self.numCols
        d['numMines']     = self.numMines
        d['randSeed']     = self.randSeed
        d['numFlagPlays'] = self.numFlagPlays
        d['numShowPlays'] = self.numShowPlays
        d['lastPlay']     = self.lastPlay
        d['startTime']    = self.startTime
        d['stopTime']     = self.stopTime
        d['elapsedTime']  = self.elapsedTime
        d['won']          = self.won
        d['numCells']       = self.numRows * self.numCols
        d['numCellShown']   = np.sum(self.isShown(self.field[1:-1, 1:-1]))
        d['numCellFlagged'] = np.sum(self.isFlagged(self.field[1:-1, 1:-1]))
        d['numCellHidden']  = d['numCells'] - d['numCellShown'] - d['numCellFlagged']
        d['fractMines']     = float(self.numMines) / d['numCells']
        d['fractShown']     = float(d['numCellShown']) / d['numCells']
        d['fractFlagged']   = float(d['numCellFlagged']) / d['numCells']
        d['fractHidden']    = float(d['numCellHidden']) / d['numCells']
        return d


    def printOutSummary(self):
        self.display()
        d = self.summarize()
        print('%d x %d (%d cells) gameboard with %d mines (%0.1f%%)' \
              % (d['numRows'], d['numCols'], d['numCells'], d['numMines'], d['fractMines'] * 100.0))
        print('  cells shown:   %d (%0.1f%%)' % (d['numCellShown'], d['fractShown'] * 100.0))
        print('  cells flagged: %d (%0.1f%%)' % (d['numCellFlagged'], d['fractFlagged'] * 100.0))
        print('  cells hidden:  %d (%0.1f%%)' % (d['numCellHidden'], d['fractHidden'] * 100.0))
        print('  elapsed time:  %0.3f s' % d['elapsedTime'])