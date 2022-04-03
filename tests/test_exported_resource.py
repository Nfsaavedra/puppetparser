import unittest

from puppetparser.parser import parse
from puppetparser.model import Resource

class TestClass(unittest.TestCase):
    def test_exported_resource(self):
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

        res = parse(code)[0]
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "@@nagios_service")