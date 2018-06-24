#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame, sys
import numpy as np

class ilChessPiece(object):
	""" """

	def __init__(self, board, pc, rect):
		self.board = board
		self.piece = pc
		self.rect = rect
		
		self.sprite = None
		if pc is not None: self.initPiece()
		
		self.moveAvail = False
		self.chosen = False
		
	def initPiece(self, pc = None):
		if pc is not None: self.piece = pc

		self.sprite = pygame.image.load('img/' + ('w' if self.piece.side == 1 else 'b') + (self.piece.letter[-1]) + '.png')
		rect = self.sprite.get_rect()

		rect.topleft = self.rect.topleft
		rect.size = self.rect.size

		self.rect = rect

		self.sprite = pygame.transform.scale(self.sprite, self.rect.size)

	def reInitNone(self):
		self.sprite = None
		self.piece = None

	def mouseOver(self, pos):
		return self.rect.collidepoint(pos)


class ilChessBoard(object):
	""" """

	def __init__(self, gui, game, rect):
		self.gui = gui
		self.game = game
		self.rect = rect
		self.rect.height = self.rect.width

		self.pcWidth = self.rect.width / 8

		self.pcs = np.empty(game.state.shape, dtype=object)
		for i, r in enumerate(game.state):
			for j, p in enumerate(r):
				self.pcs[i, j] = ilChessPiece(self, p, pygame.Rect(self.rect.left + self.pcWidth * j, self.rect.bottom - self.pcWidth * (i + 1), self.pcWidth, self.pcWidth))

		self.bgColorWhite = (245, 245, 200)
		self.bgColorBlack = (170, 170, 120)
		self.bgColorChosenWhite = (245, 245, 135)
		self.bgColorChosenBlack = (200, 200, 90)
		self.bgColorMoveWhite = (170, 225, 150)
		self.bgColorMoveBlack = (118, 156, 90)

		self.chosenPos = None

	def render(self):
		screen = self.gui.screen
		
		# Draw each cell of board
		for i, r in enumerate(self.pcs):
			for j, p in enumerate(r):
				# Choose background color
				if p.chosen: bgColor = self.bgColorChosenBlack if (i + j) % 2 == 0 else self.bgColorChosenWhite
				elif p.moveAvail: bgColor = self.bgColorMoveBlack if (i + j) % 2 == 0 else self.bgColorMoveWhite
				else: bgColor = self.bgColorBlack if (i + j) % 2 == 0 else self.bgColorWhite

				pygame.draw.rect(screen, bgColor, \
					(self.rect.left + self.pcWidth * j, self.rect.bottom - self.pcWidth * (i + 1), self.pcWidth, self.pcWidth), 0)
				
				# Draw piece if there is any in current cell
				if p.sprite is not None:
					screen.blit(p.sprite, p.rect)

		# Draw vertical and horizontal numbers
		for i in range(8):
			acctstr = str(i)
			acctfont = pygame.font.Font(None, 24)
			accttext = acctfont.render(acctstr, True, (0, 0, 0))
			acctw, accth = acctfont.size(acctstr)
			screen.blit(accttext, accttext.get_rect().move(self.rect.left + self.pcWidth * i + (self.pcWidth - acctw) / 2, self.rect.bottom + 2))
			screen.blit(accttext, accttext.get_rect().move(self.rect.left - acctw - 2, self.rect.bottom - self.pcWidth * (i + 1) + (self.pcWidth - accth) / 2))

		# Draw moves count
		mcnt_str = 'Moves: ' + str(self.game.movesCount)
		mcnt_font = pygame.font.Font(None, 24)
		mcnt_txt = mcnt_font.render(mcnt_str, True, (0, 0, 0))
		screen.blit(mcnt_txt, mcnt_txt.get_rect().move(self.rect.left, self.rect.top - mcnt_font.size(mcnt_str)[1]))

	# Set .moveAvail and .chose vars in all pieces according to available moves
	def paintAvailableMoves(self, curPiece = None, amoves = np.empty(0)):
		amoves = np.empty(0) if amoves is None else amoves
		for i in range(8):
			for j in range(8):
				self.pcs[i][j].moveAvail = False
				self.pcs[i][j].chosen = False
		if curPiece is not None and self.chosenPos is not curPiece.pos:
			for m in amoves:
				self.pcs[m[0]][m[1]].moveAvail = True
			self.pcs[curPiece.pos[0], curPiece.pos[1]].chosen = True
			self.chosenPos = curPiece.pos
		else:
			self.chosenPos = None

	def onMouseDown(self, event):
		for i, r in enumerate(self.pcs):
			for j, p in enumerate(r):
				if p.mouseOver(event.pos):
					if self.chosenPos is not None:
						# attack
						if self.game.move(self.chosenPos, [i, j]):
							self.pcs[i][j].initPiece(self.pcs[self.chosenPos[0], self.chosenPos[1]].piece)
							self.pcs[self.chosenPos[0], self.chosenPos[1]].reInitNone()
							self.paintAvailableMoves()
							#if self.game.isCheck(): sys.exit()
							break
					if p.piece is not None and p.piece.side == self.game.turn:
						if p.piece is None: self.paintAvailableMoves()
						else: self.paintAvailableMoves(p.piece, p.piece.getAvailableMoves())
					else:
						self.paintAvailableMoves()

	def onMouseUp(self, event):
		pass

class ilChessGUI(object):
	""" """

	def __init__(self, game):
		pygame.init()        
		pygame.display.set_caption('ilChess GUI')

		self.size = self.width, self.height = (800, 600)
		self.screen = pygame.display.set_mode(self.size)

		self.clock = pygame.time.Clock()
		pygame.key.set_repeat(1,1)

		self.board = ilChessBoard(self, game, pygame.Rect(120, 20, 560, 560))

		self.bgcolor = (255, 250, 245)
		
	def eventHandlerLoop(self):
		# process key presses
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.board.onMouseDown(event)
			if event.type == pygame.MOUSEBUTTONUP:
				self.board.onMouseUp(event)

	def run(self):
		while 1:
			self.clock.tick(60)
			self.eventHandlerLoop()
			

			########## <RENDER> ##########
			self.screen.fill(self.bgcolor)

			self.board.render()

			pygame.display.flip()
			########## </RENDER> #########