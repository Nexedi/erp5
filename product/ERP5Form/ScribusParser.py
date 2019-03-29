# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                     Mayoro DIAGNE <mayoro@nexedi.com>
#                     Guy Oswald OBAMA <guy@nexedi.com>
#                     thomas <thomas@nexedi.com>
#                     Mame C.Sall <mame@nexedi.com>
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
from AccessControl import ClassSecurityInfo
from lxml import etree
from zLOG import LOG,INFO
class ScribusParser:
  """
    Scribus parser API provide methods wich allow to parse a scribus file.
  """
  security = ClassSecurityInfo()

  def __init__(self, scribus_file_descriptor):
    """
    initialise self.data with scribus_file_descriptor if string's
    The __init__ function can take either a filename, an open file object
    or the content of the file
    """
    if scribus_file_descriptor is None:
      raise ValueError("No Scribus file provided, please choose a Scibus Form")

    if type(scribus_file_descriptor) == 'str':
      data = scribus_file_descriptor
    elif hasattr(scribus_file_descriptor, "read"):
      data = scribus_file_descriptor.read()
      scribus_file_descriptor.close()
    else:
      source = open(scribus_file_descriptor, "rb")
      data = source.read()
      source.close()

    self.parsed_data = etree.XML(data)

  def getData(self):
    """
    Return the content file in XML structured
    """
    return self.data

  def getEtreeXMLObject(self):
    """
    Return the content file in XML structured
    """
    return self.parsed_data


  def getXMLObjectByTagName(self, tag_name):
    """
    return a list containing all objects with tag name tag_name
    """
    root = self.getEtreeXMLObject()
    tag_list = []
    for node in root.iterdescendants():
      if node.tag == tag_name:
        tag_list.append(node)
    return tag_list

  security.declarePublic('getScribusFileVersion')
  def getScribusFileVersion(self):
    """
    Return the scribus version of the file with content content_file
    """
    root = self.getEtreeXMLObject()
    if 'Version' in root.keys():
      return root.attrib['Version']
    else:
      return None

  security.declarePublic('getPageCount')
  def getPageCount(self):
    """
    Return the page count of the scribus file
    """
    page_count = 0
    # a scribus document has just one tag DOCUMENT
    document_list = self.getXMLObjectByTagName('DOCUMENT')
    if len(document_list) != 0:
      document = document_list[0]
      if 'ANZPAGES' in document.attrib.keys():
        page_count = document.attrib['ANZPAGES']
    return int(page_count)

  security.declarePublic('getPageGap')
  def getPageGap(self):
    version = self.getScribusFileVersion()
    document_list = self.getXMLObjectByTagName('DOCUMENT')
    page_list = self.getXMLObjectByTagName('PAGE')
    page_gap = 0
    if version is not None and len(page_list) != 0:
      page0 = page_list[0]
      if 'BORDERTOP' in page0.attrib.keys():
        page_gap = page0.attrib['BORDERTOP']
      else:
        if len(document_list) != 0:
          document = document_list[0]
          if 'BORDERTOP' in document.attrib.keys():
            page_gap = document.attrib['BORDERTOP']
    return int(page_gap)

  security.declarePublic('getPageWidth')
  def getPageWidth(self):
    """
    Return the page width of the scribus file in pixel (px)
    """
    page_width = 0
    # a scribus document has just one tag DOCUMENT
    document_list = self.getXMLObjectByTagName('DOCUMENT')
    if len(document_list) != 0:
      document = document_list[0]
      if 'PAGEWIDTH' in document.attrib.keys():
        page_width = document.attrib['PAGEWIDTH']
    return float(page_width)

  security.declarePublic('getPageHeight')
  def getPageHeight(self):
    """
    Return the page height of the scribus file in pixel (px)
    """
    page_height = 0
    # a scribus document has just one tag DOCUMENT
    document_list = self.getXMLObjectByTagName('DOCUMENT')
    if len(document_list) != 0:
      document = document_list[0]
      if 'PAGEHEIGHT' in document.attrib.keys():
        page_height = document.attrib['PAGEHEIGHT']
    return float(page_height)


  security.declarePublic('getDocumentAttributeByName')
  def getDocumentAttributeByName(self, attribute_name):
    """
    Generic function for page's attributes. Return the page attribute value
    corresponding of attribute_name of the scribus file document
    """
    page_attribute = 0
    document_list = self.getXMLObjectByTagName('DOCUMENT')
    if len(document_list) != 0:
      document = document_list[0]
      if attribute_name in document.attrib.keys():
        page_attribute = document.attrib[attribute_name]
    return page_attribute

  def getAttributeValueXMLObject(self, xml_object, attribute):
    """
    return the value of the attribute attribute for xml_object
    for exemple obj refer to <PAGEOBJECT PTYPE="4" ...
    getAttributeValueXMLObject(obj, 'PTYPE') retur "4"
    """
    value = None
    if attribute in xml_object.keys():
      value = xml_object.attrib[attribute]
    return value

  security.declarePublic('getFieldIdList')
  def getFieldIdList(self):
    """
    Return a list of field ids of the scribus document
    """
    page_object_list = self.getXMLObjectByTagName('PAGEOBJECT')
    filed_id_list = []
    for element in page_object_list:
      field_name = self.getAttributeValueXMLObject(element, 'ANNAME')
      if field_name is not None:
        field_name = field_name.replace(' ','_')
        if field_name != '' and element.attrib['PTYPE']=="4":
          filed_id_list.append(field_name)
    return filed_id_list

  security.declarePublic('getFieldItemList')
  def getFieldItemList(self):
    """
    Return a list of fields of the scribus document with attributes
    """
    page_object_list = self.getXMLObjectByTagName('PAGEOBJECT')
    filed_item_list = []
    for element in page_object_list:
      field_name = self.getAttributeValueXMLObject(element, 'ANNAME')
      if field_name is not None:
        field_name = field_name.replace(' ','_')
        if field_name != '' and element.attrib['PTYPE']=="4":
          filed_item_list.append((field_name,element.attrib))
    return filed_item_list

  security.declarePublic('getFieldIdListFor')
  def getFieldIdListFor(self, page=0):
    """
    Return a list of field ids at page: page
    """
    page_object_list = self.getXMLObjectByTagName('PAGEOBJECT')
    filed_id_list = []
    for element in page_object_list:
      field_name = self.getAttributeValueXMLObject(element, 'ANNAME')
      if field_name is not None:
        field_name = field_name.replace(' ','_')
      field_page = self.getAttributeValueXMLObject(element, 'OwnPage')
      if field_page is not None:
        field_page = int(field_page)
      if field_name is not None and field_page is not None:
        if field_name != '' and field_page==page and element.attrib['PTYPE']=="4":
          filed_id_list.append(field_name)
    return filed_id_list

  security.declarePublic('getFieldItemListFor')
  def getFieldItemListFor(self, page=0):
    """
    Return a list of fields at page:page with attributes
    """
    page_object_list = self.getXMLObjectByTagName('PAGEOBJECT')
    filed_item_list = []
    for element in page_object_list:
      field_name = self.getAttributeValueXMLObject(element, 'ANNAME')
      if field_name is not None:
        field_name = field_name.replace(' ','_')
      field_page = self.getAttributeValueXMLObject(element, 'OwnPage')
      if field_page is not None:
        field_page = int(field_page)
      if field_name is not None and field_page is not None:
        if field_name != '' and field_page==page and element.attrib['PTYPE']=="4":
          filed_item_list.append((field_name, element.attrib))
    return filed_item_list

  security.declarePublic('getPropertyFieldDictFor')
  def getPropertyFieldDictFor(self, field_name):
    """
    Return a dictionnary containing properties of a given field
    """
    property_dict = {}
    for field in self.getFieldItemList():
      if field[0] == field_name:
        property_dict = field[1]
    return property_dict

  security.declarePublic('getERP5PropertyDict')
  def getERP5PropertyDict(self):
    """
    Return a dict containing properties of fields by page
    like: {0:[(field_name, {properti1:value1,...}),...]}
    After transforming scribus attributes into usable ERP5 one
    """
    #scratch_left: Space in pixel at the left of the scratch space
    document_scratch_left = self.getDocumentAttributeByName('ScratchLeft')
    #scratch_top: Space at the top of the scratch space, before the pages
    document_scratch_top = self.getDocumentAttributeByName('ScratchTop')
    erp5_property_dict = {}
    for page in range(self.getPageCount()):
      erp5_property_list = []
      for property_id, scribus_property_dict in self.getFieldItemListFor(page):
        usable_property = {}
        usable_property['position_x'] = \
                int(float(scribus_property_dict['XPOS']) - float(document_scratch_left))
        usable_property['position_y'] = \
                int(float(scribus_property_dict['YPOS']) - float(document_scratch_top))
        usable_property['size_x'] = int(float(scribus_property_dict['WIDTH']))
        usable_property['size_y'] = int(float(scribus_property_dict['HEIGHT']))
        user_property = self.getERP5AttributesFieldDict(property_id)
        usable_property['title'] = ''
        if user_property.has_key('title'):
          usable_property['title'] = user_property['title']
        temp_order = 'left'
        if user_property.has_key('order'):
          temp_order = user_property['order']
        # generating erp5 attribute order position for erp5 form
        if temp_order not in  ['left','right']:
          # temp_order is invalid
          # trying to get it from its position in original Scribus file
          if user_property['position_x'] > 280 :
            temp_order = 'right'
        usable_property['order'] = temp_order
        # defining global variables for ANFLAG tag values
        # these values can be found at http://docs.scribus.net
        # for File Format Specification for Scribus
        def_noScroll = 8388608
        def_noSpellCheck = 4194304
        def_editable = 262144
        def_password = 8192
        def_multiLine = 4096
        def_noExport = 4
        def_required = 2
        def_readOnly = 1
        # initialising properties for default values
        usable_property['noScroll'] = 0
        usable_property['noSpellCheck'] = 0
        usable_property['editable'] = 0
        usable_property['password'] = 0
        usable_property['multiline'] = 0
        usable_property['noExport'] = 0
        usable_property['required'] = 0
        usable_property['editable'] = 1
        # updating properties with real values after tests
        temp_ANFLAG = long(scribus_property_dict['ANFLAG'])
        if temp_ANFLAG - def_noScroll >= 0:
          # substracting value
          temp_ANFLAG = temp_ANFLAG - def_noScroll
          # 'do not scroll' field
          # adding property
          usable_property['noscroll'] = 1
        if temp_ANFLAG - def_noSpellCheck >= 0:
          temp_ANFLAG = temp_ANFLAG - def_noSpellCheck
          # 'do not spell check' field
          usable_property['noSpellCheck'] = 1
        if temp_ANFLAG - def_editable >= 0:
          temp_ANFLAG = temp_ANFLAG - def_editable
          # 'editable' field
          usable_property['editable'] = 1
        if temp_ANFLAG - def_password >= 0:
          temp_ANFLAG = temp_ANFLAG - def_password
          # 'password' field
          usable_property['password'] = 1
        if temp_ANFLAG - def_multiLine >= 0:
          temp_ANFLAG = temp_ANFLAG - def_multiLine
          # 'multiline' field
          usable_property['multiline'] = 1
        if temp_ANFLAG - def_noExport >= 0:
          temp_ANFLAG = temp_ANFLAG - def_noExport
          # 'do not export data' field
          usable_property['noExport'] = 1
        if temp_ANFLAG - def_required >= 0:
          temp_ANFLAG = temp_ANFLAG - def_required
          # 'required field
          usable_property['required'] = 1
        if temp_ANFLAG == def_readOnly:
          # 'read only" field
          usable_property['editable'] = 0
        if user_property.has_key('maximum_input'):
          usable_property['maximum_input'] = user_property['maximum_input']
        else:
          usable_property['maximum_input'] = scribus_property_dict['ANMC']
        # getting object type :
        # first checking for user-specified type in 'tooltip' properties
        if user_property.has_key('type'):
          # 'type' id in tooltip : using it and ignoring scribus 'type'
          usable_property['type'] = user_property['type']
        elif scribus_property_dict.has_key('ANTYPE'):
          # from scribus type (selected in the scribus PDF-form properties)
          object_type = scribus_property_dict['ANTYPE']
          if object_type == '2':
            #type 2 = PDF-Button : InputButtonField
            usable_property['type'] = 'InputButtonField'
          elif object_type == '3':
            #type 3 = PDF-Text : Stringfield by default
            usable_property['type'] = 'StringField'
            if usable_property['multiline'] == 1:
              # Stringfield is multiline, converting to TextAreaField
              usable_property['type'] = 'TextAreaField'
            elif scribus_property_dict.has_key('ANFORMAT'):
              object_format = scribus_property_dict['ANFORMAT']
              # checking kind of Stringfield
              if object_format == '1':
                #type is number
                usable_property['type'] = 'IntegerField'
              elif object_format == '2':
                #type is percentage
                usable_property['type'] = 'FloatField'
              elif object_format == '3':
                #type is date
                usable_property['type'] = 'DateTimeField'
              elif object_format == '4':
                #type is time
                usable_property['type'] = 'DateTimeField'
          elif object_type == '4':
            # type 4 = PDF-Checkbox
            usable_property['type'] = 'CheckBoxField'
          elif object_type == '5':
            # type 5 = PDF-Combobox
            usable_property['type'] = 'ListField'
          elif object_type == '6':
            # type 6 = PDF-ListBox
            usable_property['type'] = 'MultiListField'
        else:
          # object type not found in user-properties neither in
          # document-properties. Use by default StringField
          usable_property['type'] = 'StringField'
        # getting data_type relative to object type
        # (used in property_sheet to save field values).
        usable_property['data_type'] = 'string'
        usable_property['default_data'] = ''
        if usable_property['type'] == 'MultiListField':
          usable_property['data_type'] = 'tokens'
        if usable_property['type'] == 'IntegerField':
          usable_property['data_type'] = 'int'
          usable_property['default_data'] = 0
        if usable_property['type'] == 'FloatField':
          usable_property['data_type'] = 'float'
          usable_property['default_data'] = 0.0
        if usable_property['type'] == 'CheckBoxField':
          usable_property['data_type'] = 'boolean'
          usable_property['default_data'] = 0
        if usable_property['type'] == 'DateTimeField':
          usable_property['data_type'] = 'date'
          usable_property['default_data'] = '1900/01/01'
        # checking for user data if required and editable properties are defined
        #  in ANTOOLTIP otherwise keep scribus one
        if user_property.has_key('required'):
          usable_property['required'] = user_property['required']
        if user_property.has_key('editable'):
          usable_property['editable'] = user_property['editable']
        # getting type properties for special types
        usable_property['rendering'] = 'single'
        # Stringfields handle properties
        # checkbox objects belongs to a group of checkbox
        if usable_property['type'] == 'CheckBoxField' :
          # checking if THIS checkbox is in a group
          usable_property['group'] = '0'
          if user_property.has_key('group'):
            usable_property['group'] = user_property['group']
        # object is DateTimeField
        if usable_property['type'] == 'DateTimeField':
          # has been tested successfully
          usable_property['rendering'] = 'multiple'
          # checking if field has input_order property
          usable_property['input_order'] = 'ymd'
          if user_property.has_key('input_order'):
            usable_property['input_order'] = user_property['input_order']
          usable_property['date_only'] = '1'
          if user_property.has_key('date_only'):
            usable_property['date_only'] = user_property['date_only']
          # checking if special date separator is specified
          # most of PDF forms already have '/' character to differenciate
          # date fields, in this case no separator is needed and the script
          # will automatically insert ' ' between element.
          # > this value is not used in ScribusUtils.py , but in PDFForm.py
          # when creating the fdf file to fill the PDF form.
          if usable_property['editable'] == 1:
            usable_property['date_separator'] = ''
            usable_property['time_separator'] = ''
          else:
            usable_property['date_separator'] = '/'
            if user_property.has_key('date_separator'):
              usable_property['date_separator'] = user_property['date_separator']
            usable_property['time_separator'] = ':'
            if user_property.has_key('time_separator'):
              usable_property['time_separator'] = user_property['time_separator']
        # getting creation order from 'tooltip' properties
        # used to create ERP5 objects in a special order
        if user_property.has_key('nb') and str(user_property['nb']).isdigit():
          # object has a nb properties containing its creation position
          usable_property['nb'] = user_property['nb']
        erp5_property_list.append((property_id, usable_property))
      erp5_property_dict[page] = erp5_property_list
    return erp5_property_dict

  security.declarePublic('getERP5AttributesFieldDict')
  def getERP5AttributesFieldDict(self, field_name):
    """
    Return a dictionnary containing ERP5 attributes of a given field
    like: nb(creation order), type, title
    """
    erp5_attribute_dict = {}
    for field in self.getFieldItemList():
      if field[0] == field_name:
        for attributes in field[1]["ANTOOLTIP"].split("#"):
          if attributes != "":
            key,value = attributes.split(":")
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if key == "nb":
              value = int(value)
            erp5_attribute_dict[key]=value
    return erp5_attribute_dict
