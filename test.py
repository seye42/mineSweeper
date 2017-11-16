from game import *
from player import *

g = Game(8, 8, 10, 3)
playRandomCell(g)
g.display()
doAllDetermined(g)
g.display()
