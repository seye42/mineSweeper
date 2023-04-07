from game import *
from player import *


g = Game(8, 8, 10, None)
playRandomCell(g)
g.display()
doAllDetermined(g)
g.display()
playRandomCell(g)
g.display()

