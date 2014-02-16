'''
Created on Feb 3, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.tests.mock_classes import MockTorrent, MockMovie
from src.torrent.match import Match
from src.general.constants import CONF_FILE
from src.conf.configuration import Configuration
from src.torrent.email_handler import EmailHandler


class TestEmailHandler(unittest.TestCase):


    def setUp(self):
        self.matches = [Match(MockMovie("Something or other", 2011, "Feature Film"), MockTorrent("Something or other", "Myurl", title="That")),
                        Match(MockMovie("Other", 2013, "TV Series"), MockTorrent("Other.ass", "Mine..", title="Other"))]
        cfg = Configuration(CONF_FILE)
        self.email_handler = EmailHandler(self.matches, **cfg.get_handler("email"))

    def tearDown(self):
        pass

    def test_matches(self):
        self.email_handler.start()
        self.email_handler.wait()
        self.assertItemsEqual(self.email_handler.handled(), self.matches)

if __name__ == "__main__":
    unittest.main()