'''
Created on Jan 25, 2014

@author: Vincent Ketelaars
'''
import unittest

from src.tests.test_decider import get_channel
from src.tests.mock_classes import MockItem
from src.general.constants import RESOLUTION_HDTV, RESOLUTION_720,\
    RESOLUTION_1080, RESOLUTION_BRRIP, RESOLUTION_DVDRIP, RESOLUTION_ZERO

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
        self.assertEqual(item1.resolution(), RESOLUTION_720)
        
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
        self.assertEqual(item.resolution(), RESOLUTION_HDTV)
        
        title = "Game Of Thrones S03 Season 3 COMPLETE 720p HDTV x264 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Game Of Thrones")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (3,0))
        self.assertEqual(item.resolution(), RESOLUTION_720)
        
        #title = "Game of Thrones Season 1, 2, 3 Extras BDRip TSV "
        title = "Game of Thrones Season 1 Extras BDRip TSV "
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Game of Thrones")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (1,0))
        self.assertEqual(item.resolution(), RESOLUTION_BRRIP)
        
        title = "[TORRENT] Opposite Worlds S01E05E06 HDTV x264-FUM[ettv]"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Opposite Worlds")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (1,6))
        self.assertEqual(item.resolution(), RESOLUTION_HDTV)
        
        title = "The Walking Dead Extras Season 1-4 _ALCOR_"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "The Walking Dead Extras")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (4,0))
        
        title = "Dexter season 8"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Dexter")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (8,0))        
        
        title =  "Terra Nova S01E01-02 XVID Dual Audio"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Terra Nova")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (1,2))
        
        title = "How I Met Your Mother S01-S08 DVDRip XviD-SP"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "How I Met Your Mother")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (8,0))
        
        title = "Lost The Complete Series Season 1,2,3,4,5,6 + English Subs"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Lost The Complete Series")
        self.assertTrue(item.is_series())
        self.assertEqual(item.episode(), (6,0))
        
    def test_parsing_title_movie(self):        
        title = "The Counselor 2013 UNRATED EXTENDED 1080p BluRay AVC DTS HD MA 5 1 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "The Counselor")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), RESOLUTION_1080)
        
        title = "Krrish 3 2013 1080p BluRay DTS x264 PublicHD"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Krrish 3")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), RESOLUTION_1080)
        
        title = "Ender's Game 2013 720p HDRip KORSUB 750MB Ganool"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Ender's Game")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), RESOLUTION_720)
        
        title = "All Things to All Men (2013)"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "All Things to All Men")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), (0, 0))
        
        title = "Jeff, Who Lives at Home (2011) 1080p"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Jeff, Who Lives at Home")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2011)
        self.assertEqual(item.resolution(), RESOLUTION_1080)
        
        title = "[TORRENT] Troy [2004] Dir Cut BRRip XviD-SaM[ETRG]"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Troy")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2004)
        self.assertEqual(item.resolution(), RESOLUTION_BRRIP)
        
        title = "Green Street Hooligans {2005} DVDRip.Xvid~Wolftatt2~"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Green Street Hooligans")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2005)
        self.assertEqual(item.resolution(), RESOLUTION_DVDRIP)
        
        title = "Green Street Hooligans[2005]DvDrip-aXXo"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Green Street Hooligans")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2005)
        self.assertEqual(item.resolution(), RESOLUTION_DVDRIP)
        
        title = "Green Street Hooligans Duology BRRip H264(BINGOWINGZ UKB RG)"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Green Street Hooligans Duology")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), RESOLUTION_BRRIP)
        
        title = "The Last Samurai(2003)1080p BDRip In[Hindi-Tamil-English]AC3-DGrea8"        
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "The Last Samurai")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2003)
        self.assertEqual(item.resolution(), RESOLUTION_1080)
        
        title = "Indiana Jones and the Last Crusade DVD iso Subtitles English, German, French, Dutch, Norwegian, Swedish, Danish, Finnish"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Indiana Jones and the Last Crusade")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), RESOLUTION_DVDRIP)

        title = "Homefront *2013* [WEB-DL.XviD.AC3] [5:1] [ENG / Subtitles PL]"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Homefront")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), RESOLUTION_ZERO)
        
        title = "The 40 Year Old Virgin UNRATED DVDRip XviD-DiAMOND"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "The 40 Year Old Virgin UNRATED")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), RESOLUTION_DVDRIP)
        
        title = "Green Street Hooligans Trilogy 720P BRRIPS XVID AC3-MAJESTiC"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "Green Street Hooligans Trilogy")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.resolution(), RESOLUTION_BRRIP)
        
        title = "2012 2009 1080p BrRip x264 1 7 GB YIFY"
        item = MockItem(title, "")
        self.assertEqual(item.film_title(), "2012")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2009)
        self.assertEqual(item.resolution(), RESOLUTION_1080)
        
        
    def test_description_parsing(self):
        description = "RESOLUTION...................: 1920*800"
        item = MockItem("Thor: The Dark World (2013) 1080p BrRip x264 - YIFY", description)
        self.assertEqual(item.film_title(), "Thor: The Dark World")
        self.assertTrue(item.is_movie())
        self.assertEqual(item.film_year, 2013)
        self.assertEqual(item.resolution(), (1920, 800))
        
        description = "[center][img]http://imageshack.us/scaled/landing/845/122600x194.jpg[/img][/center]http://www.imdb.com/title/tt0903747/[FILE SIZE]:[275MB[RESOLUTION]::[1280x720[SUBTITLES]:[Muxed"
        item = MockItem("Arrow S02E01 - City of Heroes [275MB nItRo].mkv", description)
        self.assertEqual(item.film_title(), "Arrow")
        self.assertTrue(item.is_series())
        self.assertEqual(item.resolution(), (1280, 720))

if __name__ == "__main__":
    unittest.main()