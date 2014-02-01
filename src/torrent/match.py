'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''

class Match(object):
    '''
    This class represents a match between a movie and a torrent
    '''

    def __init__(self, movie, torrent):
        self.movie = movie
        self.torrent = torrent
        
    def __str__(self):
        return "%s %s %d" % (self.movie, self.torrent, self.quality)