'''
Created on Mar 24, 2014

@author: Vincent Ketelaars
'''

class Movie(object):
    '''
    Basic Movie representation
    '''

    def __init__(self, title, season, episode):
        self.title = title
        self.season = season
        self.episode = episode