import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Include

class TestClass(unittest.TestCase):
    def test_include(self):
        code = """
            include base::linux
            include base::linux, apache
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Include)
        self.assertIsInstance(res[1], Include)