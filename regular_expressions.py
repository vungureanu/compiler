from finite_automata import *
from context_free_grammars import *
from functools import partial

class Regular_Expression:
	rules = [
		"<exp> <exp> *",
		"<exp> <exp> ^",
		"<exp> <exp> | <exp>",
		"<exp> <exp> <exp>",
		"<exp> ( <exp> )",
		"<exp> <letter>"
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
			alphabet = {chr(i) for i in range(ord("a"), ord("c")+1)}
		letter_tokens = {Token(name = char, token_type = "terminal") for char in alphabet}
		letter_rules = [["<letter>", token, lambda t: NFA(alphabet, char_type = t.name)] for token in letter_tokens]
		rc = Rule_Conversion(Regular_Expression.rules, Regular_Expression.evaluations, additional_rules = letter_rules)
		cfg = CFG(rc.get_converted_rules())
		cfg.convert_rules_to_CNF()
		parser = CFG_Parser(cfg)
		interpretations = parser.parse([Token(name = s, token_type = "terminal") for s in string])
		# Each token is precisely one character long; no scanner is necessary
		if len(interpretations) == 0:
			raise NoValidInterpretation(string)
		# Choose an interpretation at random; it is up to the user to provide an unambiguous string
		self.dfa = interpretations[0].unwind_tree().get_value().convert()

	def test(self, string):
		return self.dfa.is_valid(string)

class NoValidInterpretation(Exception):
	def __init__(self, string):
		print("The string", string, "has no valid interpretation.")
