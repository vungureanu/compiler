class Expression:
	expression = ""
	exp_type = ""
	def __init__(self, expression):
		self.expression = expression.strip()
	def get_tree(self):
		if (self.expression.isalnum()):
			if (self.expression in name_to_number):
				return Expression_Node("variable", name_to_number[self.expression])
			else:
				variable_number = len(name_to_number)
				name_to_number[self.expression] = variable_number
				number_to_name.append(self.expression)
				return Expression_Node(variable_number, self.expression)
		else if (self.expression[0] == '(' and self.expression[-1] == ')'):
			contents = self.expression[1:-1].strip()
			if (contents[0] == "L"):
				end_of_variable = contents.find(' ')
				if (end_of_variable != -1):
					variable = contents[1:end_of_variable]
					if (variable.isalnum()):
						sub_tree = Expression(contents[end_of_variable+1:]).get_tree()
						if (sub_tree != False):
							self.exp_type = "lambda-abstraction"
							return Expression_Node("lambda-abstraction", variable, sub_tree)
				return False
			else:
				# Functional application
				depth = 0
				for i in range(len(contents)):
					if (contents[i] == '('):
						depth += 1
					else if (contents[i] == ')'):
						depth -= 1
					else if (contents[i] == ' '):
						first_argument = Expression(contents[:i])
						second_argument = Expression(contents[i+1:])
						if (first_argument.is_valid() and second_argument.is_valid()):
							self.exp_type = "functional-application"
							return True
				print("Error (functional application incorrect): %s", contents)
		else:
			print("Error (unrecognized expression): %s", self.expression)
			return False

class Expression_Node:
	exp_type = None
	# Can be "variable", "functional-application", or "lambda-abstraction"
	first_argument = None
	second_argument = None
	# Variable: "first_argument" is the variable and "second_argument" is None.
	# Functional application: "first_argument" is the function and "second_argument" is its argument.
	# Lambda abstraction: "first_argument" is the bound variable, and "second_argument" is the body.
	free_variables = []
	bound_variables = []
	def __init__(self, exp_type, arg1 = None, arg2 = None):
		self.exp_type = exp_type
		first_argument = arg1
		second_argument = arg2
	def get_type(self):
		return self.exp_type
	def evaluate(self):
		if (self.exp_type == "functional-application"):
			if (first_argument.get_type() == "lambda-abstraction"):
				first_argument.substitute(second_argument)
	def substitute(self, replacee, replacer):
		if (self.exp_type == "variable"):
			if (replacee == first_argument):
				self = replacer
		else if (self.exp_type == "functional-application"):
			self.first_argument.substitute(replacee, replacer)
			self.second_argument.substitute(replacee, replacer)
		else if (self.exp_type == "lambda-abstraction"):
			replacer.renumber_variables(1, 0)
			# If the variable to be substituted out is the bound variable,
			# or if the variable to be substituted out does not occur in the body of the lambda abstraction,
			# leave the expression unchanged.
			if (self.first_argument != replacee and replacee in self.second_argument.free_variables):
				# No variable in the replacer can become accidentally bound by the binding variable in the lambda abstraction.
				if (self.first_argument not in replacer.free_variables):
					self.second_argument.substitute(replacee, replacer)
				else:
					variable_number = len(number_to_name)
					number_to_name[variable_number] = number_to_name[replacee]
					replacer.substitute(replacee, variable_number)
					self.second_argument.substitute(replacee, replacer)
	def renumber_variables(self, offset, cutoff):
		if (self.exp_type == "variable"):
			if (self.first_argument >= cutoff):
				self.first_argument += offset
		else if (self.exp_type == "functional-application"):
			self.first_argument.renumber_variables(offset, cutoff)
			self.second_argument.renumber_variables(offset, cutoff)
		else if (self.exp_type == "lambda-abstraction"):
			self.second_argument.renumber_variables(offset, cutoff + 1)



if __name__ == "__main__":
	number_to_name = []
	name_to_number = {}



