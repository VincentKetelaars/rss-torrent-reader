'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from datetime import datetime

from src.content.imdb_movie import IMDBMovie
from src.content.merge_imdb_csv import MergeIMDBCsv
from src.rss.feed_handler import FeedHandler
from src.rss.channel import Item, Channel
from src.torrent.match_handler import MatchHandler

class MockMerger(MergeIMDBCsv):
    
    def __init__(self, movies):
        self.m = movies
        
    def wait(self, timeout):
        return
    
    def movies(self):
        return self.m

class MockTorrentFeed(FeedHandler):

    def __init__(self, url_channel):
        self.results = url_channel
        self.active_feeds = {}
        self.passive_feeds = []
        
    def wait(self, timeout):
        return
    
# Would be exhausting to put in everything without any benefit    
class MockMovie(IMDBMovie):
        
    def __init__(self, title, year, type_, **kwargs):
        IMDBMovie.__init__(self, "line", "id_", datetime.now(), datetime.now(), "description", title, type_, [], 0, 0, 0, year, [], 0, datetime.now(), "url", **kwargs)

class MockTorrent(Item):
    
    def __init__(self, filename, url, title=""):
        Item.__init__(self, None, title, "description", "category", "author", "link", "guid", "pubdate", {}, None)
        self._filename = filename
        self._url = url
    
    def filename(self):
        return self._filename
    
    def url(self):
        return self._url
    
class MockItem(Item):
    
    def __init__(self, title, description):
        Item.__init__(self, None, title, description, None, None, None, None, None, {}, None)
        
class MockChannel(Channel):
    
    def __init__(self, items):
        Channel.__init__(self, None, None, None)
        self.items = items
        
class MockHandler(MatchHandler):
    
    def wait(self, timeout=None):
        return True