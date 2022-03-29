import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import PuppetClass, Resource

class TestClass(unittest.TestCase):
    def test_resource(self):
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

        res = parser_yacc(code)
        self.assertIsInstance(res[0], PuppetClass)
        self.assertEqual(res[0].name, "webserver")
        self.assertEqual(res[0].inherits, "webserver2")
        self.assertEqual(res[0].parameters[0].name, "$content")
        self.assertEqual(res[0].parameters[0].type, "String")
        self.assertEqual(len(res[0].block), 3)
        for e in res[0].block:
            self.assertIsInstance(e, Resource)