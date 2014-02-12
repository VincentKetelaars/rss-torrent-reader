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

    def __init__(self, matches, name="MatchHandler", essential=False):
        Thread.__init__(self, name=name)
        self.setDaemon(True) # No matter what it is doing, when main is done, so is this (can be dangerous..)
        self.matches = matches
        self.event = Event()
        self.essential = essential
        self.successes = []
        
    def run(self):
        self.successes = self.handle_matches(self.matches)        
        self.event.set()
        
    def handle_matches(self, matches):
        """
        Return the successfully handled matches
        """
        successes = []
        for match in matches:
            if self.handle(match):
                successes.append(match)
        return successes
        
    def handle(self, match):
        """
        @return: True if match is successfully handled, False otherwise
        """
        raise NotImplementedError()
    
    def done(self):
        return self.event.is_set()
    
    def wait(self, timeout=None):
        self.event.wait(timeout)
        
    def handled(self):
        return self.successes