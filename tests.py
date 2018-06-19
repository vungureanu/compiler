from regular_expressions import *
from context_free_grammars import *
import unittest

class NFA_Test(unittest.TestCase):
	def test_NFA(self):
		alphabet = ['a', 'b', 'c']
		a = NFA(alphabet, NFA_State(), "a")
		b = NFA(alphabet, NFA_State(), "b")
		c = NFA(alphabet, NFA_State(), "c")
		self.assertTrue(a.is_valid("a"))
		self.assertFalse(a.is_valid("b"))
		self.assertFalse(a.is_valid("ab"))
		ab = NFA.concatenate_NFAs(a, b)
		self.assertTrue(ab.is_valid("ab"))
		self.assertFalse(ab.is_valid("a"))
		self.assertFalse(a.is_valid("abc"))
		ab_star = NFA.close_NFA(ab)
		self.assertTrue(ab_star.is_valid("ab"))
		self.assertTrue(ab_star.is_valid(""))
		self.assertFalse(ab_star.is_valid("ababa"))
		ab_star_or_c = NFA.join_NFAs(ab_star, c)
		self.assertTrue(ab_star_or_c.is_valid("c"))
		self.assertTrue(ab_star.is_valid("ababab"))
		self.assertFalse(ab_star_or_c.is_valid("ababa"))
		s = NFA.close_NFA(ab_star_or_c)
		self.assertTrue(s.is_valid("ababcab"))
		self.assertFalse(s.is_valid("cccba"))
		dfa = s.convert()
		self.assertTrue(s.is_valid("ababcab"))
		self.assertFalse(s.is_valid("ababccca"))

	def best_calculator(self):
		def r_add(args):
			return args[1] + args[3]
		def r_mul(args):
			return args[1] * args[3]
		def r_fac(args):
			p = 1
			for i in range(2, args[0]+1):
				p *= i
			return p 
		A = Symbol("A", "variable")
		B = Symbol("1", "terminal", value = 1)
		C = Symbol("2", "terminal", value = 2)
		D = Symbol("3", "terminal", value = 3)
		x = Symbol("x", "terminal")
		p = Symbol("+", "terminal")
		f = Symbol("!", "terminal")
		open_p = Symbol("(", "terminal")
		close_p = Symbol(")", "terminal")
		r1 = Rule(A, [open_p, A, x, A, close_p], r_mul)
		r2 = Rule(A, [open_p, A, p, A, close_p], r_add)
		r3 = Rule(A, [A, f], r_fac)
		r4 = Rule(A, [B], None)
		r5 = Rule(A, [C], None)
		r6 = Rule(A, [D], None)
		rules = [r1, r2, r3, r4, r5, r6]
		cfg = CFG(rules)
		cfg.convert_rules_to_CNF()
		self.assertTrue(cfg.is_normal())
		parser = CFG_Parser(cfg)
		stm = [open_p, open_p, D, x, C, close_p, p, B, close_p, f]
		r = parser.parse(stm)[0]
		print("OK:", r)
		s = r.unwind_tree()
		print("OK:", s)
		print(s.get_value())

	def test_lambda(self):
		# lambda_s = Symbol("L", "terminal")
		# open_p = Symbol("(", "terminal")
		# close_p = Symbol(")", "terminal")
		# v1 = Symbol("u", "terminal")
		# v2 = Symbol("v", "terminal")
		# dot = Symbol(".", "terminal")
		# var = Symbol("<var>", "variable")
		# exp = Symbol("<exp>", "variable")
		# start = Symbol("<start>", "start")
		# start = Rule(start, [exp])
		# fn_app = Rule(exp, [open_p, exp, exp, close_p])
		# lambda_abstraction = Rule(exp, [open_p, lambda_s, var, dot, exp, close_p])
		# var_red = Rule(exp, [var])
		# var_sim1 = Rule(var, [v1])
		# var_sim2 = Rule(var, [v2])
		#rules = [fn_app, lambda_abstraction, var_red, var_sim1, var_sim2]
		# A = Symbol("A", "variable")
		# B = Symbol("B", "variable")
		# C = Symbol("C", "variable")
		# D = Symbol("D", "terminal")
		# E = Symbol("E", "terminal")
		# r1 = Rule(A, [B, C, D, E])
		# r2 = Rule(B, [C, D, E])
		# r4 = Rule(B, [B, C])
		# r3 = Rule(C, [E])
		# rules = [r1, r2, r3, r4]
		# cfg = CFG(rules)
		# cfg.convert_rules_to_CNF()
		# for rule in cfg.rules: print(rule)
		# self.assertTrue(cfg.is_normal())
		# parser = CFG_Parser(cfg)
		# stm = [E, D, E, E, D, E]
		# r = parser.parse(stm)[0]
		# print(r, isinstance(r, Parse_Node))
		# #for s in Symbol.symbols:
		# #	print(s, s.get_expansion())
		# CFG_Parser.reduce_tree(r)
		# print(r.expansion)
		pass

	def test_RE(self):
		letters = []
		space = Symbol(" ", "terminal") # 32
		open_p = Symbol("(", "terminal") # 40
		close_p = Symbol(")", "terminal") # 41
		star = Symbol("*", "terminal") # 42
		or_s = Symbol("|", "terminal") #124
		for i in range(97, 100):
			letters.append(Symbol(chr(i), "terminal"))
		alphabet = [space, open_p, close_p, star, or_s] + letters
		for symbol in letters:
			symbol.value = NFA(alphabet, char_type = symbol)
		letter = Symbol("<letter>", "variable")
		word = Symbol("<word>", "variable")
		or_exp = Symbol("<or_exp>", "variable")
		gen_exp = Symbol("<gen_exp>", "variable")
		no_or_exp = Symbol("<no_or_exp>", "variable")
		exp = Symbol("<exp>", "variable")
		rules = [
			Rule(exp, [or_exp], None),
			Rule( word, [letter, word], lambda args: NFA.concatenate_NFAs(args[0], args[1]) ),
			Rule(word, [letter], None),
			Rule(space, [space, space], None),
			Rule(no_or_exp, [word], None),
			Rule( no_or_exp, [open_p, no_or_exp, close_p, star], lambda args: NFA.close_NFA(args[1]) ),
			Rule( no_or_exp, [open_p, no_or_exp, close_p, open_p, no_or_exp, close_p], lambda args: concatenate_NFAs(args[1], args[4])),
			Rule(or_exp, [no_or_exp, space, or_s, space, or_exp], lambda args: NFA.join_NFAs(args[0], args[4])),
			Rule(or_exp, [no_or_exp], None),
			Rule(exp, [open_p, exp, close_p, star], lambda args: NFA.close_NFA(args[1]))
		]
		rules.extend([Rule(letter, [l], None) for l in letters])

		cfg = CFG(rules)
		cfg.convert_rules_to_CNF()
		self.assertTrue(cfg.is_normal())
		parser = CFG_Parser(cfg)
		w = [open_p, letters[0], space, or_s, space, letters[1], close_p, star]
		r = parser.parse(w)[0]
		s = r.unwind_tree()
		v = s.get_value()
		v = v.convert()
		print(v)
		print(v.is_valid([letters[0]]))
		print(v.is_valid([letters[1]]))
		print(v.is_valid([letters[2]]))

if __name__ == "__main__":
	unittest.main()