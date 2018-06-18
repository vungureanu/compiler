class CFG:
	def __init__(self, rules):
		if len(rules) == 0:
			raise NoRulesError
		self.symbols = set()
		self.rules = set(rules)
		start_variable = rules[0].get_lhs()
		self.start_symbol = Symbol(name = "<start>", stype = "variable")
		self.rules.add(Rule(self.start_symbol, [start_variable]))
		for rule in rules:
			self.symbols.add(rule.get_lhs())
			for symbol in rule.get_rhs():
				self.symbols.add(symbol)
		self.simple_rules = set()
		self.complex_rules = set()

	def convert_rules_to_CNF(self):
		"""Converts own list of rules into Chomsky normal form."""

		# Eliminate rules containing terminals, except those of the form A -> b
		convert = {}
		new_rules = set()

		for rule in self.rules:
			for terminal in filter(lambda t : t not in convert, rule.terminals()):
				t_var = Symbol( name = "_" + terminal.name, stype = "variable")
				t_rule = Rule(t_var, [terminal])
				new_rules.add(t_rule)
				convert[terminal] = t_var

		for rule in self.rules:
			rule.replace_terminals(convert)
		self.rules |= new_rules

		# Split rules of the form A -> B_0...B_n into rules of the form A -> B_0{B_1...B_n} and
		# {B_i...B_n} -> B_i{B_(i+1)...B_n} for i <= n-2
		new_rules = set()
		for rule in self.rules:
			if rule.is_too_large():
				rule.split_up(new_rules)
			else:
				new_rules.add(rule)
		self.rules = new_rules

		# Eliminate rules of the form A -> ε 
		nullables = set()
		old_len = -1
		while len(nullables) > old_len:
			old_len = len(nullables)
			for rule in self.rules:
				if rule.is_nullable():
					nullables.add(rule.get_lhs())
					rule.get_lhs().set_nullable()

		new_rules = set()
		for rule in self.rules:
			rule.remove_nullables(new_rules)
		self.rules = {rule for rule in new_rules if len(rule.get_rhs()) > 0}

		# Eliminate rules of the form A -> B, where B is a variable
		removed_rules = set()
		while remove_unit_rule(self.rules, removed_rules):
			pass

		for rule in self.rules:
			if len(rule.get_rhs()) == 1:
				self.simple_rules.add(rule)
			else:
				self.complex_rules.add(rule)

	def is_normal(self):
		for rule in self.rules:
			rhs = rule.get_rhs()
			lhs = rule.get_lhs()
			if len(rhs) > 2 or (len(rhs) == 1 and rhs[0].stype == "variable") or (len(rhs) == 0 and lhs.stype != "start"):
				return False
		return True

def remove_unit_rule(rules, removed_rules):
	unit_rule = None
	for rule in rules:
		if rule.is_unit():
			unit_rule = rule
			removed_rules.add(rule)
			break
	if unit_rule == None:
		return False
	new_rules = set()
	for rule in rules:
		if rule.get_lhs() == unit_rule.get_rhs()[0]:
			if rule.old_rule == None:
				old_rule = None
			else:
				old_rule = rule.old_rule.copy()
				old_rule.lhs = unit_rule.get_lhs()
			new_rule = Rule(unit_rule.get_lhs(), rule.get_rhs(), old_rule = old_rule)
			if new_rule not in removed_rules:
				new_rules.add(new_rule)
	rules |= new_rules
	rules.remove(unit_rule)
	return True

