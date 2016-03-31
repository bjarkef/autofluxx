from . import moves

class Card:
	def __eq__(self, other):
		return self.name == other.name

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
		gs.enforceHandLimitForOthers(player)

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

class ActionTrashSomething(ActionCard):
	def __init__(self):
		self.name = "Trash Something"

	class ResolveTrashSomethingMove(moves.Move):
		def __init__(self, actingplayer, victimplayer, card):
			super(ActionTrashSomething.ResolveTrashSomethingMove, self).__init__(actingplayer)
			self.victimplayer = victimplayer
			self.card = card

		def raiseIfIllegalMove(self, gs):
			pass

		def perform(self, gs):
			gs.discardFromInFrontOfPlayer(self.victimplayer, self.card)
			gs.actionIsResolved()

		def describe(self):
			return "Trash something: {0} - {1}".format(self.victimplayer.name, self.card.name)
		

	def play(self, gs, player):
		gs.putInDiscardPile(self)
		m = []
		for victim, cards in gs.cardsInFrontOfPlayer.items():
			for c in cards:
				if isinstance(c, KeeperCard) or isinstance(c, CreeperCard):
					m.append(self.ResolveTrashSomethingMove(player, victim, c))
		gs.actionResolving(self, m)

class KeeperCard(Card):
	def play(self, gs, player):
		gs.cardsInFrontOfPlayer[player].append(self)

class KeeperTheCat(KeeperCard):
	def __init__(self): self.name = "The Cat"
class KeeperTheDrunk(KeeperCard):
	def __init__(self): self.name = "The Drunk"
class KeeperTheDreamer(KeeperCard):
	def __init__(self): self.name = "The Dreamer"
class KeeperTheGhoul(KeeperCard):
	def __init__(self): self.name = "The Ghoul"
class KeeperTheArtist(KeeperCard):
	def __init__(self): self.name = "The Artist"
class KeeperTheSocialite(KeeperCard):
	def __init__(self): self.name = "The Socialite"
class KeeperThePoet(KeeperCard):
	def __init__(self): self.name = "The Poet"
#class Keeper(KeeperCard):
#	def __init__(self): self.name = ""



class CreeperCard(Card):
	pass



class GoalCard(Card):
	def play(self, gs, player):
		gs.discardFromTableCenter([c for c in gs.cardsOnTableCenter if isinstance(c, GoalCard)])
		gs.putOnTableCenter(self)

class GoalBohemianRhapsody(GoalCard):
	def __init__(self): self.name = "Bohemian Rhapsody"
	def isFulfilled(self, playersCards):
		 goalCards = set([KeeperTheArtist(), KeeperThePoet(), KeeperTheSocialite(), KeeperTheDrunk()])
		 intersection = goalCards & set(playersCards)
		 return len(intersection) >= 3

#class GoalThingOnDoorstep(GoalCard):
#	def __init__(self): self.name = "The Thing on the Doorstep"
#	def isFulfilled(self, playersCards):
#		 goalCards = set([KeeperThePoet(), KeeperTheSocialite(), CreeperTheBody()])
#		 intersection = goalCards & set(playersCards)
#		 return len(intersection) >= 2

class GoalStrangeAllies(GoalCard):
	def __init__(self): self.name = "Strange Allies"
	def isFulfilled(self, playersCards):
		return (KeeperTheDreamer() in playersCards and
				(KeeperTheCat() in playersCards or KeeperTheGhoul() in playersCards))

class GoalPickmansModel(GoalCard):
	def __init__(self): self.name = "Pickman's Model"
	def isFulfilled(self, playersCards):
		 return KeeperTheGhoul() in playersCards and KeeperTheArtist() in playersCards

