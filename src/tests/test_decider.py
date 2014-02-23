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
        p = Preference(not_list, [], [], 0, 0,"200MB", "20GB", [], [])
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        
        self.assertEqual(len(result), 0)
        
    def test_resolution(self):
        p = Preference([], [], [], 1920, 1080,"200MB", "20GB", [], [])
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        self.assertEqual(len(result), 1)
        p = Preference([], [], [], 1921, 1081,"200MB", "20GB", [], [])
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 0)
        p = Preference([], [], [], 640, 480,"200MB", "20GB", [], [])
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 1)
        
    def test_compare(self):
        p = Preference([], [], ["IMAX", "1080p"], 1920, 1080, "200MB", "20GB", [], [])
        decider = Decider(MockMerger(self.movies), MockTorrentFeed({"" : self.channel}), p)
        matches = decider.decide()        
        self.assertEqual(len(matches), 1)
        self.assertIn(p.pref_list[0].lower(), matches[0].torrent.title.lower())
        
    def test_titles(self):
        torrent = "A Very Harold and Kumar Christmas 2011 3D HSBS YIFY"
        decider = Decider(MockMerger({"asdf" : MockMovie("A Very Harold & Kumar Christmas", 2011, "Feature Film")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],[],[],0,0,"", "20GB", [], []))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Revolution.2012.S02E13.720p.HDTV.X264-DIMENSION [PublicHD]"
        decider = Decider(MockMerger({"asdfl" : MockMovie("Revolution", 2012, "TV Series")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],[],[],0,0,"", "20GB", [], []))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "The Counselor UNRATED EXTENDED 2013 1080p BluRay AVC DTS HD MA 5 1 PublicHD"
        decider = Decider(MockMerger({"asdfl" : MockMovie("The Counselor", 2013, "Feature Film")}),
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],["unrated", "extended"],[],0,0,"", "20GB", [], []))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Safe Haven (2013) 720p BrRip x264 - YIFY"
        decider = Decider(MockMerger({"asdfl" : MockMovie("Safe", 2013, "Feature Film")}),
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],["unrated", "extended"],[],0,0,"", "20GB", [], []))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
        
    def test_languages(self):
        torrent = "Rise.Of.The.Guardians.2012.FRENCH.720p.BluRay.AC3.x264-TMB"
        decider = Decider(MockMerger({"asdf" : MockMovie("Rise Of The Guardians", 2012, "Feature Film")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],[],[],0,0,"", "20GB", ["English"], []))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        decider = Decider(MockMerger({"asdf" : MockMovie("Rise Of The Guardians", 2012, "Feature Film")}), 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference([],[],[],0,0,"", "20GB", ["French"], []))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
def get_channel():
    content = None
    with open("src/tests/torrents.xml", "r") as f:
        content = f.read()
    return TorrentRetriever(None).parse(content)

if __name__ == "__main__":
    unittest.main()