from finite_automata import *
from context_free_grammars import *
from functools import partial

class Regular_Expression:
	rules = [
		"<exp> -> <exp>*",
		"<exp> -> <exp>^",
		"<exp> -> <exp>|<exp>",
		"<exp> -> <exp><exp>",
		"<exp> -> (<exp>)",
		"<exp> -> <letter>"
	]
	evaluations = [
		lambda args: NFA.close_NFA(args[0]),
		lambda args: NFA.complement_NFA(args[0]),
		lambda args: NFA.join_NFAs([args[0], args[2]]),
		lambda args: NFA.concatenate_NFAs(args[0], args[1]),
		lambda args: args[1],
		None
	]

	def __init__(self, string, alphabet = None):
		if alphabet == None:
			alphabet = {chr(_) for _ in range(ord("a"), ord("c")+1)}
		letter_rules = [["<letter>", char, lambda l: NFA(alphabet, char_type = l)] for char in alphabet]
		rc = Rule_Conversion(Regular_Expression.rules, Regular_Expression.evaluations, additional_rules = letter_rules)
		cfg = CFG(rc.get_converted_rules())
		cfg.convert_rules_to_CNF()
		parser = CFG_Parser(cfg)
		interpretations = parser.parse(string)
		if len(interpretations) == 0:
			raise NoValidInterpretation(string)
		# Choose an interpretation at random; if the string was properly specified, they should all be correct
		self.dfa = interpretations[0].unwind_tree().get_value().convert()

	def test(self, string):
		return self.dfa.is_valid(string)

class NoValidInterpretation(Exception):
	def __init__(self, string):
		print("The string", string, "has no valid interpretation.")
