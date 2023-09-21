import unittest

from icu.utils.config import literal_eval_with_ops

class TestLiteralEvalWithOps(unittest.TestCase):

    def test_basic_operations(self):
        self.assertEqual(literal_eval_with_ops("5.5 + 3 * 2 / 1"), 11.5)
        self.assertEqual(literal_eval_with_ops("1/2 + 4"), 4.5)
        self.assertEqual(literal_eval_with_ops("[1]*3"), [1, 1, 1])

    def test_unpacking(self):
        self.assertEqual(literal_eval_with_ops("[*[1]]"), [1])
        self.assertEqual(literal_eval_with_ops("[*(1,2,3)]"), [1, 2, 3])
        self.assertEqual(literal_eval_with_ops("[*([10]*10)]"), [10, 10, 10, 10, 10, 10, 10, 10, 10, 10])

    def test_complex_expressions(self):
        self.assertEqual(literal_eval_with_ops("3 + 4.5 * 2 - 1"), 11.0)
        self.assertEqual(literal_eval_with_ops("3 - 4.5 + 2 * 1"), 0.5)
        self.assertEqual(literal_eval_with_ops("5 * 2 / 2"), 5.0)
        self.assertEqual(literal_eval_with_ops("[1, 2] + [3, 4]"), [1, 2, 3, 4])
        self.assertEqual(literal_eval_with_ops("(1, 2) + (3, 4)"), (1, 2, 3, 4))
        self.assertEqual(literal_eval_with_ops("{'a': 1}"), {'a': 1})
    
    def test_nested_collections(self):
        self.assertEqual(literal_eval_with_ops("[1, [2, 3], 4]"), [1, [2, 3], 4])
        self.assertEqual(literal_eval_with_ops("{'a': [1, 2, 3], 'b': {'c': 4, 'd': [5, 6]}}"), 
                         {'a': [1, 2, 3], 'b': {'c': 4, 'd': [5, 6]}})
        self.assertEqual(literal_eval_with_ops("[*[1, *[2, 3], 4]]"), [1, 2, 3, 4])
        self.assertEqual(literal_eval_with_ops("[*(1, 2), *[3, 4]]"), [1, 2, 3, 4])
        self.assertEqual(literal_eval_with_ops("{'a': 1 + 2, 'b': [3, 4] * 2}"), {'a': 3, 'b': [3, 4, 3, 4]})
        
    def test_invalid_expressions(self):
        with self.assertRaises(ValueError):
            literal_eval_with_ops("x = 1")
        with self.assertRaises(ValueError):
            literal_eval_with_ops("import os")
        with self.assertRaises(ValueError):
            literal_eval_with_ops("print('Hello')")

# Running the tests
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestLiteralEvalWithOps))