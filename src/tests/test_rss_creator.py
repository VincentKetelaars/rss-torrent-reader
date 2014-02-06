'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
import unittest
import os
from xml.etree.ElementTree import ElementTree

from src.torrent.match import Match
from src.tests.test_decider import get_channel
from src.tests.mock_classes import MockMovie
from src.torrent.rss_creator import RSSCreator
from src.general.constants import HANDLER_WAIT
from src.logger import get_logger
logger = get_logger(__name__)

class TestRSSCreator(unittest.TestCase):

    def setUp(self):
        self.file = "/tmp/test_torrent_rss.xml"
        channel = get_channel()
        movie = MockMovie("somethingorother", 2014, "Feature Film")
        self.matches = [Match(movie, t) for t in channel.items]
        self.title = "Something weird"
        self.link = "www.isthisworking.com"
        self.description = "This is my test"

    def tearDown(self):
        if os.path.exists(self.file):
            os.remove(self.file)

    def test_full_file(self):
        max_torrents = 25
        self.assertLess(max_torrents, len(self.matches)) # Needed for the rest of the asserts
        rsscreator = RSSCreator(self.matches, file=self.file, max_torrents=max_torrents, title=self.title, 
                                link=self.link, description=self.description)
        rsscreator.start()
        rsscreator.wait(HANDLER_WAIT)
        self.assertTrue(os.path.exists(self.file))
        et = ElementTree(file=self.file)
        channel = et.find("channel")
        items = channel.findall("item")
        self.assertEqual(len(items), max_torrents)
        self.assertItemsEqual([i.find("title").text for i in items], [m.torrent.title for m in self.matches[:max_torrents]])
        self.assertEqual(channel.find("title").text, self.title)
        self.assertEqual(channel.find("link").text, self.link)
        self.assertEqual(channel.find("description").text, self.description)

if __name__ == "__main__":
    unittest.main()