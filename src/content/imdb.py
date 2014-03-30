'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''
from threading import Lock, Event

from src.content.movie_parser import MovieParser
from src.logger import get_logger
logger = get_logger(__name__)

class IMDB(object):
    '''
    classdocs
    '''

    def __init__(self, csvs):
        self.event = Event()
        self.threads = [MovieParser(c, self.result_callback, self.error_callback) for c in csvs]
        for t in self.threads:
            t.start()
        self._returned = 0
        self.results = []
        self.lock = Lock()
        if len(self.threads) == 0:
            self.event.set()
        
    def result_callback(self, csv, result):
        with self.lock:
            if result is not None:
                self.results.append(result)
            self._returned += 1
            if self.ready():
                self.event.set()

    def error_callback(self, c):
        pass
    
    def ready(self):
        return len(self.threads) == self._returned
    
    def movies(self):
        """
        Return dictionary of movies where id is the key
        """
        return dict([m for s in self.results for m in s.items()])
    
    def wait(self, timeout):
        self.event.wait(timeout)