'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from src.general.functions import string_to_size

class Preference(object):
    '''
    Container for torrent preferences
    '''

    def __init__(self, not_list, allowed_list, pref_list, min_width, min_height, min_movie_size, 
                 max_movie_size, languages, subtitles):
        self.not_list = not_list
        self.allowed_list = allowed_list
        self.pref_list = pref_list
        self.min_width = min_width
        self.min_height = min_height
        self.min_movie_size = self.parse_size(min_movie_size)
        self.max_movie_size = self.parse_size(max_movie_size)
        self.languages = languages
        self.subtitles = subtitles
        
    def parse_size(self, s):
        return string_to_size(s)