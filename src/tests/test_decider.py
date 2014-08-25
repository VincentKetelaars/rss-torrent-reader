'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.torrent.preference import Preference
from src.torrent.decider import Decider
from src.tests.mock_classes import MockTorrentFeed, MockMovie,\
    MockChannel, MockItem
from src.rss.torrent_retriever import TorrentRetriever
from src.logger import get_logger
from src.general.constants import SERIES_TYPES, MOVIE_TYPES
from src.rss.torrent import Torrent
logger = get_logger(__name__)

class TestDecider(unittest.TestCase):

    def setUp(self):
        self.movies = {"asdf" : MockMovie("The Hunger Games Catching Fire", 2013, MOVIE_TYPES[0])}
        self.channel = get_channel()

    def tearDown(self):
        pass

    def test_not_list(self):
        not_0 = "DD5"
        not_list = [not_0]
        p = Preference(not_list)
        decider = Decider(self.movies, MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
        torrent = "Captain America The Winter Soldier 2014 720p HDCAM V2 x264 Pimp4003"
        not_list = ["cam"]
        p = Preference(not_list)
        decider = Decider({"asdf" : MockMovie("Captain America: The Winter Soldier", 2014, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), p)
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
        torrent = "Suits S03E03 720p HDTV x264 EVOLVE"
        not_list = ["ts"]
        p = Preference(not_list)
        decider = Decider({"asdf" : MockMovie("Suits", 2012, SERIES_TYPES[0], latest_season=3, latest_episode=2)}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), p)
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Need For Speed 2014 HDCAM 720p BY MTorrent"
        not_list = ["cam"]
        p = Preference(not_list)
        decider = Decider({"asdf" : MockMovie("Need for Speed", 2014, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), p)
        result = decider.decide()
        self.assertEqual(len(result), 0)        
        
    def test_resolution(self):
        p = Preference()
        decider = Decider(self.movies, MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()
        self.assertEqual(len(result), 1)
        p = Preference(min_width=1921, min_height=1081)
        decider = Decider(self.movies, MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 0)
        p = Preference(min_width=640, min_height=480)
        decider = Decider(self.movies, MockTorrentFeed({"" : self.channel}), p)
        result = decider.decide()        
        self.assertEqual(len(result), 1)
        
    def test_compare(self):
        p = Preference(pref_list=["IMAX", "1080p"], min_width=1920, min_height=1080)
        decider = Decider(self.movies, MockTorrentFeed({"" : self.channel}), p)
        matches = decider.decide()        
        self.assertEqual(len(matches), 1)
        self.assertIn(p.pref_list[0].lower(), matches[0].torrent.title.lower())
        
    def test_titles(self):
        torrent = "A Very Harold and Kumar Christmas 2011 3D HSBS YIFY"
        decider = Decider({"asdf" : MockMovie("A Very Harold & Kumar Christmas", 2011, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference())
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Revolution.2012.S02E13.720p.HDTV.X264-DIMENSION [PublicHD]"
        decider = Decider({"asdfl" : MockMovie("Revolution", 2012, SERIES_TYPES[0], latest_season=2, latest_episode=12)}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference())
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "The Counselor UNRATED EXTENDED 2013 1080p BluRay AVC DTS HD MA 5 1 PublicHD"
        decider = Decider({"asdfl" : MockMovie("The Counselor", 2013, MOVIE_TYPES[0])},
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(allowed_list=["unrated", "extended"]))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "Safe Haven (2013) 720p BrRip x264 - YIFY"
        decider = Decider({"asdfl" : MockMovie("Safe", 2013, MOVIE_TYPES[0])},
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(allowed_list=["unrated", "extended"]))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
        torrent = "24 S01 Season 1 720p WEB-DL H264-HDB [PublicHD]"
        decider = Decider({"asdfl" : MockMovie("24", -1, SERIES_TYPES[0], latest_season=0, latest_episode=0)},
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(allowed_list=["unrated", "extended"]))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
        torrent = "24.S01E01.Day.1_.12_00.A.M..-.1_00.A.M..1080p.WEB-DL.AAC2.0.H264 [PublicHD]"
        decider = Decider({"asdfl" : MockMovie("24", -1, SERIES_TYPES[0], latest_season=0, latest_episode=0)},
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(allowed_list=["unrated", "extended"]))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
    def test_languages(self):
        torrent = "Rise.Of.The.Guardians.2012.FRENCH.720p.BluRay.AC3.x264-TMB"
        decider = Decider({"asdf" : MockMovie("Rise Of The Guardians", 2012, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(languages=["English"]))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        decider = Decider({"asdf" : MockMovie("Rise Of The Guardians", 2012, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(languages=["French"]))
        result = decider.decide()
        self.assertEqual(len(result), 1)

#     def test_subtitles(self):
#         torrent = "Noah.2014.720p.BluRay[Greek Subs]LEO.avi"
#         decider = Decider({"asdf" : MockMovie("Noah", 2014, MOVIE_TYPES[0])}, 
#                           MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
#                           Preference(subtitles=["English"]))
#         result = decider.decide()
#         self.assertEqual(len(result), 0)
        
    def test_encoding(self):
        torrent = u"Rise.Of.The.Guardians.2012.FRENCH.720p.BluRay.AC3.x264-TMB"
        decider = Decider({"asdf" : MockMovie("Rise Of The Guardians", 2012, MOVIE_TYPES[0])}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(languages=["French"]))
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
    def test_extension(self):
        torrent = u"Agents of S H I E L D S01E20 720p HDTV x264 falcon.m4v"
        decider = Decider({"asdf" : MockMovie("Agents of S H I E L D", 2012, SERIES_TYPES[0], latest_season=1, latest_episode=19)}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference(excluded_extensions=["m4v"]))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
        torrent = u"Agents of S H I E L D S01E20 720p HDTV x264 falcon.m4v"
        decider = Decider({"asdf" : MockMovie("Agents of S H I E L D", 2012, SERIES_TYPES[0], latest_season=1, latest_episode=19)}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "")])}), 
                          Preference())
        result = decider.decide()
        self.assertEqual(len(result), 1)
        
    def test_min_seeders(self):
        torrent = u"the.strain.s01e07.for.services.rendered.720p.web.dl.dd5.1.h.264.ctrlhd"
        decider = Decider({"asdf" : MockMovie("The Strain", 2012, SERIES_TYPES[0], latest_season=1, latest_episode=6)}, 
                          MockTorrentFeed({"" : MockChannel([MockItem(torrent, "", torrent=Torrent({"seeds" : 2}))])}), 
                          Preference(min_seeders=5))
        result = decider.decide()
        self.assertEqual(len(result), 0)
        
def get_channel():
    content = None
    with open("src/tests/torrents.xml", "r") as f:
        content = f.read()
    return TorrentRetriever(None).parse(content)

if __name__ == "__main__":
    unittest.main()