import unittest

from puppetparser.parser import parser_yacc
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

        res = parser_yacc(code)[0]
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

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Node)
        self.assertEqual(res[0].name, "/hello/")
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

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Node)
        self.assertEqual(res[0].name, "default")
        self.assertEqual(len(res[0].block), 2)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)