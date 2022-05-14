import unittest

from puppetparser.parser import parse
from puppetparser.model import PuppetClass, Comment

class TestClass(unittest.TestCase):
    def test_comment(self):
        code = """
            class webserver (String $content = "") inherits webserver2 {
                package { 'apache2':
                    ensure => present,
                }
                # Test
                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}", # Test2
                } /* Test Test
Test Kek
Kek */

                # Hi

                service { 'apache2':
                    ensure => running,
                    enable => true,
                } 
            }
        """

        res, comments = parse(code)
        self.assertIsInstance(res[0], PuppetClass)
        self.assertEqual(len(comments), 4)
        for c in comments:
            self.assertIsInstance(c, Comment)
        self.assertEqual(comments[0].content, " Test")
        self.assertEqual(comments[0].line, 6)
        self.assertEqual(comments[0].end_line, 6)
        self.assertEqual(comments[1].content, " Test2")
        self.assertEqual(comments[1].line, 9)
        self.assertEqual(comments[2].content, " Test Test\nTest Kek\nKek ")
        self.assertEqual(comments[2].line, 10)
        self.assertEqual(comments[2].end_line, 12)
        self.assertEqual(comments[3].content, " Hi")
        self.assertEqual(comments[3].line, 14)