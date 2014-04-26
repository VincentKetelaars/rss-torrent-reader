'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element, ParseError
from xml.dom import minidom
from datetime import datetime

from src.torrent.match_handler import MatchHandler

from src.logger import get_logger
logger = get_logger(__name__)

RSSCREATOR_MAX_TORRENTS = 25

ET._original_serialize_xml = ET._serialize_xml
def _serialize_xml(write, elem, encoding, qnames, namespaces):
    if elem.tag == '![CDATA[':
        try:
            write("<%s%s]]>" % (elem.tag, elem.text.encode("utf-8")))
        except UnicodeEncodeError: # TODO, handle this better
            logger.exception("Can't encode this: %s", elem.text)
        return
    return ET._original_serialize_xml(write, elem, encoding, qnames, namespaces)
ET._serialize_xml = ET._serialize['xml'] = _serialize_xml

class RSSCreator(MatchHandler):
    '''
    This class creates a XML file to be used for RSS
    '''
    
    NAME = "RSSCreator"
    PARAMETERS = ["file", "max_torrents", "title", "link", "description"]

    def __init__(self, matches, movies_file=None, series_file=None, max_torrents=RSSCREATOR_MAX_TORRENTS, title="", link="", description="", **kwargs):
        MatchHandler.__init__(self, matches, name=RSSCreator.NAME, **kwargs)
        self.movies_file = movies_file
        self.series_file = series_file
        self.max_torrents = max_torrents
        self.title = title
        self.link = link
        self.description = description if description != "" else title
        
    def handle_matches(self, matches):
        if len(matches) == 0:
            return []
        handled = []
        if self.movies_file is not None:
            handled += self.handle_file([m for m in matches if m.movie.is_movie()], self.movies_file)
        if self.series_file is not None:
            handled += self.handle_file([m for m in matches if m.movie.is_series()], self.series_file)
        return handled
    
    def handle_file(self, matches, file):
        logger.debug("Writing %d matches to %s", len(matches), file)
        ET.register_namespace("torrent", "http://xmlns.ezrss.it/0.1/")
        try:
            tree = ElementTree(file=file)
        except (IOError, ParseError):
            # rss tag does not exist, file did not exist yet, or was corrupted somehow
            tree = ElementTree()
        root = tree.getroot()
        if tree.getroot() is None:
            root = Element("rss", attrib={"version" : "2.0"})
            tree._setroot(root)
        channel = root.find("channel")
        if channel is None:
            channel = Element("channel")
            channel.append(self.create_element_with_text("title", self.title))
            channel.append(self.create_element_with_text("link", self.link))
            channel.append(self.create_element_with_text("description", self.description))
            build_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S %j") # Sat, 07 Sep 2002 9:42:31 GMT
            channel.append(self.create_element_with_text("lastBuildDate", build_date)) 
            root.append(channel)
        if len(matches) > self.max_torrents: # If there are more than we can fit, choose the first self.max_torrents
            matches = matches[:self.max_torrents]
        for match in matches:
            channel.insert(3, match.torrent.item) # After title, link, description
        items = channel.findall("item")
        while len(items) > self.max_torrents: # If there are more elements than we can fit
            channel.remove(items.pop()) # Remove the oldest from the list        
        self.insert_CDATA(items)
#         tree.write(self.file, encoding="utf-8", xml_declaration=True)
        pretty_xml = self.prettify_xml(root)
        try:
            with open(file, "wb") as f:
                f.write(pretty_xml)
        except IOError:
            return []
        return matches
    
    def create_element_with_text(self, tag, text, attrib={}):
        e = Element(tag, attrib)
        e.text = text
        return e
    
    def insert_CDATA(self, items):
        for item in items:
            for e in item.iter():
                if (e.tag == "description" or e.tag.endswith("magnetURI")):
                    if not e.text is None and not e.text.startswith("<![CDATA["):
                        e.append(self.create_element_with_text("![CDATA[", e.text))
                        e.text = ""
                    else:
                        logger.warning("Text is None for item %s and tag %s", item.find("title").text, e.tag)
    
    def remove_empty_space(self, element):
        for e in element.iter():
            if not e.text is None:
                e.text = e.text.strip()
            if not e.tail is None:
                e.tail = e.tail.strip()
    
    def prettify_xml(self, element, encoding='utf-8'):
        """
        Return a pretty-printed XML string for the Element.
        Source: http://pymotw.com/2/xml/etree/ElementTree/create.html
        """
        self.remove_empty_space(element)
        rough_string = ET.tostring(element, encoding)
        try:
            reparsed = minidom.parseString(rough_string)
        except UnicodeEncodeError:
            logger.exception("")
            return rough_string
        return reparsed.toprettyxml(encoding=encoding)
    
    @staticmethod
    def create_html(movies_file="", series_file="", max_torrents=0, title="", link="", description="", **kwargs):
        div = MatchHandler.create_html(name=RSSCreator.NAME, class_name="rsscreator_handler", **kwargs)
        MatchHandler.add_label_input_br(div, "Movies File", 50, "movies_file", movies_file)
        MatchHandler.add_label_input_br(div, "Series File", 50, "series_file", series_file)
        MatchHandler.add_label_input_br(div, "Max torrents", 50, "max_torrents", max_torrents)
        MatchHandler.add_label_input_br(div, "Title", 50, "title", title)
        MatchHandler.add_label_input_br(div, "Link", 50, "link", link)
        MatchHandler.add_label_input_br(div, "Description", 50, "description", description)
        return div