import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Case, Function, FunctionCall, Parameter, Resource

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

    def test_function_declaration(self):
        code = """
            function apache::bool2http(Variant[String, Boolean] $arg) >> String {
                case $arg {
                    false, undef, /(?i:false)/ : { 'Off' }
                    true, /(?i:true)/          : { 'On' }
                }
            }
        """
        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], Function)
        self.assertEqual(res[0].name, "apache::bool2http")
        self.assertIsInstance(res[0].parameters[0], Parameter)
        self.assertEqual(res[0].parameters[0].name, "$arg")
        self.assertEqual(res[0].return_type, "String")
        self.assertIsInstance(res[0].body[0], Case)