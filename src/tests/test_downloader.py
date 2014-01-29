'''
Created on Jan 20, 2014

@author: Vincent Ketelaars
'''
import unittest
import os

from src.tests.mock_classes import MockTorrent
from src.torrent.match import Match
from src.tests.constants import TEST_DIRECTORY, TEST_MAX_WAIT
from src.torrent.downloader import Downloader


class TestDownloader(unittest.TestCase):


    def setUp(self):
        self.filename = "test.torrent"
        self.filename2 = "test2.torrent"
        self.url = "http://torcache.net/torrent/4FE2612383DD486E369C73A3F571D5CD3341468E.torrent?title=[kickass.to]christmas.with.johann.sebastian.bach.2013.720p.mbluray.x264.liquid.publichd"
        self.url2 = "http://www.torrenthound.com/torrent/e256280cf0dcb27ee1a3dc49b7fdd33ebf0c0f6c"
        self.directory = TEST_DIRECTORY
        self.path = os.path.join(self.directory, self.filename)
        self.path2 = os.path.join(self.directory, self.filename2)
        match = Match(None, MockTorrent(self.filename, self.url), 0)
        match2 = Match(None, MockTorrent(self.filename2, self.url2), 0)
        self.downloader = Downloader([match, match2], self.directory)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists(self.path2):
            os.remove(self.path2)
            
    def _test_torrent(self, path):
        self.assertTrue(os.path.exists(path))
        
        content = ""
        with open(path, "r") as f:
            content = f.read()
        
        self.assertTrue(content.startswith("d8:announce"))
        
    def test_download(self):
        self.downloader.start()
        self.downloader.wait(TEST_MAX_WAIT)
        self._test_torrent(self.path)
        self._test_torrent(self.path2)

if __name__ == "__main__":
    unittest.main()