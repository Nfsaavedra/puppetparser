import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Contain

class TestClass(unittest.TestCase):
    def test_contain(self):
        code = """
            contain base::linux
            contain base::linux, apache
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Contain)
        self.assertIsInstance(res[1], Contain)
        self.assertEqual(res[1].cont[0], "base::linux")