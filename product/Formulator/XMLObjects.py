# -*- coding: utf-8 -*-
from xml.dom.minidom import parse, parseString, Node
from xml.sax.saxutils import unescape
# an extremely simple system for loading in XML into objects

class Object:
    pass

class XMLObject:
    def __init__(self):
        self.elements = Object()
        self.first = Object()
        self.attributes = {}
        self.text = ''
        
    def getElementNames(self):
        return [element for element in dir(self.elements)
                if not element.startswith('__')]

    def getAttributes(self):
        return self.attributes
    
def elementToObject(parent, node):
    # create an object to represent element node
    object = XMLObject()
    # make object attributes off node attributes
    for key, value in node.attributes.items():
        object.attributes[key] = value
    # make lists of child elements (or ignore them)
    for child in node.childNodes:
        nodeToObject(object, child)
    # add ourselves to parent node
    name = str(node.nodeName)
    l = getattr(parent.elements, name, [])
    l.append(object)
    setattr(parent.elements, name, l)
    
def attributeToObject(parent, node):
    # should never be called
    pass

def textToObject(parent, node):
    # add this text to parents text content
    parent.text += unescape(node.data)
    
def processingInstructionToObject(parent, node):
    # don't do anything with these
    pass

def commentToObject(parent, node):
    # don't do anything with these
    pass

def documentToObject(parent, node):
    elementToObject(parent, node.documentElement)

def documentTypeToObject(parent, node):
    # don't do anything with these
    pass

_map = {
    Node.ELEMENT_NODE: elementToObject,
    Node.ATTRIBUTE_NODE: attributeToObject,
    Node.TEXT_NODE: textToObject,
 #   Node.CDATA_SECTION_NODE: 
 #   Node.ENTITY_NODE:
    Node.PROCESSING_INSTRUCTION_NODE: processingInstructionToObject,
    Node.COMMENT_NODE: commentToObject,
    Node.DOCUMENT_NODE: documentToObject,
    Node.DOCUMENT_TYPE_NODE: documentTypeToObject,
#    Node.NOTATION_NODE:
    }

def nodeToObject(parent, node):
    _map[node.nodeType](parent, node)

def simplify_single_entries(object):
    for name in object.getElementNames():
        l = getattr(object.elements, name)
        # set the first subelement (in case it's just one, this is easy)
        setattr(object.first, name, l[0])
        # now do the same for rest
        for element in l:
            simplify_single_entries(element)
  
def XMLToObjectsFromFile(path):
    return XMLToObjects(parse(path))

def XMLToObjectsFromString(s):
    return XMLToObjects(parseString(s))

def XMLToObjects(document):
    object = XMLObject()
    documentToObject(object, document)
    document.unlink()
    simplify_single_entries(object)
    return object
