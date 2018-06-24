from chess import *
from chessGUI import *

g = Chess()
print(g)

gui = ilChessGUI(g)
gui.run()