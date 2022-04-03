import unittest

from puppetparser.parser import parse
from puppetparser.model import PuppetClass, Resource

class TestClass(unittest.TestCase):
    def test_class(self):
        code = """
            class webserver (String $content = "") inherits webserver2 {
                package { 'apache2':
                    ensure => present,
                }

                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }

                service { 'apache2':
                    ensure => running,
                    enable => true,
                } 
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], PuppetClass)
        self.assertEqual(res[0].name, "webserver")
        self.assertEqual(res[0].inherits, "webserver2")
        self.assertEqual(res[0].parameters[0].name, "$content")
        self.assertEqual(res[0].parameters[0].type, "String")
        self.assertEqual(len(res[0].block), 3)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)

    def test_resource_declaration(self):
        code = """
            class {'apache':
                version => '2.2.21',
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], PuppetClass)
        self.assertEqual(res[0].name, "apache")
        self.assertEqual(res[0].parameters[0].key, "version")
