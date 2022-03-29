import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Operation, Resource

class TestClass(unittest.TestCase):
    def test_comparison_operators(self):
        code = """
            service { 'apache2':
                enable => true == 2 in [true, false],
                test => 5 < 7
            } 
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[0].value, Operation)
        self.assertEqual(res[0].attributes[0].value.operator, "in")
        self.assertIsInstance(res[0].attributes[0].value.arguments[0], Operation)
        self.assertEqual(res[0].attributes[0].value.arguments[1], [True, False])
        self.assertEqual(res[0].attributes[0].value.arguments[0].operator, "==")
        self.assertEqual(res[0].attributes[0].value.arguments[0].arguments, (True, 2))
        self.assertEqual(res[0].attributes[1].value.arguments, (5, 7))
