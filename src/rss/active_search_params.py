'''
Created on Feb 9, 2014

@author: Vincent Ketelaars
'''

class ActiveSearchParameters(object):
    '''
    This class holds parameters necessary for active search
    '''

    def __init__(self, urls, max_movies, max_series):
        self.urls = urls
        self.max_movies = max_movies
        self.max_series = max_series
        