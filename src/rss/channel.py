'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''


class Channel(object):
    
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
class Item(object):

    def __init__(self, title, description, category, author, link, guid, pubdate, enclosure, torrent):
        self.title = title
        self.description = description
        self.category = category
        self.author = author
        self.link = link
        self.guid = guid
        self.pubdate = pubdate
        self.enclosure = enclosure # dictionary 
        self.torrent = torrent # Torrent