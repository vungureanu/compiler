class Lambda_Expression:
	def abstract(self, variable):
		return Abstraction(variable, self)

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

	def replace_variable(self, replacee, replacer):
		result = Application( self.function.replace_variable(replacer, replacee), self.argument.replace_variable(replacer, replacee) )
		return result

	def evaluate(self, argument):
		return Application(self, argument)

	def __repr__(self):
		return "(" + str(self.function) + " " + str(self.argument) + ")"

class Abstraction(Lambda_Expression):
	def __init__(self, variable, body):
		self.variable = variable
		self.body = body
		self.number = max(variable.number, body.number)
		self.free_variables = body.free_variables - {variable}

	def substitute(self, replacer, replacee):
		#print("Replacing", replacee, "in", self, "with", replacer, replacer.free_variables)
		if replacee == self.variable:
			return self
		elif self.variable not in replacer.free_variables:
			return Abstraction(self.variable, self.body.substitute(replacer, replacee))
		else:
			new_bound_variable = Variable()
			self.variable = new_bound_variable
			self.body = self.body.replace_variable(self.variable, new_bound_variable)
			return Abstraction(self.variable, self.body.substitute(replacer, replacee))

	def replace_variable(self, replacee, replacer):
		if self.variable != replacee:
			return self.body.replace_variable(replacee, replacer)

	def evaluate(self, argument):
		result = self.body.substitute(argument, self.variable)
		#print("Evaluation:", self, argument, "->", result)
		return result

	def __repr__(self):
		return "(λ" + str(self.variable) + "." + str(self.body) + ")"


