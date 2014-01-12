'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
import sys

from src.logger import get_logger
logger = get_logger(__name__)

class Decider(object):
    '''
    This class takes in the movie merger and torrent_retriever.
    It matches the torrents with the movies and the results are pairs of compatible torrents and movies.
    '''

    def __init__(self, merger, torrent_retriever):
        self.merger = merger
        self.torrent_retriever = torrent_retriever
        
    def decide(self):
        self.torrent_retriever.wait(30)
        self.merger.wait(60)
        logger.info("Start deciding")
        results = []
        movies = [m for m in self.merger.movies() if m.should_download(sys.maxint, sys.maxint) ]
        torrents = self.torrent_retriever.torrents()
        for t in torrents:
            logger.debug("Torrent %s %d", t.title, t.torrent.get("contentLength") if t.torrent.get("contentLength") is not None else -1)
            for m in movies:
                if self.match(m, t):
                    results.append((m, t))
                    logger.debug("Match %s %s", m.title, t.title)
                    break
        return results
        
    def match(self, movie, torrent):
        """
        This method decides whether these two are a match
        @return: True if match
        """
        if torrent.title.find(movie.title) >= 0:
            return True
        return False