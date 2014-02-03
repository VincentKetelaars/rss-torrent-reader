'''
Created on Feb 3, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.conf.configuration import Configuration
from src.constants.constants import CONF_FILE


class Test(unittest.TestCase):


    def setUp(self):
        self.cfg = Configuration(CONF_FILE)

    def tearDown(self):
        pass

    def test_parse_option(self):
        self.assertEqual(self.cfg._parse_option('""'), None)
        self.assertItemsEqual(self.cfg._parse_option('asdf, asdf'), ["asdf", "asdf"])
        self.assertEqual(self.cfg._parse_option(''), None)

if __name__ == "__main__":
    unittest.main()