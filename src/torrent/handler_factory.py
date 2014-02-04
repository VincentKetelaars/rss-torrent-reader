'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

from src.torrent.downloader import Downloader
from src.torrent.rss_creator import RSSCreator

from src.logger import get_logger
from src.constants.constants import HANDLER_WAIT
from src.torrent.email_handler import EmailHandler
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
        primary, secondary = cfg.get_handlers()
        logger.info("Primary handlers %s and secondary handlers %s", primary, secondary)
        self.handler_threads = []
        for h in primary:
            handler = self._get_handler(h, cfg.get_handler(h), primary=True)
            if handler is not None:
                self.handler_threads.append(handler)
        for h in secondary:
            handler = self._get_handler(h, cfg.get_handler(h), primary=False)
            if handler is not None:
                self.handler_threads.append(handler)
        self.event = Event()   
        self.handled_matches = set(self.matches) # Initially all are handled
    
    def _get_handler(self, handler, params, primary=False):
        if handler == "downloader":
            return Downloader(self.matches, essential=primary, **params)
        elif handler == "rsscreator":
            return RSSCreator(self.matches, essential=primary, **params)
        elif handler == "email":
            return EmailHandler(self.matches, essential=primary, **params)
        else:
            logger.error("This %s handler is unknown", handler)
        return None
            
    def run(self):
        for handler in self.handler_threads:
            handler.start()
        for _ in range(0, int(HANDLER_WAIT / self.LOOP_WAIT)):
            for handler in self.handler_threads:
                if handler.done():
                    self.handler_threads.remove(handler)
                    # We collect the set of matches that are handled by all primary handlers
                    if handler.essential:
                        self.handled_matches.intersection_update(handler.handled())
            if len(self.handler_threads) > 0:
                self.event.wait(self.LOOP_WAIT)
            else:
                break
        self.event.set()
        
    def wait(self, timeout=0.0):
        self.event.wait(timeout)
        
    def handled(self):
        if all([h.done() for h in self.handler_threads if h.essential]):
            return list(self.handled_matches)
        return []