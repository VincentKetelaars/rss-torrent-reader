'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
import xml.etree.ElementTree as ET

from src.general.get_parse import GetParse
from src.rss.channel import Channel, Item
from src.rss.torrent import Torrent
from src.http.request import Request

from src.logger import get_logger
logger = get_logger(__name__)

class TorrentRetriever(GetParse):
       
    NAMESPACES = {"torrent" : "http://xmlns.ezrss.it/0.1/"}
    
    def parse(self, page):
        if page is not None:
            rss = ET.fromstring(page)
            c = rss.find("channel")
            title = c.find("title")
            desc = c.find("description")
            link = c.find("link")
            channel = Channel(title.text, desc.text, link.text)
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
                            t_dic[a] = te.text
                        except:
                            logger.exception("")
                    item = Item(i, t.text, d.text, cat.text, author.text, l.text, g.text, p.text, en_dic, Torrent(t_dic))
                    channel.add_item(item)
                except:
                    logger.exception("Couldn't parse this item %s", i)
            return channel
        return None
    
    def get(self, feed):
        logger.debug(feed)
        request = Request(feed)
        return request.request()