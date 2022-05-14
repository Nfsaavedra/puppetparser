import unittest

from puppetparser.parser import parse
from puppetparser.model import Node, Resource

class TestClass(unittest.TestCase):
    def test_node(self):
        code = """
            node "webserver" {
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
        self.assertEqual(len(res[0].block), 2)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)

    def test_node_regex(self):
        code = """
            node /hello/ {
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
        self.assertEqual(res[0].name.value, "hello")
        self.assertEqual(len(res[0].block), 2)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)

    def test_node_default(self):
        code = """
            node default {
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
        self.assertEqual(res[0].line, 2)
        self.assertEqual(res[0].col, 13)
        self.assertEqual(res[0].end_line, 11)
        self.assertEqual(res[0].end_col, 14)
        self.assertEqual(res[0].name, "default")
        self.assertEqual(len(res[0].block), 2)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)
        self.assertEqual(res[0].block[1].line, 7)