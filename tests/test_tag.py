import unittest

from puppetparser.parser import parse
from puppetparser.model import Tag
from tests.utility import assertArray

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

        res, comments = parse(code)
        self.assertIsInstance(res[0].block[0], Tag)
        assertArray(self, res[0].block[0].tags, ['us_mirror1', 'us_mirror2'])
