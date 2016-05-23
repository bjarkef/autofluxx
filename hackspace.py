import random
import math
import graphviz as gv

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
	#players = [Player("Player " + str(n)) for n in range(1, num_players+1)]
	#gs = GameState(num_players)
	#gs.currentDrawLimit = 2

	pickle = "/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4Af0A+5dAEAAyAMwdj8K88p6ofMt18+8Q9ZjWAUUB2jbJR85TnsFIvD0BLy9M6CE4MOzZdPT8vWBrRvlt7lYh6JUlJ+/OETHBXrqs6FxyQFeGBHLn2T2gWtJmt5kEJ3AJp7dkxSfkCT3dMcZGcASo8+xvF34u0N0uSOw7ZDdvpjYPPpfaIrRci5hXLk6oRTlsOKySsMCi6pU9HI5Z6KbcsE/n8xSG+IAnWAH3jSZxPZxey7SwLZ+cLEHXBgAkKlevS+UWUBMn8eJp04YZ5JMgpA7zRHRKPkhnwyq9pLSZK0rgu7mzt1p9jyknxFqX79o04QFenI4XK7Nf/1Md5XD5PXXVM7ZgTBSEzz6bTkP7agbnK8VtVN2R9IbCC6anAdgDoUIVgCgpgskMSmqZ0/gUB7WeI2Lsg8pDhcuzh6jhcLIahsrq7vHpa+WGY0qCaQu9NdhdAImT5+4VDs+QmJBmf2/FcDuMHzui4GRk7mj881PR9E+1BVHryJNWimMPC48eFR3NTrUaIOeMvuMWpqeuMyftijNGI9L0l6DckDxGgZTgIAgNNe5TVpBoaED/diK2KfS0PKzoR8FbekTCoIkqvwUnZGYN7J2xzkXIyUKvwQ7AXZB7QwB6DE2TFs74u6FUalvubHG662pUq3Fw4T8Fj0YPFhXcEt4OYpa5B7pLJcFcjBGSss95Ah06gwYUsbymKeACNq6bCmZJRQZs33HD73+MWhNTgz0zbVh9IYZI26hqg8OvxCctwMoXn+fYYsbKNgd240ZIsn4VbEFiDsOTG4/bWVofRoPL7h/+0qddRLtoixfyIqmolXhFJ+beB/lpJpOmPmVztwkYf7zHI/KhLnSjUThYdZkgMPPs+gjdK7VYGOjemy6xz/16RQyWvutgGooMOGhJihfsaXu+F06AzbObh1AUzO8STwXbVaHdxB/jBlMqCIuX8EbUeEVXONcPbPp5SFuYgaM6UJm9CPmuRihxCNZRIXE9fW7RLzN7OZKseerj/1bUb4i7wS3ljI4No/cPqdvskMRcD1aG5kk+h3z6GR2WlD0KUdnd9otN6wJ6ipzYr5a8nje/90pTTx91A8kX17F/1/b/OxHcAZLZwAwYpMJ5hmapd3Z8/v5XhvviG0jOAjmR0VbasDJ8G4pSfGSTIpovoy4FllM5fJKUqa9avNwi7mZow4KKITudhZbFBa2awC97wKMemOyJ4akw9mIF3w1Z35YlaC2B5MSRtMSnac3Ha+YU5iw8ET1BCnzApkCFWtSpeXPHcooxYGFta/4jkLj4ErnYbX6pC/RIVaGHfrearPrUx6LLaf7uWOXfJwNMW+fh8xGczcreuMRxTsGe0wAAADYc4rjPztjuAABigj1DwAACgnq9rHEZ/sCAAAAAARZWg=="
	gs = GameState.asciiDeserialize(pickle)
	print("Players: {0}".format(gs.num_players))
	
	rootnode = TreeNode(gs, None)
	for i in range(0,50):
		selected_node = selection(rootnode)
		selected_node = expansion(selected_node)

		print("Selected node:")
		selected_node.gamestate.printState()
	
		for s in range(0,10):		

			transitions, winning_players = simulation(selected_node.gamestate)
			turns = sum([1 for s,m in transitions if isinstance(m, EndTurnMove)])
			print("Simulation: Turns: {} Winning player(s): {}".format(turns, winning_players))

			#win = (gs.turn in winning_players) / len(winning_players)
			backpropagation(selected_node, winning_players)

		draw_tree(rootnode, "tree")

	draw_tree(rootnode, "tree")

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

def backpropagation(node, winning_players):
	while node != None:
		node.visits += 1
		if (node.gamestate.turn in winning_players):
			node.wins += 1
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

def draw_tree(rootnode, filename):
	graph = gv.Digraph(format='svg')
	graph.node(str(id(rootnode)), "root")
	draw_children(graph, rootnode)
	graph.render(filename=filename)

def draw_children(graph, node):
	if node.children == None: return

	for m,c in node.children.items():
		if c.visits == 0:
			stats = "{}/{}≃NaN".format(c.wins, c.visits)
		else:
			stats = "{}/{}≃{:.2f}".format(c.wins, c.visits, c.wins/float(c.visits))
		graph.node(str(id(c)), stats)
		graph.edge(str(id(node)), str(id(c)), label=m.describe())
		draw_children(graph, c)
	

if __name__=="__main__":
   main()

