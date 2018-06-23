﻿#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
import abc
import operator

class Piece(object):
	""" """

	def __init__(self, game, side, pos):
		self.game = game
		self.side = side
		self.pos = pos
		self.history = []
		self.value = -1

	@abc.abstractmethod
	def getAvailableMoves(self):
		""" """
		raise NotImplementedError

	@abc.abstractmethod
	def checkAvailableMoves(self, moves):
		""" """
		raise NotImplementedError

	def moveAvailable(self, to):
		""" Returns 'True' if move is available and 'False' otherwise """
		moves = self.getAvailableMoves()
		print(moves)
		if to in moves: return True
		return False
	
	@staticmethod
	def isMoveNotOuter(m):
		return m[0] >= 0 and m[0] < 8 and m[1] >= 0 and m[1] < 8

	def removeOuterAndAlliesOccupied(self, moves):
		""" Removes all invalid moves: out of board and occupied by ally pieces """
		return [m for m in moves if Piece.isMoveNotOuter(m)\
		   and (self.game.state[m[0], m[1]] is None or np.sign(self.game.state[m[0], m[1]].side) != self.side)]
	
	def traverse(self, cnt, moves, diry, dirx):
		""" Propagates lines from self.pos in (diry, dirx) directions (Used for bishops, rooks and queens) """
		y = self.pos[0] if diry < 0 else (7 - self.pos[0] if diry > 0 else 8)
		x = self.pos[1] if dirx < 0 else (7 - self.pos[1] if dirx > 0 else 8)
		rng = range(1, min(x, y) + 1)
		for i in rng:
			p = [self.pos[0] + diry * i, self.pos[1] + dirx * i]
			if self.game.state[p[0], p[1]] is None:
				moves[cnt[0]] = p
				cnt[0] += 1
			else:
				if np.sign(self.game.state[p[0], p[1]].side) != np.sign(self.side):
					moves[cnt[0]] = p
					cnt[0] += 1
				return
		return

	def traverseRook(self):
		""" Propogates lines in 'plus' directions """
		moves = np.empty(14, dtype=object)
		cnt = [0]
		Piece.traverse(self, cnt, moves, -1, 0)
		Piece.traverse(self, cnt, moves, 1, 0)
		Piece.traverse(self, cnt, moves, 0, -1)
		Piece.traverse(self, cnt, moves, 0, 1)
		return moves[:cnt[0]]

	def traverseBishop(self):
		""" Propogates lines in 'cross' directions """
		moves = np.empty(14, dtype=object)
		cnt = [0]
		Piece.traverse(self, cnt, moves, -1, -1)
		Piece.traverse(self, cnt, moves, -1, 1)
		Piece.traverse(self, cnt, moves, 1, -1)
		Piece.traverse(self, cnt, moves, 1, 1)
		return moves[:cnt[0]]

	def __str__(self):
		return '{}({}, {}){}'.format(self.symbol, self.pos[0], self.pos[1], 'W' if self.side == 1 else 'B')