class Rule:
	number = 0
	def __init__(self, lhs, rhs, old_rule = None):
		print("Adding rule:", lhs, "->", rhs)
		self.lhs = lhs
		self.rhs = rhs
		self.number = Rule.number
		self.old_rule = old_rule # the rule, if any, whose splitting up led to creation of present rule
		Rule.number += 1

	def __eq__(self, other):
		if not isinstance(other, Rule):
			return False
		return self.lhs == other.lhs and self.rhs == other.rhs

	def __repr__(self):
		string = self.lhs.name + " ->"
		for symbol in self.rhs:
			string += " " + symbol.name
		return string

	def __hash__(self):
		if len(self.rhs) > 2:
			return hash(tuple([self.lhs] + self.rhs))
		s = hash(self.lhs) * 2
		for symbol, prime in zip(self.rhs, [3, 5]):
			s += hash(symbol) * prime
		return s

	def get_lhs(self):
		return self.lhs

	def get_rhs(self):
		return self.rhs

	def set_lhs(lhs):
		self.lhs = lhs

	def is_too_large(self):
		return len(self.rhs) > 2

	def is_unit(self):
		return len(self.rhs) == 1 and self.rhs[0].stype == "variable"

	def copy(self):
		return Rule(self.lhs, list(self.rhs), old_rule = self.old_rule)

	def terminals(self):
		"""Returns list of non-solitary terminals"""
		terminals = filter(lambda s: s.stype == "terminal", self.rhs)
		if len(self.rhs) > 1:
			return terminals
		else:
			return []

	def replace_terminals(self, convert):
		if len(self.rhs) == 1:
			return None
		for i in range(len(self.rhs)):
			symbol = self.rhs[i]
			if symbol in convert:
				self.rhs[i] = convert[symbol]

	def split_up(self, rules):
		names = [symbol.name for symbol in self.rhs]
		current_symbol = self.lhs
		for i in range(len(self.rhs)-2):
			new_symbol = Symbol.exists(self.rhs[i+1:])
			if new_symbol != None:
				rules.add( Rule(current_symbol, [self.rhs[i], new_symbol], old_rule = self) )
				return None
			else:
				new_symbol = Symbol(expansion = self.rhs[i+1:])
				rules.add( Rule(current_symbol, [self.rhs[i], new_symbol], old_rule = self) )
				current_symbol = new_symbol
		rules.add( Rule(current_symbol, self.rhs[-2:], old_rule = self) )
		return None

	def is_nullable(self):
		return all( map(lambda s: s.is_nullable(), self.rhs) )

	def remove_nullables(self, rules, index = 0):
		for i in range(index, len(self.rhs)):
			if self.rhs[i].is_nullable():
				new_rule = self.copy()
				new_rule.rhs.pop(i)
				new_rule.remove_nullables(rules, index = i)
		rules.add(self)


class NoRulesError(Exception):
	def __init__(self):
		print("Error: no rules have been specified.")

class EmptyError(Exception):
	def __init__(self):
		print("Error: attempting to parse empty string.")

class CFG_Parser:
	def __init__(self, cfg):
		self.cfg = cfg
		self.roots = [] # All possible ways of parsing statement

	def parse(self, symbol_array):
		# The input consists of symbols w_0w_1...w_(length-1), where w_i = symbol_array[i]
		length = len(symbol_array)
		if length == 0:
			raise EmptyError
		table = [ [set() for _ in range(length)] for _ in range(length) ]
		# table[i][j] consists of all derivations of the substring w_i...w_j, where j >= i
		for i in range(length):
			symbol = symbol_array[i]
			for rule in self.cfg.simple_rules:
				if rule.get_rhs() == [symbol]:
					table[i][i].add( Parse_Node(rule.get_lhs(), [symbol], rule) )
		# We will search for progressively longer derivations of the form A -> BC in the table.
		# The derivations of the each of the three terms will span the following ranges:
		# A: [i, i+l-1]
		# B: [i, j-1]
		# C: [j-1, i+l-1]
		# We must have i+l-1 <= length-1, and so i <= length-l.
		for l in range(2, length+1):
			for i in range(length-l+1):
				for j in range(i+1, i+l):
					prefix = table[i][j-1]
					suffix = table[j][i+l-1]
					full_s = table[i][i+l-1]
					for rule in self.cfg.complex_rules:
						lhs = rule.get_lhs()
						rhs = rule.get_rhs()
						left_variables = []
						right_variables = []
						for node in prefix:
							if node.lhs == rhs[0]:
								left_variables.append(node)
						for node in suffix:
							if node.lhs == rhs[1]:
								right_variables.append(node)
						for left_variable in left_variables:
							for right_variable in right_variables:
								full_s.add( Parse_Node(lhs, [left_variable, right_variable], rule) )
		self.roots = [node for node in table[0][l-1] if node.lhs == self.cfg.start_symbol]
		return self.roots

