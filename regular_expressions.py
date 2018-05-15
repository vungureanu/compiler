from functools import partial

class Regular_Expression:
	def __init__(self, expression):
		self.expression = expression
	def parse(self):

	def convert_to_NFA(self):


class NFA:
	def __init__(self, tree):
		self.accepting_states = []
		self.n = None
		# Number of states (numbered from 0 to n-1)
		self.fn = None
		# Transition function; the ith element of "fn" maps c to a list of states reachable from state i given input c
	def shift_up(array, n):
		for i in range(len(array)):
			array[i] += n
	def concatenate_NFAs(nfa1, nfa2):
		nfa_concat = NFA()
		nfa_concat.n = nfa1.n + nfa2.n
		nfa_concat.accepting_states = [s + nfa1.n for s in nfa2.accepting_states]
		nfa_concat.fn = nfa1.fn + nfa2.fn
		for old_state in range(nfa2.n):
			for char in nfa2.fn[i]:
				nfa_concat.append([new_state + nfa1.n for new_state in nfa2.fn[old_state][char]])
		for state in nfa1.accepting_states:
			nfa_concat.fn[state][None].append(nfa1.n)
		return nfa_concat
	def join_NFAs(nfa1, nfa2):
		nfa_join = NFA()
		nfa_join.n = nfa1.n + nfa2.n + 1
		nfa_join.fn = [{None: [1, nfa1.n]}]
		nfa_join.accepting_states = [x + 1 for x in nfa1.accepting_states] + [x + nfa1.n for x in nfa2.accepting_states]
		for old_state in range(nfa1.n):
			for char in nfa1.fn[i]:
				nfa_join.append([new_state + 1 for new_state in nfa1.fn[old_state][char]])
		for old_state in range(nfa2.n):
			for char in nfa2.fn[i]:
				nfa_join.append([new_state + nfa1.n for new_state in nfa1.fn[old_state][char]])

		return nfa_join
	def close_NFA(nfa):
		nfa_closure = NFA()
		nfa_closure.n = nfa.n
		nfa_closure.accepting_states = nfa.accepting_states
		nfa_closure.fn = nfa.fn

