'''
Created on Dec 29, 2013

@author: Vincent Ketelaars
'''
import xml.etree.ElementTree as ET
from threading import Lock
from sets import Set

from src.http.request import Request
from src.general.get_parse import GetParse
from src.rss.channel import Channel, Item
from src.rss.torrent import Torrent
from src.logger import get_logger
logger = get_logger(__name__)

class FeedHandler(object):
    '''
    This class obtains a rss torrent feeds and reads in all torrents
    '''
    class TorrentRetriever(GetParse):
        
        NAMESPACES = {"torrent" : "http://xmlns.ezrss.it/0.1/"}
        
        def parse(self, page):
            if page is not None:
                rss = ET.fromstring(page)
                c = rss.find("channel")
                title = c.find("title")
                desc = c.find("description")
                link = c.find("link")
                channel = Channel(title, desc, link)
                items = c.findall("item")
                for i in items:
                    try: 
                        t = i.find("title")
                        d = i.find("description")
                        cat = i.find("category")
                        author = i.find("author")
                        l = i.find("link")
                        g = i.find("guid")
                        p = i.find("pubDate")
                        enclosure = i.find("enclosure")
                        en_dic = {}
                        for e in enclosure.items():
                            en_dic[e[0]] = e[1]
                        t_dic = {}
                        for a in Torrent.ATTRIBUTES:
                            try:
                                te = i.find("torrent:" + a, namespaces=self.NAMESPACES)
                                t_dic[te.tag] = te.text
                            except:
                                logger.exception("")
                        item = Item(t, d, cat, author, l, g, p, en_dic, Torrent(t_dic))
                        channel.add_item(item)
                    except:
                        logger.exception("Couldn't parse this item %s", i)
                return channel
            return None
        
        def get(self, feed):
            logger.debug(feed)
            request = Request(feed)
            return request.request()

    def __init__(self, feeds, event):
        self.url_feeds = feeds
        self.event = event
        self.threads = [self.TorrentRetriever(f, self.result_callback, self.error_callback) for f in feeds]
        for t in self.threads: 
            t.start()
        self.results = []
        self.returned = 0
        self.lock = Lock()

    def result_callback(self, result):
        with self.lock:
            if result is not None:
                self.results.append(result)
            self.returned += 1
            if self.ready():
                self.event.set()

    def error_callback(self, c):
        pass
    
    def ready(self):
        return len(self.threads) == self.returned
    
    def channels(self):
        return self.results
    
    def torrents(self):
        return [t for c in self.results for t in c.items]
        