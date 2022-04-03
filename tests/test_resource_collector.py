import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, ResourceCollector

class TestClass(unittest.TestCase):
    def test_resource_collector(self):
        code = """
            User <| title == 'luke' |>
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], ResourceCollector)
        self.assertIsInstance(res[0].search, Operation)
        self.assertEqual(res[0].search.operator, "==")