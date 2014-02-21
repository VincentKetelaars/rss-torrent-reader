'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
import re

class Preference(object):
    '''
    Container for torrent preferences
    '''
    
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024

    def __init__(self, not_list, allowed_list, pref_list, min_width, min_height, min_movie_size, max_movie_size):
        self.not_list = not_list
        self.allowed_list = allowed_list
        self.pref_list = pref_list
        self.min_width = min_width
        self.min_height = min_height
        self.min_movie_size = self.parse_size(min_movie_size)
        self.max_movie_size = self.parse_size(max_movie_size)
        
    def parse_size(self, s):
        s = s.strip()
        m = re.match("\d+", s)
        num = 0
        if m is not None:
            num = int(m.group(0))
        mul = 0
        if s.find("KB") > 0:
            mul = self.KB
        elif s.find("MB") > 0:
            mul = self.MB
        elif s.find("GB") > 0:
            mul = self.GB
        elif s.find("TB") > 0:
            mul = self.TB
        return num * mul