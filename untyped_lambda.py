from regular_expressions import *

class Lambda_Rules:
	rules = [
		"<exp> -> λ<var>.<exp>",
		"<exp> -> <exp> <exp>",
		"<exp> -> (<exp>)",
		"<exp> -> <var>"
	]
	evaluations = [
		lambda args: Abstraction(variable = args[1], body = args[3]),
		lambda args: args[0].evaluate(args[2]),
		lambda args: args[1],
		lambda args: None
	]

	alphabet = {chr(i) for i in range(ord("a"), ord("z")+1)}
	special_symbols = {"λ", "(", ")", ".", " "}
	letter_nfas = [NFA({char}, char_type = char) for char in alphabet]
	variable_names = NFA.close_NFA(NFA.join_NFAs(letter_nfas), new_token_type = "variable")
	special_nfas = [NFA({char}, char_type = char, token_type = char) for char in special_symbols]
	scanner = NFA.join_NFAs(letter_nfas + special_nfas).convert()

	def __init__(self):
		self.variables = {}
		rc = Rule_Conversion(Lambda_Rules.rules, Lambda_Rules.evaluations)

		def variable_match(prefix, suffix):
			"""Returns the "Variable" named "prefix", if any such exists"""
			if isinstance(prefix, Token) and prefix.name in self.variables:
				return [self.variables[prefix.name]]
			return None

		vc = Dynamic_Rule(rc.get_translation()["<var>"], lambda x: x, variable_match)
		self.cfg = CFG(rc.get_converted_rules() + [vc])
		self.cfg.convert_rules_to_CNF()
		self.parser = CFG_Parser(self.cfg)

	def parse(self, string):
		tokens = []
		for token in Lambda_Rules.scanner.scan(string):
			if "variable" in token.token_type:
				if token in self.variables:
					tokens.append(self.variables[token])
				else:
					new_variable = Variable(name = token.string)
					self.variables[token.string] = new_variable
					tokens.append(Token(name = token.string, stype = "variable"))
			else:
				tokens.append(token.string)
		return self.parser.parse(tokens)[0].unwind_tree().get_value()
		
class Lambda_Expression:

	def abstract(self, variable):
		return Abstraction(variable, self)

	def can_be_simplified(self):
		return False

	def simplify(self):
		return self

class Variable(Lambda_Expression):
	number = 1
	def __init__(self, name = None):
		if name == None:
			self.name = "v_" + str(Variable.number)
		else:
			self.name = name
		self.free_variables = {self}
		self.number = Variable.number
		Variable.number += 1

	def substitute(self, replacer, replacee):
		if self == replacee:
			return replacer
		else:
			return self

	def replace_variable(self, replacer, replacee):
		if self == replacee:
			return replacer
		else:
			return self

	def evaluate(self, argument):
		return Application(self, argument)

	def __eq__(self, other):
		if isinstance(other, Variable):
			return self.name == other.name
		else:
			return False

	def __hash__(self):
		return self.number

	def __repr__(self):
		return self.name

class Application:
	def __init__(self, function, argument):
		self.function = function
		self.argument = argument
		self.free_variables = function.free_variables | argument.free_variables
		self.number = max(function.number, argument.number)

	def substitute(self, replacer, replacee):
		result = Application( self.function.substitute(replacer, replacee), self.argument.substitute(replacer, replacee) )
		return result

	def replace_variable(self, replacer, replacee):
		result = Application( self.function.replace_variable(replacer, replacee), self.argument.replace_variable(replacer, replacee) )
		return result

	def evaluate(self, argument):
		return Application(self, argument)

	def can_be_simplified(self):
		return isinstance(self.function, Abstraction)		

	def simplify(self):
		if isinstance(self.function, Abstraction):
			return self.function.evaluate(self.argument)
		else:
			return Application(self.function.simplify(), self.argument.simplify())

	def __repr__(self):
		return "(" + str(self.function) + " " + str(self.argument) + ")"

class Abstraction(Lambda_Expression):
	def __init__(self, variable, body):
		self.variable = variable
		self.body = body
		self.number = max(variable.number, body.number)
		self.free_variables = body.free_variables - {variable}

	def substitute(self, replacer, replacee):
		if replacee == self.variable:
			return self
		elif self.variable not in replacer.free_variables:
			return Abstraction(self.variable, self.body.substitute(replacer, replacee))
		else:
			new_bound_variable = Variable()
			self.variable = new_bound_variable
			self.body = self.body.replace_variable(self.variable, new_bound_variable)
			return Abstraction(self.variable, self.body.substitute(replacer, replacee))

	def replace_variable(self, replacer, replacee):
		if self.variable != replacee:
			return self.body.replace_variable(replacer, replacee)

	def evaluate(self, argument):
		result = self.body.substitute(argument, self.variable)
		while result.can_be_simplified():
			result = result.simplify()
		return result

	def __repr__(self):
		return "(λ" + str(self.variable) + "." + str(self.body) + ")"
