import unittest

from puppetparser.parser import parser_yacc
from puppetparser.model import Tag

class TestClass(unittest.TestCase):
    def test_tag(self):
        code = """
            class role::public_web {
                tag 'us_mirror1', 'us_mirror2'

                apache::vhost {'docs.puppetlabs.com':
                    port => 80,
                }
                ssh::allowgroup {'www-data': }
            }
        """

        res, comments = parser_yacc(code)
        self.assertIsInstance(res[0].block[0], Tag)
        self.assertEqual(res[0].block[0].tags, ['us_mirror1', 'us_mirror2'])
