import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, Resource

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
        self.assertEqual(res[0].value, [1, 2, 3])
        self.assertEqual(res[1].attributes[0].value.operator, "[]")