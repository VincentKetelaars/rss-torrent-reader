'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

class MatchHandler(Thread):
    '''
    This class will act as interface for all match handlers. 
    Their implementations will take care of downloading torrents or otherwise use them
    '''

    def __init__(self, matches, name="MatchHandler"):
        Thread.__init__(self, name=name)
        self.matches = matches
        self.event = Event()
        
    def run(self):
        self.successes = []
        for match in self.matches:
            if self.handle(match):
                self.successes.append(match)
        self.event.set()
        
    def handle(self, match):
        raise NotImplementedError()
    
    def wait(self, timeout=None):
        self.event.wait(timeout)
        
    def handled(self):
        return self.successes