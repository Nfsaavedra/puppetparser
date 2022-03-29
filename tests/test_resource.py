import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Attribute, Resource

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
            } 
        """

        res = parser_yacc(code)
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(len(res[0].attributes), 8)
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
        self.assertEqual(res[0].line, 2)
        self.assertEqual(res[0].attributes[4].line, 7)


