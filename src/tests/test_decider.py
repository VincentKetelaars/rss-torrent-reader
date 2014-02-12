'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.torrent.preference import Preference
from src.torrent.decider import Decider
from src.tests.mock_classes import MockMerger, MockTorrentFeed, MockMovie,\
    MockChannel, MockItem
from src.rss.torrent_retriever import TorrentRetriever
from src.logger import get_logger
logger = get_logger(__name__)

class TestDecider(unittest.TestCase):

    def setUp(self):
        self.movies = {"asdf" : MockMovie("The Hunger Games Catching Fire", 2013, "Feature Film")}
        self.channel = get_channel()

    def tearDown(self):
        pass

    def test_not_list(self):
        not_0 = "DD5"
        not_list = [not_0]
        p = Preference(not_list, [], [], 0, 0)
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        
        self.assertEqual(len(result), 0)
        
    def test_resolution(self):
        p = Preference([], [], [], 1920, 1080)
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        self.assertEqual(len(result), 1)
        p = Preference([], [], [], 1921, 1081)
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 0)
        p = Preference([], [], [], 640, 480)
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 1)
        
    def test_compare(self):
        p = Preference([], [], ["IMAX", "1080p"], 1920, 1080)
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        matches = decider.decide()        
        self.assertEqual(len(matches), 1)
        self.assertIn(p.pref_list[0].lower(), matches[0].torrent.title.lower())
        
    def test_titles(self):
        torrent = "A Very Harold and Kumar Christmas 2011 3D HSBS YIFY"
        movie = "A Very Harold & Kumar Christmas"
        decider = Decider(MockMerger({"asdf" : MockMovie(movie, 2011, "Feature Film")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), Preference([],[],[],0,0))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Revolution.2012.S02E13.720p.HDTV.X264-DIMENSION [PublicHD]"
        series = "Revolution"
        decider = Decider(MockMerger({"asdfl" : MockMovie(series, 2012, "TV Series")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), Preference([],[],[],0,0))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
def get_channel():
    content = None
    with open("src/tests/torrents.xml", "r") as f:
        content = f.read()
    return TorrentRetriever(None).parse(content)

if __name__ == "__main__":
    unittest.main()