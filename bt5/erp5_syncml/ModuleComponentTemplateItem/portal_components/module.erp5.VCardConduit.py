# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from erp5.component.module.ERP5Conduit import ERP5Conduit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
import difflib
import six

from zLOG import LOG

class VCardConduit(ERP5Conduit):
  """
  A conduit is in charge to read data from a particular structure,
  and then to save this data in another structure.

  VCardConduit is a piece of code to update VCards from text stream
  """


  # Declarative security
  security = ClassSecurityInfo()


  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, xml=None, object=None, previous_xml=None, # pylint: disable=redefined-builtin
      object_id=None, sub_object=None, force=0, simulate=0, **kw):
    """
    add a new person corresponding to the vcard
    if the person already exist, she's updated
    """
    #LOG('VCardConduit',0,'addNode, object=%s, object_id=%s, sub_object:%s, \
        #xml:\n%s' % (str(object), str(object_id), str(sub_object), xml))
    if not isinstance(xml, bytes):
      xml = self.nodeToString(xml)
    portal_type = 'Person' #the VCard can just use Person
    if sub_object is None:

      new_object, _, _ = ERP5Conduit.constructContent(self, object, object_id, portal_type)
    else: #if the object exist, it juste must be update
      new_object = sub_object
    #LOG('addNode', 0, 'new_object:%s, sub_object:%s' % (new_object, sub_object))
    self.updateNode(xml=xml,
                    object=new_object,
                    force=force,
                    simulate=simulate,
                    **kw)
    #in a first time, conflict are not used
    return {'conflict_list':[], 'object': new_object}

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteNode')
  def deleteNode(self, xml=None, object=None, object_id=None, force=None, # pylint: disable=redefined-builtin
      simulate=0, **kw):
    """
    A node is deleted
    """
    #LOG('deleteNode :', 0, 'object:%s, object_id:%s' % (str(object), str(object_id)))
    try:
      object._delObject(object_id)
    except (AttributeError, KeyError):
      LOG('VCardConduit',0,'deleteNode, Unable to delete: %s' % str(object_id))
    return []

  security.declareProtected(Permissions.ModifyPortalContent, 'updateNode')
  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    """
    A node is updated
    """
    #LOG('updateNode :',0, 'xml:%s, object:%s, previous_xml:%s, force:%s,simulate:%s, kw:%s' % (xml, object, previous_xml, force, simulate, kw))
    vcard_dict = self.vcard2Dict(xml)
    object.edit(**vcard_dict)
    return []

  def getCapabilitiesCTTypeList(self):
    """
    return the a list of CTType capabilities supported
    """
    return ('text/xml', 'text/vcard', 'text/x-vcard',)

  def getCapabilitiesVerCTList(self, capabilities_ct_type):
    """
    return a list of version of the CTType supported
    """
    #add here the other version supported
    verCTTypeList = {}
    verCTTypeList['text/vcard'] = ('3.0',)
    verCTTypeList['text/x-vcard'] = ('2.1',)
    return verCTTypeList[capabilities_ct_type]

  def getPreferedCapabilitieVerCT(self):
    """
    return the prefered capabilitie VerCT
    """
    prefered_version = '2.1'
    return prefered_version

  def getPreferedCapabilitieCTType(self):
    """
    return the prefered capabilitie VerCT
    """
    prefered_type = 'text/x-vcard'
    return prefered_type

  def changePropertyEncoding(self, property_parameters_list,
      property_value_list):
    """
    if there is a property 'ENCODING', change the string encoding to utf-8
    """
    encoding=''

#    for item in property_parameters_list :
#      if ENCODING in item:
#        encoding = item['ENCODING']

    property_value_list_well_incoded=[]
    if encoding == 'QUOTED-PRINTABLE':
      import mimify  # pylint:disable=import-error
      for property_value in property_value_list:
        property_value = mimify.mime_decode(property_value)
        property_value_list_well_incoded.append(property_value)
    #elif ... put here the other encodings
    else:
      property_value_list_well_incoded = property_value_list

    return property_value_list_well_incoded

  def vcard2Dict(self, vcard):
    """
    transalate the vcard to a dict understandable by erp5 like
    {'fisrt_name':'MORIN', 'last_name':'Fabien'}
    """
    #LOG('vcard =',0,vcard)
    convert_dict = {}
    convert_dict['FN'] = 'first_name'
    convert_dict['N'] = 'last_name'
    convert_dict['TEL'] = 'default_telephone_text'
    edit_dict = {}
    if isinstance(vcard, bytes):
      vcard = vcard.decode('utf-8')
    vcard_list = vcard.splitlines()
    for vcard_line in vcard_list:
      if ':' in vcard_line:
        property_, property_value = vcard_line.split(':')
        property_value_list = property_value.split(';')
        property_parameters_list = []
        property_name = ''
        if ';' in property_:
          property_list = property_.split(';')
          property_name = property_list[0] #the property name is the 1st element
          if len(property_list) > 1 and property_list[1] != '':
            property_parameters_list = property_list[1:len(property_list)]
            tmp = []
            for property_parameter in property_parameters_list:
              if '=' in property_parameter:
                property_parameter_name, property_parameter_value = \
                    property_parameter.split('=')
              else:
                property_parameter_name = property_parameter
                property_parameter_value = None
              tmp.append({property_parameter_name:property_parameter_value})
            property_parameters_list = tmp
            #now property_parameters_list looks like :
            # [{'ENCODING':'QUOTED-PRINTABLE'}, {'CHARSET':'UTF-8'}]

            property_value_list = \
                self.changePropertyEncoding(property_parameters_list,
                                            property_value_list)

        else:
          property_name=property_
        if six.PY2 and isinstance(property_name, six.text_type):
          property_name = property_name.encode('utf-8')

        tmp = []
        for property_value in property_value_list:
          if six.PY2 and isinstance(property_value, six.text_type):
            property_value = property_value.encode('utf-8')
          tmp.append(property_value)
        property_value_list = tmp
        if property_name in convert_dict.keys():
          if property_name == 'N' and len(property_value_list) > 1:
            edit_dict[convert_dict['N']] = property_value_list[0]
            edit_dict[convert_dict['FN']] = property_value_list[1]
          else:
            edit_dict[convert_dict[property_name]] = property_value_list[0]
    #LOG('edit_dict =',0,edit_dict)
    return edit_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                            'replaceIdFromXML')
  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    """
      Return the Same vlue
    """
    return xml

  def getContentType(self):
    """Content-Type of binded data
    """
    return 'text/vcard'

  def generateDiff(self, new_data, former_data):
    """return unified diff for plain-text documents
    """
    if isinstance(new_data, bytes):
      new_data = new_data.decode('utf-8')
    if isinstance(former_data, bytes):
      former_data = former_data.decode('utf-8')
    diff = '\n'.join(difflib.unified_diff(new_data.splitlines(),
                                          former_data.splitlines()))
    return diff


  def applyDiff(self, original_data, diff):
    """Use difflib to patch original_data
    """
    raise NotImplementedError('patch unified diff')
