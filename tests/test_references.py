import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Operation, Reference, Resource

class TestClass(unittest.TestCase):
    def test_access(self):
        code = """
            file { "/etc/second.conf":
                mode   => File["/etc/first.conf"]["mode"],
                owner  => File["/etc/first.conf", "test"]["owner"],
            }
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[0].value, Operation)
        self.assertIsInstance(res[0].attributes[0].value.arguments[0], Reference)
        self.assertEqual(res[0].attributes[0].value.arguments[0].type, "File")
        self.assertEqual(res[0].attributes[0].value.arguments[0].references, ["/etc/first.conf"])
        self.assertIsInstance(res[0].attributes[1].value, Operation)
        self.assertIsInstance(res[0].attributes[1].value.arguments[0], Reference)
        self.assertEqual(res[0].attributes[1].value.arguments[0].type, "File")
        self.assertEqual(res[0].attributes[1].value.arguments[0].references, ["/etc/first.conf", "test"])