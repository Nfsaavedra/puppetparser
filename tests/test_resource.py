import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Attribute, Reference, Regex, Resource

class TestResource(unittest.TestCase):
    def test_resource(self):
        code = """
            test { 'test123':
                ensure => running,
                enable => true,
                content => "hello",
                int => 123,
                float => 0.1,
                scinot => 1.0e-10,
                hexa => 0x777,
                octal => 0777,
                array => [1, 2.0, "kek"],
                hash => {
                    1 => "hello",
                    "kek" => 2
                },
                regex => /$\/*hello*/^/,
                undefined => undef
            } 
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(len(res[0].attributes), 12)
        self.assertEqual(res[0].type, "test")
        self.assertEqual(res[0].title, "test123")

        for i in range(8):
            self.assertIsInstance(res[0].attributes[0], Attribute)
        self.assertEqual(res[0].attributes[0].value, "running")
        self.assertEqual(res[0].attributes[1].value, True)
        self.assertEqual(res[0].attributes[2].value, "hello")
        self.assertEqual(res[0].attributes[3].value, 123)
        self.assertEqual(res[0].attributes[4].value, 0.1)
        self.assertEqual(res[0].attributes[5].value, 1e-10)
        self.assertEqual(res[0].attributes[6].value, 0x777)
        self.assertEqual(res[0].attributes[7].value, 0o777)
        self.assertEqual(res[0].attributes[8].value, [1, 2.0, "kek"])
        self.assertEqual(res[0].attributes[9].value, {1: "hello", "kek": 2})
        self.assertIsInstance(res[0].attributes[10].value, Regex)
        self.assertEqual(res[0].attributes[10].value.content, "/$\/*hello*/^/")
        self.assertEqual(res[0].line, 2)
        self.assertEqual(res[0].attributes[4].line, 7)
        self.assertEqual(res[0].attributes[11].value, None)

    def test_resource_without_comma(self):
        code = """
            test { 'test123':
                ensure => running,
                enable => true,
                content => "hello",
                int => 123,
                float => 0.1,
                scinot => 1.0e-10,
                hexa => 0x777,
                octal => 0777,
                array => [1, 2.0, "kek"],
            } 
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)

    def test_stage(self):
        code = """
            stage { 'first':
                before => Stage['main'],
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "stage")

    def test_abstract_resource(self):
        code = """
            $mytype = File
            Resource[$mytype] { "/tmp/foo": ensure => file, }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[1], Resource)
        self.assertIsInstance(res[1].type, Reference)