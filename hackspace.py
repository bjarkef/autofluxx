#!/usr/bin/env python3
from fluxx.gamestate import GameState
from fluxx.mcts import MonteCarloTreeSearch


# Start game with four players
def main():
	#pickle = "/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4Af0A+5dAEAAyAMwdj8K88p6ofMt18+8Q9ZjWAUUB2jbJR85TnsFIvD0BLy9M6CE4MOzZdPT8vWBrRvlt7lYh6JUlJ+/OETHBXrqs6FxyQFeGBHLn2T2gWtJmt5kEJ3AJp7dkxSfkCT3dMcZGcASo8+xvF34u0N0uSOw7ZDdvpjYPPpfaIrRci5hXLk6oRTlsOKySsMCi6pU9HI5Z6KbcsE/n8xSG+IAnWAH3jSZxPZxey7SwLZ+cLEHXBgAkKlevS+UWUBMn8eJp04YZ5JMgpA7zRHRKPkhnwyq9pLSZK0rgu7mzt1p9jyknxFqX79o04QFenI4XK7Nf/1Md5XD5PXXVM7ZgTBSEzz6bTkP7agbnK8VtVN2R9IbCC6anAdgDoUIVgCgpgskMSmqZ0/gUB7WeI2Lsg8pDhcuzh6jhcLIahsrq7vHpa+WGY0qCaQu9NdhdAImT5+4VDs+QmJBmf2/FcDuMHzui4GRk7mj881PR9E+1BVHryJNWimMPC48eFR3NTrUaIOeMvuMWpqeuMyftijNGI9L0l6DckDxGgZTgIAgNNe5TVpBoaED/diK2KfS0PKzoR8FbekTCoIkqvwUnZGYN7J2xzkXIyUKvwQ7AXZB7QwB6DE2TFs74u6FUalvubHG662pUq3Fw4T8Fj0YPFhXcEt4OYpa5B7pLJcFcjBGSss95Ah06gwYUsbymKeACNq6bCmZJRQZs33HD73+MWhNTgz0zbVh9IYZI26hqg8OvxCctwMoXn+fYYsbKNgd240ZIsn4VbEFiDsOTG4/bWVofRoPL7h/+0qddRLtoixfyIqmolXhFJ+beB/lpJpOmPmVztwkYf7zHI/KhLnSjUThYdZkgMPPs+gjdK7VYGOjemy6xz/16RQyWvutgGooMOGhJihfsaXu+F06AzbObh1AUzO8STwXbVaHdxB/jBlMqCIuX8EbUeEVXONcPbPp5SFuYgaM6UJm9CPmuRihxCNZRIXE9fW7RLzN7OZKseerj/1bUb4i7wS3ljI4No/cPqdvskMRcD1aG5kk+h3z6GR2WlD0KUdnd9otN6wJ6ipzYr5a8nje/90pTTx91A8kX17F/1/b/OxHcAZLZwAwYpMJ5hmapd3Z8/v5XhvviG0jOAjmR0VbasDJ8G4pSfGSTIpovoy4FllM5fJKUqa9avNwi7mZow4KKITudhZbFBa2awC97wKMemOyJ4akw9mIF3w1Z35YlaC2B5MSRtMSnac3Ha+YU5iw8ET1BCnzApkCFWtSpeXPHcooxYGFta/4jkLj4ErnYbX6pC/RIVaGHfrearPrUx6LLaf7uWOXfJwNMW+fh8xGczcreuMRxTsGe0wAAADYc4rjPztjuAABigj1DwAACgnq9rHEZ/sCAAAAAARZWg=="
	#gs = GameState.asciiDeserialize(pickle)
	#print("Players: {0}".format(gs.num_players))
	
	gs = GameState.createFromHumanReadableString("P:3,H:{Cat,Str,P3,D2},T:{Poe,Sho},C:{Boh,HL3},D:1,L:0")

	move_statistics = {}

	while True:
		gs = gs.randomInformation()

		mcts = MonteCarloTreeSearch()
		result = mcts.run(gs, 100, 1)

		for m,wr in result.items():
			#print("{}: {:0.2f}".format(m.describe(), wr))
			if m not in move_statistics:
				move_statistics[m] = []
			move_statistics[m].append(wr)

		print()
		for m,wrs in move_statistics.items():
			wr = sum(wrs)/len(wrs)
			print("{}: {:0.2f}".format(m.describe(), wr))


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

