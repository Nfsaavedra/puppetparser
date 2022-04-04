import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, Resource
from tests.utility import assertArray

class TestClass(unittest.TestCase):
    def test_comparison_operators(self):
        code = """
            service { 'apache2':
                enable => (true == 2) in [true, false],
                test => 5 < 7
            } 
        """

        res, comments = parse(code)
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[0].value, Operation)
        self.assertEqual(res[0].attributes[0].value.operator, "in")
        self.assertIsInstance(res[0].attributes[0].value.arguments[0], Operation)
        assertArray(self, res[0].attributes[0].value.arguments[1].value, [True, False])
        self.assertEqual(res[0].attributes[0].value.arguments[0].operator, "==")
        assertArray(self, res[0].attributes[0].value.arguments[0].arguments, (True, 2))
        assertArray(self, res[0].attributes[1].value.arguments, (5, 7))
