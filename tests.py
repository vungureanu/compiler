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

	def test_CFG(self):
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
		A = Symbol("A", "variable")
		B = Symbol("1", "terminal")
		C = Symbol("2", "terminal")
		D = Symbol("3", "terminal")
		x = Symbol("x", "terminal")
		p = Symbol("+", "terminal")
		f = Symbol("!", "terminal")
		terminal_values = {B : 1, C : 2, D : 3, x : "x", p : "+", f : "!"}
		r1 = Rule(A, [A, x, A])
		r2 = Rule(A, [A, p, A])
		r3 = Rule(A, [A, f])
		r4 = Rule(A, [B])
		r5 = Rule(A, [C])
		r6 = Rule(A, [D])
		rules = [r1, r2, r3, r4, r5, r6]
		cfg = CFG(rules)
		cfg.convert_rules_to_CNF()
		for rule in cfg.rules: print(rule)
		self.assertTrue(cfg.is_normal())
		for rule in cfg.rules:
			print("Rule:", rule)
			print("Old:", rule.old_rule)
		parser = CFG_Parser(cfg)
		stm = [B, x, C, p, D, f]
		#r = parser.parse(stm)[0]
		#print("OK:", r)
		#s = r.produce_original_tree()
		#print("OK:", s, isinstance(s, Parse_Node))
		def r_add(args):
			return args[0] + args[2]
		def r_mul(args):
			return args[0] * args[2]

if __name__ == "__main__":
	unittest.main()