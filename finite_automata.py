from itertools import chain
import unittest

epsilon = None

class State:
	number = 0
	def __init__(self, accepting = False, starting = False, token_type = None, dead_end = False):
		self.transition = {}
		self.accepting = accepting
		self.starting = starting
		self.token_type = token_type
		self.dead_end = dead_end
		self.number = State.number
		State.number += 1

	def is_dead_end(self):
		return self.dead_end

	def __bool__(self):
		return self.accepting

	def __repr__(self):
		return str(self.number)

	def __hash__(self):
		return self.number

class NFA_State(State):
	""" Represents a possible state of an NFA.  Its transition function is a mapping from characters of the \
	NFA's alphabet to sets of its states.  If c is mapped to {s_1, ..., s_n}, then an NFA which is in the \
	current state and receives the character c as input can enter any of the states s_1, ..., s_n.  The value
	None is mapped to the set of states reachable from the current state with one epsilon-move."""
	def add_transition(self, input_char, state):
		if input_char in self.transition:
			self.transition[input_char].add(state)
		else:
			self.transition[input_char] = {state}

	def get_epsilon_neighbors(self):
		"""Returns the set of states the NFA can reach in one hop from the current state without receiving any input.""" 
		if None in self.transition:
			return self.transition[None]
		else:
			return []

	def __repr__(self):
		mark = "?"
		if self.accepting:
			mark = "!"
		return str(self.number) + mark + ": " + ",".join([str(char) + " -> " + str([s.number for s in self.transition[char]]) for char in self.transition])

	def __bool__(self):
		return self.accepting

class DFA_State(State):
	def add_transition(self, input_char, state):
		self.transition[input_char] = state

	def __repr__(self):
		mark = "?"
		if self.accepting:
			mark = "!"
		elif self.is_dead_end():
			mark = "x"
		return str(self.number) + mark + ": " + "\t" + "\t".join([str(char) + " -> " + str(self.transition[char].number) for char in self.transition])

class NFA:
	""" Represents a non-deterministic finite automaton.  It is defined by its alphabet, transition function, and \
	set of states, one of which is the starting state and some of which are accepting states."""
	def __init__(self, alphabet, start_state = None, char_type = "", token_type = None):
		self.alphabet = alphabet
		self.accepting_states = set()
		if start_state == None:
			self.start_state = NFA_State(starting = True)
		else:
			self.start_state = start_state
		self.states = [self.start_state]
		for char in char_type:
			self.states.append( NFA_State() )
			self.states[-2].add_transition(char, self.states[-1])
		self.states[-1].accepting = True
		self.states[-1].token_type = {token_type}
		self.accepting_states = {self.states[-1]}

	def do_not_accept(self):
		for state in self.accepting_states:
			state.accepting = False
		self.accepting_states = set()

	def concatenate_NFAs(nfa1, nfa2): #may modify arguments
		"""Returns an NFA which recognizes the language {ab | nfa1 accepts a and nfa2 accepts b}"""
		nfa_concat = NFA(nfa1.alphabet | nfa2.alphabet, start_state = nfa1.start_state)
		nfa_concat.accepting_states = nfa2.accepting_states
		nfa_concat.states = nfa1.states + nfa2.states
		for state in nfa1.accepting_states:
			state.add_transition(epsilon, nfa2.start_state)
		nfa1.do_not_accept()
		nfa2.start_state.starting = False
		return nfa_concat

	def join_NFAs(nfa_list): #may modify arguments
		"""Returns an NFA which recognizes the language {a | nfa1 accepts a or nfa2 accepts a}"""
		nfa_join = NFA(set())
		for nfa in nfa_list:
			nfa_join.alphabet |= nfa.alphabet
			nfa_join.states.extend(nfa.states)
			nfa_join.accepting_states |= nfa.accepting_states
			nfa_join.start_state.add_transition(epsilon, nfa.start_state)
			nfa.start_state.starting = False
		return nfa_join

	def close_NFA(nfa, new_token_type = None): #may modify arguments
		"""Modifies an NFA so that it recognizes the language {a_1...a_n | nfa accepts a_i for all 0 <= i <= n}"""
		if new_token_type == None:
			token_type = set()
		else:
			token_type = {new_token_type}
		for state in nfa.accepting_states:
			if state is not nfa.start_state:
				state.add_transition(epsilon, nfa.start_state)
			if new_token_type == None:
				token_type |= state.token_type
			else:
				state.token_type = {new_token_type}
		nfa.start_state.accepting = True
		nfa.accepting_states.add(nfa.start_state)
		nfa.start_state.token_type = token_type
		return nfa

	def complement_NFA(nfa):
		complementary_nfa = NFA(nfa.alphabet)
		complementary_nfa.states = nfa.convert().complement_DFA().convert_states()
		complementary_nfa.accepting_states = {s for s in complementary_nfa.states if s}
		for state in [s for s in complementary_nfa.states if s.starting]:
			complementary_nfa.start_state = state
		return complementary_nfa

	def e_closure(self, starting_states):
		"""Returns all states which can be reached from some state in starting_states along epsilon-paths (i.e., without any input)."""
		reachable_states = []
		frontier_states = starting_states
		while (len(frontier_states) > 0):
			reachable_states += frontier_states
			new_states = chain(*[state.get_epsilon_neighbors() for state in frontier_states])
			frontier_states = [s for s in new_states if s not in reachable_states]
		return frozenset(reachable_states)

	def states_after_move(self, states, char):
		next_states = [ state.transition[char] for state in filter(lambda state: char in state.transition, states) ]
		return self.e_closure( set(chain(*next_states)) )

	def move(self, char):
		self.possible_states = self.states_after_move(self.possible_states, char)

	def convert(self):
		"""Returns an equivalent DFA (i.e., one which recognizes the same language)"""
		dfa = DFA(self.alphabet)
		trans = Translation(dfa)
		starting_states = self.e_closure([self.start_state])
		dfa.set_start_state( trans.translate(starting_states).dfa_state )
		active_states = {starting_states}
		while len(active_states) > 0:
			nfa_states = active_states.pop()
			old_dfa_state = trans.translate(nfa_states).dfa_state
			for char in self.alphabet:
				new_states = self.states_after_move(nfa_states, char)
				result = trans.translate(new_states)
				old_dfa_state.add_transition(char, result.dfa_state)
				if result.unvisited:
					active_states.add(new_states)
		return dfa

	def is_valid(self, string):
		"""Determines whether the NFA accepts the given list of symbols"""
		self.possible_states = self.e_closure([self.start_state])
		for char in string:
			if char not in self.alphabet:
				return False
			self.move(char)
		return any(self.possible_states)

	def __repr__(self):
		return "States:" + str([s.number for s in self.states]) + "\nStart: " + str(self.start_state.number) + "\n" + "\n".join([str(s) for s in self.states])

