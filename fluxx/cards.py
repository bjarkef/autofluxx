from . import moves

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

	class ResolveTrashANewRuleMove(moves.Move):
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
