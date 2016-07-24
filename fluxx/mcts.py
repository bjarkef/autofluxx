import random
import math
import graphviz as gv
import shutil

from . import moves
#from . import gamestate


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
		if self.wins == 0:
			return 0
		return self.wins / self.visits

	def uct(self):
		if self.visits == 0:
			return math.inf
		return self.win_ratio() + 2 / math.sqrt(2) * math.sqrt((2 * math.log(self.parent.visits)) / self.visits)

class MonteCarloTreeSearch():
	def run(self, gamestate, iterations=100, simulations_per_iteration=1):
		rootnode = TreeNode(gamestate, None)
		for i in range(0,iterations):
			#print("Iteration {}".format(i))
			selected_node = self.selection(rootnode)
			selected_node = self.expansion(selected_node)
	
			#print("Selected node:")
			#selected_node.gamestate.printState()
		
			for s in range(0,simulations_per_iteration):
				transitions, winning_players = self.simulation(selected_node.gamestate)
				#turns = sum([1 for s,m in transitions if isinstance(m, moves.EndTurnMove)])
				#print("Simulation: Turns: {} Winning player(s): {}".format(turns, winning_players))
	
				self.backpropagation(selected_node, winning_players)
	
			#self.draw_tree(rootnode, "tree")
			#print()
			#print()
			print(".", end="",flush=True)
	
		self.draw_tree(rootnode, "tree")
		print()

		return {m:n.win_ratio() for m, n in rootnode.children.items()}



	def selection(self, node):
		if node.children == None:
			return node
	
		children = node.children.values()
		return self.selection(max(children, key=lambda c: c.uct()))
	

	def expansion(self, node):
		node.children = {
				move: TreeNode(node.gamestate.performMove(move), node)
				for move in node.gamestate.getLegalMoves()}
		return random.choice(list(node.children.values()))	
	

	def simulation(self, from_state):
		transitions = []
		state = from_state
		while not state.isFinished():
			moves = state.getLegalMoves()
			move = random.choice(moves)
			transitions.append((state, move))
			state = state.performMove(move)
	
		transitions.append((state, None))
		return (transitions, transitions[-1][0].getWinningPlayers())
	

	def backpropagation(self, node, winning_players):
		while node != None:
			node.visits += 1
			if (node.gamestate.turn in winning_players):
				node.wins += 1
			node = node.parent
	
	
	def draw_tree(self, rootnode, filename):
		graph = gv.Digraph(format='svg')
		graph.node(str(id(rootnode)), "root")
		self.draw_children(graph, rootnode)
		temp_file = ".{}.tmp".format(filename)
		graph.render(filename=temp_file)
		shutil.copyfile("{}.svg".format(temp_file), "{}.svg".format(filename))
	

	def draw_children(self, graph, node):
		if node.children == None: return
	
		for m,c in node.children.items():
			if c.visits == 0:
				stats = "{}/{}≃NaN".format(c.wins, c.visits)
			else:
				stats = "{}/{}≃{:.2f}".format(c.wins, c.visits, c.wins/float(c.visits))
			graph.node(str(id(c)), stats)
			graph.edge(str(id(node)), str(id(c)), label=m.describe())
			self.draw_children(graph, c)
	

