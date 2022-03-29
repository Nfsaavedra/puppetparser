import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import PuppetClass, Comment

class TestClass(unittest.TestCase):
    def test_resource(self):
        code = """
            class webserver (String $content = "") inherits webserver2 {
                package { 'apache2':
                    ensure => present,
                }
                # Test
                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}", # Test2
                }

                service { 'apache2':
                    ensure => running,
                    enable => true,
                } 
            }
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0], PuppetClass)
        self.assertEqual(len(comments), 2)
        for c in comments:
            self.assertIsInstance(c, Comment)
        self.assertEqual(comments[0].content, " Test")
        self.assertEqual(comments[0].line, 6)
        self.assertEqual(comments[1].content, " Test2")
        self.assertEqual(comments[1].line, 9)