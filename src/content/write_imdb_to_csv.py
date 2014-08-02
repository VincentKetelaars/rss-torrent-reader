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

    def __init__(self, movies, movies_file, series_file, handler_factory=None):
        Thread.__init__(self, name="IMDBCSVWriter")
        self.movies = movies
        self.handler_factory = handler_factory
        self.movies_file = movies_file
        self.series_file = series_file
        
    def run(self):
        if self.handler_factory is not None:
            self.handler_factory.wait(HANDLER_WAIT * self.handler_factory.num_matches())
        
        if len(self.movies) == 0: # Something has probably gone wrong.. Not overwriting the current file
            logger.info("We are not writing %d movies to file", len(self.movies))
            return
        
        if self.handler_factory is not None:
            for match in self.handler_factory.handled():
                logger.info("%s %shas been handled", match.torrent.film_title(), "%s " % (match.torrent.episode(),) if match.movie.is_series() else "")
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
