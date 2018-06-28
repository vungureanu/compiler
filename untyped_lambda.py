from regular_expressions import *

class Lambda_Calculus:

	rules = [
		"<exp> -> λ<var>.<exp>",
		"<exp> -> <exp> <right>",
		"<right> -> λ<var>.<exp>",
		"<right> -> (<exp>)",
		"<exp> -> <right>",
		"<right> -> <var>"
	]
	evaluations = [
		lambda args: Abstraction(variable = args[1], body = args[3]),
		lambda args: Application(args[0], args[2]),
		lambda args: Abstraction(variable = args[1], body = args[3]),
		lambda args: args[1],
		lambda args: None,
		lambda args: None
	]

	# Define valid words of language

	alphabet = [chr(i) for i in range(ord("a"), ord("z")+1)]
	digits = {str(i) for i in range(10)}
	special_symbols = {"λ", "(", ")", ".", " "}
	letter_nfas = [NFA({char}, char_type = char) for char in alphabet]
	variable_names = NFA.close_NFA(NFA.join_NFAs(letter_nfas), new_token_type = "variable")
	special_nfas = [NFA({char}, char_type = char, token_type = "special symbol") for char in special_symbols]
	digit_nfas = [NFA({digit}, char_type = digit) for digit in digits]
	number_nfa = NFA.close_NFA(NFA.join_NFAs(digit_nfas), new_token_type = "number")
	scanner = NFA.join_NFAs([variable_names] + special_nfas + digit_nfas).convert()

	def __init__(self, recursion_limit = 300):
		self.recursion_limit = recursion_limit
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
		keyword_parsing = Dynamic_Rule(rc.get_translation()["<right>"], lambda kw: self.keywords[kw], keyword_match)

		x = Expression_Type("x", None)
		f = Expression_Type(x, x)
		nat = Expression_Type(f, f)
		succ = Expression_Type(nat, nat)

		self.cfg = CFG(rc.get_converted_rules() + [variable_conversion, keyword_parsing])
		self.cfg.convert_rules_to_CNF()
		self.parser = CFG_Parser(self.cfg)
		self.define("succ", "λn.λf.λx.(f (n f x))", expression_type = succ)
		#self.define("pow", "λa.λb.(b a)")
		self.define("0", "λa.λb.b", expression_type = nat)
		self.define("plus", "λm.λn.(m succ n)")
		self.define("mul", "λm.λn.λf.(m (n f))")
		self.define("pred", "λn.λf.λx.(n (λg.λh.(h (g f))) (λu.x) (λu.u))")
		self.define("true", "λx.λy.x")
		self.define("false", "λx.λy.y")
		self.define("and", "λp.λq.(p q p)")
		self.define("or", "λp.λq.(p p q)")
		self.define("not", "λp.(p false)")
		self.define("ternary", "λp.λa.λb.(p a b)")
		self.define("iszero", "λn.(n (λx.false) true)")
		#self.define("fac", "λr.λn.(ternary (iszero n) 0 ((r r (pred n))))")
		self.define("fac", "λf.λn.(ternary (iszero n) (succ 0) (mul n (f (pred n))))")
		self.define("fix", "λf.((λx.(f (x x))) (λx.(f (x x))))", simplify = False)
		self.define("1", "succ 0")
		self.define("2", "succ 1")
		self.define("3", "succ 2")
		#self.parse("mul 2 2", verbose = True)
		#print(self.parse("(mul n (f (pred n))) n"))
		print("OK:", self.parse("fix fac (succ (succ 0))", verbose = False))
		#self.simplify(self.parse("mul 2 2", simplify = False), verbose = True)
		print("-----")
		#self.parse("ternary (iszero 0) 0 (pow 3 3)", True)
		#print("OK:", self.parse("(fac fac) (succ (succ 0))", True))

	def parse(self, string, verbose = False, simplify = True):
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
		elif len(interpretations) > 1:
			print("Warning:", string, "has", len(interpretations), "interpretations; choosing one at random")
		result = interpretations[0].unwind_tree().get_value()
		if simplify:
			return self.simplify(result, verbose = verbose)
		else:
			return result

	def define(self, variable, string, simplify = True, expression_type = None):
		self.keywords[variable] = self.parse(string, simplify = simplify)
		self.keywords[variable].expression_type = expression_type

	def simplify(self, value, verbose = False, count = None):
		if count == None:
			count = self.recursion_limit
		if verbose:
			value.describe()
			print()
		while value.can_be_simplified():
			value = value.simplify_step()
			if verbose:
				value.describe()
				print()
			count -= 1
			if count == 0:
				break
		return value
		
class Lambda_Expression:

	def abstract(self, variable):
		return Abstraction(variable, self)

	def can_be_simplified(self):
		return False

	def simplify_step(self, count = 10, verbose = False):
		return self

	def __eq__(self, other):
		return self.is_equal(other, {})

