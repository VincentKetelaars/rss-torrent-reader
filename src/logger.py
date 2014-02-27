'''
Created on Dec 24, 2013

@author: Vincent Ketelaars
'''
import logging
import os

def get_logger(name):
    logger = logging.getLogger(name)
    return logger

class SafeTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        dirs = os.path.dirname(filename)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        logging.handlers.TimedRotatingFileHandler.__init__(self, filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)