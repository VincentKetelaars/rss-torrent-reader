'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from src.http.elementtree import add_label_input_br, create_div, _add_element,\
    add_break, add_option, add_select, add_input
from threading import Thread, Event

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
        div = create_div({"class" : class_name})
        title = _add_element(div, "h4", text=name)
        add_input(title, {"type" : "image", "src" : "pics/remove.jpg", "height" : "20", "width" : "20", 
                          "onclick" : "return remove_handler(this)"})
        select = add_select(div, {"name" : name + "-importance"})
        add_option(select, {"value" : "inactive"}) # No text
        primary = add_option(select, {"value" : "primary"})
        primary.text = "primary"
        secondary = add_option(select, {"value" : "secondary"})
        secondary.text = "secondary"
        if essential is not None:
            if essential:
                primary.attrib["selected"] = "selected"
            else:
                secondary.attrib["selected"] = "selected"
        add_break(div)
        return div
    
    @staticmethod
    def add_label_input_br(element, label, size, name, value, explanation=None):
        return add_label_input_br(element, label, size, name, value, explanation)