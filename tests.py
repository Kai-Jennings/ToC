import unittest
from language import Engine

LETTERS = set("abcdefghijklmnopqrstuvwxyz")
DIGITS = set("0123456789")
GLYPHS = set("+×∸⊤⊥←↑→↓∷Θ")

engine = Engine("input")


class TestCases(unittest.TestCase):

    def test_numeral(self):
        self.assertTrue(engine.parse("2026"))

    def test_long_numeral(self):
        self.assertTrue(engine.parse("31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"))

    def test_variable(self):
        self.assertTrue(engine.parse("kai-j"))

    def test_each_glyph(self):
        for g in GLYPHS:
            with self.subTest(glyph=g):
                self.assertTrue(engine.parse(g))

    def test_each_letter(self):
        for l in LETTERS:
            with self.subTest(letter=l):
                self.assertTrue(engine.parse(l))

    def test_empty_string(self):
        self.assertFalse(engine.parse(""))

    def test_whitespace(self):
        self.assertFalse(engine.parse(" \t\n"))

    def test_only_spaces(self):
        self.assertFalse(engine.parse("  "))

    def test_leading_trailing_spaces_ignored(self):
        self.assertTrue(engine.parse("  a   "))

    def test_broken_application(self):
        self.assertFalse(engine.parse("a b"))

    def test_multiple_glyphs(self):
        self.assertFalse(engine.parse("⊤⊤"))

    def test_variable_cannot_start_with_digit(self):
        self.assertFalse(engine.parse("1a"))

    def test_simple_abstraction(self):
        self.assertTrue(engine.parse("λx.x"))

    def test_optional_space(self):
        self.assertTrue(engine.parse("λ x . x"))

    def test_nested_abstractions(self):
        self.assertTrue(engine.parse("λx.λy.λz.xyz"))

    def test_mixed_expression_types(self):
        self.assertTrue(engine.parse("λa.5"))
        self.assertTrue(engine.parse("λh.⊤"))
        self.assertTrue(engine.parse("λa.λb.+"))
        self.assertTrue(engine.parse("λt.(c s)"))

    def test_missing_variable(self):
        self.assertFalse(engine.parse("λ.x"))

    def test_missing_dot(self):
        self.assertFalse(engine.parse("λa b"))

    def test_missing_expression(self):
        self.assertFalse(engine.parse("λf."))

    def test_bare_lambda(self):
        self.assertFalse(engine.parse("λ"))

    def test_simple_app(self):
        self.assertTrue(engine.parse("(a b)"))

    def test_extra_spaces(self):
        self.assertTrue(engine.parse("(  a    b )"))

    def test_nested_app(self):
        self.assertTrue(engine.parse("((t c) s)"))
        self.assertTrue(engine.parse("(t (c s))"))
        self.assertTrue(engine.parse("((a b) (y z))"))

    def test_deeply_nested_app(self):
        self.assertTrue(engine.parse("((((((a b) ((((c d) e) f) g)) h) i) (((j k) l) m)) n)"))

    def test_numeral_app(self):
        self.assertTrue(engine.parse("(1 2)"))

    def test_variable_app(self):
        self.assertTrue(engine.parse("(kai j)"))

    def test_glyph(self):
        self.assertTrue(engine.parse("(⊤ ⊤)"))

    def test_abstraction(self):
        self.assertTrue(engine.parse("(λx.1 λa.2)"))

    def test_required_space(self):
        self.assertFalse(engine.parse("(ab)"))

    def test_empty(self):
        self.assertFalse(engine.parse("()"))

    def test_single_exp(self):
        self.assertFalse(engine.parse("(a)"))

    def test_missing_open_par(self):
        self.assertFalse(engine.parse("a b)"))

    def test_missing_close_par(self):
        self.assertFalse(engine.parse("(a b"))

    def test_single_close_par(self):
        self.assertFalse(engine.parse(")"))

    def test_three_exp(self):
        self.assertFalse(engine.parse("(a b c)"))

    # missing last required space
    def test_broken_deeply_nested_app(self):
        self.assertFalse(engine.parse("((((((a b) ((((c d) e) f) g)) h) i) (((j k) l) m))n)"))

    def test_generated_tests(self):
        with open("testcases.txt", "r", encoding="utf-8") as f:
            testcases = f.read()
        for testcase in testcases.split("\n"):
            with self.subTest(testcase=testcase):
                self.assertTrue(engine.parse(testcase))

        # These tests were generated with engine.generate() as shown below
        """        
        for i in range(1000):
            testcase = engine.generate("input", max_depth=100)
            while len(testcase) < 50:
                testcase = engine.generate("input", max_depth=100)
            with open("testcases.txt", "a", encoding="utf-8") as f:
                f.write(f"{testcase}\n")
        """


if __name__ == '__main__':
    unittest.main()
