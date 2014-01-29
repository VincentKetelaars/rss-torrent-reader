'''
Created on Jan 25, 2014

@author: Vincent Ketelaars
'''
import unittest

from src.tests.test_decider import get_channel
from src.tests.mock_classes import MockItem

class TestItem(unittest.TestCase):

    def setUp(self):
        self.channel = get_channel()


    def tearDown(self):
        pass


    def test_parsing(self):
        title = "ThingamaBob"
        for i in range(0, len(self.channel.items)):
            if self.channel.items[i].title.startswith(title):
                return
        item1 = self.channel.items[i]
        self.assertEqual(item1.film_title(), title)
        self.assertTrue(item1.is_series())
        self.assertEqual(item1.episode(), (1,1))
        self.assertEqual(item1.resolution(), (1280, 720))
        
        item2 = self.channel.items[i+1]
        self.assertEqual(item2.film_title(), "thingamaBob")
        self.assertTrue(item2.is_series())
        self.assertEqual(item2.episode(), (1,1))
        self.assertEqual(item2.resolution(), (1280, 718))
        
    def test_parsing_title_series(self):
        title = "Banshee 1x01 HDTV x264 EVOLVE eztv"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Banshee")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (1,1))
        self.assertEqual(item.resolution(), (0, 0))
        
        title = "Game Of Thrones S03 Season 3 COMPLETE 720p HDTV x264 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Game Of Thrones")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (3,0))
        self.assertEqual(item.resolution(), (1280, 720))
        
        #title = "Game of Thrones Season 1, 2, 3 Extras BDRip TSV "
        title = "Game of Thrones Season 1 Extras BDRip TSV "
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Game of Thrones")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (1,0))
        self.assertEqual(item.resolution(), (0, 0))
        
    def test_parsing_title_movie(self):        
        title = "The Counselor 2013 UNRATED EXTENDED 1080p BluRay AVC DTS HD MA 5 1 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "The Counselor")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), (1920, 1080))
        
        title = "Krrish 3 2013 1080p BluRay DTS x264 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Krrish 3")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), (1920, 1080))
        
        title = "Ender's Game 2013 720p HDRip KORSUB 750MB Ganool"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Ender's Game")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), (1280, 720))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()