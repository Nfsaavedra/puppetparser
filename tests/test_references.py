import unittest

from puppetparser.parser import parse
from puppetparser.model import Operation, Reference, Resource
from tests.utility import assertArray

class TestClass(unittest.TestCase):
    def test_access(self):
        code = """
            file { "/etc/second.conf":
                mode   => File["/etc/first.conf"]["mode"],
                owner  => File["/etc/first.conf", "test"]["owner"],
            }
        """

        res, comments = parse(code)
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[0].value, Operation)
        self.assertIsInstance(res[0].attributes[0].value.arguments[0], Reference)
        self.assertEqual(res[0].attributes[0].value.arguments[0].type, "File")
        assertArray(self, res[0].attributes[0].value.arguments[0].references, ["/etc/first.conf"])
        self.assertIsInstance(res[0].attributes[1].value, Operation)
        self.assertIsInstance(res[0].attributes[1].value.arguments[0], Reference)
        self.assertEqual(res[0].attributes[1].value.arguments[0].type, "File")
        assertArray(self, res[0].attributes[1].value.arguments[0].references, ["/etc/first.conf", "test"])
        self.assertEqual(res[0].attributes[1].value.arguments[0].line, 4)
        self.assertEqual(res[0].attributes[1].value.arguments[0].end_line, 4)
        self.assertEqual(res[0].attributes[1].value.arguments[0].end_col, 58)