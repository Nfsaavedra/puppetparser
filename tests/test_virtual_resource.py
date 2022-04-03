import unittest

from puppetparser.parser import parse
from puppetparser.model import Realize, Resource

class TestClass(unittest.TestCase):
    def test_virtual_resource(self):
        code = """
            @user {'deploy':
                uid     => 2004,
                comment => 'Deployment User',
                groups  => ["enterprise"],
                tag     => [deploy, web],
            }
            realize(User['deploy'], User['zleslie'])
        """

        res = parse(code)[0]
        self.assertIsInstance(res[0], Resource)
        self.assertEqual(res[0].type, "@user")
        self.assertIsInstance(res[1], Realize)