import unittest

from puppetparser.parser import parse
from puppetparser.model import Assignment, Node, Resource, Id
from tests.utility import assertArray, assertHash


class TestClass(unittest.TestCase):
    def test_assignment_node(self):
        code = """$a = 1
            node "webserver" {
                $hello = 123
                package { 'apache2':
                    ensure => present,
                }

                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }
            }
        """

        res = parse(code)[0]

        self.assertIsInstance(res[0].name, Id)
        self.assertEqual(res[0].name.value, "$a")
        self.assertEqual(res[0].value.value, 1)
        self.assertEqual(res[0].line, 1)
        self.assertEqual(res[0].end_line, 1)
        self.assertEqual(res[0].col, 1)
        self.assertEqual(res[0].end_col, 7)

        self.assertIsInstance(res[1], Node)
        self.assertEqual(res[1].name, "webserver")
        self.assertEqual(len(res[1].block), 3)
        self.assertIsInstance(res[1].block[0], Assignment)
        self.assertIsInstance(res[1].block[0].name, Id)
        self.assertEqual(res[1].block[0].name.value, "$hello")
        self.assertEqual(res[1].block[0].value.value, 123)
        self.assertIsInstance(res[1].block[1], Resource)
        self.assertIsInstance(res[1].block[2], Resource)
        self.assertEqual(res[1].block[0].line, 3)
        self.assertEqual(res[1].block[0].col, 17)
        self.assertEqual(res[1].block[0].end_col, 29)
        self.assertEqual(res[1].block[1].line, 4)
        self.assertEqual(res[1].block[1].col, 17)
        self.assertEqual(res[1].block[1].end_line, 6)
        self.assertEqual(res[1].block[1].end_col, 18)

    def test_assignment_array(self):
        code = """
            node "webserver" {
                [$a, $b, $c] = [1, 2, 3]
                package { 'apache2':
                    ensure => present,
                }

                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Node)
        self.assertEqual(res[0].name, "webserver")
        self.assertEqual(len(res[0].block), 3)
        self.assertIsInstance(res[0].block[0], Assignment)
        assertArray(self, res[0].block[0].name.value, ["$a", "$b", "$c"])
        assertArray(self, res[0].block[0].value.value, [1, 2, 3])
        self.assertIsInstance(res[0].block[1], Resource)
        self.assertIsInstance(res[0].block[2], Resource)
        self.assertEqual(res[0].block[2].line, 8)
        self.assertEqual(res[0].block[2].col, 17)

    def test_assignment_hash(self):
        code = """
            node "webserver" {
                [$a, $b, $c] = {$a => 1, $b => 2, $c => 3}
                package { 'apache2':
                    ensure => present,
                }

                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Node)
        self.assertEqual(res[0].name, "webserver")
        self.assertEqual(len(res[0].block), 3)
        self.assertIsInstance(res[0].block[0], Assignment)
        assertArray(self, res[0].block[0].name.value, ["$a", "$b", "$c"])
        assertHash(self, res[0].block[0].value.value, {"$a": 1, "$b": 2, "$c": 3})
        self.assertIsInstance(res[0].block[1], Resource)
        self.assertIsInstance(res[0].block[2], Resource)
        self.assertEqual(res[0].block[2].line, 8)
        self.assertEqual(res[0].block[2].col, 17)

    def test_assignment_type_alias(self):
        code = """
            type Unbound::Local_zone_type = Enum[
                'deny',
                'refuse',
                'static',
                'transparent',
                'redirect',
                'nodefault',
                'typetransparent',
                'inform',
                'inform_deny',
                'always_transparent',
                'always_refuse',
                'always_nxdomain',
            ]
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Assignment)
        self.assertIsInstance(res[0].name, Id)
        self.assertEqual(res[0].name.value, "type Unbound::Local_zone_type")

    def test_assignment_variable(self):
        code = """$a = $b"""
        res = parse(code)[0]
        self.assertIsInstance(res[0], Assignment)
        self.assertIsInstance(res[0].name, Id)
        self.assertEqual(res[0].name.value, "$a")
        self.assertIsInstance(res[0].value, Id)
        self.assertEqual(res[0].value.value, "$b")
