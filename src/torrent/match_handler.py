'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from threading import Thread, Event
import xml.etree.ElementTree as ET

class MatchHandler(Thread):
    '''
    This class will act as interface for all match handlers. 
    Their implementations will take care of downloading torrents or otherwise use them
    '''
    
    # Should be defined for each handler, among others for WebGUI
    NAME = "MatchHandler" 
    PARAMETERS = []

    def __init__(self, matches, name="", essential=False):
        if name == "":
            name = MatchHandler.NAME
        Thread.__init__(self, name=name)
        self.setDaemon(True) # No matter what it is doing, when main is done, so is this (can be dangerous..)
        self.matches = matches
        self.event = Event()
        self.essential = essential
        self.successes = []
        
    def run(self):
        self.successes = self.handle_matches(self.matches)        
        self.event.set()
        
    def handle_matches(self, matches):
        """
        Return the successfully handled matches
        """
        for match in matches:
            if self.handle(match):
                self.successes.append(match)
        return self.successes
        
    def handle(self, match):
        """
        @return: True if match is successfully handled, False otherwise
        """
        raise NotImplementedError()
    
    def done(self):
        return self.event.is_set()
    
    def wait(self, timeout=None):
        self.event.wait(timeout)
        
    def handled(self):
        return self.successes
    
    @staticmethod
    def create_html(name=None, class_name=None, essential=None):
        if name is None or class_name is None:
            return None        
        div = ET.Element("div", attrib={"class" : class_name})
        title = ET.SubElement(div, "h4")
        title.text = name
        ET.SubElement(title, "input", attrib={"type" : "image", "src" : "pics/remove.jpg", "height" : "20", "width" : "20", 
                                              "onclick" : "return remove_handler(this)"})
        select = ET.SubElement(div, "select", attrib={"name" : name + "-importance"})
        ET.SubElement(select, "option", attrib={"value" : "inactive"}) # No text
        primary = ET.SubElement(select, "option", attrib={"value" : "primary"})
        primary.text = "primary"
        secondary = ET.SubElement(select, "option", attrib={"value" : "secondary"})
        secondary.text = "secondary"
        if essential is not None:
            if essential:
                primary.attrib["selected"] = "selected"
            else:
                secondary.attrib["selected"] = "selected"
        ET.SubElement(div, "br")
        return div
    
    @staticmethod
    def add_label_input_br(element, label, size, name, value, explanation=None):
        elabel = ET.SubElement(element, "label")
        elabel.text = label
        ET.SubElement(element, "input", attrib={"type" : "text", "size" : str(size), "name" : name, "value" : str(value)})
        if explanation is not None:
            alabel = ET.SubElement(element, "label")
            alabel.text = explanation
        ET.SubElement(element, "br")