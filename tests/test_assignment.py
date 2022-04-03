import unittest

from puppetparser.parser import parse
from puppetparser.model import Assignment, Node, Resource

class TestClass(unittest.TestCase):
    def test_assignment(self):
        code = """
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
        self.assertIsInstance(res[0], Node)
        self.assertEqual(res[0].name, "webserver")
        self.assertEqual(len(res[0].block), 3)
        self.assertIsInstance(res[0].block[0], Assignment)
        self.assertEqual(res[0].block[0].name, "$hello")
        self.assertEqual(res[0].block[0].value, 123)
        self.assertIsInstance(res[0].block[1], Resource)
        self.assertIsInstance(res[0].block[2], Resource)

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
        self.assertEqual(res[0].block[0].name, ["$a", "$b", "$c"])
        self.assertEqual(res[0].block[0].value, [1, 2, 3])
        self.assertIsInstance(res[0].block[1], Resource)
        self.assertIsInstance(res[0].block[2], Resource)

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
        self.assertEqual(res[0].block[0].name, ["$a", "$b", "$c"])
        self.assertEqual(res[0].block[0].value, {"$a": 1, "$b": 2, "$c": 3})
        self.assertIsInstance(res[0].block[1], Resource)
        self.assertIsInstance(res[0].block[2], Resource)