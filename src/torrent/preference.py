'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''

class Preference(object):
    '''
    Container for torrent preferences
    '''

    def __init__(self, not_list, pref_list, min_width, min_height):
        self.not_list = not_list
        self.pref_list = pref_list
        self.min_width = min_width
        self.min_height = min_height       
        