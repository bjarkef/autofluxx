import random

from fluxx.moves import EndTurnMove
from fluxx.gamestate import GameState

class Player:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		return self.name == other.name

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.name)



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

