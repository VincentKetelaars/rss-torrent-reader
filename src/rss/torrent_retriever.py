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
from xml.etree.ElementTree import ParseError
logger = get_logger(__name__)

class TorrentRetriever(GetParse):
       
    NAMESPACES = {"torrent" : "http://xmlns.ezrss.it/0.1/"}
    
    def item_text(self, item, child):
        x = item.find(child)
        if x is not None:
            return x.text
        return ""
    
    def parse(self, page):
        if page is not None:
            try:
                rss = ET.fromstring(page)
            except ParseError:
                return None
            c = rss.find("channel")
            title = c.find("title")
            desc = c.find("description")
            link = c.find("link")
            channel = Channel(title.text, desc.text, link.text)
            items = c.findall("item")
            for i in items:
                t = self.item_text(i, "title")
                d = self.item_text(i, "description")
                cat = self.item_text(i, "category")
                author = self.item_text(i, "author")
                l = self.item_text(i, "link")
                g = self.item_text(i, "guid")
                p = self.item_text(i, "pubDate")
                enclosure = i.find("enclosure")
                en_dic = {}
                if enclosure is not None:
                    for e in enclosure.items():
                        en_dic[e[0]] = e[1]
                t_dic = {}
                for a in Torrent.ATTRIBUTES:
                    te = i.find("torrent:" + a, namespaces=self.NAMESPACES)
                    if te is not None:
                        t_dic[a] = te.text
                channel.add_item(Item(i, t, d, cat, author, l, g, p, en_dic, Torrent(t_dic)))
            return channel
        return None
    
    def get(self, feed):
        logger.debug(feed)
        request = Request(feed)
        return request.request()