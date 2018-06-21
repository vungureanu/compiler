from finite_automata import *
from context_free_grammars import *
from functools import partial

class Regular_Expression:
	rules = []
	terminal_symbols = ["(", ")", "*", "|"]
	letters = [chr(i) for i in range(97, 100)]
	alphabet = {Symbol(char, "terminal") for char in letters}
	for char_s in alphabet:
		char_s.value = partial(lambda x: NFA(Regular_Expression.alphabet, char_type = x), char_s)
	variables = ["<letter>", "<word>", "<exp>"]
	translation = {}
	for char in terminal_symbols:
		translation[char] = Symbol(char, "terminal")
	for char, char_s in zip(letters, alphabet):
		translation[char] = char_s
	for variable in variables:
		translation[variable] = Symbol(variable, "variable")
	rule_schemas = [
		"<exp> -> (<exp>)*",
		"<exp> -> <exp>|<exp>",
		"<exp> -> <exp><exp>",
		"<exp> -> <word>",
		"<word> -> <letter><word>",
		"<word> -> <letter>"
	]
	evaluations = [
		lambda args: NFA.close_NFA(args[1]),
		lambda args: NFA.join_NFAs(args[0], args[2]),
		lambda args: NFA.concatenate_NFAs(args[0], args[1]),
		None,
		lambda args: NFA.concatenate_NFAs(args[0], args[1]),
		None
	]

	def __init__(self, string):
		self.string = [Regular_Expression.translation[char] for char in string]
		interpretations = Regular_Expression.parser.parse(self.string)
		if len(interpretations) == 0:
			raise NoValidInterpretation(string)
		# Choose an interpretation at random; if the string was properly specified, they should all be correct
		self.dfa = interpretations[0].unwind_tree().get_value().convert()

	def test(self, string):
		return self.dfa.is_valid([Regular_Expression.translation[char] for char in string])

	def add_rule(rule, evaluation, rules, translation):
		lhs_string, rhs_string = rule.split(" -> ")
		rhs = []
		current_string = ""
		flag = False
		for char in rhs_string:
			if flag:
				current_string += char
				if char == ">":
					rhs.append(translation[current_string])
					current_string = ""
					flag = False

			else:
				if char == "<":
					current_string = "<"
					flag = True
				else:
					rhs.append(translation[char])
		rules.append(Rule(translation[lhs_string], rhs, evaluation))

	for rule, evaluation in zip(rule_schemas, evaluations):
		add_rule(rule, evaluation, rules, translation)
	for char in letters:
		rules.append(Rule(translation["<letter>"], [translation[char]], None))
	cfg = CFG(rules)
	cfg.convert_rules_to_CNF()
	parser = CFG_Parser(cfg)

class NoValidInterpretation(Exception):
	def __init__(self, string):
		print("The string", string, "has no valid interpretation.")
