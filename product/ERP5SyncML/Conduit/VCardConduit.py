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

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName
from Products.ERP5SyncML.SyncCode import SyncCode
from Products.ERP5SyncML.Subscription import Subscription
from Acquisition import aq_base, aq_inner, aq_chain, aq_acquire
from ZODB.POSException import ConflictError

from zLOG import LOG

class VCardConduit(ERP5Conduit, SyncCode):
  """
  A conduit is in charge to read data from a particular structure,
  and then to save this data in another structure.

  VCardConduit is a peace of code to update VCards from text stream
  """


  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, '__init__')
  def __init__(self):
    self.args = {}


  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, xml=None, object=None, previous_xml=None,
      object_id=None, sub_object=None, force=0, simulate=0, **kw):
    """
    add a new person corresponding to the vcard
    if the person already exist, she's updated
    """
    #LOG('VCardConduit',0,'addNode, object=%s, object_id=%s, sub_object:%s, \
        #xml:\n%s' % (str(object), str(object_id), str(sub_object), xml))
    if not isinstance(xml, str):
      xml = self.nodeToString(xml)
    portal_type = 'Person' #the VCard can just use Person
    if sub_object is None:

      new_object, reset_local_roles, reset_workflow = ERP5Conduit.constructContent(self, object, object_id,
      portal_type)
    else: #if the object exist, it juste must be update
      new_object = sub_object
    #LOG('addNode', 0, 'new_object:%s, sub_object:%s' % (new_object, sub_object)) 
    self.updateNode(xml=xml,
                    object=new_object,
                    force=force,
                    simulate=simulate,
                    **kw)
    #in a first time, conflict are not used
    return {'conflict_list':None, 'object': new_object}

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteNode')
  def deleteNode(self, xml=None, object=None, object_id=None, force=None,
      simulate=0, **kw):
    """
    A node is deleted
    """
    #LOG('deleteNode :', 0, 'object:%s, object_id:%s' % (str(object), str(object_id)))
    conflict_list = []
    try:
      object._delObject(object_id)
    except (AttributeError, KeyError):
      LOG('VCardConduit',0,'deleteNode, Unable to delete: %s' % str(object_id))
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'updateNode')
  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, 
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
    return self.MEDIA_TYPE.values()

  def getCapabilitiesVerCTList(self, capabilities_ct_type):
    """
    return a list of version of the CTType supported
    """
    #add here the other version supported
    verCTTypeList = {}
    verCTTypeList[self.MEDIA_TYPE['TEXT_VCARD']]=('3.0',)
    verCTTypeList[self.MEDIA_TYPE['TEXT_XVCARD']]=('2.1',)
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
    prefered_type = self.MEDIA_TYPE['TEXT_XVCARD']
    return prefered_type
  
  def changePropertyEncoding(self, property_parameters_list, 
      property_value_list):
    """
    if there is a property 'ENCODING', change the string encoding to utf-8
    """
    encoding=''

    for item in property_parameters_list :
      if item.has_key('ENCODING'):
        encoding = item['ENCODING']

    property_value_list_well_incoded=[]
    if encoding == 'QUOTED-PRINTABLE':
      import mimify
      for property_value in property_value_list:
        property_value = mimify.mime_decode(property_value)
        property_value_list_well_incoded.append(property_value)
    #elif ... put here the other encodings
    else:
      property_value_list_well_incoded=property_value_list

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
    vcard_list = vcard.split('\n')
    for vcard_line in vcard_list:
      if ':' in vcard_line:
        property, property_value = vcard_line.split(':')
        property_value_list=property_value.split(';')
        property_parameters_list = []
        property_name = ''
        if ';' in property:
          property_list = property.split(';')
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
          property_name=property
        if type(property_name) is type(u'a'):
          property_name = property_name.encode('utf-8')

        tmp=[]
        for property_value in property_value_list:
          if type(property_value) is type(u'a'):
            property_value = property_value.encode('utf-8')
          tmp.append(property_value)
        property_value_list=tmp
        if property_name in convert_dict.keys():
          if property_name == 'N' and len(property_value_list) > 1:
            edit_dict[convert_dict['N']]=property_value_list[0]
            edit_dict[convert_dict['FN']]=property_value_list[1]
          else:
            edit_dict[convert_dict[property_name]]=property_value_list[0]
    #LOG('edit_dict =',0,edit_dict)
    return edit_dict

