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


class TreeNode:
	def __init__(self, gamestate, parent, children):
		self.gamestate = gamestate
		self.parent = parent
		self.children = children
		self.depth = self.parent.depth + 1 if self.parent != None else 0

# Start game with four players
def main():
	num_players = 4
	players = [Player("Player " + str(n)) for n in range(1, num_players+1)]
	gs = GameState(num_players)
	print("Players: {0}".format(gs.num_players))
	
	
	#rootnode = TreeNode(gs, None, {m:None for m in gs.getLegalMoves()})
	#dfs(rootnode)
	
	while True:
		transitions = playout_random_game(gs)
		print("Moves performed: {} Winning player(s): {}".format(
			len(transitions),
			list(p+1 for p in transitions[-1][0].getWinningPlayers())))

def playout_random_game(from_state):
	transitions = []
	state = from_state
	while not state.isFinished():
		moves = state.getLegalMoves()
		move = random.choice(moves)
		transitions.append((state, move))
		state = state.performMove(move)

	transitions.append((state, None))
	return transitions

def dfs(node):
	if node.depth > 700:
		print("Max depth reached")
		return
	for m,c in node.children.items():
		if c == None:
			childstate = node.gamestate.performMove(m)
			c = TreeNode(childstate, node, {m:None for m in childstate.getLegalMoves()})
			if not childstate.isFinished():
				dfs(c)
			else:
				print("Game is finished winning players: {0} Depth: {1}".format(list(p+1 for p in childstate.getWinningPlayers()), node.depth))

if __name__=="__main__":
   main()

