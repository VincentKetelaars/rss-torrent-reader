'''
Created on Feb 16, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.tests.mock_classes import MockMovie

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_should_download(self):
        movie = MockMovie("Name", 2013, "TV Series", latest_season=2, latest_episode=5)
        self.assertFalse(movie.should_download(0, 0))
        self.assertFalse(movie.should_download())
        self.assertFalse(movie.should_download(2, 5))
        self.assertFalse(movie.should_download(2, 1))
        self.assertFalse(movie.should_download(1, 8))
        self.assertTrue(movie.should_download(3, 4))
        self.assertTrue(movie.should_download(2, 6))
        self.assertTrue(movie.should_download(*(2, 6)))
        movie.download = False
        self.assertFalse(movie.should_download(3, 4))
        
    def test_handled(self):
        movie = MockMovie("Name", 2013, "TV Series", latest_season=2, latest_episode=5)
        movie.handled(2, 6)
        self.assertTrue(movie.should_download(3, 4))
        self.assertFalse(movie.should_download(2, 6))
        self.assertFalse(movie.should_download(*(2, 6)))
        
if __name__ == "__main__":
    unittest.main()