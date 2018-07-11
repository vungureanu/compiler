from regular_expressions import *
from sys import stdin, stdout

class Lambda_Calculus:

	rules = [
		"<str> <exp>",
		"<str> <def>",
		"<exp> <var>",
		"<exp> <app>",
		"<exp> <lda>",
		"<app> <cls>",
		"<exp> ( <exp> )",
		"<app> ( <exp> ) _ <lda>",
		"<cls> ( <exp> ) _ <var>",
		"<cls> ( <exp> ) _ ( <exp> )",
		"<app> <cls> _ <lda>",
		"<cls> <cls> _ <var>",
		"<cls> <cls> _ ( <exp> )",
		"<app> <var> _ <lda>",
		"<cls> <var> _ <var>",
		"<cls> <var> _ ( <exp> )",
		"<lda> λ <var> . <exp>",
		"<def> <var> _ := _ <exp>",
	]
	evaluations = [
		lambda args: None,
		lambda args: None,
		lambda args: None,
		lambda args: None,
		lambda args: None,
		lambda args: None,
		lambda args: args[1],
		lambda args: Application(args[1], args[4]),
		lambda args: Application(args[1], args[4]),
		lambda args: Application(args[1], args[5]),
		lambda args: Application(args[0], args[2]),
		lambda args: Application(args[0], args[2]),
		lambda args: Application(args[0], args[3]),
		lambda args: Application(args[0], args[2]),
		lambda args: Application(args[0], args[2]),
		lambda args: Application(args[0], args[3]),
		lambda args: Abstraction(variable = args[1], body = args[3]),
		lambda args: Definition(variable = args[0], expression = args[4])
	]

	# Define valid tokens of lambda caluclus for use in scanner

	alphabet = [chr(i) for i in range(ord("a"), ord("z")+1)]
	digits = {str(i) for i in range(10)}
	special_symbols = {"λ", "(", ")", ".", " ", ":="}
	letter_nfas = [NFA({char}, char_type = char) for char in alphabet]
	variable_names = NFA.close_NFA(NFA.join_NFAs(letter_nfas), new_token_type = "variable")
	special_nfas = [NFA(set(char), char_type = char, token_type = "special symbol") for char in special_symbols]
	digit_nfas = [NFA({digit}, char_type = digit) for digit in digits]
	number_nfa = NFA.close_NFA(NFA.join_NFAs(digit_nfas), new_token_type = "number")
	scanner = NFA.join_NFAs([variable_names] + special_nfas + digit_nfas).convert()

	def __init__(self, recursion_limit = 1000, length_limit = 1000):
		self.recursion_limit = recursion_limit
		self.length_limit = length_limit
		self.variables = set()
		self.keywords = {}

		rc = Rule_Conversion(Lambda_Calculus.rules, Lambda_Calculus.evaluations)

		def evaluate_number(n):
			x = Variable(name = "x")
			f = Variable(name = "f")
			current_number = x
			for _ in range(int(n)):
				current_number = Application(f, current_number)
			return Abstraction(f, Abstraction(x, current_number), alias = n)

		var_token = Token(name = "<var>", token_type = "variable")
		variable_conversion = Dynamic_Rule(var_token, lambda v: Variable(name = v.name), lambda prefix, suffix: prefix.name in self.variables)
		keyword_parsing = Dynamic_Rule(var_token, lambda kw: self.keywords[kw.name], lambda prefix, suffix: prefix.name in self.keywords)
		number_parsing = Dynamic_Rule(var_token, lambda n: evaluate_number(n.name), lambda prefix, suffix: prefix.token_type == "number")

		self.cfg = CFG(rc.get_converted_rules() + [variable_conversion, keyword_parsing, number_parsing])
		self.cfg.convert_rules_to_CNF()
		self.parser = CFG_Parser(self.cfg)
		self.define("succ", "λn.λf.λx.f (n f x)")
		self.define("pow", "λa.λb.b a")
		self.define("plus", "λm.λn.m succ n")
		self.define("mul", "λm.λn.λf.m (n f)")
		self.define("pred", "λn.λf.λx.n (λg.λh.(h (g f))) (λu.x) λu.u")
		self.define("true", "λx.λy.x")
		self.define("false", "λx.λy.y")
		self.define("and", "λp.λq.p q p")
		self.define("or", "λp.λq.p p q")
		self.define("not", "λp.p false true")
		self.define("ternary", "λp.λa.λb.(p a b)")
		self.define("iszero", "λn.n (λx.false) true")
		self.define("fac", "λf.λn.ternary (iszero n) 1 (mul n (f (pred n)))")
		self.define("fix", "λf.(λx.f (x x)) λx.f (x x)", simplify = False)

	def parse(self, string, verbose = False, simplify = True):
		tokens = []
		for token in Lambda_Calculus.scanner.scan(string):
			if token.string in self.keywords:
				tokens.append(Token(name = token.string, token_type = "keyword"))
			elif "number" in token.token_type:
				tokens.append(Token(name = token.string, token_type = "number"))
			elif "variable" in token.token_type:
				if token.string in self.variables:
					tokens.append(Token(name = token.string, token_type = "variable"))
				else:
					self.variables.add(token.string)
					tokens.append(Token(name = token.string, token_type = "variable"))
			else:
				tokens.append(Token(name = token.string, token_type = "terminal"))
		interpretations = self.parser.parse(tokens)
		if len(interpretations) == 0:
			raise InvalidParseStringError(string)
		elif len(interpretations) > 1:
			for i in interpretations:
				print(i.unwind_tree())
			print("Warning:", string, "has", len(interpretations), "interpretations; choosing one at random")
		result = interpretations[0].unwind_tree().get_value()
		if isinstance(result, Definition):
			return result.define(self)
		if simplify:
			return self.simplify(result, verbose = verbose)
		else:
			return result

	def define(self, variable, string, simplify = True):
		result = self.parse(string, simplify = simplify)
		result.alias = variable
		self.variables -= {variable}
		self.keywords[variable] = result

	def simplify(self, value, verbose = False, limit = None):
		count = 0
		if limit == None:
			limit = self.recursion_limit
		intermediate_steps = ""
		while value.can_be_simplified():
			intermediate_steps += value.details() + "\n"
			value = value.simplify_step()
			count += 1
			if count == limit or value.length >= self.length_limit:
				raise CannotSimplifyError
		if verbose:
			print(intermediate_steps)
		return value
		
