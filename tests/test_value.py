import unittest

from puppetparser.parser import parse
from puppetparser.model import Value

class TestClass(unittest.TestCase):
    def test_value_string(self):
        code = "'test'"

        res, _ = parse(code)
        self.assertIsInstance(res[0], Value)
        self.assertEqual(res[0].value, 'test')
        self.assertEqual(res[0].line, 1)
        self.assertEqual(res[0].end_line, 1)
        self.assertEqual(res[0].col, 0)
        self.assertEqual(res[0].end_col, 6)

    def test_value_string_multiline(self):
        code = """
            'test
test'
        """

        res, _ = parse(code)
        self.assertIsInstance(res[0], Value)
        self.assertEqual(res[0].value, 'test\ntest')
        self.assertEqual(res[0].line, 2)
        self.assertEqual(res[0].end_line, 3)
        self.assertEqual(res[0].col, 13)
        self.assertEqual(res[0].end_col, 6)
