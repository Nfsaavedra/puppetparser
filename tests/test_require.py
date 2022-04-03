import unittest

from puppetparser.parser import parse
from puppetparser.model import Require

class TestClass(unittest.TestCase):
    def test_require(self):
        code = """
            require apache
            require mysql
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Require)
        self.assertIsInstance(res[1], Require)