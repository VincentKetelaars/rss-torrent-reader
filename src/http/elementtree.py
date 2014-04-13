'''
Created on Apr 13, 2014

@author: Vincent Ketelaars
'''
PICS_ADD = "pics/add.png"
PICS_REMOVE = "pics/remove.jpg"

import xml.etree.ElementTree as ET

def _add_element(parent, tag, text=None, **attributes):
    el = ET.SubElement(parent, tag, attrib=attributes)
    if text is not None:
        el.text = text
    return el

def add_break(parent):
    return _add_element(parent, "br")

def add_button(parent, attributes):
    return _add_element(parent, "button", **attributes)

def add_configuration_header(element, h3_text, p_text):
    h3 = ET.SubElement(element, "h3")
    h3.text = h3_text
    p = ET.SubElement(element, "p")
    p.text = p_text
    
def add_div(parent, attributes):
    return _add_element(parent, "div", **attributes)

def add_form(parent, attributes):
    return _add_element(parent, "form", **attributes)

def add_input(parent, attributes):
    return _add_element(parent, "input", **attributes)

def add_option(parent, attributes):
    return _add_element(parent, "option", **attributes)

def add_select(parent, attributes):
    return _add_element(parent, "select", **attributes)

def add_label_input_br(element, label, size, name, value, explanation=None):
    elabel = ET.SubElement(element, "label")
    elabel.text = label
    ET.SubElement(element, "input", attrib={"type" : "text", "size" : str(size), "name" : name, 
                                            "value" : str(value) if value is not None else ""})
    if explanation is not None:
        alabel = ET.SubElement(element, "label")
        alabel.text = explanation
    ET.SubElement(element, "br")
    
def _create_element(tag, text=None, **attributes):
    el = ET.Element(tag, attrib=attributes)
    if text is not None:
        el.text = text
    return el
    
def create_div(attributes):
    return _create_element("div", **attributes)
    
def create_input(attributes):
    return _create_element("input", **attributes)

def create_td(attributes):
    return _create_element("td", **attributes)

def create_tr_with_tds(*tds):
    tr = ET.Element("tr")
    for td in tds:
        if isinstance(td, ET.Element) and td.tag == "td":
            tr.append(td) # td element
            continue
        etd = ET.SubElement(tr, "td")
        if isinstance(td, ET.Element):
            etd.append(td) # Other element, which will be subelement of td
        else:
            etd.text = td # text content of td
    return tr

def fromstring(s):
    return ET.fromstring(s)

def onclick_icon(element, add, onclick_text):
    ET.SubElement(element, "input", attrib={"type" : "image", "src" : PICS_ADD if add else PICS_REMOVE, 
                                            "height" : "20", "width" : "20", "onclick" : onclick_text})

def to_html_string(root):
    return ET.tostring(root, encoding="utf-8", method="html")