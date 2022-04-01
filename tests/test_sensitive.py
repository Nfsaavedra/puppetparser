import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import FunctionCall, Resource

class TestClass(unittest.TestCase):
    def test_sensitive(self):
        code = """
            $secret = Sensitive.new('myPassword')
            $secret = Sensitive('myPassword')
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0].value, FunctionCall)
        self.assertIsInstance(res[1].value, FunctionCall)