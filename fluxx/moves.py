class IllegalMove(Exception):
	pass

class Move:
	def __init__(self, player):
		self.player = player

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

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
	"""Draw a single card from the draw pile"""

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

	def __hash__(self):
		return 0

	def perform(self, gs):
		card = gs.drawFromDrawPile()
		gs.playersHands[self.player].append(card)
		card.drawn(gs, self.player)

	@staticmethod
	def raiseIfIllegalMoveStatic(gs):
		if gs.remainingDraws == 0:
			raise IllegalMove("No more draws remaining")
		if gs.drawPile != None:
			if len(gs.drawPile) == 0:
				raise IllegalMove("drawPile is empty")
		if gs.creeperJustDrawn:
			raise IllegalMove("Creeper was just drawn")

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

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return self.card == other.card

	def __hash__(self):
		return hash(self.card)
	
	def raiseIfIllegalMove(self, gs):
		# TODO: Also ask the card itself if it is currently playable
		try:
			DrawMove.raiseIfIllegalMoveStatic(gs)
		except IllegalMove:
			pass
		else:
			raise IllegalMove("Drawing is allowed thus no cards can be played")

		if gs.creeperJustDrawn and not self.card.isCreeper():
			raise IllegalMove("Creeper just drawn")

		if gs.turn != self.player and not gs.creeperJustDrawn:
			raise IllegalMove("Out of turn")

		if gs.remainingPlays == 0 and not gs.creeperJustDrawn:
			raise IllegalMove("No remaining plays")

		if self.card not in gs.playersHands[self.player]:
			raise IllegalMove("Card {0} is not in players hand".format(self.card.name))

	def perform(self, gs):
		gs.playCard(self.player, self.card)

	def describe(self):
		return "Play: {0}".format(self.card.name)

class DiscardMove(Move):
	def __init__(self, player, card):
		super(DiscardMove, self).__init__(player)
		self.card = card

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return self.card == other.card

	def __hash__(self):
		return hash(self.card)

	def raiseIfIllegalMove(self, gs):
		if gs.enforceHandLimitForOtherPlayersExcept == None:
			EndTurnMove.raiseIfIllegalIgnoringHandLimit(gs, self.player)
		
			if gs.turn != self.player:
				raise IllegalMove("Out of turn")

		if len(gs.playersHands[self.player]) <= gs.currentHandLimit:
			raise IllegalMove("Handlimit not exceeded")

		if self.card not in gs.playersHands[self.player]:
			raise IllegalMove("Card not in players hand")

	def perform(self, gs):
		gs.discardFromHand(self.player, self.card)
	
	def describe(self):
		return "Discard: {0}".format(self.card.name)

class EndTurnMove(Move):

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

	def __hash__(self):
		return 0

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

		if gs.remainingPlays > 0 and len(gs.playersHands[player]) > 0:
			raise IllegalMove("Plays remaining")

	def raiseIfIllegalMove(self, gs):
		if len(gs.playersHands[self.player]) > gs.currentHandLimit:
			raise IllegalMove("Hand limit exceeded")
		EndTurnMove.raiseIfIllegalIgnoringHandLimit(gs, self.player)

	def perform(self, gs):
		gs.nextTurn()
	
	def describe(self):
		return "End turn"
