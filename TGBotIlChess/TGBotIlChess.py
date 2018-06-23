from chess import *
from chessGUI import *

g = Chess()
print(g)

g.state[1, 0].moveAvailable([3, 2])
g.state[3, 2].moveAvailable([3, 2])

gui = ilChessGUI(g)
gui.run()