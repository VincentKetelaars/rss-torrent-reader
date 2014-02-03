'''
Created on Feb 3, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.tests.mock_classes import MockTorrent
from src.torrent.match import Match
from src.constants.constants import CONF_FILE
from src.conf.configuration import Configuration
from src.torrent.email_handler import EmailHandler


class TestEmailHandler(unittest.TestCase):


    def setUp(self):
        self.matches = [Match(None, MockTorrent("Something or other", "Myurl")),
                        Match(None, MockTorrent("Other", "Mine.."))]
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