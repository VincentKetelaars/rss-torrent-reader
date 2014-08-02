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

    def __init__(self, passive_feeds, active_feeds):
        """
        @type passive_feeds: List(str)
        @type active_feeds: {str, IMDBMovie}
        """
        self.passive_feeds = passive_feeds
        self.active_feeds = active_feeds
        self.event = Event()
        self.threads = [TorrentRetriever(f, self.result_callback, self.error_callback) for f in passive_feeds + active_feeds.keys()]
        for t in self.threads: 
            t.start()
        self.results = {}
        self._returned = 0
        self.lock = Lock()
        if len(self.threads) == 0:
            self.event.set()

    def result_callback(self, feed, result):
        with self.lock:
            if result is not None:
                self.results[feed] = result
            self._returned += 1
            if self.ready():
                self.event.set()

    def error_callback(self, c):
        pass
    
    def num_feeds(self):
        return len(self.passive_feeds) + len(self.active_feeds)
    
    def ready(self):
        return len(self.threads) == self._returned
    
    def channels(self):
        return self.results.values()
    
    def torrents(self):
        return [t for c in self.results.values() for t in c.items]
    
    def passive_torrents(self):
        return [t for u, c in self.results.iteritems() for t in c.items if not u in self.active_feeds.keys()]
    
    def active_channels(self):
        return [(c, self.active_feeds.get(u)) for u, c in self.results.iteritems() if u in self.active_feeds.keys()]
    
    def wait(self, timeout):
        try:
            self.event.wait(timeout)
        except (KeyboardInterrupt, SystemExit):
            logger.info("We have %d out of %d: %s\n\nWe lack %s" % (self._returned, len(self.threads), self.results, 
                                                                    [t.input for t in self.threads if not t.input in self.results.keys()]))
            raise