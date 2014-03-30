'''
Created on Feb 3, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.conf.configuration import Configuration, get_location_from_text_file
from src.general.constants import CONF_LOCATION_FILE


class Test(unittest.TestCase):


    def setUp(self):
        cfg_file = get_location_from_text_file(CONF_LOCATION_FILE)
        self.cfg = Configuration(cfg_file)

    def tearDown(self):
        pass

    def test_parse_option(self):
        self.assertEqual(self.cfg._parse_option('""'), None)
        self.assertItemsEqual(self.cfg._parse_option('asdf, asdf'), ["asdf", "asdf"])
        self.assertEqual(self.cfg._parse_option('"asdf, asdf"'), "asdf, asdf")
        self.assertItemsEqual(self.cfg._parse_option('"asdf", "asdf"', is_list=True), ["asdf", "asdf"])
        self.assertEqual(self.cfg._parse_option(''), None)
        self.assertEqual(self.cfg._parse_option("5"), 5)
        self.assertEqual(self.cfg._parse_option("5, 4, 2,1"), [5,4,2,1])
        self.assertEqual(self.cfg._parse_option('"asdf" '), "asdf")

if __name__ == "__main__":
    unittest.main()