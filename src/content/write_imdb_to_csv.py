'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
from threading import Thread

from src.logger import get_logger
from src.general.constants import NEWLINE, HANDLER_WAIT
logger = get_logger(__name__)

class WriteIMDBToCsv(Thread):
    '''
    Write the list of movies and series to two separate files
    '''

    def __init__(self, movies, handler, movies_file, series_file):
        Thread.__init__(self)
        self.movies = movies
        self.handler = handler
        self.movies_file = movies_file
        self.series_file = series_file
        
    def run(self):
        self.handler.wait(HANDLER_WAIT)
        
        if len(self.movies) == 0: # Something has probably gone wrong.. Not overwriting this
            return
        
        for match in self.handler.handled():
            self.movies[match.movie.id].handled(*match.torrent.episode()) # Update episode number
        
        def write(content, path):
            try:
                with open(path, "wb") as f:
                    return f.write(content)
            except IOError:
                logger.error("Could not write to %s", path)
                
        sorted_movies = sorted(self.movies.values(), key=lambda x: x.modified, reverse=True)
        movies_content = ""
        series_content = ""
        for m in sorted_movies:
            if m.is_movie():
                movies_content += m.to_line() + NEWLINE
            elif m.is_series():
                series_content += m.to_line() + NEWLINE
            else:
                logger.warning("Neither movie or series..: %s", m.type)
        
        write(movies_content, self.movies_file)
        write(series_content, self.series_file)                                         
        logger.info("Wrote %d movies to %s and %d series to %s", sum([m.is_movie() for m in sorted_movies]), 
                     self.movies_file, sum([m.is_series() for m in sorted_movies]), self.series_file)
