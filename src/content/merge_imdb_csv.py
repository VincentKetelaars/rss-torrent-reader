'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event
from sets import Set

from src.content.movie_parser import MovieParser
from src.logger import get_logger
logger = get_logger(__name__)


class MergeIMDBCsv(Thread):

    def __init__(self, imdb, movies_file, series_file):
        Thread.__init__(self)
        self.imdb = imdb
        self.movies_file = movies_file
        self.series_file = series_file
        self.result = Set()
        self.event = Event()
        
    def run(self):
        movies = {}
        series = {}
        try:
            mf = open(self.movies_file, "r")
            sf = open(self.series_file, "r")
            
            movies = MovieParser(None).parse(mf.read())
            series = MovieParser(None).parse(sf.read())
            logger.debug("Read %s and %s", self.movies_file, self.series_file)
        except:
            logger.exception("Reading of %s and %s failed", self.movies_file, self.series_file)
        finally:
            try:
                mf.close()
                sf.close()
            except:
                pass
        
        self.imdb.wait(60) # If already done this will return directly
        
        self.result = self.imdb.movies()
        for m in self.result:
            if m.is_movie():
                m.merge(movies.get(m.id))
            elif m.is_series():
                m.merge(series.get(m.id))    
            
        self.event.set()

    def wait(self, timeout):
        self.event.wait(timeout)
    
    def movies(self):
        """
        Return set of IMDBMovie
        """
        return self.result