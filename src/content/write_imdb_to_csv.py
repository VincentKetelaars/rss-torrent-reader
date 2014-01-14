'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
from threading import Thread

from src.logger import get_logger
from src.constants.constants import NEWLINE
logger = get_logger(__name__)

class WriteIMDBToCsv(Thread):
    '''
    Write the list of movies and series to two separate files
    '''

    def __init__(self, movies, movies_file, series_file):
        Thread.__init__(self)
        self.movies = movies
        self.movies_file = movies_file
        self.series_file = series_file
        
    def run(self):
        if len(self.movies) == 0: # Something has probably gone wrong.. Not overwriting this
            return
        try:
            mf = open(self.movies_file, "w")
            sf = open(self.series_file, "w")
            
            i = 0
            j = 0
            
            sorted_movies = sorted(self.movies, key=lambda x: x.modified, reverse=True)
            for m in sorted_movies:
                if m.is_movie():
                    mf.write(m.to_line() + NEWLINE)
                    i += 1
                elif m.is_series():
                    sf.write(m.to_line() + NEWLINE)
                    j += 1
                else:
                    logger.debug("Neither movie or series..: %s", m.type)                                    
            logger.debug("Wrote %d movies to %s and %d series to %s", i, self.movies_file, j, self.series_file)
        except:
            logger.exception("Failed to write to %s and %s", self.movies_file, self.series_file)
        finally:
            try:
                mf.close()
                sf.close()
            except:
                pass              
        
        
        