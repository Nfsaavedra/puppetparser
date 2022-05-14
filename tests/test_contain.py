import unittest

from puppetparser.parser import parse
from puppetparser.model import Contain

class TestClass(unittest.TestCase):
    def test_contain(self):
        code = """
            contain base::linux
            contain base::linux, apache
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Contain)
        self.assertIsInstance(res[1], Contain)
        self.assertEqual(res[1].cont[0].value, "base::linux")
        self.assertEqual(res[1].line, 3)
        self.assertEqual(res[1].end_line, 3)