from itertools import cycle
from copy import deepcopy
from enum import Enum
from time import sleep
import random
import sys


class IllegalMove(Exception):
	pass

class Move:
	def __init__(self, player):
		self.player = player

	def isLegal(self, gs):
		try:
			self.raiseIfIllegalMove(gs)
		except IllegalMove:
			return False
		else:
			return True

	def raiseIfIllegalMove(self, gs):
		pass

class DrawMove(Move):
	"""Draw a single card from the deck"""
	def perform(self, gs):
		card = gs.drawFromDeck()
		gs.putCardOnCurrentPlayersHand(card)

	@staticmethod
	def raiseIfIllegalMoveStatic(gs):
		if gs.remainingDraws == 0:
			raise IllegalMove("No more draws remaining")
		if len(gs.deck) == 0:
			raise IllegalMove("Deck is empty")

	def raiseIfIllegalMove(self, gs):
		if gs.turn != self.player:
			raise IllegalMove("Out of turn")
		DrawMove.raiseIfIllegalMoveStatic(gs)
	
	def describe(self):
		return "Draw"

class PlayMove(Move):
	# Play a card from the hand
	def __init__(self, player, card):
		super(PlayMove, self).__init__(player)
		self.card = card
	
	def raiseIfIllegalMove(self, gs):
		# TODO: Also ask the card itself if it is currently playable
		try:
			DrawMove.raiseIfIllegalMoveStatic(gs)
		except IllegalMove:
			pass
		else:
			raise IllegalMove("Drawing is allowed thus no cards can be played")

		if gs.turn != self.player:
			raise IllegalMove("Out of turn")

		if gs.remainingPlays == 0:
			raise IllegalMove("No remaining plays")

		if self.card not in gs.playershands[self.player]:
			raise IllegalMove("Card {0} is not in players hand".format(self.card.name))

	def perform(self, gs):
		gs.playCard(self.player, self.card)

	def describe(self):
		return "Play: {0}".format(self.card.name)

class DiscardMove(Move):
	def __init__(self, player, card):
		super(DiscardMove, self).__init__(player)
		self.card = card

	def raiseIfIllegalMove(self, gs):
		EndTurnMove.raiseIfIllegalIgnoringHandLimit(gs, self.player)
		
		if gs.turn != self.player:
			raise IllegalMove("Out of turn")

		if len(gs.playershands[self.player]) <= gs.currentHandLimit:
			raise IllegalMove("Handlimit not exceeded")

		if self.card not in gs.playershands[self.player]:
			raise IllegalMove("Card not in players hand")

	def perform(self, gs):
		gs.discardFromHand(self.player, self.card)
	
	def describe(self):
		return "Discard: {0}".format(self.card.name)

class EndTurnMove(Move):
	@staticmethod
	def raiseIfIllegalIgnoringHandLimit(gs, player):
		try:
			DrawMove.raiseIfIllegalMoveStatic(gs)
		except IllegalMove:
			pass
		else:
			raise IllegalMove("Drawing is legal move")

		if gs.turn != player:
			raise IllegalMove("Out of turn")

		if gs.remainingPlays > 0 and len(gs.playershands[player]) > 0:
			raise IllegalMove("Plays remaining")

	def raiseIfIllegalMove(self, gs):
		if len(gs.playershands[self.player]) > gs.currentHandLimit:
			raise IllegalMove("Hand limit exceeded")
		EndTurnMove.raiseIfIllegalIgnoringHandLimit(gs, self.player)

	def perform(self, gs):
		gs.nextTurn()
	
	def describe(self):
		return "End turn"



class Card:
	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.name)

class DummyCard(Card):
	def __init__(self, n):
		self.name = "Dummy {0}".format(n)

	def play(self, gs, player):
		gs.putInDiscardPile(self)

class RuleCard(Card):
	def replaceRuleCard(self, gs, rulecardtype):
		gs.discardFromTableCenter([c for c in gs.cardsOnTableCenter if isinstance(c, rulecardtype)])
		gs.putOnTableCenter(self)

class DrawNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Draw {0}".format(n)

	def play(self, gs, player):
		self.replaceRuleCard(gs, DrawNCard)
		gs.currentDrawLimit = self.n

class PlayNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Play {0}".format(n)
	
	def play(self, gs, player):
		self.replaceRuleCard(gs, PlayNCard)
		gs.currentPlayLimit = self.n

class HandLimitNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Hand limit {0}".format(n)
	
	def play(self, gs, player):
		self.replaceRuleCard(gs, HandLimitNCard)
		gs.currentHandLimit = self.n

class ActionCard(Card):
	pass

class ActionTrashANewRule(ActionCard):
	def __init__(self):
		self.name = "Trash a New Rule"

	class ResolveTrashANewRuleMove(Move):
		def __init__(self, player, card):
			super(ActionTrashANewRule.ResolveTrashANewRuleMove, self).__init__(player)
			self.card = card

		def raiseIfIllegalMove(self, gs):
			pass

		def perform(self, gs):
			gs.discardFromTableCenter([self.card])
			gs.actionIsResolved()

		def describe(self):
			return "Trash a New Rule: {0}".format(self.card.name)
		

	def play(self, gs, player):
		gs.putInDiscardPile(self)
		gs.actionResolving(self, [self.ResolveTrashANewRuleMove(player, c) for c in gs.cardsOnTableCenter if isinstance(c, RuleCard)])



