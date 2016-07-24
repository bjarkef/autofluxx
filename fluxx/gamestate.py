import binascii
import inspect
import random
import pickle
import lzma
import sys
import re

from itertools import cycle
from copy import deepcopy

from . import cards
from . import moves


class GameState:

	@staticmethod
	def createFromHumanReadableString(string):		
		deck = GameState.createFullDeck()
		
		statedata = eval("{{{}}}".format(re.sub(r"([a-zA-Z]\w*)",r"'\1'", string)))
		players = statedata['P']
		draws = statedata['D']
		plays = statedata['L']
		
		hand = []
		for string_card in statedata['H']:
			for card in deck[:]:
				if card.shortName().startswith(string_card):
					hand.append(card)
					deck.remove(card)
		
		table = []
		for string_card in statedata['T']:
			for card in deck[:]:
				if card.shortName().startswith(string_card):
					table.append(card)
					deck.remove(card)

		center = []
		for string_card in statedata['C']:
			for card in deck[:]:
				if card.shortName().startswith(string_card):
					center.append(card)
					deck.remove(card)

		#print("Players: {}".format(players))
		#print("Hand: {}".format(hand))
		#print("Table: {}".format(table))
		#print("Center: {}".format(center))

		return GameState(players, hand, table, center, draws, plays)

	@staticmethod
	def createFullDeck(without=[]):
		deck = []
		deck.extend(list(cards.DrawNCard(n) for n in range(2, 5)))
		deck.extend(list(cards.PlayNCard(n) for n in range(2, 5)))
		deck.extend(list(cards.HandLimitNCard(n) for n in range(1, 3)))
		deck.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.KeeperCard) and c != cards.KeeperCard])
		deck.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.CreeperCard) and c != cards.CreeperCard])
		deck.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.GoalCard) and c != cards.GoalCard])
		deck.extend([c() for c in cards.__dict__.values() if inspect.isclass(c) and issubclass(c, cards.ActionCard) and c != cards.ActionCard])

		for c in without:
			deck.remove(c)

		return deck

	def __init__(self, num_players, hand=[], table=[], center=[], draws=0, plays=0):
		self.completeinformation = False

		self.num_players = num_players
		self.players = list(range(num_players))
		self.turniter = cycle(self.players)
		
		self.drawPile = None

		self.playersHands = {p:[] for p in self.players}
		self.playersTable = {p:[] for p in self.players}

		self.playersHands[0] = hand
		self.playersTable[0] = table
		self.centerTable = center

		self.discardPile = []

		self.currentDrawLimit = 1
		self.currentPlayLimit = 1
		self.currentHandLimit = sys.maxsize

		self.actionResolvingMoves = []
		self.enforceHandLimitForOtherPlayersExcept = None
		self.creeperJustDrawn = False

		self.nextTurn()

		self.usedPlays = plays
		self.usedDraws = draws

		for c in self.centerTable:
			if isinstance(c, cards.RuleCard):
				c.applyRule(self)

	def randomInformation(self):
		copy = deepcopy(self)
		without = []
		without.extend(copy.playersHands[self.turn])
		without.extend(copy.playersTable[self.turn])
		without.extend(copy.centerTable)
		copy.drawPile = GameState.createFullDeck(without)
		copy.shuffleDrawPile()
		copy.completeinformation = True

		return copy

	def nextTurn(self):
		self.turn = next(self.turniter)
		self.usedDraws = 0
		self.usedPlays = 0

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

		if self.creeperJustDrawn:
			m = [moves.PlayMove(self.turn, c) for c in self.playersHands[self.turn] if c.isCreeper()]
			return m

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

	def performMove(self, move):
		if not self.completeinformation:
			raise RuntimeError("Cannot apply move to incomple information game state")
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

	def printState(self, extended=False, pickle=False):
		print("Current turn is: Player {0} out of {1}".format(self.turn+1, self.num_players))
		print("Remaining draws: {0}, Remaining plays: {1}".format(self.remainingDraws, self.remainingPlays))
		
		if extended:
			print("Draw pile: {0}". format(list(c.name for c in self.drawPile)))
			print("Discard pile: {0}". format(list(c.name for c in self.discardPile)))
		print("Center Table: {0}". format(list(c.name for c in self.centerTable)))
		
		if self.enforceHandLimitForOtherPlayersExcept != None:
			print("Enforcing hand limit for all players except: {0}".format(self.enforceHandLimitForOtherPlayersExcept + 1))
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
			if not self.completeinformation and i == 0:
				break


		if extended:
			print("Legal moves: {0}".format([m.describe() for m in self.getLegalMoves()]))
		if pickle:
			print("Pickle: {}".format(self.asciiSerialize()))

	def asciiSerialize(self):
		return binascii.b2a_base64(lzma.compress(pickle.dumps(self))).decode('ascii')

	@staticmethod
	def asciiDeserialize(serialized):
		return pickle.loads(lzma.decompress(binascii.a2b_base64(serialized)))

