from regular_expressions import *
from context_free_grammars import *
from untyped_lambda import *
import unittest
from functools import partial

class NFA_Test(unittest.TestCase):
	def test_join(self):
		alphabet = {'a', 'b'}
		a = NFA(alphabet, char_type = "a")
		b = NFA(alphabet, char_type = "b")
		a = NFA.close_NFA(a)
		b = NFA.close_NFA(b)
		c = NFA.join_NFAs(a, b)
		self.assertTrue(c.is_valid("bbb"))
		self.assertFalse(c.is_valid("ab"))
	def test_NFA(self):
		alphabet = {'a', 'b', 'c'}
		a = NFA(alphabet, char_type = "a", token_type = "OK")
		b = NFA(alphabet, char_type = "b", token_type = "OK")
		c = NFA(alphabet, char_type = "c", token_type = "Cool")
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
		self.assertTrue(dfa.is_valid("ababcab"))
		self.assertTrue(dfa.is_valid("ccababccabc"))
		self.assertFalse(dfa.is_valid("ababccca"))
		self.assertFalse(dfa.is_valid("ccca"))
		x = dfa.scan("cccabaa")
		def ttt(fa):
			print(fa)
			for s in fa.states:
				if s.accepting:
					print("Check:", s, s.token_type)
		#print(s)
		#for k in dfa.states:
		#	print(k.number, k.accepting, k.token_type)
		#print(dfa)

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
		s = r.unwind_tree()

	def best_RE(self):
		letters = []
		#space = Symbol(" ", "terminal") # 32
		open_p = Symbol("(", "terminal") # 40
		close_p = Symbol(")", "terminal") # 41
		star = Symbol("*", "terminal") # 42
		or_s = Symbol("|", "terminal") #124
		for i in range(97, 100):
			letters.append(Symbol(chr(i), "terminal"))
		alphabet = [open_p, close_p, star, or_s] + letters
		#def fn(i):
		#	return NFA(alphabet, char_type = letters[i])
		for letter in letters:
			letter.value = partial(lambda l: NFA(alphabet, char_type = l), letter) # Apparently necessary given the way Python handles closures (?)
		letter = Symbol("<letter>", "variable")
		word = Symbol("<word>", "variable")
		or_exp = Symbol("<or>", "variable")
		gen_exp = Symbol("<gen_exp>", "variable")
		no_or_exp = Symbol("<nor>", "variable")
		exp = Symbol("<exp>", "variable")
		rules = [
			Rule(exp, [or_exp], None),
			Rule( word, [letter, word], lambda args: NFA.concatenate_NFAs(args[0], args[1]) ),
			Rule(word, [letter], None),
			Rule(no_or_exp, [word], None),
			Rule( no_or_exp, [open_p, no_or_exp, close_p, star], lambda args: NFA.close_NFA(args[1]) ),
			Rule( no_or_exp, [open_p, no_or_exp, close_p, open_p, no_or_exp, close_p], lambda args: concatenate_NFAs(args[1], args[4])),
			Rule(or_exp, [no_or_exp, or_s, or_exp], lambda args: NFA.join_NFAs(args[0], args[2])),
			Rule(or_exp, [no_or_exp], None),
			Rule(exp, [open_p, exp, close_p, star], lambda args: NFA.close_NFA(args[1]))
		]
		rules.extend([Rule(letter, [l], None) for l in letters])

		cfg = CFG(rules)
		cfg.convert_rules_to_CNF()
		self.assertTrue(cfg.is_normal())
		parser = CFG_Parser(cfg)
		w = [open_p, letters[0], letters[1], close_p, star, or_s, open_p, letters[1], close_p, star]
		r = parser.parse(w)[0]
		s = r.unwind_tree()
		v = s.get_value()
		print(s)
		v = v.convert()
		self.assertTrue(v.is_valid([letters[0], letters[1], letters[0], letters[1]]))
		self.assertTrue(v.is_valid([letters[1], letters[1], letters[1]]))
		self.assertFalse(v.is_valid([letters[0], letters[1], letters[1]]))

	def test_lambda(self):
		lda = Symbol("λ", "terminal")
		var = Symbol("<var>", "variable")
		open_p = Symbol("(", "terminal") # 40
		close_p = Symbol(")", "terminal") # 41
		dot = Symbol(".", "terminal")
		space = Symbol("_", "terminal")
		exp = Symbol("<exp>", "variable")
		variables = [Symbol(chr(i), "terminal") for i in range(97, 100)]
		alphabet = [lda, open_p, close_p, dot, space] + variables
		a, b, c = variables[0], variables[1], variables[2]
		av, bv, cv, = Variable(name = "a"), Variable(name = "b"), Variable(name = "c")
		a.value = lambda: av
		b.value = lambda: bv
		c.value = lambda: cv
		letters = {"a", "b", "c"}
		special_symbols = {"λ", "(", ")", ".", " "}
		alphabet = letters | special_symbols
		letter_NFAs = [ NFA(alphabet, char_type = l, token_type = l) for l in letters]
		nfa_l = NFA(alphabet, char_type = "λ", token_type = "λ")
		nfa_o = NFA(alphabet, char_type = "(", token_type = "(")
		nfa_c = NFA(alphabet, char_type = ")", token_type = ")")
		nfa_d = NFA(alphabet, char_type = ".", token_type = ".")
		nfa_s = NFA.close_NFA(NFA(alphabet, char_type = " ", token_type = " "))
		jn = NFA.close_NFA(NFA.join_NFAs(letter_NFAs[0], letter_NFAs[1], letter_NFAs[2]))
		def ttt(fa):
			print(fa)
			for s in fa.states:
				if s.accepting:
					print("Check:", s, s.token_type)
		nj = NFA.join_NFAs(jn, nfa_l, nfa_o, nfa_c, nfa_d, nfa_s)
		nj = nj.convert()
		print(nj.scan("((λab.b)    (λabc.bb))"))
		#ttt(nj)
		rules = [
			Rule(exp, [open_p, exp, space, exp, close_p], lambda args: args[1].evaluate(args[3])),
			Rule(exp, [open_p, lda, var, dot, exp, close_p], lambda args: Abstraction(args[2], args[4])),
			Rule(exp, [var], None),
		]

		rules.extend( [Rule(var, [v], None) for v in variables] )
		cfg = CFG(rules)
		cfg.convert_rules_to_CNF()
		self.assertTrue(cfg.is_normal())
		parser = CFG_Parser(cfg)
		w = [open_p, open_p, lda, c, dot, open_p, lda, a, dot, c, close_p, close_p, space, a, close_p]
		r = parser.parse(w)[0]
		s = r.unwind_tree()
		#print("Tree:", s)
		v = s.get_value()
		#print("Value:", v)

if __name__ == "__main__":
	unittest.main()