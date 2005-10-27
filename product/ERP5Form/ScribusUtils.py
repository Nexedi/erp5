##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Guy Oswald OBAMA <guy@nexedi.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.PythonScripts.Utility import allow_class
from ZPublisher.HTTPRequest import FileUpload
from xml.dom.ext.reader import PyExpat
from xml.dom import Node, minidom
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, get_request
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO
from zLOG import LOG
import imghdr
import random
import getopt, sys, os, string
from urllib import quote



class ScribusParser:
  """
  Parses a Scribus file
  """
  
  # Declarative security
  security = ClassSecurityInfo()
  
    
  security.declarePublic('getXmlObjectsProperties')
  def getXmlObjectsProperties(self, xml_string):
    # Create the PyExpat reader
    reader = PyExpat.Reader()
  
    # Create DOM tree from the xml string
    dom_tree = reader.fromString(xml_string)
  
    text_field_list = {}
    
    dom_root = dom_tree.documentElement
    page_object_list = dom_root.getElementsByTagName("PAGEOBJECT")
  
    # Take Xml objects properties
    for page_object in page_object_list:
      text_field_properties = {}
      field_name = None
      for attribute in page_object.attributes:
        node_name  = str(attribute.nodeName)
        node_value = str(attribute.nodeValue)
        if node_name == 'ANNAME':
          if node_value != '':
            field_name = node_value
        else:
            text_field_properties[node_name] = node_value
      if field_name != None:
        text_field_list[field_name] = text_field_properties
  
    return text_field_list   

   
  security.declarePublic('getPropertiesConversion')
  def getPropertiesConversion(self, text_field_list):
  # Get Scribus field properties
  
    field_scribus_properties_dict = {}
  
    for field_name in text_field_list.keys():
      text_field_properties = text_field_list[field_name]
      field_scribus_properties_dict[field_name] = text_field_properties['ANTOOLTIP']
  
    widget_properties_list = []
    index = 1    
  
    while index < len(field_scribus_properties_dict):
      for key, item in field_scribus_properties_dict.items():
        if string.atoi(item[:3]) == index:
          property_field_list = item[4:].split('#')
          widget_properties_buffer = {}
          for property_field in property_field_list:
            property_field_split = property_field.split(':')
            if property_field_split[0] == 'items':
              property_field_split[1] = property_field_split[1].split('|')
            widget_properties_buffer[property_field_split[0]] = property_field_split[1]
          widget_properties_list.append((key, widget_properties_buffer))
          break
      index = index + 1
  
    for key, item in field_scribus_properties_dict.items():
      if string.atoi(item[:3]) == 999:
        property_field_list = item[4:].split('#')
        widget_properties_buffer = {}
        for property_field in property_field_list:
          property_field_split = property_field.split(':')
          widget_properties_buffer[property_field_split[0]] = property_field_split[1]
        widget_properties_list.append((key, widget_properties_buffer))
  
    return widget_properties_list

        
  security.declareProtected('Import/Export objects', 'getContentFile')
  def getContentFile(self, file_descriptor):
    """ Get file content """
    return file_descriptor.read()
  
      
InitializeClass(ScribusParser)
allow_class(ScribusParser)  


  