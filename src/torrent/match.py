'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''

class Match(object):
    '''
    This class represents a match between a movie and a torrent
    '''


    def __init__(self, movie, torrent, quality):
        self.movie = movie
        self.torrent = torrent
        self.quality = quality # -1 means no indication