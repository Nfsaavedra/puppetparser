import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Resource

class TestClass(unittest.TestCase):
    def test_exportedresource(self):
        code = """
            @@nagios_service { "check_zfs${::hostname}":
                use                 => 'generic-service',
                host_name           => $::fqdn,
                check_command       => 'check_nrpe_1arg!check_zfs',
                service_description => "check_zfs${::hostname}",
                target              => '/etc/nagios3/conf.d/nagios_service.cfg',
                notify              => Service[$nagios::params::nagios_service],
            }
        """

        res = parser_yacc(code)[0]
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "@@nagios_service")