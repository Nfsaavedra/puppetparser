import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Operation, Resource

class TestClass(unittest.TestCase):
    def test_boolean_operators(self):
        code = """
            service { 'apache2':
                enable => !false and true,
                test => $hello or $hello2
            } 
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[0].value, Operation)
        self.assertEqual(res[0].attributes[0].value.operator, "and")
        self.assertEqual(res[0].attributes[0].value.arguments[0].operator, "!")
        self.assertEqual(res[0].attributes[0].value.arguments[1], True)
        self.assertEqual(res[0].attributes[1].value.operator, "or")