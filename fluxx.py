from itertools import cycle
from copy import deepcopy
from enum import Enum
from time import sleep
import random

class Card:
	pass

class RuleCard:
	pass

class DrawNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Draw {0}".format(n)

	def play(self, gs):
		gs.discardFromTableCenter([c for c in gs.cardsOnTableCenter if isinstance(c, DrawNCard)])
		gs.putOnTableCenter(self)
		gs.currentDrawLimit = self.n

class PlayNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Play {0}".format(n)
	
	def play(self, gs):
		gs.discardFromTableCenter([c for c in gs.cardsOnTableCenter if isinstance(c, PlayNCard)])
		gs.putOnTableCenter(self)
		gs.currentPlayLimit = self.n

class Player:
	def __init__(self, name):
		self.name = name

class Move():
	def isLegalMove(self, gs):
		return False

class DrawMove(Move):
	"""Draw a single card from the deck"""
	def perform(self, gs):
		card = gs.drawFromDeck()
		gs.putCardOnCurrentPlayersHand(card)

	def isLegalMove(self, gs):
		return gs.remainingDraws > 0
	
	def describe(self):
		return "Draw 1 card from deck"

class PlayMove(Move):
	# Play a card from the hand
	def __init__(self, card):
		self.card = card
	
	def isLegalMove(self, gs):
		# TODO: Also ask the card itself if it is currently playable
		return gs.remainingPlays > 0 and self.card in gs.currentPlayersHand()

	def perform(self, gs):
		gs.playCard(self.card)

	def describe(self):
		return "Play card: {0}".format(self.card.name)

class EndTurnMove(Move):
	def isLegalMove(self, gs):
		if gs.remainingDraws > 0:
			return False
		if gs.remainingPlays == 0 or len(gs.currentPlayersHand()) == 0:
			return True
		return False

	def perform(self, gs):
		gs.nextTurn()
	
	def describe(self):
		return "End my turn"

class GameState:
#	class TurnState(Enum):
#		draw = 0
#		play = 1

	class InvalidMove(Exception):
		pass

	def __init__(self, players):
#		self.players = [Player("Player " + str(n)) for n in range(1, players+1)]
		self.players = players
		self.turniter = cycle(self.players)
		
		self.deck = []
		self.deck.extend(list(DrawNCard(n) for n in range(2, 4+1)))
		self.deck.extend(list(PlayNCard(n) for n in range(2, 4+1)))
		self.shuffleDeck()

		self.playershands = {p:[] for p in self.players}

		self.cardsOnTableCenter = []
		self.discards = []

		self.currentDrawLimit = 1
		self.currentPlayLimit = 1

		self.nextTurn()

	def isFinished(self):
		# Is the game finished somehow?
		# TODO: Check for goal completion
		return False

	def nextTurn(self):
		self.turn = next(self.turniter)
		self.usedDraws = 0
		self.usedPlays = 0

	def progress(self):
		""" Return a new instance of GameState with the next move applied.
		    Does not modify self. """

		gs = deepcopy(self)
		move = gs.turn.act(gs)
		if move.isLegalMove(gs):
			gs.performMove(move)
		else:
			raise self.InvalidMove(move.describe())
		return (gs, move)

	def performMove(self, move):
		move.perform(self)

	def shuffleDeck(self):
		random.shuffle(self.deck)

	def drawFromDeck(self):
		if len(self.deck) == 0:
			self.deck = self.discards
			self.discards = []
			self.shuffleDeck()

		self.usedDraws += 1
		return self.deck.pop(0)

	def putCardOnCurrentPlayersHand(self, card):
		self.playershands[self.turn].append(card)

	def playCard(self, card):
		self.currentPlayersHand().remove(card)
		self.usedPlays += 1
		card.play(self)

	def discardFromTableCenter(self, cards):
		for ct in self.cardsOnTableCenter:
			for c in cards:
				if ct == c:
					self.discards.append(c)
					self.cardsOnTableCenter.remove(c)

	def putOnTableCenter(self, card):
		self.cardsOnTableCenter.append(card)

	def currentPlayersHand(self):
		return self.playershands[self.turn]

	@property
	def remainingPlays(self):
		return self.currentPlayLimit - self.usedPlays
	
	@property
	def remainingDraws(self):
		return self.currentDrawLimit - self.usedDraws


	def printState(self):
		print("Current turn is: {0}".format(self.turn.name))
		print("Deck: {0}". format(list(c.name for c in self.deck)))
		print("Center Table: {0}". format(list(c.name for c in self.cardsOnTableCenter)))
		for i,p in enumerate(self.players):
			print("Player {0}'s hand: {1}"
				.format(
					i,
					list(c.name for c in self.playershands[p])))



class SimpleAutoPlayer(Player):
	# Simple player that always plays the first n cards of his hand
	def __init__(self, name):
		super(SimpleAutoPlayer, self).__init__(name)

	def act(self, gs):
		# TODO: Get list of valid moves from gamestate and just pick one of thoese instead
		if gs.remainingDraws > 0:
			m = DrawMove()
		elif gs.remainingPlays > 0 and len(gs.currentPlayersHand()) > 0:
			m = PlayMove(gs.currentPlayersHand()[0])
		else:
			m = EndTurnMove()
		return m


# Start game with four players
players = 4
gs = GameState([SimpleAutoPlayer("Player " + str(n)) for n in range(1, players+1)])
print("Players: {0}".format(len(gs.players)))

while not gs.isFinished():
	gs.printState()
	gs, move = gs.progress()
	print("Performed move: {0}".format(move.describe()))
	print()
	sleep(1)
	if isinstance(move, EndTurnMove):
		print()
		print()
		sleep(5)



#for i,c in enumerate(gs.deck):
#	print("Card {0}: {1}".format(i, c.name))


