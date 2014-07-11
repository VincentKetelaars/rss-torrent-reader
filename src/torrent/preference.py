'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from src.general.functions import string_to_size

class Preference(object):
    '''
    Container for torrent preferences
    '''

    def __init__(self, not_list=[], allowed_list=[], pref_list=[], not_in_desc=[], min_width=0, min_height=0, min_movie_size="0MB", 
                 max_movie_size="50GB", min_series_size="0MB", max_series_size="50GB", languages=[], subtitles=[], excluded_extensions=[]):
        self.not_list = not_list # Should not be in title
        self.allowed_list = allowed_list # Keywords that are allowed around the title name
        self.pref_list = pref_list # Order of preference in titles
        self.not_in_desc = not_in_desc # Not allowed in description
        self.min_width = min_width
        self.min_height = min_height
        self.min_movie_size = self.parse_size(min_movie_size) #bytes
        self.max_movie_size = self.parse_size(max_movie_size) #bytes
        self.min_series_size = self.parse_size(min_series_size) #bytes
        self.max_series_size = self.parse_size(max_series_size) #bytes
        self.languages = languages
        self.subtitles = subtitles
        self.excluded_extensions = excluded_extensions
        
    def parse_size(self, s):
        return string_to_size(s)