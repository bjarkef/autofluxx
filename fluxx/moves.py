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
