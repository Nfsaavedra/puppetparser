import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Assignment, Case, If, Include, Operation, Regex, Resource, Selector, Unless

class TestClass(unittest.TestCase):
    def test_if(self):
        code = """
            if $facts['is_virtual'] {
                package { 'apache2':
                    ensure => present,
                }
            } elsif $facts['os']['name'] == 'Darwin' {
                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }
            } else {
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], If)
        self.assertIsInstance(res[0].condition, Operation)
        self.assertIsInstance(res[0].block[0], Resource)
        self.assertIsInstance(res[0].elseblock, If)
        self.assertIsInstance(res[0].elseblock.block[0], Resource)
        self.assertIsInstance(res[0].elseblock.elseblock, If)
        self.assertEqual(res[0].elseblock.elseblock.elseblock, None)

    def test_unless(self):
        code = """
            unless $facts['is_virtual'] {
                package { 'apache2':
                    ensure => present,
                }
            } else {
                file { '/var/www/html/index.html':
                    ensure  => file,
                    content => "${content} ${::facts['ipaddress']}",
                }
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Unless)
        self.assertIsInstance(res[0].condition, Operation)
        self.assertIsInstance(res[0].block[0], Resource)
        self.assertIsInstance(res[0].elseblock, Unless)
        self.assertEqual(res[0].elseblock.elseblock, None)

    def test_case(self):
        code = """
            case $facts['os']['name'] {
                'RedHat', 'CentOS':  { include role::redhat  } # Apply the redhat class
                /^(Debian|Ubuntu)$/: { include role::debian  } # Apply the debian class
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Case)
        self.assertIsInstance(res[0].control, Operation)
        self.assertEqual(len(res[0].matches), 2)
        self.assertEqual(res[0].matches[0].expressions[0], 'RedHat')
        self.assertIsInstance(res[0].matches[1].expressions[0], Regex)
        self.assertIsInstance(res[0].matches[1].block[0], Include)

    def test_selector(self):
        code = """
            $rootgroup = $facts['os']['family'] ? {
                'Redhat'                    => 'wheel',
                'Debian'                    => 'wheel',
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Assignment)
        self.assertIsInstance(res[0].value, Selector)
        self.assertIsInstance(res[0].value.control, Operation)
        self.assertEqual(res[0].value.hash, {
            'Redhat': 'wheel', 
            'Debian': 'wheel',
        })
