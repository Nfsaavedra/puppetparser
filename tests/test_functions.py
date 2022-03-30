import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import FunctionCall, Resource

class TestClass(unittest.TestCase):
    def test_function_prefix(self):
        code = """
            each($binaries) |$binary| {
                file {"/usr/bin/$binary":
                    ensure => link,
                    target => "/opt/puppetlabs/bin/$binary",
                }
            }
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], FunctionCall)
        self.assertEqual(res[0].name, "each")
        self.assertEqual(res[0].arguments[0], "$binaries")
        self.assertEqual(res[0].lamb.parameters[0].name, "$binary")
        self.assertIsInstance(res[0].lamb.block[0], Resource)

    def test_function_prefix_without_lambda(self):
        code = """
            test($binaries)
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], FunctionCall)
        self.assertEqual(res[0].name, "test")
        self.assertEqual(res[0].arguments[0], "$binaries")

    def test_function_prefix_empty(self):
        code = """
            test()
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], FunctionCall)
        self.assertEqual(res[0].name, "test")

    def test_function_chained(self):
        code = """
            $binaries.each |$binary| {
                file {"/usr/bin/$binary":
                    ensure => link,
                    target => "/opt/puppetlabs/bin/$binary",
                }
            }
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], FunctionCall)
        self.assertEqual(res[0].name, "each")
        self.assertEqual(res[0].arguments[0], "$binaries")
        self.assertEqual(res[0].lamb.parameters[0].name, "$binary")
        self.assertIsInstance(res[0].lamb.block[0], Resource)

    def test_function_chained_without_lambda(self):
        code = """
            $binaries.test
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], FunctionCall)
        self.assertEqual(res[0].name, "test")
        self.assertEqual(res[0].arguments[0], "$binaries")