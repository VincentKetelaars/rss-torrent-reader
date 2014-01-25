'''
Created on Jan 25, 2014

@author: Vincent Ketelaars
'''
import unittest

from src.tests.test_decider import get_channel

class TestItem(unittest.TestCase):

    def setUp(self):
        self.channel = get_channel()


    def tearDown(self):
        pass


    def testName(self):
        item1 = self.channel.items[1]
        self.assertEqual(item1.film_title(), "ThingamaBob")
        self.assertTrue(item1.is_series())
        self.assertEqual(item1.episode(), (1,1))
        self.assertEqual(item1.resolution(), (1280, 720))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()