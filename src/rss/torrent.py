'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

class Torrent(object):

    ATTRIBUTES = ["contentLength", "infoHash", "magnetURI", "seeds", "peers", "leechs", "verified", "fileName"]
    
    def __init__(self, dictionary):
        self.dict = dictionary
            
    def get(self, key, default=None):
        return self.dict.get(key, default)    