import random
import math

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
	def __init__(self, gamestate, parent):
		self.gamestate = gamestate
		self.parent = parent
		self.depth = self.parent.depth + 1 if self.parent != None else 0
		self.wins = 0
		self.visits = 0
		self.children = None

	def win_ratio(self):
		return self.wins / self.visits

	def uct(self):
		if self.visits == 0:
			return math.inf
		return self.win_ratio() + 2 / math.sqrt(2) * math.sqrt((2 * math.log(self.parent.visits)) / self.visits)

# Start game with four players
def main():
	num_players = 4
	players = [Player("Player " + str(n)) for n in range(1, num_players+1)]
	gs = GameState(num_players)
	print("Players: {0}".format(gs.num_players))
	
	rootnode = TreeNode(gs, None)
	for i in range(1,5):
		selected_node = selection(rootnode)
		selected_node = expansion(selected_node)

		print("Selected node:")
		selected_node.gamestate.printState()
	
		transitions, winning_players = simulation(selected_node.gamestate)
		turns = sum([1 for s,m in transitions if isinstance(m, EndTurnMove)])
		print("Simulation: Turns: {} Winning player(s): {}".format(turns, winning_players))

		win = (gs.turn in winning_players) / len(winning_players)
		backpropagation(selected_node, win)


def selection(node):
	if node.children == None:
		return node

	children = node.children.values()
	return selection(max(children, key=lambda c: c.uct()))

def expansion(node):
	node.children = {
			move: TreeNode(node.gamestate.performMove(move), node)
			for move in node.gamestate.getLegalMoves()}
	return random.choice(list(node.children.values()))
		

def simulation(from_state):
	transitions = []
	state = from_state
	while not state.isFinished():
		moves = state.getLegalMoves()
		move = random.choice(moves)
		transitions.append((state, move))
		state = state.performMove(move)

	transitions.append((state, None))
	return (transitions, list(p+1 for p in transitions[-1][0].getWinningPlayers()))

def backpropagation(node, win):
	while node != None:
		node.visits += 1
		node.wins += win
		node = node.parent

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

