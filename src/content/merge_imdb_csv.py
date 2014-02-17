'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

from src.logger import get_logger
from src.general.constants import IMDB_WAIT
logger = get_logger(__name__)

class MergeIMDBCsv(Thread):

    def __init__(self, imdb, movies_from_file, series_from_file):
        Thread.__init__(self, name="IMDBMerger")
        self.imdb = imdb
        self.movies_from_file = movies_from_file
        self.series_from_file = series_from_file
        self.result = {}
        self.event = Event()
        
    def run(self):
        
        self.imdb.wait(IMDB_WAIT) # If already done this will return directly
        
        logger.debug("We have a total of %d films", len(self.imdb.movies()))
        
        self.result = self.imdb.movies()
        for m in self.result.itervalues():
            if m.is_movie():
                m.merge(self.movies_from_file.get(m.id))
            elif m.is_series():
                m.merge(self.series_from_file.get(m.id))   
                
        if len(self.result) == 0: # No luck getting the newest version, lets just use the one we have
            self.result = dict(self.movies_from_file.items() + self.series_from_file.items())
            logger.debug("Since we have no newer version we use the stored one with %d films", len(self.result))
            
        self.event.set()

    def wait(self, timeout):
        self.event.wait(timeout)
    
    def movies(self):
        """
        Return dictionary of IMDBMovie with id as key
        """
        return self.result