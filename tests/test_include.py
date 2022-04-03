import unittest

from puppetparser.parser import parse
from puppetparser.model import Include

class TestClass(unittest.TestCase):
    def test_include(self):
        code = """
            include base::linux
            include base::linux, apache
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Include)
        self.assertIsInstance(res[1], Include)