class King(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = np.Infinity
		self.symbol = {1: '♔', -1: '♚'}
		self.letter = {1: 'K', -1: 'k'}
	
	def getAvailableMoves(self):
		moves = [list(map(operator.add, m, self.pos)) for m in [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]]
		moves = super().removeOuterAndAlliesOccupied(moves)
		# TODO: Castling! (with no possibility to castle when field is under attack)
		# TODO: check for king-attack
		return moves
	
class Knight(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = 3
		self.symbol = {1: '♘', -1: '♞'}
		self.letter = {1: 'N', -1: 'n'}
	
	def getAvailableMoves(self):
		moves = [list(map(operator.add, m, self.pos)) for m in [[-2, 1], [-1, 2], [1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1]]]
		moves = super().removeOuterAndAlliesOccupied(moves)
		# TODO: check for king-attack
		return moves
	
class Rook(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = 5
		self.symbol = {1: '♖', -1: '♜'}
		self.letter = {1: 'R', -1: 'r'}
	
	def getAvailableMoves(self):
		moves = super().traverseRook()
		
		# TODO: Castling
		# TODO: check for king-attack
		return moves
	
class Bishop(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = 3.5
		self.symbol = {1: '♗', -1: '♝'}
		self.letter = {1: 'B', -1: 'b'}
	
	def getAvailableMoves(self):
		moves = super().traverseBishop()
		
		# TODO: Castling
		# TODO: check for king-attack
		return moves

class Queen(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = 9.5
		self.symbol = {1: '♕', -1: '♛'}
		self.letter = {1: 'Q', -1: 'q'}
	
	def getAvailableMoves(self):
		moves = np.concatenate((super().traverseRook(), super().traverseBishop()))
		
		# TODO: check for king-attack
		return moves
	
class Pawn(Piece):
	""" """

	def __init__(self, game, side, pos):
		super().__init__(game, side, pos)
		self.value = 1
		self.symbol = {1: '♙', -1: '♟'}
		self.letter = {1: 'P', -1: 'p'}
	
	def getAvailableMoves(self):
		def moveTakePawn(p, cnt):
			if not Piece.isMoveNotOuter(p): return 0
			if not self.game.state[p[0], p[1]] is None:
				if np.sign(self.game.state[p[0], p[1]].side) != np.sign(self.side):
					moves[cnt] = p
					return 1
			return 0

		moves = np.empty(3, dtype=object)

		cnt = 0
		# Pawn Takes by diagonal
		cnt += moveTakePawn([self.pos[0] + self.side, self.pos[1] - 1], cnt)
		cnt += moveTakePawn([self.pos[0] + self.side, self.pos[1] + 1], cnt)
		
		p = [self.pos[0] + self.side, self.pos[1]]
		if self.game.state[p[0], p[1]] is None:
			# Simple move forward
			moves[cnt] = p
			cnt += 1

			# Move 2 steps forward
			p2 = [p[0] + self.side, p[1]]
			if self.pos[0] % 5 == 1:
				if self.game.state[p2[0], p2[1]] is None:
					moves[cnt] = p2
					cnt += 1
		
		moves = moves[:cnt]
		
		# TODO: check for ability to take en passant
		# TODO: check for king-attack
		return moves


class Chess(object):
	""" Chess class """

	def __init__(self):
		self.state = np.empty((8, 8), dtype=object)
		
		self.state[0, 4] = King(self, 1, [0, 4])
		self.state[7, 4] = King(self, -1, [7, 4])
		
		self.state[0, 1] = Knight(self, 1, [0, 1])
		self.state[0, 6] = Knight(self, 1, [0, 6])
		self.state[7, 1] = Knight(self, -1, [7, 1])
		self.state[7, 6] = Knight(self, -1, [7, 6])

		self.state[0, 0] = Rook(self, 1, [0, 0])
		self.state[0, 7] = Rook(self, 1, [0, 7])
		self.state[7, 0] = Rook(self, -1, [7, 0])
		self.state[7, 7] = Rook(self, -1, [7, 7])

		self.state[0, 2] = Bishop(self, 1, [0, 2])
		self.state[0, 5] = Bishop(self, 1, [0, 5])
		self.state[7, 2] = Bishop(self, -1, [7, 2])
		self.state[7, 5] = Bishop(self, -1, [7, 5])

		self.state[0, 3] = Queen(self, 1, [0, 3])
		self.state[7, 3] = Queen(self, -1, [7, 3])

		for i in range(8):
			self.state[1, i] = Pawn(self, 1, [1, i])
			self.state[6, i] = Pawn(self, -1, [6, i])
		
		# Debug
		self.state[5, 0] = Bishop(self, -1, [5, 0])
		self.state[2, 3] = Knight(self, 1, [2, 3])
		self.state[3, 7] = Rook(self, 1, [3, 7])
		self.state[3, 2] = Queen(self, 1, [3, 2])

	# Function with all check for availability of the move
	def move(self, fr, to):
		stFr = self.state[fr[0]][fr[1]]
		if stFr is None: return False

		amoves = self.state[fr[0]][fr[1]].getAvailableMoves()
		avail = False
		for m in amoves:
			if m[0] == to[0] and m[1] == to[1]:
				avail = True
				break
		if not avail: return False
		
		self.state[to[0]][to[1]] = self.state[fr[0]][fr[1]]
		self.state[to[0]][to[1]].pos = to
		self.state[fr[0]][fr[1]] = None
		return True

	def __str__(self):
		res = ''
		for ri, r in enumerate(reversed(self.state)):
			res += str(8 - ri) + '   '
			for ci, i in enumerate(r):
				res += (' ' if i is None else i.letter[i.side]) + ' '
			res += '\n'
		res += '\n    '
		for i in range(8):
			res += chr(65 + i) + ' '
		return res