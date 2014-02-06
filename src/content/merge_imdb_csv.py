'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

from src.content.movie_parser import MovieParser
from src.logger import get_logger
from src.general.constants import IMDB_WAIT
logger = get_logger(__name__)


class MergeIMDBCsv(Thread):

    def __init__(self, imdb, movies_file, series_file):
        Thread.__init__(self)
        self.imdb = imdb
        self.movies_file = movies_file
        self.series_file = series_file
        self.result = {}
        self.event = Event()
        
    def run(self):
        
        def read(path):
            try:
                with open(path, "r") as f:
                    return MovieParser(None).parse(f.read())
            except IOError:
                logger.debug("Reading of %s failed", path)
        
        movies = read(self.movies_file)
        series = read(self.series_file)
        
        self.imdb.wait(IMDB_WAIT) # If already done this will return directly
        
        logger.debug("We have a total of %d films", len(self.imdb.movies()))
        
        self.result = self.imdb.movies()
        for m in self.result.itervalues():
            if m.is_movie():
                m.merge(movies.get(m.id))
            elif m.is_series():
                m.merge(series.get(m.id))   
                
        if len(self.result) == 0: # No luck getting the newest version, lets just use the one we have
            self.result = dict(movies.items() + series.items())
            logger.debug("Since we have no newer version we use the stored one with %d films", len(self.result))
            
        self.event.set()

    def wait(self, timeout):
        self.event.wait(timeout)
    
    def movies(self):
        """
        Return dictionary of IMDBMovie with id as key
        """
        return self.result