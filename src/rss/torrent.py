'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

class Torrent(object):

    ATTRIBUTES = ["contentLength", "infoHash", "magnetURI", "seeds", "peers", "verified", "fileName"]
    
    def __init__(self, dictionary):
        self.dict = dictionary
            
    def get(self, key):
        return self.dict.get(key, None)        