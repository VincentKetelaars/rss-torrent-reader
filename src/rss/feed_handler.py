'''
Created on Dec 29, 2013

@author: Vincent Ketelaars
'''
from threading import Lock, Event

from src.rss.torrent_retriever import TorrentRetriever

from src.logger import get_logger
logger = get_logger(__name__)

class FeedHandler(object):
    '''
    This class obtains a rss torrent feeds and reads in all torrents
    '''

    def __init__(self, feeds):
        self.url_feeds = feeds
        self.event = Event()
        self.threads = [TorrentRetriever(f, self.result_callback, self.error_callback) for f in feeds]
        for t in self.threads: 
            t.start()
        self.results = []
        self.returned = 0
        self.lock = Lock()

    def result_callback(self, result):
        with self.lock:
            if result is not None:
                self.results.append(result)
            self.returned += 1
            if self.ready():
                self.event.set()

    def error_callback(self, c):
        pass
    
    def ready(self):
        return len(self.threads) == self.returned
    
    def channels(self):
        return self.results
    
    def torrents(self):
        return [t for c in self.results for t in c.items]
    
    def wait(self, timeout):
        self.event.wait(timeout)
        