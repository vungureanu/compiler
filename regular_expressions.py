import itertools

class Regular_Expression:
	def __init__(self, expression):
		self.expression = expression
	def parse(self):

	def convert_to_NFA(self):


class NFA:
	# Each non-deterministic finite automoton is defined by its alphabet, transition function, and set of accepting states.
	# The alphabet consists of the disjoint sets of characters a_1, ..., a_m (e.g., {a, b, c}, {d, 1}, {!}).  The
	# characters in each set are intended to be equivalent from the perspective of the language.
	# It has n states, numbered 0, ..., n-1, where 0 is the starting state; a subset of these are accepting states.
	# The transition function fn is a list of dictionaries, each of which maps some a_k to a set of states.  The NFA
	# can move directly from state s_i to state s_j upon receiving a character in a_k iff fn[s_i][a_k] contains s_j.
	# Epsilon-moves are indicated by None.

	def __init__(self, alphabet, char_type = None):
		# Number of states (numbered from 0 to n-1); the start state is numbered 0
		# Transition function; the ith element of "fn" maps c to a list of states reachable from state i given input c
		self.possible_states = [0]
		self.alphabet = alphabet
		if char_type != None:
			self.fn = [[{char_type: 1}], []]

	def shift_up(fn, n):
		return [ {char: [s + n for s in new_states] for char, new_states in old_state.items()} for old_state in fn ]

	def concatenate_NFAs(nfa1, nfa2):
		nfa_concat = NFA(nfa1.alphabet)
		nfa_concat.n = nfa1.n + nfa2.n
		nfa_concat.accepting_states = [s + nfa1.n for s in nfa2.accepting_states]
		nfa_concat.fn = nfa1.fn + NFA.shift_up(nfa2.fn, nfa1.n)
		for state in nfa1.accepting_states:
			if None in nfa_concat.fn[state]:
				nfa_concat.fn[state][None].append(nfa1.n)
			else:
				nfa_concat.fn[state][None] = [nfa1.n]
		return nfa_concat

	def join_NFAs(nfa1, nfa2):
		nfa_join = NFA()
		nfa_join.n = nfa1.n + nfa2.n + 1
		nfa_join.fn = [ {None: [1, nfa1.n+1]} ] + NFA.shift_up(nfa1.fn, 1) + NFA.shift_up(nfa2.fn, n+1)
		nfa_join.accepting_states = [x + 1 for x in nfa1.accepting_states] + [x + nfa1.n for x in nfa2.accepting_states]
		return nfa_join

	def close_NFA(nfa):
		nfa_closure = NFA()
		nfa_closure.n = nfa.n
		nfa_closure.accepting_states = [0] + [s + 1 for s in nfa.accepting_states]
		nfa_closure.fn = [ {None: [1]} ] + shift_up(nfa.fn, 1)
		for state in nfa1.accepting_states:
			if None in nfa_closure.fn[state]:
				nfa_closure.fn[state][None].append(1)
			else:
				nfa_closure.fn[state][None] = [1]

	def e_closure(self, starting_states):
		reachable_states = []
		frontier_states = starting_states
		while (len(frontier_states) > 0):
			new_states = itertools.chain(*[self.fn[state][None] for state in frontier_states])
			frontier_states = filter(lambda x: x not in reachable_states, new_states)
			reachable_states += frontier_states
		return reachable_states

	def state_after_move(self, char):
		return [self.fn[state][char] for state in filter(lambda x: char in x, self.e_closure(possible_states))]

	def move(self, char):
		self.possible_states = self.state_after_move(char)

	def convert_to_DFA(self):
		active_states = [self.possible_states]
		DFA_states = [self.possible_states]
		DFA_fn = {}
		while (len(accepting_states) > 0):
			state = accepting_states.pop()
			for char in alphabet:
				new_state = self.state_after_move(char)
				if state in DFA_fn:
					DFA_fn[state][char] = new_state
				else:
					DFA_fn[state] = {char: new_state}
				if new_state not in DFA_states:
					DFA_states.append(new_state)
					active_states.append(new_state)

		state_to_index = {DFA_states[i] : i for i in range(len(DFA_states))}
		simplified_fn = [None] * len(DFA_fn)
		for state in DFA_fn:
			simplified_fn[state_to_index[state]] = {char: state_to_index[new_state] for char, new_state in DFA_fn[state]}
		
		return DFA(simplified_fn)



class DFA:
	self.accepting_states = []
	self.n = None
	self.fn = None