class DFA:
	"""Represents a deterministic finite automaton.  Differs from an NFA in that its transition function returns \
	a single state rather than a set of states."""
	class Match:
		def __init__(self, string, token_type):
			self.string = string
			self.token_type = token_type.copy()

		def __repr__(self):
			return self.string + ": " + str(self.token_type)

	def __init__(self, alphabet, token_type = None):
		self.states = []
		self.alphabet = alphabet
		self.accepting_states = set()
		self.start_state = None
		self.token_type = token_type

	def set_start_state(self, state):
		self.start_state = state
		state.starting = True
		
	def add_state(self, accepting, token_type, dead_end = False):
		new_state = DFA_State(accepting = accepting, token_type = token_type, dead_end = dead_end)
		self.states.append(new_state)
		return new_state

	def is_valid(self, string):
		self.current_state = self.start_state
		for char in string:
			self.current_state = self.current_state.transition[char]
		return self.current_state.accepting

	def scan(self, string):
		"""Scans "string", whose symbols are drawn from "alphabet", and returns a list of matches.  \
		If the string is s_1...s_n, and s_i...s_j is a match, then s_(j+1)...s_k will be in the list \
		iff k is the largest integer such that the NFA accepts s_(j+1)...s_k."""
		matches = []
		start_index = 0
		while start_index < len(string):
			best_match = self.longest_match(string[start_index:])
			if best_match == None or len(best_match.string) == 0:
				return matches
			else:
				matches.append(best_match)
				start_index += len(best_match.string)
		return matches

	def longest_match(self, string):
		best_match = None
		current_state = self.start_state
		for i in range(len(string)):
			current_state = current_state.transition[string[i]]
			if current_state:
				best_match = DFA.Match(string[:i+1], current_state.token_type)
			elif current_state.is_dead_end():
				return best_match
		return best_match

	def convert_states(self):
		translation = {state: NFA_State(accepting = state.accepting, starting = state.starting, token_type = state.token_type) for state in self.states}
		for state in self.states:
			for char in self.alphabet:
				translation[state].add_transition( char, translation[state.transition[char]] )
		return translation.values()

	def complement_DFA(self):
		for state in self.states:
			state.accepting = not state.accepting
		return self

	def __repr__(self):
		return "Start: " + str(self.start_state.number) + "\n" + "\n".join([str(s) for s in self.states])

class Translation:
	class Result:
		def __init__(self, dfa_state, unvisited):
			self.dfa_state = dfa_state
			self.unvisited = unvisited

	def __init__(self, dfa):
		self.dfa = dfa
		self.dead_end = dfa.add_state(accepting = False, token_type = [], dead_end = True)
		for char in dfa.alphabet:
			self.dead_end.add_transition(char, self.dead_end)
		self.nfa_to_dfa = { frozenset(): self.dead_end}

	def translate(self, states):
		if states in self.nfa_to_dfa:
			return Translation.Result(self.nfa_to_dfa[states], False)
		else:
			token_type = set(chain(*[s.token_type for s in states if s]))
			new_state = self.dfa.add_state(accepting = any(states), token_type = token_type)
			self.nfa_to_dfa[states] = new_state
			return Translation.Result(new_state, True)
