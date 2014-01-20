'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
import sys

from src.logger import get_logger
from src.torrent.match import Match
from src.constants.constants import FEED_WAIT, MERGER_WAIT
logger = get_logger(__name__)

class Decider(object):
    '''
    This class takes in the movie merger and torrent_retriever.
    It matches the torrents with the movies and the results are pairs of compatible torrents and movies.
    '''

    def __init__(self, merger, feeds, preference):
        self.merger = merger
        self.feeds = feeds
        self.preference = preference
        
    def decide(self):
        self.feeds.wait(FEED_WAIT)
        self.merger.wait(MERGER_WAIT)
        logger.info("Start deciding")
        results = []
        movies = [m for m in self.merger.movies().itervalues() if m.should_download(sys.maxint, sys.maxint) ]
        torrents = self.feeds.torrents()
        for t in torrents:
            if self.meets_requirements(t):
                for m in movies:
                    if self.match(m, t):
                        p = self.quality(t)
                        results.append(Match(m, t, p))
                        logger.debug("Match %s %s %d", m.title, t.title, p)
                        break
        return results
    
    def meets_requirements(self, torrent):
        """
        Determine if the torrent meets the user requirements
        """
        ttitle = torrent.title.lower()
        
        # Ensure that none of the option in not list are present
        for n in self.preference.not_list:
            if ttitle.find(n.lower()) >= 0:
                logger.debug("%s contains the unwanted signature %s", torrent.title, n)
                return False
        
        width, height = torrent.resolution()
        if width < self.preference.min_width or height < self.preference.min_height:
            logger.debug("%s does not have the required resolution of %dx%d with only %dx%d", 
                         torrent.title, self.preference.min_width, self.preference.min_height, width, height)
            return False
        return True
        
    def match(self, movie, torrent):
        """
        This method decides whether these two are a match
        @return: True if match        
        """
        ttitle = torrent.title.lower()
        mtitle = movie.title.replace(".", " ").lower()
        
        if ttitle.find(mtitle) == 0: # It should start with it
            return True
        
        if torrent.description.find(movie.url) >= 0:
            return True
        return False
    
    def quality(self, torrent):
        """
        This function returns a number that represents the quality of the match according to the user
        @return: -1 if no preference match, otherwise index of list
        """
        for i in range(0, len(self.preference.pref_list)):
            if self.preference.pref_list[i].lower() in torrent.title.lower():
                return i
        return -1