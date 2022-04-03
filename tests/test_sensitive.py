import unittest

from puppetparser.parser import parse
from puppetparser.model import FunctionCall

class TestClass(unittest.TestCase):
    def test_sensitive(self):
        code = """
            $secret = Sensitive.new('myPassword')
            $secret = Sensitive('myPassword')
        """

        res, comments = parse(code)
        self.assertIsInstance(res[0].value, FunctionCall)
        self.assertIsInstance(res[1].value, FunctionCall)