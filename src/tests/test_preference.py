'''
Created on Feb 21, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.torrent.preference import Preference

class TestPreference(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse(self):
        pref = Preference([], [], [], 0, 0, "", "", [], [])
        self.assertEqual(pref.min_movie_size, 0)
        self.assertEqual(pref.max_movie_size, 0)
        sizes = "700MB"
        size = 700 * Preference.MB
        self.assertEqual(pref.parse_size(sizes), size)
        sizes = "5GB"
        size = 5 * Preference.GB
        self.assertEqual(pref.parse_size(sizes), size)
        pref = Preference([], [], [], 0, 0, "234KB", "2313MB", [], [])
        self.assertEqual(pref.min_movie_size, 234 * Preference.KB)
        self.assertEqual(pref.max_movie_size, 2313 * Preference.MB)

if __name__ == "__main__":
    unittest.main()