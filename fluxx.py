import random

from fluxx.moves import EndTurnMove
from fluxx.gamestate import GameState

class Player:
	def __init__(self, name):
		self.name = name

	def __eq__(self, other):
		if other == None: return False
		return self.name == other.name

	def __hash__(self):
		return hash(self.name)



# Start game with two players
def main():
	num_players = 4
	players = [Player("Player " + str(n)) for n in range(1, num_players+1)]
	gs = GameState(num_players)
	print("Players: {0}".format(gs.num_players))
	
	pretotalcards = len(gs.drawPile)
	
	turns = 0
	
	move = None
	while not gs.isFinished():
		if (isinstance(move, EndTurnMove)):
			gs.printState()
		moves = gs.getLegalMoves()
		print("Legal moves: {0}".format([m.describe() for m in moves]))
		move = random.choice(moves)
		gs = gs.performMove(move)
		print("Performed move: {0}".format(move.describe()))
		
		if isinstance(move, EndTurnMove):
			turns += 1
			print()
			print()
	#		sleep(1)
	
		#sleep(0.1)
	
		if gs.countCards() != pretotalcards:
			raise Exception("Lost a card somehow, expected {0} counted {1}"
					.format(pretotalcards, gs.countCards()))

	print()
	print("Game is finished after {1} turns, winning players: {0}".format(list(p+1 for p in gs.getWinningPlayers()), turns))




if __name__=="__main__":
   main()