class Player:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.name)


class GameState:
	def __init__(self, players):
		self.players = players
		self.turniter = cycle(self.players)
		
		self.deck = []
		self.deck.extend(list(DrawNCard(n) for n in range(2, 5)))
		self.deck.extend(list(PlayNCard(n) for n in range(2, 5)))
		self.deck.extend(list(HandLimitNCard(n) for n in range(1, 3)))
		self.deck.extend(list(DummyCard(n) for n in range(1, 11)))
		self.deck.append(ActionTrashANewRule())
		self.shuffleDeck()

		self.playershands = {p:[] for p in self.players}

		self.cardsOnTableCenter = []
		self.discards = []

		self.currentDrawLimit = 1
		self.currentPlayLimit = 1
		self.currentHandLimit = sys.maxsize

		self.actionResolvingMoves = []

		self.nextTurn()

	def getLegalMoves(self):

		if len(self.actionResolvingMoves) > 0:
			return self.actionResolvingMoves

		# Iterate over all possible moves and return which is allowed
		moves = []
		moves.extend([m for m in [DrawMove(p) for p in self.players] if m.isLegal(self)])
		moves.extend([m for m in [PlayMove(p, c) for p in self.players for c in self.playershands[p]]
				if m.isLegal(self)])
		moves.extend([m for m in [DiscardMove(p, c) for p in self.players for c in self.playershands[p]]
				if m.isLegal(self)])
		moves.extend([m for m in [EndTurnMove(p) for p in self.players] if m.isLegal(self)])
		return moves

	def isFinished(self):
		# Is the game finished somehow?
		# TODO: Check for goal completion
		return False

	def nextTurn(self):
		self.turn = next(self.turniter)
		self.usedDraws = 0
		self.usedPlays = 0

	def performMove(self, move):
		move.raiseIfIllegalMove(self)
		nextState = deepcopy(self)
		move.perform(nextState)
		return nextState

	def shuffleDeck(self):
		random.shuffle(self.deck)

	def drawFromDeck(self):
		self.usedDraws += 1
		card = self.deck.pop(0)
		
		if len(self.deck) == 0 and len(self.discards) > 0:
			self.shuffleDiscardIntoDeck()

		return card

	def putInDiscardPile(self, card):
		self.discards.append(card)
		if len(self.deck) == 0:
			self.shuffleDiscardIntoDeck()

	def shuffleDiscardIntoDeck(self):
		self.deck = self.discards
		self.discards = []
		self.shuffleDeck()

	def putCardOnCurrentPlayersHand(self, card):
		self.playershands[self.turn].append(card)

	def playCard(self, player, card):
		self.playershands[player].remove(card)
		self.usedPlays += 1
		card.play(self, player)

	def discardFromTableCenter(self, cards):
		for c in cards:
			self.cardsOnTableCenter.remove(c)
			self.putInDiscardPile(c)

	def discardFromHand(self, player,card):
		self.playershands[player].remove(card)
		self.putInDiscardPile(card)

	def putOnTableCenter(self, card):
		self.cardsOnTableCenter.append(card)

	def actionResolving(self, card, moves):
		self.actionResolvingMoves = moves

	def actionIsResolved(self):
		self.actionResolvingMoves = []

	@property
	def remainingPlays(self):
		return max(0, self.currentPlayLimit - self.usedPlays)
	
	@property
	def remainingDraws(self):
		return max(0, self.currentDrawLimit - self.usedDraws)


	def countCards(self):
		c = len(self.deck)
		c += len(self.discards)
		c += len(self.cardsOnTableCenter)
		for h in self.playershands.values():
			c += len(h)
		return c

	def printState(self):
		print("Current turn is: {0}".format(self.turn.name))
		print("Remaining draws: {0}, Remaining plays: {1}".format(self.remainingDraws, self.remainingPlays))
		print("Deck: {0}". format(list(c.name for c in self.deck)))
		print("Discards: {0}". format(list(c.name for c in self.discards)))
		print("Center Table: {0}". format(list(c.name for c in self.cardsOnTableCenter)))
		for i,p in enumerate(self.players):
			print("Player {0}'s hand: {1}"
				.format(
					i+1,
					list(c.name for c in self.playershands[p])))


# Start game with two players
def main():
	players = 4
	gs = GameState([Player("Player " + str(n)) for n in range(1, players+1)])
	print("Players: {0}".format(len(gs.players)))
	
	pretotalcards = len(gs.deck)
	
	turns = 0
	
	while not gs.isFinished():
		gs.printState()
		moves = gs.getLegalMoves()
		print("Legal moves: {0}".format([m.describe() for m in moves]))
		move = random.choice(moves)
		gs = gs.performMove(move)
		print("Performed move: {0}".format(move.describe()))
		print()
		
		if isinstance(move, EndTurnMove):
			turns += 1
			print()
			print()
	#		sleep(1)
	
		#sleep(0.1)
	
		if gs.countCards() != pretotalcards:
			raise Exception("Lost a card somehow, expected {0} counted {1}"
					.format(pretotalcards, gs.countCards()))




if __name__=="__main__":
   main()

