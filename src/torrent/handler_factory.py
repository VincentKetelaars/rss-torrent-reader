'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

from src.torrent.downloader import Downloader
from src.torrent.rss_creator import RSSCreator

from src.logger import get_logger
from src.constants.constants import HANDLER_WAIT
logger = get_logger(__name__)

class HandlerFactory(Thread):
    '''
    This class takes in Configuration and instantiates the handlers it is supposed to use
    '''
    
    LOOP_WAIT = 0.5 # Seconds

    def __init__(self, matches, cfg):
        Thread.__init__(self, name="HandlerFactory")
        self.setDaemon(True)
        self.matches = matches
        handlers = cfg.get_handlers()
        logger.info("Handlers %s", handlers)
        handlers_info = {}
        for h in handlers:
            handlers_info[h] = cfg.get_handler(h)
        self.handler_threads = self.create_handlers(handlers_info)
        self.event = Event()   
        self.handled_matches = set()
        
    def create_handlers(self, info):
        handlers = []
        for k, v in info.iteritems():
            handler = self._get_handler(k, v)
            if handler is not None:
                handlers.append(handler)
        return handlers
    
    def _get_handler(self, handler, params):
        if handler == "downloader":
            return Downloader(self.matches, **params)
        elif handler == "rsscreator":
            return RSSCreator(self.matches, **params)
        else:
            logger.error("This %s handler is unknown", handler)
        return None
            
    def run(self):
        for handler in self.handler_threads:
            handler.start()
        for _ in range(0, int(HANDLER_WAIT / self.LOOP_WAIT)):
            for handler in self.handler_threads:
                if handler.done():
                    # We collect the set of matches that are handled by at least one handler
                    self.handled_matches.update(handler.handled()) 
                    self.handler_threads.remove(handler)
            if len(self.handler_threads) > 0:
                self.event.wait(self.LOOP_WAIT)
            else:
                break
        self.event.set()
        
    def wait(self, timeout=0.0):
        self.event.wait(timeout)
        
    def handled(self):
        return list(self.handled_matches)