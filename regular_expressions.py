import itertools
import unittest

epsilon = None

class Regular_Expression:
	def __init__(self, expression):
		self.expression = expression
	def parse(self):
		pass
	def convert_to_NFA(self):
		pass

class State:
	number = 0
	def __init__(self, accepting = False):
		self.transition = {}
		self.accepting = accepting
		self.number = NFA_State.number
		State.number += 1

	def __bool__(self):
		return self.accepting

	def __repr__(self):
		return str(self.number)

class NFA_State(State):
	def add_transition(self, input_char, state):
		if input_char in self.transition:
			self.transition[input_char].append(state)
		else:
			self.transition[input_char] = [state]

	def get_epsilon_neighbors(self):
		if None in self.transition:
			return self.transition[None]
		else:
			return []

class DFA_State(State):
	def add_transition(self, input_char, state):
		self.transition[input_char] = state

class NFA:
	# Each non-deterministic finite automaton is defined by its alphabet, transition function, and set of accepting states.
	# The alphabet consists of the disjoint sets of characters a_1, ..., a_m (e.g., {a, b, c}, {d, 1}, {!}).  The
	# characters in each set are intended to be equivalent from the perspective of the language.
	# It has n states, numbered 0, ..., n-1, where 0 is the starting state; a subset of these are accepting states.
	# The transition function fn is a list of dictionaries, each of which maps some a_k to a set of states.  The NFA
	# can move directly from state s_i to state s_j upon receiving a character in a_k iff fn[s_i][a_k] contains s_j.
	# Epsilon-moves are indicated by None.

	def __init__(self, alphabet, start_state = None, char_type = None):
		self.alphabet = alphabet
		self.accepting_states = []
		if start_state == None:
			self.start_state = NFA_State()
		else:
			self.start_state = start_state
		self.states = [start_state]
		self.number_of_states = 1
		if char_type != None:
			accepting_state = NFA_State(accepting = True)
			self.accepting_states = [accepting_state]
			self.start_state.add_transition(char_type, accepting_state)
			self.states.append(accepting_state)
			self.number_of_states += 1

	def do_not_accept(self):
		for state in self.accepting_states:
			state.accepting = False

	def concatenate_NFAs(nfa1, nfa2):
		"""Returns an NFA which recognizes the language {ab | nfa1 accepts a and nfa2 accepts b}"""
		nfa_concat = NFA(nfa1.alphabet + nfa2.alphabet, start_state = nfa1.start_state)
		nfa_concat.number_of_states = nfa1.number_of_states + nfa2.number_of_states
		nfa_concat.accepting_states = nfa2.accepting_states
		nfa_concat.states = nfa1.states + nfa2.states
		for state in nfa1.accepting_states:
			state.add_transition(epsilon, nfa2.start_state)
		nfa1.do_not_accept()
		return nfa_concat

	def join_NFAs(nfa1, nfa2):
		"""Returns an NFA which recognizes the language {a | nfa1 accepts a or nfa2 accepts a}"""
		nfa_join = NFA(nfa1.alphabet + nfa2.alphabet)
		nfa_join.number_of_states = nfa1.number_of_states + nfa2.number_of_states + 1
		nfa_join.states.extend(nfa1.states + nfa2.states)
		nfa_join.accepting_states = nfa1.accepting_states + nfa2.accepting_states
		nfa_join.start_state.add_transition(epsilon, nfa1.start_state)
		nfa_join.start_state.add_transition(epsilon, nfa2.start_state)
		return nfa_join

	def close_NFA(nfa):
		"""Modifies an NFA so that it recognizes the language {a_1...a_n | nfa accepts a_i for all 0 <= i <= n}"""
		for state in nfa.accepting_states:
			state.add_transition(epsilon, nfa.start_state)
		new_start_state = NFA_State(accepting = True)
		new_start_state.add_transition(epsilon, nfa.start_state)
		nfa.start_state = new_start_state
		return nfa

	def e_closure(self, starting_states):
		"""Returns all states which can be reached from some state in starting_states along epsilon-paths (i.e., without any input)."""
		reachable_states = []
		frontier_states = starting_states
		while (len(frontier_states) > 0):
			reachable_states += frontier_states
			new_states = itertools.chain(*[state.get_epsilon_neighbors() for state in frontier_states])
			frontier_states = [s for s in new_states if s not in reachable_states]
		return set(reachable_states)

	def states_after_move(self, states, char):
		next_states = [ state.transition[char] for state in filter(lambda state: char in state.transition, states) ]
		return self.e_closure( set(itertools.chain(*next_states)) )

	def move(self, char):
		self.possible_states = self.states_after_move(self.possible_states, char)

	def convert(self):
		"""Returns an equivalent DFA (i.e., one which recognizes the same language)"""
		dfa = DFA(self.alphabet)
		trans = Translation(dfa)
		active_states = [ self.e_closure([self.start_state]) ]
		while len(active_states) > 0:
			nfa_states = active_states.pop()
			old_dfa_state = trans.translate(nfa_states)
			for char in self.alphabet:
				new_states = self.states_after_move(nfa_states, char)
				new_dfa_state = trans.translate(new_states)
				old_dfa_state.add_transition(char, new_dfa_state)
		return dfa

	def is_valid(self, string):
		"""Determines whether the NFA accepts the given string"""
		self.possible_states = self.e_closure([self.start_state])
		for char in string:
			self.move(char)
		return any(self.possible_states)


class DFA:
	def __init__(self, alphabet):
		self.states = []
		self.alphabet = alphabet
		self.transition = {}
		self.accepting_states = []
		
	def add_state(self):
		new_state = DFA_State()
		self.states.append(new_state)
		return new_state

	def is_valid(self, string):
		self.current_state = self.start_state
		for char in string:
			self.current_state = self.current_state.transition[char]
		return self.current_state.accepting

class Translation:
	def __init__(self, dfa):
		self.nfa_states = []
		self.dfa_state = []
		self.dfa = dfa
		dead_end = dfa.add_state()
		for char in dfa.alphabet:
			dead_end.add_transition(char, dead_end)

	def translate(self, states):
		if states in self.nfa_states:
			return self.dfa_state[ self.nfa_states.index(states) ]
		else:
			new_state = self.dfa.add_state()
			self.nfa_states.append(states)
			self.dfa_state.append(new_state)
			return new_state
