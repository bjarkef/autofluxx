from . import moves

class Card:
	def play(self, gs, player):
		pass

	def drawn(self, gs, player):
		pass

	def isCreeper(self):
		return False

	def shortName(self):
		withoutThe = self.name.split()
		if withoutThe[0] == "The":
			withoutThe = withoutThe[1:]
		return "".join(withoutThe)


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
		gs.discardFromTableCenter([c for c in gs.centerTable if isinstance(c, rulecardtype)])
		gs.putOnTableCenter(self)

class DrawNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Draw {0}".format(n)

	def play(self, gs, player):
		self.replaceRuleCard(gs, DrawNCard)
		self.applyRule(gs)

	def applyRule(self, gs):
		gs.currentDrawLimit = self.n

	def shortName(self):
		return "D{}".format(self.n)

class PlayNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Play {0}".format(n)
	
	def play(self, gs, player):
		self.replaceRuleCard(gs, PlayNCard)
		self.applyRule(gs)

	def applyRule(self, gs):
		gs.currentPlayLimit = self.n

	def shortName(self):
		return "P{}".format(self.n)


class HandLimitNCard(RuleCard):
	def __init__(self, n):
		self.n = n
		self.name = "Hand limit {0}".format(n)
	
	def play(self, gs, player):
		self.replaceRuleCard(gs, HandLimitNCard)
		self.applyRule(gs)
		gs.enforceHandLimitForOthers(player)

	def applyRule(self, gs):
		gs.currentHandLimit = self.n

	def shortName(self):
		return "HL{}".format(self.n)


class ActionCard(Card):
	pass

class ActionTrashANewRule(ActionCard):
	def __init__(self):
		self.name = "Trash a New Rule"

	class ResolveTrashANewRuleMove(moves.Move):
		def __init__(self, player, card):
			super(ActionTrashANewRule.ResolveTrashANewRuleMove, self).__init__(player)
			self.card = card

		def __eq__(self, other):
			if not isinstance(other, self.__class__):
				return False
			return self.card == other.card

		def __hash__(self):
			return hash(self.card)

		def raiseIfIllegalMove(self, gs):
			pass

		def perform(self, gs):
			gs.discardFromTableCenter([self.card])
			gs.actionIsResolved()

		def describe(self):
			return "Trash a New Rule: {0}".format(self.card.name)
		

	def play(self, gs, player):
		gs.putInDiscardPile(self)
		gs.actionResolving(self, [self.ResolveTrashANewRuleMove(player, c) for c in gs.centerTable if isinstance(c, RuleCard)])

class ActionRulesReset(ActionCard):
	def __init__(self):
		self.name = "Rules Reset"

	class ResolveRulesResetMove(moves.Move):
		def __init__(self, player):
			super(ActionRulesReset.ResolveRulesResetMove, self).__init__(player)

		def __eq__(self, other):
			if not isinstance(other, self.__class__):
				return False

		def __hash__(self):
			return 0

		def raiseIfIllegalMove(self, gs):
			pass

		def perform(self, gs):
			gs.discardFromTableCenter([c for c in gs.centerTable if isinstance(c, RuleCard)])
			gs.actionIsResolved()

		def describe(self):
			return "Rules Reset"

	def play(self, gs, player):
		gs.putInDiscardPile(self)
		gs.actionResolving(self, [self.ResolveRulesResetMove(player)])

class ActionTrashSomething(ActionCard):
	def __init__(self):
		self.name = "Trash Something"

	class ResolveTrashSomethingMove(moves.Move):
		def __init__(self, actingplayer, victimplayer, card):
			super(ActionTrashSomething.ResolveTrashSomethingMove, self).__init__(actingplayer)
			self.victimplayer = victimplayer
			self.card = card

		def __eq__(self, other):
			if not isinstance(other, self.__class__):
				return False
			return self.card == other.card

		def __hash__(self):
			return hash(self.card)

		def raiseIfIllegalMove(self, gs):
			pass

		def perform(self, gs):
			gs.discardFromPlayersCards(self.victimplayer, self.card)
			gs.actionIsResolved()

		def describe(self):
			return "Trash: P{0} - {1}".format(self.victimplayer+1, self.card.name)
		

	def play(self, gs, player):
		gs.putInDiscardPile(self)
		m = []
		for victim, cards in gs.playersTable.items():
			for c in cards:
				if isinstance(c, KeeperCard) or isinstance(c, CreeperCard):
					m.append(self.ResolveTrashSomethingMove(player, victim, c))
		gs.actionResolving(self, m)

class KeeperCard(Card):
	def play(self, gs, player):
		gs.playersTable[player].append(self)

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
	def play(self, gs, player):
		gs.creeperJustDrawn = False
		gs.playersTable[player].append(self)

	def drawn(self, gs, player):
		gs.creeperJustDrawn = True

	def isCreeper(self):
		return True

class CreeperTheBody(CreeperCard):
	def __init__(self): self.name = "The Body"
class CreeperTheFungi(CreeperCard):
	def __init__(self): self.name = "The Fungi"
class CreeperTheShottoth(CreeperCard):
	def __init__(self): self.name = "The Shottoth"
class CreeperYogSothoth(CreeperCard):
	def __init__(self): self.name = "Yog-Sothoth"
#class Creeper(CreeperCard):
#	def __init__(self): self.name = ""


class GoalCard(Card):
	def play(self, gs, player):
		gs.discardFromTableCenter([c for c in gs.centerTable if isinstance(c, GoalCard)])
		gs.putOnTableCenter(self)

	def creepers(self, cards):
		return [c for c in cards if isinstance(c, CreeperCard)]

class GoalBohemianRhapsody(GoalCard):
	def __init__(self): self.name = "Bohemian Rhapsody"
	def isFulfilled(self, playersTable):
		 goalCards = set([KeeperTheArtist(), KeeperThePoet(), KeeperTheSocialite(), KeeperTheDrunk()])
		 intersection = goalCards & set(playersTable)
		 return len(intersection) >= 3 and not self.creepers(playersTable)

class GoalThingOnDoorstep(GoalCard):
	def __init__(self): self.name = "The Thing on the Doorstep"
	def isFulfilled(self, playersTable):
		 goalCards = set([KeeperThePoet(), KeeperTheSocialite(), CreeperTheBody()])
		 intersection = goalCards & set(playersTable)
		 return len(intersection) >= 2 and (not self.creepers(playersTable) or self.creepers(playersTable) == [CreeperTheBody()])

class GoalStrangeAllies(GoalCard):
	def __init__(self): self.name = "Strange Allies"
	def isFulfilled(self, playersTable):
		return not self.creepers(playersTable) and (KeeperTheDreamer() in playersTable and
				(KeeperTheCat() in playersTable or KeeperTheGhoul() in playersTable))

class GoalPickmansModel(GoalCard):
	def __init__(self): self.name = "Pickman's Model"
	def isFulfilled(self, playersTable):
		 return not self.creepers(playersTable) and KeeperTheGhoul() in playersTable and KeeperTheArtist() in playersTable

