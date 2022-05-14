import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, Resource
from tests.utility import assertArray

class TestClass(unittest.TestCase):
    def test_access(self):
        code = """
            $array = [1, 2, 3]
            service { 'apache2':
                test => $array[1],
                testsec => $array[1, 2],
            } 
        """

        res, comments = parse(code)
        assertArray(self, res[0].value.value, [1, 2, 3])
        self.assertEqual(res[1].attributes[0].value.operator, "[]")
        self.assertEqual(res[1].attributes[0].line, 4)
        self.assertEqual(res[1].attributes[0].col, 17)
        self.assertEqual(res[1].attributes[0].end_line, 4)
        self.assertEqual(res[1].attributes[0].end_col, 34)