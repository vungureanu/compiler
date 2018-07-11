class CFG:
	def __init__(self, rules):
		if len(rules) == 0:
			raise NoStatic_RulesError
		self.tokens = set()

		self.rules = set(rules)
		start_variable = rules[0].lhs
		self.start_token = Token(name = "<start>", cfg = self)
		self.rules.add( Static_Rule(self.start_token, [start_variable], None) )
		for rule in rules:
			self.tokens.add(rule.lhs)
			for token in rule.rhs:
				self.tokens.add(token)
		self.simple_rules = set()
		self.complex_rules = set()

	def exists(self, expansion):
		for token in self.tokens:
			if token.expansion == expansion:
				return token
		return None 

	def add_simple_rule(self, variable, terminal, evaluation):
		new_rule = Static_Rule(variable, [terminal], lambda x: evaluation)
		self.rules.add(new_rule)
		self.simple_rules.add(new_rule)

	def convert_rules_to_CNF(self):
		"""Converts own list of rules into Chomsky normal form."""

		# Eliminate rules containing terminals, except those of the form A -> b
		convert = {}
		new_rules = set()

		for rule in self.rules:
			for terminal in filter(lambda token: token.name not in convert, rule.terminals()):
				t_var = Token(name = terminal.name + "v", token_type = "variable", cfg = self)
				t_rule = Static_Rule(t_var, [terminal], lambda a: None)
				new_rules.add(t_rule)
				convert[terminal.name] = t_var

		for rule in self.rules:
			rule.replace_terminals(convert)
		self.rules |= new_rules

		# Split rules of the form A -> B_0...B_n into rules of the form A -> B_0{B_1...B_n} and
		# {B_i...B_n} -> B_i{B_(i+1)...B_n} for i <= n-2
		new_rules = set()
		for rule in self.rules:
			if rule.is_too_large():
				rule.split_up(new_rules, self)
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
					nullables.add(rule.lhs)
					rule.lhs.set_nullable()

		new_rules = set()
		for rule in self.rules:
			rule.remove_nullables(new_rules)
		self.rules = {rule for rule in new_rules if rule.is_not_empty()}

		# Eliminate rules of the form A -> B, where B is a variable
		removed_rules = set()
		while remove_unit_rule(self.rules, removed_rules):
			pass

		self.simple_rules = {rule for rule in self.rules if len(rule.rhs) < 2}
		self.complex_rules = {rule for rule in self.rules if len(rule.rhs) >= 2}

	def is_normal(self):
		for rule in self.rules:
			if len(rule.rhs) > 2 or (len(rule.rhs) == 1 and rule.rhs[0].token_type == "variable") or (len(rule.rhs) == 0 and rule.lhs != start_token):
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
		if rule.lhs == unit_rule.rhs[0]:
			new_rule = rule.get_merger(unit_rule)
			if new_rule not in removed_rules:
				new_rules.add(new_rule)
	rules |= new_rules
	rules.remove(unit_rule)
	return True

class Rule:
	"""Represents a rule of the form A -> B_1...B_n, where each B_i is a variable or terminal token"""

	number = 0
	def __init__(self, lhs, rhs, evaluation, old_rule = None, match_function = None):
		"""Represents the rule A -> B_1...B_n iff "lhs" is the "Token" representing A and "rhs" is
		the list [C_1, ..., C_n], where C_i is either the "Token" or string representing B_i.
		"evaluation" is a function which maps the values of B_1, ..., B_n to the value of A.
		"""
		self.lhs = lhs
		self.rhs = rhs
		self.evaluation = evaluation
		self.old_rule = old_rule # the rule, if any, whose splitting up led to creation of present rule
		self.number = Static_Rule.number
		self.match_function = match_function
		Rule.number += 1

	def __eq__(self, other):
		if not isinstance(other, Static_Rule):
			return False
		return self.lhs == other.lhs and self.rhs == other.rhs

	def __repr__(self):
		string = self.lhs.name + " ->"
		for token in self.rhs:
			string += " " + token.name
		return string

	def __hash__(self):
		if len(self.rhs) > 2:
			return hash(tuple([self.lhs] + self.rhs))
		s = hash(self.lhs) * 2
		for token, prime in zip(self.rhs, [3, 5]):
			s += hash(token) * prime
		return s

	def is_too_large(self):
		return len(self.rhs) > 2

	def make_node(self, prefix, suffix = None):
		# If "suffix" is not None, then "prefix" and "suffix" are both "Parse_Node"s
		if len(self.rhs) == 1:
			if suffix != None:
				return None
			if self.rhs[0] != prefix:
				return None
			return Parse_Node(self.lhs, [prefix], self)
		if suffix != None and self.rhs[0] == prefix.lhs and self.rhs[1] == suffix.lhs:
			return Parse_Node(self.lhs, [prefix, suffix], self)

	def terminals(self):
		"""Returns list of non-solitary terminals"""
		terminals = filter(lambda t: t.token_type == "terminal", self.rhs)
		if len(self.rhs) > 1:
			return terminals
		else:
			return []

	def replace_terminals(self, convert):
		if len(self.rhs) == 1:
			return None
		for i in range(len(self.rhs)):
			token = self.rhs[i]
			if token.name in convert:
				self.rhs[i] = convert[token.name]

	def split_up(self, rules, cfg):
		names = [token.name for token in self.rhs]
		current_variable = self.lhs
		for i in range(len(self.rhs)-2):
			new_variable = cfg.exists(self.rhs[i+1:])
			if new_variable != None:
				rules.add( Static_Rule(current_variable, [self.rhs[i], new_variable], self.evaluation, old_rule = self) )
				return None
			else:
				new_variable = Token(expansion = self.rhs[i+1:], cfg = cfg)
				rules.add( Static_Rule(current_variable, [self.rhs[i], new_variable], self.evaluation, old_rule = self) )
				current_variable = new_variable
		rules.add( Static_Rule(current_variable, self.rhs[-2:], self.evaluation, old_rule = self) )
		return None

	def is_nullable(self):
		return all( (s.nullable for s in self.rhs) )

	def remove_nullables(self, rules, index = 0):
		for i in range(index, len(self.rhs)):
			if self.rhs[i].nullable:
				new_rule = self.copy()
				new_rule.rhs.pop(i)
				new_rule.remove_nullables(rules, index = i)
		rules.add(self)

