import unittest

from puppetparser.parser import InvalidPuppetScript, parse
from puppetparser.model import Attribute, Reference, Regex, Resource, ResourceCollector, ResourceDeclaration, ResourceExpression

class TestResource(unittest.TestCase):
    def test_resource(self):
        code = """
            test { 'test123':
                ensure => running,
                enable => true,
                content => "hello",
                int => 123,
                float => 0.1,
                scinot => 1.0e-10,
                hexa => 0x777,
                octal => 0777,
                array => [1, 2.0, "kek"],
                hash => {
                    1 => "hello",
                    "kek" => 2
                },
                regex => /$\/*hello*/^/,
                undefined => undef
            } 
        """

        res = parse(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(len(res[0].attributes), 12)
        self.assertEqual(res[0].type, "test")
        self.assertEqual(res[0].title, "test123")

        for i in range(8):
            self.assertIsInstance(res[0].attributes[0], Attribute)
        self.assertEqual(res[0].attributes[0].value, "running")
        self.assertEqual(res[0].attributes[1].value, True)
        self.assertEqual(res[0].attributes[2].value, "hello")
        self.assertEqual(res[0].attributes[3].value, 123)
        self.assertEqual(res[0].attributes[4].value, 0.1)
        self.assertEqual(res[0].attributes[5].value, 1e-10)
        self.assertEqual(res[0].attributes[6].value, 0x777)
        self.assertEqual(res[0].attributes[7].value, 0o777)
        self.assertEqual(res[0].attributes[8].value, [1, 2.0, "kek"])
        self.assertEqual(res[0].attributes[9].value, {1: "hello", "kek": 2})
        self.assertIsInstance(res[0].attributes[10].value, Regex)
        self.assertEqual(res[0].attributes[10].value.content, "/$\/*hello*/^/")
        self.assertEqual(res[0].line, 2)
        self.assertEqual(res[0].attributes[4].line, 7)
        self.assertEqual(res[0].attributes[11].value, None)

    def test_resource_without_comma(self):
        code = """
            test { 'test123':
                ensure => running,
                enable => true,
                content => "hello",
                int => 123,
                float => 0.1,
                scinot => 1.0e-10,
                hexa => 0x777,
                octal => 0777,
                array => [1, 2.0, "kek"],
            } 
        """

        res = parse(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)

    def test_stage(self):
        code = """
            stage { 'first':
                before => Stage['main'],
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "stage")

    def test_abstract_resource(self):
        code = """
            $mytype = File
            Resource[$mytype] { "/tmp/foo": ensure => file, }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[1], Resource)
        self.assertIsInstance(res[1].type, Reference)

    def test_abstract_resource_error(self):
        code = """
            $mytype = File
            Test[$mytype] { "/tmp/foo": ensure => file, }
        """
        self.assertRaises(InvalidPuppetScript, parse, code)

    def test_attributes_from_hash(self):
        code = """
            file { "/etc/passwd":
                ensure => file,
                *      => $file_ownership,
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Resource)
        self.assertIsInstance(res[0].attributes[1], Attribute)
        self.assertEqual(res[0].attributes[1].key, "*")

    def test_array_of_titles(self):
        code = """
            $rc_dirs = [
                '/etc/rc.d',       '/etc/rc.d/init.d','/etc/rc.d/rc0.d',
                '/etc/rc.d/rc1.d', '/etc/rc.d/rc2.d', '/etc/rc.d/rc3.d',
                '/etc/rc.d/rc4.d', '/etc/rc.d/rc5.d', '/etc/rc.d/rc6.d',
            ]

            file { $rc_dirs:
                ensure => directory,
                owner  => 'root',
                group  => 'root',
                mode   => '0755',
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[1], Resource)
        self.assertEqual(res[1].title, "$rc_dirs")

    def test_add_attributes(self):
        code = """
        file {'/etc/passwd':
            ensure => file,
        }

        File['/etc/passwd'] {
            owner => 'root',
            group => 'root',
            mode  => '0640',
        }

        File <| tag == 'base::linux' |> {
            owner => 'root',
            group => 'root',
            mode => '0640',
        }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[1], Resource)
        self.assertEqual(res[1].title, None)
        self.assertIsInstance(res[2], Resource)
        self.assertIsInstance(res[2].type, ResourceCollector)
        self.assertEqual(res[2].type.search.arguments[0], "tag")

    def test_define_resource(self):
        code = """
        define apache::vhost (
            Integer $port,
            String[1] $docroot,
            String[1] $servername = $title,
            String $vhost_name = '*',
        ) {
            include apache # contains package['httpd'] and service['httpd']
            include apache::params # contains common config settings

            $vhost_dir = $apache::params::vhost_dir

            # the template used below can access all of the parameters and variable from above.
            file { "${vhost_dir}/${servername}.conf":
                ensure  => file,
                owner   => 'www',
                group   => 'www',
                mode    => '0644',
                content => template('apache/vhost-default.conf.erb'),
                require  => Package['httpd'],
                notify    => Service['httpd'],
            }
        }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], ResourceDeclaration)
        self.assertEqual(res[0].name, "apache::vhost")
        self.assertEqual(res[0].parameters[3].type, "String")
        self.assertEqual(res[0].block[3].type, "file")

    def test_resource_default(self):
        code = """
        Exec {
            path        => '/usr/bin:/bin:/usr/sbin:/sbin',
            environment => 'RUBYLIB=/opt/puppetlabs/puppet/lib/ruby/site_ruby/2.1.0/',
            logoutput   => true,
            timeout     => 180,
        }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "Exec")

    def test_resource_expression(self):
        code = """
            file {
                default:
                    ensure => file,
                    mode   => '0600',
                    owner  => 'root',
                    group  => 'root',
                ;
                '/etc/ssh_host_dsa_key':
                ;
                '/etc/ssh_host_key':
                ;
                '/etc/ssh_host_dsa_key.pub':
                    mode => '0644',
                ;
                '/etc/ssh_host_key.pub':
                    mode => '0644',
                ;
            }
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], ResourceExpression)
        self.assertIsInstance(res[0].default, Resource)
        self.assertEqual(res[0].default.title, "default")
        self.assertEqual(len(res[0].resources), 4)
        for r in res[0].resources:
            self.assertIsInstance(r, Resource)