import unittest

from puppetparser.parser import parse
from puppetparser.model import Chaining, Reference, Resource, ResourceCollector

class TestClass(unittest.TestCase):
    def test_chaining_1(self):
        code = """
        Package['ntp'] -> File['/etc/ntp.conf'] ~> Service['ntpd']
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Chaining)
        self.assertIsInstance(res[0].op1, Reference)
        self.assertIsInstance(res[0].op2, Chaining)
        self.assertIsInstance(res[0].op2.op1, Reference)
        self.assertIsInstance(res[0].op2.op2, Reference)

    def test_chaining_2(self):
        code = """
            package { 'openssh-server':
                ensure => present,
            } # and then:
            -> file { '/etc/ssh/sshd_config':
                ensure => file,
                mode   => '0600',
                source => 'puppet:///modules/sshd/sshd_config',
            } # and then:
            ~> service { 'sshd':
                ensure => running,
                enable => true,
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Chaining)
        self.assertIsInstance(res[0].op1, Resource)
        self.assertIsInstance(res[0].op2, Chaining)
        self.assertIsInstance(res[0].op2.op1, Resource)
        self.assertIsInstance(res[0].op2.op2, Resource)

    def test_chaining_3(self):
        code = """
        Yumrepo <| |> -> Package <| |>
        """
        
        res = parse(code)[0]
        self.assertIsInstance(res[0], Chaining)
        self.assertIsInstance(res[0].op1, ResourceCollector)
        self.assertIsInstance(res[0].op2, ResourceCollector)