class Variable(Lambda_Expression):
	number = 1
	def __init__(self, name = None, expression_type = None):
		if name == None:
			self.name = "v_" + str(Variable.number)
		else:
			self.name = name
		self.expression_type = expression_type
		self.free_variables = {self}
		self.variable_names = {name}
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

	def describe(self):
		print("Simple variable:", self)

	def is_equal(self, other, translation):
		if not isinstance(other, Variable):
			return False
		if self in translation:
			return translation[self] == other
		else:
			return self == other

class Application:
	def __init__(self, function, argument, expression_type = None):
		self.function = function
		self.argument = argument
		if (expression_type != None):
			self.expression_type = expression_type
		elif self.function.expression_type != None and self.argument.expression_type != None:
			self.expression_type = self.function.expression_type.apply_to(self.argument.expression_type)
		else:
			self.expression_type = None
		self.free_variables = function.free_variables | argument.free_variables
		self.variable_names = function.variable_names | argument.variable_names
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
		return isinstance(self.function, Abstraction) or self.function.can_be_simplified() or self.argument.can_be_simplified()		

	def simplify_step(self):
		if isinstance(self.function, Abstraction):
			return self.function.evaluate(self.argument)
		elif self.function.can_be_simplified():
			return Application(self.function.simplify_step(), self.argument)
		elif self.argument.can_be_simplified():
			return Application(self.function, self.argument.simplify_step())
		else:
			raise CannotSimplifyError

	#def simplify_step(self):
	#	if self.expression_type != None:
	#		result = self.function.simplify().evaluate(self.argument.simplify())
	#		result.expression_type = self.expression_type

	def is_equal(self, other, translation):
		if not isinstance(other, Application):
			return False
		return self.function.is_equal(other.function, translation) and self.argument.is_equal(other.argument, translation)

	def describe(self):
		print("Function:", type(self.function), self.function)
		print("Argument:", type(self.argument), self.argument)

	def __repr__(self):
		if isinstance(self.function, Abstraction) or not isinstance(self.argument, Variable):
			return str(self.function) + " (" + str(self.argument) + ")"
		else:
			return str(self.function) + " " + str(self.argument)

class Abstraction(Lambda_Expression):
	def __init__(self, variable, body, expression_type = None):
		self.variable = variable
		self.body = body
		self.expression_type = expression_type
		self.number = max(variable.number, body.number)
		self.free_variables = body.free_variables - {variable}
		self.variable_names = body.variable_names | {variable.name}

	def substitute(self, replacer, replacee):
		if replacee == self.variable or replacee.name not in self.variable_names:
			return self
		elif self.variable not in replacer.free_variables:
			return Abstraction(self.variable, self.body.substitute(replacer, replacee))
		else:
			new_bound_variable = Variable(name = self.next_available_name())
			new_body = self.body.replace_variable(new_bound_variable, self.variable)
			return Abstraction(new_bound_variable, new_body.substitute(replacer, replacee))

	def next_available_name(self):
		s = ""
		while True:
			for char in Lambda_Calculus.alphabet:
				if char + s not in self.variable_names:
					return char + s
			s += "'"

	def replace_variable(self, replacer, replacee):
		if self.variable != replacee:
			return Abstraction(self.variable, self.body.replace_variable(replacer, replacee))
		else:
			return self

	def evaluate(self, argument):
		result = self.body.substitute(argument, self.variable)
		return result

	def can_be_simplified(self):
		return self.body.can_be_simplified()

	def simplify_step(self):
		return Abstraction(self.variable, self.body.simplify_step())

	def is_equal(self, other, translation):
		if not isinstance(other, Abstraction):
			return False
		if self.variable in translation:
			new_translation = dict(translation)
			del new_translation[self.variable]
		else:
			new_translation = translation
		if self.variable == other.variable:
			return self.body.is_equal(other.body, new_translation)
		else:
			new_translation[self.variable] = other.variable
			return self.body.is_equal(other.body, new_translation)

	def describe(self):
		print("Variable: λ" + str(self.variable))
		print("Body:", self.body)

	def __repr__(self):
		if isinstance(self.body, Application):
			return "λ" + str(self.variable) + ".(" + str(self.body) + ")"
		else:
			return "λ" + str(self.variable) + "." + str(self.body)

class Expression_Type:
	def __init__(self, argument_type = None, result_type = None):
		self.argument_type = argument_type
		self.result_type = result_type

	def apply_to(self, argument_type):
		if argument_type == self.argument_type:
			return self.result_type
		else:
			return None

	def __eq__(self, other):
		if not isinstance(other, Expression_Type):
			return False
		return self.argument_type == other.argument_type and self.result_type == other.result_type

	def __repr__(self):
		if self.result_type == None:
			return self.argument_type
		else:
			return "(" + str(self.argument_type) + " -> " + str(self.result_type) + ")"

class InvalidParseStringError(Exception):
	def __init__(self, string):
		print("The string", string, "cannot be parsed.")

class CannotSimplifyError(Exception):
	pass