class Static_Rule(Rule):
	def __init__(self, lhs, rhs, evaluation = None, old_rule = None):
		super().__init__(lhs, rhs, evaluation, old_rule = old_rule)

	def is_unit(self):
		return len(self.rhs) == 1 and self.rhs[0].token_type == "variable"

	def copy(self):
		return Static_Rule(self.lhs, list(self.rhs), self.evaluation, old_rule = self.old_rule)

	def is_not_empty(self):
		return len(self.rhs) > 0

	def get_merger(self, unit_rule):
		"""Combine self (rule of form B -> C_1...C_n) with "unit_rule" of form A -> B to yield A -> C_1...C_n"""
		return Static_Rule(unit_rule.lhs, self.rhs, self.evaluation, old_rule = self.old_rule)

class Dynamic_Rule(Rule):
	"""A rule whose right-hand side cannot be determined when program is started"""

	"""Useful for allowing rules of the form A -> t_1...t_n, where each t_i is a terminal token.  These
	may be provided by the user after program is started
	"""
	def __init__(self, lhs, evaluation, match_function):
		super().__init__(lhs, [], evaluation)
		self.match_function = match_function

	def make_node(self, prefix, suffix = []):
		if self.match_function(prefix, suffix):
			return Parse_Node(self.lhs, [prefix] + suffix, self)
		else:
			return None

	def get_merger(self, unit_rule):
		return Dynamic_Rule(unit_rule.lhs, self.evaluation, self.match_function)

	def is_unit(self):
		return False

	def is_nullable(self):
		return False

	def is_not_empty(self):
		return True

	def __hash__(self):
		return hash((self.lhs, self.evaluation, self.match_function))

	def __repr__(self):
		return str(self.lhs) + " -> ?"

class NoStatic_RulesError(Exception):
	def __init__(self):
		print("Error: no rules have been specified.")

class EmptyError(Exception):
	def __init__(self):
		print("Error: attempting to parse empty string.")

class CFG_Parser:
	""" Converts sequence of tokens into tree of "Parse_Node"s."""

	"""Given a sequence of "Token"s and/or strings, returns a list of all "Parse_Node"s which
	represent that sequence.  A "Parse_Node" (A, t, A -> t) represents the token t.
	If p = (A, ...) represents s_1...s_i and q = (B, ...) represents t_1...t_j, then
	(C, [p, q], C -> AB) represents s_1...s_it_1...t_j."""
	def __init__(self, cfg):
		self.cfg = cfg

	def parse(self, token_array):
		"""Converts a list of tokens into a list of "Parse_Node"s, each of which is the root of
		a derivation tree for that list of tokens."""

		length = len(token_array)
		if length == 0:
			raise EmptyError
		table = [ [set() for _ in range(length)] for _ in range(length) ]
		# table[i][j] consists of all derivations of the substring w_i...w_j, where j >= i
		for i in range(length):
			token = token_array[i]
			for rule in self.cfg.simple_rules:
				parse_node = rule.make_node(token)
				if parse_node != None:
					#print("Adding:", parse_node)
					table[i][i].add(parse_node)
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
						left_variables = []
						right_variables = []
						for left_node in prefix:
							for right_node in suffix:

								parse_node = rule.make_node(left_node, right_node)
								if parse_node != None:
									#print(left_node, right_node, "by", rule)
									full_s.add( parse_node )
		return [node for node in table[0][length-1] if node.lhs == self.cfg.start_token]

