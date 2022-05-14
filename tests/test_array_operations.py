import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, Resource

class TestClass(unittest.TestCase):
    def test_array_operators(self):
        code = """
            $a = [1, 2, 3]
            service { 'apache2':
                enable => *$a,
                test => [1, 2, 3] << 4
            }
        """

        res, _ = parse(code)
        self.assertIsInstance(res[1], Resource)
        self.assertIsInstance(res[1].attributes[0].value, Operation)
        self.assertEqual(res[1].attributes[0].value.operator, "*")
        self.assertEqual(res[1].attributes[1].value.operator, "<<")
        self.assertEqual(res[1].attributes[1].line, 5)
        self.assertEqual(res[1].attributes[1].col, 17)