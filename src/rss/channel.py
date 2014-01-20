'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''
import re

from src.logger import get_logger
logger = get_logger(__name__)

class Channel(object):
    
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
class Item(object):

    def __init__(self, item, title, description, category, author, link, guid, pubdate, enclosure, torrent):
        self.item = item
        self.title = title
        self.description = description
        self.category = category
        self.author = author
        self.link = link
        self.guid = guid
        self.pubdate = pubdate
        self.enclosure = enclosure # dictionary 
        self.torrent = torrent # Torrent
        
    def url(self):
        return self.enclosure.get("url", None)
    
    def filename(self):
        f = self.torrent.get("fileName")
        if f is None:
            f = self.title + ".torrent"
        return f
    
    def episode(self):
        """
        @return: (season, episode) or (0, 0)
        """
        episode = re.findall("S\d{2}E\d{2}", self.title)
        if len(episode) > 0:
            v = episode[0] # Use the first, even if there are more
            return (int(v[1:2]), int(v[4:5]))
        return (0, 0)
        
    def resolution(self):
        """
        Parse description for resolution and return (width, height)
        """
        resolution = re.findall("\d{3,4}x\d{3,4}", self.description)
        width = 0
        height = 0
        if len(resolution) > 0:
            r = resolution[0] # Use only the first, even if there are more
            ints = r.split("x")
            width = int(ints[0])
            height = int(ints[1])
        else: # Not explicitly mentioned, so look for 720p or 1080p, ratio, bitrate, size?
            if self.description.lower().find("720p") > 0 or self.description.lower().find("1080p") > 0:
                pass # Find some way to deal with this, because we shouldn't trust these values outright
                    
        return (width, height)
        
    def __str__(self):
        return self.title