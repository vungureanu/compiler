class CFG:
	def __init__(self, rules):
		self.rules = []
		self.variables = set()
		for rule in rules:
			lhs = rule.split(":")[0]
			rhs = rule.split(":")[1]
			if lhs in self.rules:
				self.rules[lhs].append(rhs)
			else:
				self.rules[lhs] = [rhs]
			self.variables.add(lhs)

	def convert_rules_to_CNF(self):
		"""Converts own list of rules into Chomsky normal form."""
		new_rules = set()
		removed_rules = set()
		for rule in self.rules:
			if rule.lhs != start_variable and rule.rhs == [empty_symbol]:
				new_rules |= self.remove_occurrences(rule.lhs, self.rules, removed_rules)
				removed_rules.add(rule)
		self.rules = (self.rules | new_rules) - removed_rules

		new_rules = set()
		removed_rules = set()
		for rule in self.rules:
			if len(rule.rhs) == 1 and rule.rhs[0].stype == "variable":
				new_rules |= self.modify_occurrences(rule.lhs, rule.rhs[0], self.rules, removed_rules)
				removed_rules.append(rule)
		self.rules = (self.rules | new_rules) - removed_rules

		new_rules = set()
		for rule in self.rules:
			if len(rule.rhs) >= 3:
				new_rules |= self.split_up(rule)
		self.rules = new_rules

	def remove_occurrences(self, v, rules, removed_rules):
		"""Generates new rules by removing occurrences of v from the RHS of old rules.

		Returns a set S of rules.  For every set of occurrences of v on the right-hand side
		of a rule R in "rules", the rule obtained by removing exactly those occurrences
		from R is in S, except if R is X -> v and X -> ε is in "removed_rules"."""
		for rule in rules:
			new_rules = [ Rule(rule.lhs, []) ]
			if rule.rhs == [v]:
				if (Rule(rule.lhs, []) in removed_rules):
					continue
			for symbol in rule.rhs:
				for new_rule in new_rules:
					if symbol == v:
						new_rules.append(new_rule.copy())
					new_rule.rhs.append(symbol)
		return set(new_rules)

	def modify_occurrences(self, v1, v2, rules, removed_rules):
		new_rules = set()
		for rule in filter(lambda rule: rule.lhs == v2, rules):
			new_rule = Rule(v1, rule.rhs)
			if new_rule not in removed_rules:
				new_rules.add(new_rule)
		return new_rules

	def split_up(self, rule):
		new_rules = set()
		rhs_variables = []
		for symbol in rule.rhs:
			if symbol.stype == "variable":
				rhs_variables.append(symbol)
			else:
				new_var = Symbol("terminal_to_variable", "variable")
				rhs_variables.append(new_var)
				new_rules.append( Rule(new_var, [symbol]) )
		lhs = rule.lhs
		for v in rhs_variables[:-1]:
			aux_var = Symbol("auxiliary_variable", "variable")
			new_rules.append(Rule(lhs, [v, aux_var]))
			lhs = v

class Rule:
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs

	def __eq__(self, other):
		return self.lhs == other.lhs and self.rhs == other.rhs

	def copy(self):
		return Rule(self.lhs, self.rhs)

class NPDA:
	def __init__(self, cfg):
		self.cfg = cfg
	def parse_input(symbol_array, cfg):
		self.possible_states = [new Possible_State([], symbol_array)]
		# Each state consists of the remaining input and the stack
		while len(possible_states) > 0:
			for i in range(len(possible_states)):
				state = possible_states.pop(0)
				next_symbol = state.remaining_input.pop(0)
				if next_symbol.number in cfg.variables:
					for rule in cfg.rules[next_symbol.number]:
						possible_states.append(new Possible_State(rule + stack, state.remaining_input))
				else:
					while next_symbol.number == state[0]:

class CFG_Parser:
	def __init__(self, cfg):
		self.cfg = cfg
	def parse(self, symbol_array):
		# The input consists of symbols w_0w_1...w_n, where w_i = symbol_array[i]
		l = len(symbol_array)
		table = [ [set() for _ in range(l)] for _ in range(l) ]
		# table[i][j] consists of all derivations of the substring w_i...w_j, where j >= i
		if len(symbol_array) == 0:
			if empty_symbol in self.cfg.start_variable:
				return True
			else:
				return False
		for i in range(l):
			symbol = symbol_array[i]
			for rule in cfg.rules:
				if symbol == rule.rhs:
					table[i][i] = Parse_Node(rule, [])
		for i in range(l-1):
			for j in range(i, l-1):
				for k in range(j+1, l):
					prefix = table[i][j]
					suffix = table[j+1][k]
					full_s = table[i][k]
					for rule in cfg.complex_rules:
						if (rule.rhs[0] in prefix) and (rule.rhs[1] in suffix):
							full_s.add(Parse_Node(rule, [prefix, suffix]))
		if cfg.start_variable in table[1][n]:
			return True
		else:
			return False

class Parse_Node:
	def __init__(self, rule, children):
		self.rule = rule
		self.children = children

class Symbol:
	number = 0
	def __init__(self, name, stype):
		self.number = Symbol.number
		Symbol.number += 1
		self.name = name
		self.stype = stype

	def __eq__(self, other):
		return self.number == other.number

class Possible_State:
	def __init__(self, stack, remaining_input):
		self.stack = stack
		self.remaining_input = remaining_input

lambda_calculus = CFG(["Start:Exp"], ["Start:Var"], ["Exp:(L.Var Exp)"], ["Exp:(Exp Exp)"])