class Evaluator:
	def __init__(self, functions, terminal_values):
		self.functions = functions
		self.terminal_values = terminal_values

	def get_value(node):
		# Evaluates the tree whose root is "node"
		if node.is_unitary():
			return self.terminal_values(node.rhs[0])
		args = [get_value(node) for node in self.rhs]
		return functions[node.rule](args)

class Parse_Node:
	# Represents a derivation of the form A -> D_1D_2, where D_1 and D_2 are derivations,
	# or A -> b, where b is a terminal symbol.
	def __init__(self, lhs, rhs, rule):
		self.lhs = lhs
		self.rhs = rhs
		self.expansion = []
		self.rule = rule

	def is_unitary():
		return len(self.rhs) == 1

	def has_abbreviation(self):
		# Returns whether represents derivation of the form A -> B{CD}
		if len(self.rhs) < 2:
			return False
		return self.rhs[1].is_abbreviation()

	def is_abbreviation(self):
		# Returns whether derives variable of the form {A_1...A_n} 
		return self.lhs.is_abbreviation()

	def get_expansion(self):
		# Returns [A_1, ..., A_n] if derives variable of the form {A_1...A_n}
		return self.lhs.get_expansion()

	def unwind(self):
		if not self.rhs[1].is_abbreviation():
			return self.rhs
		else:
			return [self.rhs[0]] + self.rhs[1].unwind()

	def produce_original_tree(self):
		if len(self.rhs) == 1:
			return self.rhs
		if self.rhs[1].is_abbreviation():
			left_child = [self.rhs[0].produce_original_tree()]
			right_child = [node.produce_original_tree() for node in self.rhs[1].unwind()]
			return Parse_Node(self.lhs, left_child + right_child, self.rule.old_rule)

		else:
			children = [node.produce_original_tree() for node in self.rhs]
			return Parse_Node(self.lhs, children, self.rule)

	def __repr__(self):
		if len(self.rhs) > 1:
			return str(self.lhs) + " -> " + str(self.rhs)
		else:
			return str(self.rhs[0])

	def __eq__(self, other):
		if not isinstance(other, Parse_Node):
			return False
		return self.lhs == other.lhs and self.rhs == other.rhs

	def __hash__(self):
		if len(self.rhs) == 1:
			return hash((self.lhs, self.rhs[0]))
		else:
			return hash((self.lhs, self.rhs[0], self.rhs[1]))

class Symbol:
	number = 0
	symbols = [] # contains all symbols without duplicates
	def __init__(self, name = None, stype = None, expansion = None):
		# The expansion of a symbol {AB} is the list [A, B]
		print("Creating symbol:", name, expansion)
		self.number = Symbol.number
		Symbol.number += 1
		if name != None:
			self.name = name
		elif expansion != None:
			self.name = "{" + "".join([s.name for s in expansion]) + "}"
		self.stype = stype
		self.nullable = False
		self.expansion = expansion
		Symbol.symbols.append(self)

	def exists(expansion):
		for symbol in Symbol.symbols:
			if symbol.expansion == expansion:
				return symbol
		return None 

	def is_abbreviation(self):
		return self.expansion != None

	def get_expansion(self):
		return self.expansion

	def set_nullable(self):
		self.nullable = True

	def is_nullable(self):
		return self.nullable

	def __eq__(self, other):
		if not isinstance(other, Symbol):
			return False
		return self.number == other.number

	def __hash__(self):
		return self.number

	def __repr__(self):
		return self.name