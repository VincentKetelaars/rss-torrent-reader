'''
Created on May 4, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.torrent.execution_handler import ExecutionHandler
from src.tests.mock_classes import MockMovie, MockTorrent
import os
from src.torrent.match import Match


class TestExecutionHandler(unittest.TestCase):


    def setUp(self):
        self.filename = "test.torrent"
        self.url = "http://www.torrenthound.com/torrent/e256280cf0dcb27ee1a3dc49b7fdd33ebf0c0f6c"
        self.directory = "/tmp"
        self.command = "tribler " + ExecutionHandler.PLACE_HOLDER + " &"
        self.path = os.path.join(self.directory, self.filename)
        self.match = Match(MockMovie("", 1234, "Feature Film"), MockTorrent(self.filename, self.url))

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_execution(self):
        executioner = ExecutionHandler([], None, None, True)
        executioner.handle(self.directory, self.command, False, self.match, [])
        self._test_torrent(self.path)
        
    def _test_torrent(self, path):
        self.assertTrue(os.path.exists(path))
        
        content = ""
        with open(path, "r") as f:
            content = f.read()
        
        self.assertTrue(content.startswith("d8:announce"))