class Lambda_Expression:
	def abstract(self, variable):
		return Abstraction(variable, self)

	def can_be_simplified(self):
		return False

	def is_number(self):
		"""Returns False if expression does not represent number, and number it represents otherwise.""" 
		return False

	def __init__(self, alias):
		self.alias = alias

	def __eq__(self, other):
		return self.is_equal(other, {})

	def __repr__(self):
		number = self.is_number()
		if self.alias != None:
			return self.alias
		elif number != False:
			return str(number)
		else:
			return self.details()

	def details(self):
		# If written recursively, this function may exceed Python's stack limits
		stack = [ self ]
		description = ""
		while len(stack) > 0:
			token = stack.pop()
			if isinstance(token, Variable):
				description += token.name
			elif isinstance(token, Application):
				if isinstance(token.argument, Application):
					stack.append(")")
					stack.append(token.argument)
					stack.append("(")
				else:
					stack.append(token.argument)
				if token.function.ends_with_abstraction():
					stack.append(")")
					stack.append(token.function)
					stack.append("(")
				else:
					stack.append(token.function)
			elif isinstance(token, Abstraction):
				description += "λ" + token.variable.name + "."
				stack.append(token.body)
			else:
				description += token
		return description

	def ends_with_abstraction(self):
		# If written recursively, this function may exceed Python's stack limits
		term = self
		while True:
			if isinstance(term, Variable):
				return False
			elif isinstance(term, Abstraction):
				return True
			else:
				term = term.argument

class Variable(Lambda_Expression):
	number = 1
	def __init__(self, name = None, alias = None):
		super().__init__(name)
		if name == None:
			self.name = "v_" + str(Variable.number)
		else:
			self.name = name
		self.free_variables = {self.name}
		self.variable_names = {self.name}
		self.length = 1
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

	def simplify_step(self):
		return self

	def is_equal(self, other, translation):
		if not isinstance(other, Variable):
			return False
		if self.name in translation:
			return translation[self.name] == other.name
		else:
			return self.name == other.name

class Application(Lambda_Expression):
	def __init__(self, function, argument, alias = None):
		super().__init__(alias)
		self.function = function
		self.argument = argument
		self.free_variables = function.free_variables | argument.free_variables
		self.variable_names = function.variable_names | argument.variable_names
		self.length = function.length + argument.length

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

	def is_equal(self, other, translation):
		if not isinstance(other, Application):
			return False
		return self.function.is_equal(other.function, translation) and self.argument.is_equal(other.argument, translation)

class Abstraction(Lambda_Expression):
	def __init__(self, variable, body, alias = None):
		super().__init__(alias)
		self.variable = variable
		self.body = body
		self.free_variables = body.free_variables - {variable.name}
		self.variable_names = body.variable_names | {variable.name}
		self.length = body.length + 1

	def substitute(self, replacer, replacee):
		if replacee.name not in self.free_variables:
			return self
		elif self.variable.name not in replacer.free_variables:
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
		if self.variable.name in translation:
			new_translation = dict(translation)
			del new_translation[self.variable.name]
		else:
			new_translation = translation
		if self.variable == other.variable:
			return self.body.is_equal(other.body, new_translation)
		else:
			new_translation[self.variable.name] = other.variable.name
			return self.body.is_equal(other.body, new_translation)

	def is_number(self):
		if not isinstance(self.body, Abstraction):
			return False
		f = self.variable
		x = self.body.variable
		number = 0
		current = self.body.body
		while isinstance(current, Application) and current.function == f:
			current = current.argument
			number += 1
		if current == x:
			return number
		else:
			return False

	#def details(self):
	#	if isinstance(self.body, Application):
	#		return "λ" + str(self.variable) + ".(" + str(self.body) + ")"
	#	else:
	#		return "λ" + str(self.variable) + "." + str(self.body)

class Definition:
	def __init__(self, variable, expression):
		self.name = variable.alias
		self.expression = expression

	def define(self, context):
		context.variables -= {self.name}
		try:
			result = context.simplify(self.expression, limit = 100)
		except CannotSimplifyError:
			result = self.expression
		result.alias = self.name
		context.keywords[self.name] = result
		return result

class InvalidParseStringError(Exception):
	def __init__(self, string):
		self.message = "The string " + string + " cannot be parsed."

class CannotSimplifyError(Exception):
	pass

if __name__ == "__main__":
	lc = Lambda_Calculus()
	while True:
		stdout.write(">> ")
		stdout.flush()
		user_input = stdin.readline().strip()
		if user_input == "exit":
			stdout.write("Goodbye.\n")
			exit()
		else:
			try:
				result = lc.parse(user_input, verbose = True)
				if result.details() != result:
					print(result.details())
				print("Alias:", result)
			except InvalidParseStringError as err:
				print(err.message)
			except InvalidCharacterError as err:
				print(err.message)
			except CannotSimplifyError:
				print("Expression could not be reduced to normal form.")

