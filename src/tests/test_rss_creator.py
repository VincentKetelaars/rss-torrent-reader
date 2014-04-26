'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
import unittest
import os
import re
from xml.etree.ElementTree import ElementTree

from src.torrent.match import Match
from src.tests.test_decider import get_channel
from src.tests.mock_classes import MockMovie
from src.torrent.rss_creator import RSSCreator
from src.general.constants import HANDLER_WAIT
from src.tests.constants import TEST_DIRECTORY
from src.logger import get_logger
logger = get_logger(__name__)

class TestRSSCreator(unittest.TestCase):

    def setUp(self):
        self.movies_file = os.path.join(TEST_DIRECTORY, "test_torrent_rss_movies.xml")
        self.series_file = os.path.join(TEST_DIRECTORY, "test_torrent_rss_series.xml")
        channel = get_channel()
        movie = MockMovie("somethingorother", 2014, "Feature Film")
        self.matches = [Match(movie, t) for t in channel.items]
        self.title = "Something weird"
        self.link = "www.isthisworking.com"
        self.description = "This is my test"

    def tearDown(self):
        if os.path.exists(self.movies_file):
            os.remove(self.movies_file)

    def test_full_file(self):
        max_torrents = 25
        self.assertLess(max_torrents, len(self.matches)) # Needed for the rest of the asserts
        rsscreator = RSSCreator(self.matches, movies_file=self.movies_file, series_file=self.series_file, max_torrents=max_torrents, title=self.title, 
                                link=self.link, description=self.description)
        rsscreator.start()
        rsscreator.wait(HANDLER_WAIT)
        self.assertTrue(os.path.exists(self.movies_file))
        et = ElementTree(file=self.movies_file)
        channel = et.find("channel")
        items = channel.findall("item")
        self.assertEqual(len(items), max_torrents)
        self.assertItemsEqual([i.find("title").text for i in items], [m.torrent.title for m in self.matches[:max_torrents]])
        self.assertEqual(channel.find("title").text, self.title)
        self.assertEqual(channel.find("link").text, self.link)
        self.assertEqual(channel.find("description").text, self.description)
        
        # Check for CDATA
        content = ""
        with open(self.movies_file, "r") as f:
            content = f.read()        
        cdata = re.findall("\<\!\[CDATA\[", content)
        self.assertEqual(len(items) * 2, len(cdata))
        
    def test_write_read_write(self):
        max_torrents = 25
        number = 10 # Lower than max_torrents / 2
        rsscreator = RSSCreator(self.matches[:number], movies_file=self.movies_file, series_file=self.series_file, max_torrents=max_torrents, title=self.title, 
                                link=self.link, description=self.description)
        rsscreator.start()
        rsscreator.wait(HANDLER_WAIT)
        rsscreator = RSSCreator(self.matches[number:number * 2], movies_file=self.movies_file, series_file=self.series_file, max_torrents=max_torrents, title=self.title, 
                                link=self.link, description=self.description)
        rsscreator.start()
        rsscreator.wait(HANDLER_WAIT)
        et = ElementTree(file=self.movies_file)
        channel = et.find("channel")
        items = channel.findall("item")
        self.assertEqual(len(items), number * 2)
        self.assertEqual(channel.find("title").text, self.title)
        self.assertEqual(channel.find("link").text, self.link)
        self.assertEqual(channel.find("description").text, self.description)
        self.maxDiff = None
        self.assertItemsEqual([i.find("title").text for i in items], [m.torrent.title for m in self.matches[:number * 2]])
        
        # Check for CDATA
        content = ""
        with open(self.movies_file, "r") as f:
            content = f.read()        
        cdata = re.findall("\<\!\[CDATA\[", content)
        self.assertEqual(len(items) * 2, len(cdata))
        

if __name__ == "__main__":
    unittest.main()