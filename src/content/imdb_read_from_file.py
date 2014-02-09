'''
Created on Feb 9, 2014

@author: Vincent Ketelaars
'''

from src.logger import get_logger
from src.content.movie_parser import MovieParser
logger = get_logger(__name__)

class IMDBReadFromFile(object):
    '''
    This class takes in IMDB csv file and outputs a dictionary of movies
    '''
    
    def __init__(self, file):
        '''
        @param file: CSV file of movies
        '''
        self.file = file
        
    def read(self):
        try:
            with open(self.file, "r") as f:
                return MovieParser(None).parse(f.read())
        except IOError:
            logger.debug("Reading of %s failed", self.file)
        return None     