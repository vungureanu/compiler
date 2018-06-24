from finite_automata import *
from context_free_grammars import *
from untyped_lambda import *
from regular_expressions import *
import unittest
from functools import partial

class NFA_Test(unittest.TestCase):
	def test_join(self):
		alphabet = {'a', 'b'}
		a = NFA(alphabet, char_type = "a")
		b = NFA(alphabet, char_type = "b")
		a = NFA.close_NFA(a)
		b = NFA.close_NFA(b)
		c = NFA.join_NFAs([a, b])
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
		ab_star_or_c = NFA.join_NFAs([ab_star, c])
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

	def best_re(self):
		re = Regular_Expression("(ab)*c")
		self.assertFalse(re.test("abab"))
		self.assertTrue(re.test("ababc"))
		self.assertFalse(re.test("ababcc"))
		re = Regular_Expression("((a*)(b*)c)*")
		self.assertTrue(re.test("aaabbbcaabbbbbc"))
		self.assertFalse(re.test("abac"))
		re = Regular_Expression("(bab)|(abb)")
		self.assertTrue(re.test("bab"))
		self.assertTrue(re.test("abb"))
		self.assertFalse(re.test("baa"))
		re = Regular_Expression("(a*)^")
		self.assertTrue(re.test("aaab"))
		self.assertFalse(re.test("aaa"))

	def test_lda(self):
		lr = Lambda_Calculus()
		#print(lr.parse("((λa.(a c)) abb)"))
		succ = "(λa.λb.λc.(b ((a b) c)))"
		one = "(λf.λx.(f x))"
		x = lr.parse("((" + succ + " " + one + ") " + "d) e")
		y = x.simplify().simplify()
		print(y)
		print(lr.parse("mul"))
		x = lr.parse("(mul 0) 0")
		print(x)
		lr.define("1", "succ 0")
		lr.define("2", "succ 1")
		lr.parse("2")
		print(lr.parse("(mul 2) 2"))
		lr.define("plus", "λm.λn.((m succ) n)")
		print(lr.parse("(((plus 1) 1) f) x"))

if __name__ == "__main__":
	unittest.main()