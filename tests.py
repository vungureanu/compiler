from finite_automata import *
from context_free_grammars import *
from untyped_lambda import *
from regular_expressions import *
import unittest

class NFA_Test(unittest.TestCase):

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

	def test_re(self):
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
		self.assertTrue(re.test("b"))

	def test_lda(self):
		lr = Lambda_Calculus()
		self.assertTrue(lr.parse("succ (pow 2 3)") == lr.parse("pow 3 2"))
		self.assertTrue(lr.parse("fix fac 3") == lr.parse("pred 7"))
		self.assertFalse(lr.parse("mul 2 2") == lr.parse("plus 2 3"))
		lr.parse("f := fix fac")
		self.assertTrue(lr.parse("f 0") == lr.parse("1"))

if __name__ == "__main__":
	unittest.main()