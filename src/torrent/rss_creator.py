'''
Created on Feb 1, 2014

@author: Vincent Ketelaars
'''
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element, ParseError

from src.torrent.match_handler import MatchHandler
from xml.dom import minidom

from src.logger import get_logger
logger = get_logger(__name__)

RSSCREATOR_MAX_TORRENTS = 25

ET._original_serialize_xml = ET._serialize_xml
def _serialize_xml(write, elem, encoding, qnames, namespaces):
    if elem.tag == '![CDATA[':
        try:
            write("<%s%s]]>" % (elem.tag, elem.text))
        except UnicodeEncodeError: # TODO, handle this better
            logger.error("Can't encode this: %s", elem.text)
        return
    return ET._original_serialize_xml(write, elem, encoding, qnames, namespaces)
ET._serialize_xml = ET._serialize['xml'] = _serialize_xml

class RSSCreator(MatchHandler):
    '''
    This class creates a XML file to be used for RSS
    '''

    def __init__(self, matches, file=None, max_torrents=RSSCREATOR_MAX_TORRENTS, title="", link="", description="", **kwargs):
        MatchHandler.__init__(self, matches, "RSSCreator", **kwargs)
        self.file = file
        self.max_torrents = max_torrents
        self.title = title
        self.link = link
        self.description = description if description != "" else title
        
    def handle_matches(self, matches):
        if self.file is None or len(matches) == 0:
            return []
        ET.register_namespace("torrent", "http://xmlns.ezrss.it/0.1/")
        try:
            tree = ElementTree(file=self.file)
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
            root.append(channel)
        if len(matches) > self.max_torrents: # If there are more than we can fit, choose the first self.max_torrents
            matches = matches[:self.max_torrents]
        self.insert_CDATA(matches)
        for match in matches:
            channel.insert(3, match.torrent.item) # After title, link, description
        items = channel.findall("item")
        while len(items) > self.max_torrents: # If there are more elements than we can fit
            channel.remove(items.pop()) # Remove the oldest from the list
        tree.write(self.file, encoding="utf-8", xml_declaration=True)
        pretty_xml = self.prettify_xml(root)
        with open(self.file, "wb") as f:
            f.write(pretty_xml)
        return matches
    
    def create_element_with_text(self, tag, text, attrib={}):
        e = Element(tag, attrib)
        e.text = text
        return e
    
    def insert_CDATA(self, matches):
        for m in matches:
            for e in m.torrent.item.iter():
                if e.tag == "description" or e.tag.endswith("magnetURI") and not e.text.startswith("<![CDATA["):
                    e.append(self.create_element_with_text("![CDATA[", e.text))
                    e.text = None
    
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
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(encoding=encoding)