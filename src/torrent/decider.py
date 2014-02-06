'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
import sys

from src.logger import get_logger
from src.torrent.match import Match
from src.general.constants import FEED_WAIT, MERGER_WAIT
import re
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
        results = {}
        movies = [m for m in self.merger.movies().itervalues() if m.should_download(sys.maxint, sys.maxint) ]
        torrents = self.feeds.torrents()
        for t in torrents:
            if self.meets_requirements(t):
                for m in movies:
                    if self.match(m, t):
                        if m.is_movie():
                            logger.info("Match %s %s", m.title, t.title)
                        elif m.is_series():
                            logger.info("Match %s %s, episode %s", m.title, t.title, t.episode())
                            
                        if m.id not in results:
                            results[m.id] = t
                        else:
                            results[m.id] = self.compare_torrents(results[m.id], t)
                        break
                    
        return [Match(self.merger.movies().get(k), v) for k, v in results.iteritems()]
    
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
        # Ensure that either both are series, or both are movies
        if (movie.is_series() and not torrent.is_series()) or (movie.is_movie() and torrent.is_series()):
            return False
        
        match, rank = self._match_titles(movie.title, torrent.film_title())
        if match and rank == 0:
            if movie.is_series() and not movie.should_download(*torrent.episode()):
                return False
            return True
        
        if not match: # Only partial matches continue
            return False
        
        if torrent.description.find(movie.url) >= 0:
            return True
        
        logger.debug("Partial match %s %s", movie.title, torrent.title)
        for a in self.preference.allowed_list:
            if a in torrent.film_title().lower():
                return True
        
        if str(movie.year) in torrent.film_title():
            return True
        return False
    
    def _match_titles(self, mtitle, ttitle):
        """
        Determine whether two titles are equal
        It gives a perfect match a score of 0, subsequent 'worse' matches are given increasing higher numbers
        If there is not match at all it returns (False, -1)
        @rtype: (Boolean, int) 
        """
        # Make both lowercase
        mtitle = mtitle.lower() 
        ttitle = ttitle.lower()
        if mtitle == ttitle:
            return (True, 0)
        p = re.compile("[':,]")
        m_removed, _ = p.subn("", mtitle)
        if m_removed == ttitle:
            return (True, 0)
        m_nodots = m_removed.replace(".", " ").strip()
        if m_nodots == ttitle:
            return (True, 0)
        m_removed = m_removed.replace("&", "(\&|and)") # Allow for '&' and 'and'
        year = re.compile("d{4}")
        m_removed = year.sub("(\\0)?", m_removed)
        partial = re.match(m_removed, ttitle, re.IGNORECASE)
        if partial:
            if partial.group(0) == ttitle: # Complete match
                return (True, 0)
            else: # Partial
                return (True, 1)
        return (False, -1) # No match whatsoever
        
    def compare_torrents(self, t1, t2):
        """
        This function is intended to compare two torrents for the same movie/series,
        and return the best. The comparision is first done on the preference list from the config file.
        If that does not result in a choice, a comparison is made based on the resolution.
        @return: the better of the two torrents, defaults to the first
        """
        t1_title = t1.title.lower()
        t2_title = t2.title.lower()
        for item in self.preference.pref_list:
            if item.lower() in t1_title and item.lower() not in t2_title:
                return t1
            elif item.lower() not in t1_title and item.lower() in t2_title:
                return t2
            # Otherwise they both don't have the keyword or both have the keyword
        # Resolution compare (x, y) with (a, b), the x and a comparison is done first, only when equal are y and b compared
        if t1.resolution() < t2.resolution():
            return t2
        elif t1.resolution() > t2.resolution():
            return t1
        return t1 # We have to default to something