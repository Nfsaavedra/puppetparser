import unittest

from puppetparser.parser import parse
from puppetparser.model import Debug, Fail

class TestClass(unittest.TestCase):
    def test_debug(self):
        code = """
            debug "DEBUG"
            info "INFO"
            notice "NOTICE"
            warning "WARNING"
            err "ERR"
            fail "FAIL"
        """

        res = parse(code)[0]
        for stat in res[:-1]:
            self.assertIsInstance(stat, Debug)
        self.assertEqual(res[0].args[0], "DEBUG")
        self.assertEqual(res[1].args[0], "INFO")
        self.assertEqual(res[2].args[0], "NOTICE")
        self.assertEqual(res[3].args[0], "WARNING")
        self.assertEqual(res[4].args[0], "ERR")
        self.assertIsInstance(res[-1], Fail)
        self.assertEqual(res[-1].args[0], "FAIL")