'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event

from src.torrent.downloader import Downloader
from src.torrent.rss_creator import RSSCreator
from src.torrent.email_handler import EmailHandler
from src.torrent.execution_handler import ExecutionHandler

from src.logger import get_logger
logger = get_logger(__name__)

HANDLER_LOOKUP = {"downloader" : Downloader, "rsscreator" : RSSCreator, "email" : EmailHandler, "executioner" : ExecutionHandler}

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
        call = HANDLER_LOOKUP.get(handler.lower(), None)
        if call is not None:
            return call(self.matches, essential=primary, **params)
        else:
            logger.error("This %s handler is unknown", handler)
        return None
            
    def run(self):
        for handler in self.handler_threads:
            handler.start()
        while(len(self.handler_threads)):
            for handler in self.handler_threads:
                if handler.done():
                    self.handler_threads.remove(handler)
                    # We collect the set of matches that are handled by all primary handlers
                    if handler.essential:
                        self.handled_matches.intersection_update(handler.handled())
                    if len(handler.handled()) > 0:
                        logger.info("%s handled %s correctly", handler.name, [m.torrent.film_title() for m in handler.handled()])
                    not_handled = set(self.matches) - set(handler.handled())
                    if len(not_handled) > 0: # Some didn't go so well
                        logger.warning("%s did not handle %s correctly", handler.name, [m.torrent.film_title() for m in not_handled])
            self.event.wait(self.LOOP_WAIT)
        self.event.set()
        
    def num_matches(self):
        return len(self.matches)
        
    def wait(self, timeout=0.0):
        self.event.wait(timeout)
        
    def handled(self):
        if all([h.done() for h in self.handler_threads if h.essential]):
            logger.debug("Handled matches: %s", [m.torrent.film_title() for m in self.handled_matches])
            return list(self.handled_matches)
        # Also if only partially done, check for those
        handled = set(self.matches)
        for handler in self.handler_threads:
            if handler.essential:
                handled.intersection_update(handler.handled())
        logger.debug("Partially done, these are handled: %s", [m.torrent.film_title() for m in handled])
        return list(handled)