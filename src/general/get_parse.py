'''
Created on Jan 2, 2014

@author: Vincent Ketelaars
'''
from threading import Thread

from src.logger import get_logger
logger = get_logger(__name__)

class GetParse(Thread):
    '''
    This class forms an abstract class that allows for http requests and subsequent parsing
    @param result_callback: Callback function returns input and result
    '''

    def __init__(self, input_, result_callback=None, error_callback=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.input = input_
        self.result_callback = result_callback
        self.error_callback = error_callback
        
    def parse(self, page):
        raise NotImplementedError()
    
    def get(self, input_):
        raise NotImplementedError()
    
    def run(self):
        result = None
        try:
            result = self.parse(self.get(self.input))
        except:
            logger.exception("Could not use %s", self.input)
            self.error_callback(self.input)
        finally:
            if self.result_callback is not None:
                self.result_callback(self.input, result)
        
    def value(self):
        return self.result