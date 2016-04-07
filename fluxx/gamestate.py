import sys
import random
import inspect

from itertools import cycle
from copy import deepcopy

from . import cards
from . import moves


class GameState:
	def __init__(self, players):
		self.players = players
		self.turniter = cycle(self.players)
		
		self.drawPile = []
		self.drawPile.extend(list(cards.DrawNCard(n) for n in range(2, 5)))
		self.drawPile.extend(list(cards.PlayNCard(n) for n in range(2, 5)))
		self.drawPile.extend(list(cards.HandLimitNCard(n) for n in range(1, 3)))
		#self.drawPile.extend(list(cards.DummyCard(n) for n in range(1, 11)))
		self.drawPile.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.KeeperCard) and c != cards.KeeperCard])
		self.drawPile.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.CreeperCard) and c != cards.CreeperCard])
		self.drawPile.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.GoalCard) and c != cards.GoalCard])
		self.drawPile.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.ActionCard) and c != cards.ActionCard])

		self.shuffleDrawPile()

		self.playersHands = {p:[] for p in self.players}
		self.playersTable = {p:[] for p in self.players}

		self.centerTable = []
		self.discardPile = []

		self.currentDrawLimit = 1
		self.currentPlayLimit = 1
		self.currentHandLimit = sys.maxsize

		self.actionResolvingMoves = []
		self.enforceHandLimitForOtherPlayersExcept = None
		self.creeperJustDrawn = False

		self.nextTurn()

	def getLegalMoves(self):
		if self.isFinished():
			return []

		if len(self.actionResolvingMoves) > 0:
			return self.actionResolvingMoves

		if self.enforceHandLimitForOtherPlayersExcept != None:
			m = [moves.DiscardMove(p, c) for p in self.players for c in self.playersHands[p] if p != self.enforceHandLimitForOtherPlayersExcept and len(self.playersHands[p]) > self.currentHandLimit]
			if m:
				return m
			else:
				self.enforceHandLimitForOtherPlayersExcept = None

		# Iterate over all possible moves and return which is allowed
		m = []
		m.extend([m for m in [moves.DrawMove(p) for p in self.players] if m.isLegal(self)])
		m.extend([m for m in [moves.PlayMove(p, c) for p in self.players for c in self.playersHands[p]]
				if m.isLegal(self)])
		m.extend([m for m in [moves.DiscardMove(p, c) for p in self.players for c in self.playersHands[p]]
				if m.isLegal(self)])
		m.extend([m for m in [moves.EndTurnMove(p) for p in self.players] if m.isLegal(self)])
		return m

	def isFinished(self):
		return bool(self.getWinningPlayers())

	def getWinningPlayers(self):
		winningPlayers = []
		for p,h in self.playersTable.items():
			for c in self.centerTable:
				if isinstance(c, cards.GoalCard):
					if c.isFulfilled(h):
						winningPlayers.append(p)

		return winningPlayers

	def nextTurn(self):
		self.turn = next(self.turniter)
		self.usedDraws = 0
		self.usedPlays = 0

	def performMove(self, move):
		move.raiseIfIllegalMove(self)
		nextState = deepcopy(self)
		move.perform(nextState)
		return nextState

	def shuffleDrawPile(self):
		random.shuffle(self.drawPile)

	def drawFromDrawPile(self):
		self.usedDraws += 1
		card = self.drawPile.pop(0)
		
		if len(self.drawPile) == 0 and len(self.discardPile) > 0:
			self.shuffleDiscardIntoDrawPile()

		return card

	def putInDiscardPile(self, card):
		self.discardPile.append(card)
		if len(self.drawPile) == 0:
			self.shuffleDiscardIntoDrawPile()

	def shuffleDiscardIntoDrawPile(self):
		self.drawPile = self.discardPile
		self.discardPile = []
		self.shuffleDrawPile()

	def playCard(self, player, card):
		self.playersHands[player].remove(card)
		if not isinstance(card, cards.CreeperCard):
			self.usedPlays += 1
		card.play(self, player)

	def discardFromTableCenter(self, cards):
		for c in cards:
			self.centerTable.remove(c)
			self.putInDiscardPile(c)

	def discardFromHand(self, player, card):
		self.playersHands[player].remove(card)
		self.putInDiscardPile(card)

	def discardFromPlayersCards(self, player, card):
		self.playersTable[player].remove(card)
		self.putInDiscardPile(card)		

	def putOnTableCenter(self, card):
		self.centerTable.append(card)

	def actionResolving(self, card, moves):
		self.actionResolvingMoves = moves

	def actionIsResolved(self):
		self.actionResolvingMoves = []

	def enforceHandLimitForOthers(self, player):
		self.enforceHandLimitForOtherPlayersExcept = player

	@property
	def remainingPlays(self):
		return max(0, self.currentPlayLimit - self.usedPlays)
	
	@property
	def remainingDraws(self):
		return max(0, self.currentDrawLimit - self.usedDraws)


	def countCards(self):
		c = len(self.drawPile)
		c += len(self.discardPile)
		c += len(self.centerTable)
		for h in self.playersHands.values():
			c += len(h)
		for t in self.playersTable.values():
			c += len(t)
		return c

	def printState(self):
		print("Current turn is: {0}".format(self.turn.name))
		print("Remaining draws: {0}, Remaining plays: {1}".format(self.remainingDraws, self.remainingPlays))
		print("Draw pile: {0}". format(list(c.name for c in self.drawPile)))
		print("Discard pile: {0}". format(list(c.name for c in self.discardPile)))
		print("Center Table: {0}". format(list(c.name for c in self.centerTable)))
		if self.enforceHandLimitForOtherPlayersExcept != None:
			print("Enforcing hand limit for all players except: {0}".format(self.enforceHandLimitForOtherPlayersExcept.name))
		if self.creeperJustDrawn:
			print("Creeper just drawn")
		for i,p in enumerate(self.players):
			print("Player {0}'s hand: {1}"
				.format(
					i+1,
					list(c.name for c in self.playersHands[p])))
			print("Player {0}'s table cards: {1}"
				.format(
					i+1,
					list(c.name for c in self.playersTable[p])))