class Parse_Node:
	""" Represents a derivation yielded by a rule of the form A -> BC."""

	"""Represents a derivation of the form A -> D_1D_2, where D_1 and D_2 are derivations,
	or A -> b, where b is a terminal token.  In either case, "lhs" is the "Token" A.  In the
	former case, D_1 and D_2 are "Parse_Node"s, and "rule" is the rule A -> L_1L_2, where L_i
	is the left-hand side of D_i. in the latter case, b is a "Token" or a string, and "rule"
	is the rule A -> b."""
	def __init__(self, lhs, rhs, rule):
		self.lhs = lhs
		self.rhs = rhs
		self.rule = rule

	def is_abbreviation(self):
		# Returns whether derives variable of the form {A_1...A_n} 
		return self.lhs.is_abbreviation()

	def get_expansion(self):
		# Returns [A_1, ..., A_n] if derives variable of the form {A_1...A_n}
		return self.lhs.get_expansion()

	def unwind(self):
		# Returns [D_1, ..., D_n] if derives derivation of the form D_1D_2, where D_i derives D_{i+1}D_{i+2}
		# for i <= n-2, and D_i is of the form {...} for 2 <= i <= n-1.
		if not self.rhs[1].is_abbreviation():
			return self.rhs
		else:
			return [self.rhs[0]] + self.rhs[1].unwind()

	def unwind_tree(self):
		if len(self.rhs) == 1:
			return self
		if self.rhs[1].is_abbreviation():
			left_child = [self.rhs[0].unwind_tree()]
			right_child = [node.unwind_tree() for node in self.rhs[1].unwind()]
			return Parse_Node(self.lhs, left_child + right_child, self.rule.old_rule)
		else:
			children = [node.unwind_tree() for node in self.rhs]
			return Parse_Node(self.lhs, children, self.rule)

	def get_value(self):
		if len(self.rhs) == 1:
			return self.rule.evaluation(self.rhs[0])
		args = [node.get_value() for node in self.rhs]
		return self.rule.evaluation(args)

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

class Token:
	"""Represents a variable in the CFG's rule-set"""
	number = 0
	def __init__(self, name = None, expansion = None, token_type = None, cfg = None):
		# The expansion of a token {AB} is the list [A, B]
		if name != None:
			self.name = name
		elif expansion != None:
			self.name = "{" + "".join([s.name for s in expansion]) + "}"
		self.cfg = cfg
		self.nullable = False
		self.expansion = expansion
		self.token_type = token_type
		self.number = Token.number
		Token.number += 1

	def is_abbreviation(self):
		return self.expansion != None

	def get_expansion(self):
		return self.expansion

	def set_nullable(self):
		self.nullable = True

	def __eq__(self, other):
		if not isinstance(other, Token):
			return False
		return self.name == other.name and self.expansion == other.expansion and self.token_type == other.token_type

	def __hash__(self):
		if self.expansion == None:
			return hash((self.name, self.token_type, None))
		else:
			return hash((self.name, self.token_type) + tuple(self.expansion))

	def __repr__(self):
		return self.name

class Rule_Conversion:
	def __init__(self, rules, evaluations, additional_rules = None):
		"""Converts rules given in string form to rules given in canonical form."""

		"""A rule is a string of the form <x> -> w_1...w_n, where x is any alpha-numeric string, and each
		w_i is either of the form y or <y>, where y is an alpha-numeric string.  "additional_rules" is a list
		of rule in standard format."""
		self.rules = []
		self.translation = {}
		for rule, evaluation in zip(rules, evaluations):
			self.add_rule(rule, evaluation)
		if additional_rules != None:
			for rule in additional_rules:
				self.rules.append(Static_Rule(self.translation[rule[0]], [rule[1]], evaluation = rule[2]))

	def get_converted_rules(self):
		return self.rules

	def get_translation(self):
		return self.translation

	def add_rule(self, rule, evaluation, match_function = None):
		tokens = rule.split(" ")
		if len(tokens) == 0:
			raise InvalidRuleException(rule)
		token_list = []
		for token in tokens:
			if token == "_":
				# This allows the rule to be written more legibly
				token = " "
			if token not in self.translation:
				if token[0] == "<" and token[-1] == ">":
					self.translation[token] = Token(name = token, token_type = "variable")
				else:
					self.translation[token] = Token(name = token, token_type = "terminal")
			token_list.append(self.translation[token])
		self.rules.append(Static_Rule(token_list[0], token_list[1:], evaluation))

class InvalidRuleError(Exception):
	def __init__(self, rule):
		self.message = "Invalid rule: " + str(rule)
