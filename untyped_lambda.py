from regular_expressions import *

class Lambda_Calculus:

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

	# Define valid words of language

	alphabet = {chr(i) for i in range(ord("a"), ord("z")+1)}
	digits = {str(i) for i in range(10)}
	special_symbols = {"λ", "(", ")", ".", " "}
	letter_nfas = [NFA({char}, char_type = char) for char in alphabet]
	variable_names = NFA.close_NFA(NFA.join_NFAs(letter_nfas), new_token_type = "variable")
	special_nfas = [NFA({char}, char_type = char, token_type = "special symbol") for char in special_symbols]
	digit_nfas = [NFA({digit}, char_type = digit) for digit in digits]
	number_nfa = NFA.close_NFA(NFA.join_NFAs(digit_nfas), new_token_type = "number")
	scanner = NFA.join_NFAs([variable_names] + special_nfas + digit_nfas).convert()

	def __init__(self):
		self.variables = {}
		self.keywords = {}
		# "variable_match" must refer to a different function for each member of Lambda_Calculus
		rc = Rule_Conversion(Lambda_Calculus.rules, Lambda_Calculus.evaluations)

		def variable_match(prefix, suffix):
			"""Returns the "Variable" named "prefix", if any such exists"""
			if isinstance(prefix, Token) and prefix.name in self.variables:
				return [prefix.name]
			return None

		def keyword_match(prefix, suffix):
			if isinstance(prefix, Token) and prefix.name in self.keywords:
				return [prefix.name]

		variable_conversion = Dynamic_Rule(rc.get_translation()["<var>"], lambda v: self.variables[v], variable_match)
		keyword_parsing = Dynamic_Rule(rc.get_translation()["<exp>"], lambda kw: self.keywords[kw], keyword_match)

		self.cfg = CFG(rc.get_converted_rules() + [variable_conversion, keyword_parsing])
		self.cfg.convert_rules_to_CNF()
		self.parser = CFG_Parser(self.cfg)
		self.keywords = {
			"fix" : None,
			"succ" : self.parse("(λn.λf.λx.(f ((n f) x)))"),
			"mul" : self.parse("(λm.λn.λf.λx.((m f) ((n f) x)))"),
			"0" : self.parse("λf.λx.x")
		}

	def parse(self, string):
		tokens = []
		for token in Lambda_Calculus.scanner.scan(string):
			if token.string in self.keywords:
				tokens.append(Token(name = token.string))
			elif "variable" in token.token_type:
				if token.string in self.variables:
					tokens.append(Token(name = token.string))
				else:
					new_variable = Variable(name = token.string)
					self.variables[token.string] = new_variable
					tokens.append(Token(name = token.string))
			else:
				tokens.append(token.string)
		interpretations = self.parser.parse(tokens)
		if len(interpretations) == 0:
			raise InvalidParseStringError(string)
		return interpretations[0].unwind_tree().get_value()

	def define(self, variable, string):
		self.keywords[variable] = self.parse("(" + string + ")")
		
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
		return self.function.simplify().evaluate(self.argument.simplify())

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
		return self.body.substitute(argument, self.variable).simplify()

	def simplify(self):
		return Abstraction(self.variable, self.body.simplify())

	def __repr__(self):
		return "(λ" + str(self.variable) + "." + str(self.body) + ")"

class InvalidParseStringError(Exception):
	def __init__(self, string):
		print("The string", string, "cannot be parsed.")
