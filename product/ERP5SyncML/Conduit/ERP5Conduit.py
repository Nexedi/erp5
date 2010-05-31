# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5SyncML.XMLSyncUtils import XMLSyncUtilsMixin
from Products.ERP5SyncML.Conflict import Conflict
from Products.ERP5Type.Utils import deprecated
from Products.ERP5Type.XMLExportImport import MARSHALLER_NAMESPACE_URI
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime
from email.MIMEBase import MIMEBase
from email import Encoders
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5Type.Globals import PersistentMapping
import pickle
from xml.sax.saxutils import unescape
import re
from lxml import etree
from lxml.etree import Element
parser = etree.XMLParser(remove_blank_text=True)
from xml_marshaller.xml_marshaller import load_tree as unmarshaller
from xupdate_processor import xuproc
from zLOG import LOG, INFO, DEBUG
from base64 import standard_b64decode
from zope.interface import implements
from copy import deepcopy

class ERP5Conduit(XMLSyncUtilsMixin):
  """
    A conduit is a piece of code in charge of

    - updating an object attributes from an XUpdate XML stream

    (Conduits are not in charge of creating new objects which
    are eventually missing in a synchronisation process)

    If an object has be created during a synchronisation process,
    the way to proceed consists in:

    1- creating an empty instance of the appropriate class
      in the appropriate directory

    2- updating that empty instance with the conduit

    The first implementation of ERP5 synchronisation
    will define a default location to create new objects and
    a default class. This will be defined at the level of the synchronisation
    tool

    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
    Look carefully when we are adding elements,
    for example, when we do 'insert-after', with 2 xupdate:element,
    so adding 2 differents objects, actually it adds only XXXX one XXX object
    In this case the getSubObjectDepth(), doesn't have
    too much sence
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    There is also one problem, when we synchronize a conflict, we are not waiting
    the response of the client, so that we are not sure if it take into account,
    we may have CONFLICT_NOT_SYNCHRONIZED AND CONFLICT_SYNCHRONIZED
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  """

  # Declarative interfaces
  implements( interfaces.IConduit, )

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,'getEncoding')
  def getEncoding(self):
    """
    return the string corresponding to the local encoding
    """
    #return "iso-8859-1"
    return "utf-8"

  security.declareProtected(Permissions.ModifyPortalContent, '__init__')
  def __init__(self):
    self.args = {}

  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, xml=None, object=None, sub_object=None, reset=None,
                                       simulate=None, **kw):
    """
    A node is added

    xml : the xml wich contains what we want to add

    object : from where we want to add something

    previous_xml : the previous xml of the object, if any

    force : apply updates even if there's a conflict

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,subscriber_value]
    """
    reset_local_roles = False
    reset_workflow = False
    conflict_list = []
    xml = self.convertToXml(xml)
    #LOG('ERP5Conduit.addNode', INFO, 'object path:%s' % object.getPath())
    #LOG('ERP5Conduit.addNode', INFO, '\n%s' % etree.tostring(xml, pretty_print=True))
    if xml is None:
      return {'conflict_list': conflict_list, 'object': sub_object}
    # In the case where this new node is a object to add
    xpath_expression = xml.get('select')
    if xml.xpath('local-name()') == self.history_tag and not reset:
      conflict_list += self.addWorkflowNode(object, xml, simulate)
    elif xml.xpath('name()') in self.XUPDATE_INSERT_OR_ADD and\
                            MARSHALLER_NAMESPACE_URI not in xml.nsmap.values():
      # change the context according select expression
      context = self.getContextFromXpath(object, xpath_expression)
      for element in xml.findall('{%s}element' % xml.nsmap['xupdate']):
        xml = self.getElementFromXupdate(element)
        conflict_list += self.addNode(xml=xml, object=context, **kw)\
                                                              ['conflict_list']
    elif xml.xpath('local-name()') == self.xml_object_tag:
      sub_object = self._createContent(xml=xml,
                                      object=object,
                                      sub_object=sub_object,
                                      reset_local_roles=reset_local_roles,
                                      reset_workflow=reset_workflow,
                                      reset=reset,
                                      simulate=simulate,
                                      **kw)
    elif xml.xpath('local-name()') in self.local_role_list:
      self.addLocalRoleNode(object, xml)
    elif xml.xpath('local-name()') in self.local_permission_list:
      conflict_list += self.addLocalPermissionNode(object, xml)
    else:
      conflict_list += self.updateNode(xml=xml, object=object, reset=reset,
                                                       simulate=simulate, **kw)
    # We must returns the object created
    return {'conflict_list':conflict_list, 'object': sub_object}

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteNode')
  def deleteNode(self, xml=None, object=None, object_id=None, **kw):
    """
    A node is deleted
    """
    #LOG('ERP5Conduit.deleteNode', INFO, 'object path:%s' % object.getPath())
    #LOG('ERP5Conduit deleteNode', INFO, 'object_id:%r' % object_id)
    if object_id is not None:
      self._deleteContent(object=object, object_id=object_id)
      return []
    xml = self.convertToXml(xml)
    #LOG('ERP5Conduit deleteNode', INFO, etree.tostring(xml, pretty_print=True))
    xpath_expression = xml.get('select')
    context_to_delete = self.getContextFromXpath(object, xpath_expression)
    if context_to_delete != object:
      self._deleteContent(object=context_to_delete.getParentValue(),
                                           object_id=context_to_delete.getId())
    else:
      #same context
      if [role for role in self.local_role_list if role in xpath_expression]:
        user = self.extract_id_from_xpath.findall(xpath_expression)[-1][3]
        #LOG('ERP5Conduit.deleteNode local_role: ', INFO, 'user: %r' % user)
        if self.local_role_tag in xpath_expression:
          object.manage_delLocalRoles([user])
        elif self.local_group_tag in xpath_expression:
          object.manage_delLocalGroupRoles([user])
      if [permission for permission in self.local_permission_list if\
                                               permission in xpath_expression]:
        permission = self.extract_id_from_xpath.findall(xpath_expression)[-1][3]
        #LOG('ERP5Conduit.deleteNode permission: ', INFO,
                                                 #'permission: %r' % permission)
        object.manage_setLocalPermissions(permission)
    return []

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteObject')
  def deleteObject(self, object, object_id):
    try:
      object._delObject(object_id)
    except (AttributeError, KeyError):
      #LOG('ERP5Conduit.deleteObject', DEBUG, 'Unable to delete: %s' % str(object_id))
      pass

  security.declareProtected(Permissions.ModifyPortalContent, 'updateNode')
  def updateNode(self, xml=None, object=None, previous_xml=None, force=False,
                 simulate=False, reset=False, xpath_expression=None, **kw):
    """
    A node is updated with some xupdate
      - xml : the xml corresponding to the update, it should be xupdate
      - object : the object on wich we want to apply the xupdate
      - [previous_xml] : the previous xml of the object, it is mandatory
                         when we have sub objects
    """
    conflict_list = []
    if xml is None:
      return {'conflict_list':conflict_list, 'object':object}
    xml = self.convertToXml(xml)
    #LOG('ERP5Conduit.updateNode, force: ', INFO, force)
    #LOG('ERP5Conduit updateNode', INFO, object.getPath())
    #LOG('ERP5Conduit updateNode', INFO, '\n%s' % etree.tostring(xml, pretty_print=True))
    if xml.tag == '{%s}modifications' % xml.nsmap.get('xupdate'):
      conflict_list += self.applyXupdate(object=object,
                                         xupdate=xml,
                                         previous_xml=previous_xml,
                                         force=force,
                                         simulate=simulate,
                                         reset=reset,
                                         **kw)
    # we may have only the part of an xupdate
    else:
      args = {}
      if self.isProperty(xml):
        keyword = None
        value = xml.get('select')
        if value is not None:
          select_list = value.split('/') # Something like:
                                         #('','object[1]','sid[1]')
          new_select_list = []
          for select_item in select_list:
            if select_item.find('[') >= 0:
              select_item = select_item[:select_item.find('[')]
            new_select_list.append(select_item)
          select_list = new_select_list # Something like : ('','object','sid')
          keyword = select_list[-1] # this will be 'sid'
        data = None
        if xml.xpath('name()') not in self.XUPDATE_INSERT_OR_ADD:
          for subnode in xml:
            if subnode.xpath('name()') in self.XUPDATE_ELEMENT:
              keyword = subnode.get('name')
              data_xml = subnode
        else:
          #XXX find something better than hardcoded prefix
          # We can call add node
          conflict_list += self.addNode(xml=xml,
                                        object=object,
                                        force=force,
                                        simulate=simulate,
                                        reset=reset,
                                        **kw)
          return conflict_list
        if xml.xpath('name()') in self.XUPDATE_DEL:
          conflict_list += self.deleteNode(xml=xml,
                                           object=object,
                                           force=force,
                                           simulate=simulate,
                                           reset=reset,
                                           **kw)
          return conflict_list
        if keyword is None: # This is not a selection, directly the property
          keyword = xml.xpath('name()')
        if keyword not in self.NOT_EDITABLE_PROPERTY:
          # We will look for the data to enter
          xpath_expression = xml.get('select', xpath_expression)
          context = self.getContextFromXpath(object, xpath_expression)
          data_type = context.getPropertyType(keyword)
          #LOG('ERP5Conduit.updateNode', INFO, 'data_type:%r for keyword: %s' % (data_type, keyword))
          data = self.convertXmlValue(xml, data_type=data_type)
          args[keyword] = data
          args = self.getFormatedArgs(args=args)
          # This is the place where we should look for conflicts
          # For that we need :
          #   - data : the data from the remote box
          #   - old_data : the data from this box but at the time of the i
          #last synchronization
          #   - current_data : the data actually on this box
          isConflict = False
          if previous_xml is not None and not force:
          # if no previous_xml, no conflict
            #old_data = self.getObjectProperty(keyword, previous_xml,
                                              #data_type=data_type)
            previous_xml_tree = self.convertToXml(previous_xml)
            old_result = previous_xml_tree.xpath(xpath_expression)
            if old_result:
              old_data = self.convertXmlValue(old_result[0])
            else:
              raise ValueError('Xpath expression does not apply on previous'\
                                                  ' xml:%r' % xpath_expression)
            current_data = self.getProperty(context, keyword)
            #LOG('ERP5Conduit.updateNode', INFO, 'Conflict keyword: %s' % keyword)
            #LOG('ERP5Conduit.updateNode', INFO, 'Conflict data: %s' % str(data))
            #LOG('ERP5Conduit.updateNode', INFO, 'Conflict old_data: %s' % str(old_data))
            #LOG('ERP5Conduit.updateNode', INFO, 'Conflict current_data: %s' % str(current_data))
            if (old_data != current_data) and (data != current_data) \
                and keyword not in self.force_conflict_list:
              #LOG('ERP5Conduit.updateNode', INFO, 'Conflict on : %s' % keyword)
              # This is a conflict
              isConflict = True
              xml_string = etree.tostring(xml, encoding='utf-8')
              conflict = Conflict(object_path=context.getPhysicalPath(),
                                  keyword=keyword)
              conflict.setXupdate(xml_string)
              if not (data_type in self.binary_type_list):
                conflict.setLocalValue(current_data)
                conflict.setRemoteValue(data)
              conflict_list += [conflict]
          # We will now apply the argument with the method edit
          if args and (not isConflict or force) and \
              (not simulate or reset):
            self._updateContent(object=context, **args)
            # It is sometimes required to do something after an edit
            if getattr(context, 'manage_afterEdit', None) is not None:
              context.manage_afterEdit()

        if keyword == 'object':
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=xml,
                                        object=object,
                                        force=force,
                                        simulate=simulate,
                                        reset=reset,
                                        **kw)['conflict_list']
        elif keyword == self.history_tag and not simulate:
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=subnode, object=object,
                                        force=force, simulate=simulate,
                                        reset=reset, **kw)['conflict_list']
        elif keyword in (self.local_role_tag, self.local_permission_tag) and not simulate:
          # This is the case where we have to update Roles or update permission
          #LOG('ERP5Conduit.updateNode', DEBUG, 'we will add a local role')
          #user = self.getSubObjectId(xml)
          #roles = self.convertXmlValue(data,data_type='tokens')
          #object.manage_setLocalRoles(user,roles)
          conflict_list += self.addNode(xml=xml, object=object,
                                       force=force, simulate=simulate,
                                       reset=reset, **kw)['conflict_list']
    return conflict_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getFormatedArgs')
  def getFormatedArgs(self, args=None):
    """
    This lookd inside the args dictionnary and then
    convert any unicode string to string
    """
    new_args = {}
    for keyword in args.keys():
      data = args[keyword]
      if isinstance(keyword, unicode):
        keyword = keyword.encode(self.getEncoding())
      if isinstance(data, (tuple, list)):
        new_data = []
        for item in data:
          if isinstance(item, unicode):
            item = item.encode(self.getEncoding())
          new_data.append(item)
        data = new_data
      if isinstance(data, unicode):
        data = data.encode(self.getEncoding())
      if keyword == 'binary_data':
        #LOG('ERP5Conduit.getFormatedArgs', DEBUG, 'binary_data keyword: %s' % str(keyword))
        msg = MIMEBase('application','octet-stream')
        Encoders.encode_base64(msg)
        msg.set_payload(data)
        data = msg.get_payload(decode=True)
      new_args[keyword] = data
    return new_args

  security.declareProtected(Permissions.AccessContentsInformation, 'isProperty')
  def isProperty(self, xml):
    """
    Check if it is a simple property
    not an attribute @type it's a metadata
    """
    bad_list = (self.history_exp, self.attribute_type_exp,)
    value = xml.get('select')
    if value is not None:
      for bad_string in bad_list:
        if bad_string.search(value) is not None:
          return False
    return True

  def getContextFromXpath(self, context, xpath):
    """Return the last object from xpath expression
    /object[@gid='foo']/object[@id='bar']/object[@id='freak']/property
    will return object.getId() == 'freak'
    - We ignore the first object_block /object[@gid='foo'] intentionaly
    because the targeted context is already actual context.
    """
    if xpath is None:
      return context
    result_list = self.extract_id_from_xpath.findall(xpath)
    first_object = True
    while result_list:
      object_block = result_list[0][0]
      sub_context_id = result_list[0][3]
      sub_context = context._getOb(sub_context_id, None)
      if first_object:
        first_object = False
      elif sub_context is not None:
        context = sub_context
      else:
        # Ignore non existing objects
        LOG('ERP5Conduit', INFO, 'sub document of %s not found with id:%r'%\
                                         (context.getPath(), sub_context_id))
      xpath = xpath.replace(object_block, '', 1)
      result_list = self.extract_id_from_xpath.findall(xpath)
    return context

  security.declareProtected(Permissions.AccessContentsInformation,
                                                         'getSubObjectXupdate')
  @deprecated
  def getSubObjectXupdate(self, xml):
    """
    This will change the xml in order to change the update
    from the object to the subobject
    """
    xml_copy = deepcopy(xml)
    self.changeSubObjectSelect(xml_copy)
    return xml_copy

  security.declareProtected(Permissions.AccessContentsInformation,
      'isHistoryAdd')
  def isHistoryAdd(self, xml):
    bad_list = (self.history_exp,)
    value = xml.get('select')
    if value is not None:
      for bad_string in bad_list:
        if bad_string.search(value) is not None:
          if self.bad_history_exp.search(value) is None:
            return 1
          else:
            return -1
    return 0

  security.declareProtected(Permissions.AccessContentsInformation,
                                                     'isSubObjectModification')
  @deprecated
  def isSubObjectModification(self, xml):
    """
    Check if it is a modification from an subobject
    """
    good_list = (self.sub_object_exp,)
    value = xml.attrib.get('select', None)
    if value is not None:
      for good_string in good_list:
        if good_string.search(value) is not None:
          return 1
    return 0

  security.declareProtected(Permissions.AccessContentsInformation,
                                                           'getSubObjectDepth')
  @deprecated
  def getSubObjectDepth(self, xml):
    """
    Give the Depth of a subobject modification
    0 means, no depth
    1 means it is a subobject
    2 means it is more depth than subobject
    """
    #LOG('getSubObjectDepth',0,'xml.tag: %s' % xml.tag)
    if xml.xpath('name()') in self.XUPDATE_TAG:
      i = 0
      if xml.xpath('name()') in self.XUPDATE_INSERT:
        i = 1
      #LOG('getSubObjectDepth',0,'xml2.tag: %s' % xml.tag)
      value = xml.attrib.get('select', None)
      if value is not None:
        #LOG('getSubObjectDepth',0,'subnode.nodeValue: %s' % subnode.nodeValue)
        if self.sub_sub_object_exp.search(value) is not None:
          return 2 # This is sure in all cases
        elif self.sub_object_exp.search(value) is not None:
          #new_select = self.getSubObjectSelect(value) # Still needed ???
          #if self.getSubObjectSelect(new_select) != new_select:
          #  return (2 - i)
          #return (1 - i)
          return (2 - i)
        elif self.object_exp.search(value) is not None:
          return (1 - i)
    return 0

  security.declareProtected(Permissions.ModifyPortalContent,
      'changeSubObjectSelect')
  @deprecated
  def changeSubObjectSelect(self, xml):
    """
    Return a string wich is the selection for the subobject
    ex: for "/object[@id='161']/object[@id='default_address']/street_address"
    it returns "/object[@id='default_address']/street_address"
    """
    select = xml.attrib.get('select')
    if self.object_exp.search(select) is not None:
      s = '/'
      if re.search('/.*/', select) is not None: # This means we have more than just object
        new_value = select[select.find(s, select.find(s)+1):]
      else:
        new_value = '/'
      select = new_value
    xml.attrib['select'] = select

  security.declareProtected(Permissions.AccessContentsInformation,
      'getSubObjectId')
  @deprecated
  def getSubObjectId(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    value = xml.attrib.get('select', None)
    if value is not None:
      if self.object_exp.search(value) is not None:
        s = "'"
        first = value.find(s) + 1
        object_id = value[first:value.find(s, first)]
        return object_id
    return object_id

  security.declareProtected(Permissions.AccessContentsInformation,
      'getHistoryIdFromSelect')
  def getHistoryIdFromSelect(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    value = xml.attrib.get('select', None)
    if value is not None:
      if self.history_exp.search(value) is not None:
        s = self.history_tag
        object_id = value[value.find(s):]
        object_id = object_id[object_id.find("'") + 1:]
        object_id = object_id[:object_id.find("'")]
        return object_id
    return object_id

  security.declareProtected(Permissions.AccessContentsInformation,
      'getSubObjectXml')
  def getSubObjectXml(self, object_id, xml):
    """
    Return the xml of the subobject which as the id object_id
    """
    xml = self.convertToXml(xml)
    for subnode in xml:
      if subnode.xpath('local-name()') == self.xml_object_tag:
        if object_id == subnode.get('id'):
          return subnode
    return None

  security.declareProtected(Permissions.AccessContentsInformation,
                                                                'getAttribute')
  @deprecated
  def getAttribute(self, xml, param):
    """
    Retrieve the given parameter from the xml
    """
    return xml.attrib.get(param, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                                                           'getObjectProperty')
  @deprecated
  def getObjectProperty(self, property, xml, data_type=None):
    """
    Retrieve the given property
    """
    xml = self.convertToXml(xml)
    # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
    for subnode in xml:
      if subnode.xpath('local-name()') == property:
        return self.convertXmlValue(subnode)
    return None

  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    """
      return a xml with id replace by a new id
    """
    if isinstance(xml, str):
      xml = etree.XML(xml, parser=parser)
    else:
      #copy of xml object for modification
      xml = deepcopy(xml)
    object_element = xml.find('object')
    del object_element.attrib['id']
    object_element.attrib[attribute_name] = new_id
    if as_string:
      return etree.tostring(xml)
    return xml

  def getXMLFromObjectWithId(self, object, xml_mapping):
    """
      return the xml with Id of Object
    """
    xml = ''
    if xml_mapping is None:
      return xml
    func = getattr(object, xml_mapping, None)
    if func is not None:
      xml = func()
    return xml

  def getXMLFromObjectWithGid(self, object, gid, xml_mapping, as_string=True):
    """
      return the xml with Gid of Object
    """
    xml_with_id = self.getXMLFromObjectWithId(object, xml_mapping)
    return self.replaceIdFromXML(xml_with_id, 'gid', gid, as_string=as_string)


  def getXMLFromObjectWithRid(self, object, rid, xml_mapping, as_string=True):
    """
      return the xml with Rid of Object
    """
    xml_id = self.getXMLFromObjectWithId(object, xml_mapping)
    xml_rid = self.replaceIdFromXML(xml_id, 'rid', rid, as_string=as_string)
    return xml_rid

  security.declareProtected(Permissions.AccessContentsInformation,'convertToXml')
  def convertToXml(self, xml):
    """
    if xml is a string, convert it to a node
    """
    if xml is None: return None
    if isinstance(xml, (str, unicode)):
      if isinstance(xml, unicode):
        xml = xml.encode('utf-8')
      xml = etree.XML(xml, parser=parser)
    # If we have the xml from the node erp5, we just take the subnode
    if xml.xpath('local-name()') == 'erp5':
      xml = xml[0]
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,
                                                               'getObjectType')
  def getObjectType(self, xml):
    """
    Retrieve the portal type from an xml
    """
    return xml.get('portal_type')

  security.declareProtected(Permissions.AccessContentsInformation,
                                                             'getPropertyType')
  def getPropertyType(self, xml):
    """
    Retrieve the portal type from an xml
    """
    return xml.get('type')

  security.declareProtected(Permissions.AccessContentsInformation,
                                                        'getXupdateObjectType')
  @deprecated
  def getXupdateObjectType(self, xml):
    """
    Retrieve the portal type from an xupdate
    XXXX  This should not be used any more !!! XXXXXXXXXXX
    """
    return xml.xpath('string(.//*[name() == "xupdate:attribute"][@name = "portal_type"])') or None

  security.declareProtected(Permissions.ModifyPortalContent, 'newObject')
  def newObject(self, object=None, xml=None, simulate=False,
                reset_local_roles=True, reset_workflow=True):
    """
      modify the object with datas from
      the xml (action section)
    """
    args = {}
    if simulate:
      return
    # Retrieve the list of users with a role and delete default roles
    if reset_local_roles:
      user_role_list = [x[0] for x in object.get_local_roles()]
      object.manage_delLocalRoles(user_role_list)
    if getattr(object, 'workflow_history', None) is not None and reset_workflow:
      object.workflow_history = PersistentMapping()
    if xml.prefix == 'xupdate':
      xml = xml[0]
    for subnode in xml.xpath('*'):
      #get only Element nodes (not Comments or Processing instructions)
      if subnode.xpath('name()') not in self.NOT_EDITABLE_PROPERTY:
        keyword_type = self.getPropertyType(subnode)
        # This is the case where the property is a list
        keyword = subnode.xpath('name()')
        args[keyword] = self.convertXmlValue(subnode, keyword_type)
      elif subnode.xpath('local-name()') in self.ADDABLE_PROPERTY + (self.xml_object_tag,):
        self.addNode(object=object, xml=subnode, force=True)
    # We should first edit the object
    args = self.getFormatedArgs(args=args)
    # edit the object with a dictionnary of arguments,
    # like {"telephone_number":"02-5648"}
    self.editDocument(object=object, **args)
    if getattr(object, 'manage_afterEdit', None) is not None:
      object.manage_afterEdit()
    self.afterNewObject(object)

  security.declareProtected(Permissions.AccessContentsInformation,
                                                              'afterNewObject')
  def afterNewObject(self, object):
    """Overloadable method
    """
    pass

  security.declareProtected(Permissions.AccessContentsInformation,
                                                            'getStatusFromXml')
  def getStatusFromXml(self, xml):
    """
    Return a worklow status from xml
    """
    status = {}
    for subnode in xml:
      keyword = subnode.tag
      value = self.convertXmlValue(xml.find(keyword))
      status[keyword] = value
    return status

  security.declareProtected(Permissions.AccessContentsInformation,
                                                       'getXupdateElementList')
  @deprecated
  def getXupdateElementList(self, xml):
    """
    Retrieve the list of xupdate:element subnodes
    """
    return xml.xpath('|'.join(['.//*[name() = "%s"]' % name for name in self.XUPDATE_ELEMENT]))

  security.declareProtected(Permissions.AccessContentsInformation,
                                                       'getElementFromXupdate')
  def getElementFromXupdate(self, xml):
    """
    return a fragment node with applied xupdate
    This method simulate an xupdate transformation on given XML.
    It transform the xupdate into node handleable by Conduit
    """
    if xml.xpath('name()') in self.XUPDATE_ELEMENT:
      new_node = Element(xml.get('name'), nsmap=xml.nsmap)
      for subnode in xml.findall('{%s}attribute' % xml.nsmap['xupdate']):
        new_node.attrib.update({subnode.get('name'): subnode.text})
      ## Then dumps the xml and remove xupdate:attribute nodes
      new_node.extend(deepcopy(child) for child in\
                                 xml.xpath('*[name() != "xupdate:attribute"]'))
      new_node.text = xml.text
      new_node.tail = xml.tail
      return new_node
    if xml.xpath('name()') in (self.XUPDATE_UPDATE + self.XUPDATE_DEL):
      # This condition seems not used anymore and not efficient
      # Usage of xupdate_processor is recommanded
      result = u'<'
      attribute = xml.attrib.get('select')
      s = '[@id='
      s_place = attribute.find(s)
      select_id = None
      if (s_place > 0):
        select_id = attribute[s_place+len(s):]
        select_id = select_id[:select_id.find("'",1)+1]
      else:
        s_place = len(attribute)
      property = attribute[:s_place].strip('/')
      result += property
      if select_id is not None:
        result += ' id=%s' % select_id
      result +=  '>'
      xml_string = self.nodeToString(xml)
      maxi = xml_string.find('>')+1
      result += xml_string[maxi:xml_string.find('</%s>' % xml.xpath('name()'))]
      result += '</%s>' % (property)
      #LOG('getElementFromXupdate, result:',0,repr(result))
      return self.convertToXml(result)
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,
                                                    'getWorkflowActionFromXml')
  def getWorkflowActionFromXml(self, xml):
    """
    Return the list of workflow actions
    """
    action_list = []
    if xml.xpath('name()') in self.XUPDATE_ELEMENT:
      action_list.append(xml)
      return action_list
    for subnode in xml:
      if subnode.xpath('local-name()') == self.action_tag:
        action_list.append(subnode)
    return action_list

  security.declareProtected(Permissions.AccessContentsInformation,
                                                             'convertXmlValue')
  def convertXmlValue(self, node, data_type=None):
    """Cast xml information into appropriate python type
    """
    if node is None:
      return None
    if data_type is None:
      data_type = self.getPropertyType(node)
    if data_type == self.none_type:
      return None
    data = node.text
    if data is not None and isinstance(data, unicode):
      data = data.encode('utf-8')
    elif data is None and data_type in self.text_type_list:
      return ''
    # We can now convert string in tuple, dict, binary...
    if data_type in self.list_type_list:
      data = unmarshaller(node[0])
    elif data_type in self.text_type_list:
      data = unescape(data)
    elif data_type in self.data_type_list:
      if data is None:
        # data is splitted inside  block_data nodes
        data = ''.join([standard_b64decode(block.text) for\
                                                 block in node.iterchildren()])
    elif data_type in self.pickle_type_list:
      data = pickle.loads(standard_b64decode(data))
    elif data_type in self.date_type_list:
      data = DateTime(data)
    elif data_type in self.int_type_list:
      data = int(data)
    return data


  security.declareProtected(Permissions.ModifyPortalContent, 'applyXupdate')
  def applyXupdate(self, object=None, xupdate=None, previous_xml=None, **kw):
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if isinstance(xupdate, (str, unicode)):
      xupdate = etree.XML(xupdate, parser=parser)
    #LOG("applyXupdate", INFO, etree.tostring(xupdate, pretty_print=True))
    xupdate_builded = False
    xpath_expression_update_dict = {}
    for subnode in xupdate:
      selection_name = ''
      original_xpath_expression = subnode.get('select', '')
      if not xupdate_builded and\
                            MARSHALLER_NAMESPACE_URI in subnode.nsmap.values()\
                                  or 'block_data' in original_xpath_expression:
        # It means that the xpath expression is targetting
        # marshalled values or data nodes. We need to rebuild the original xml
        # in its own context in order to retrieve original value

        # We are insde a loop build the XUpdated tree only once
        xupdate_builded = True

        # Find the prefix used by marshaller.
        for prefix, namespace_uri in subnode.nsmap.iteritems():
          if namespace_uri == MARSHALLER_NAMESPACE_URI:
            break
        # TODO add support of etree objects for xuproc to avoid
        # serializing tree into string
        if not isinstance(previous_xml, str):
          previous_xml = etree.tostring(previous_xml)
        xupdated_tree = xuproc.applyXUpdate(xml_xu_string=etree.tostring(xupdate),
                                            xml_doc_string=previous_xml)
      if MARSHALLER_NAMESPACE_URI in subnode.nsmap.values():
        xpath_expression = original_xpath_expression
        context = self.getContextFromXpath(object, xpath_expression)
        base_xpath_expression = xpath_expression\
                                            [:xpath_expression.index(prefix)-1]
        xupdated_node_list = xupdated_tree.xpath(base_xpath_expression)
        if xupdated_node_list:
          xupdated_node = xupdated_node_list[0]
        else:
          ValueError('Wrong xpath expression:%r' % base_xpath_expression)
        if base_xpath_expression not in xpath_expression_update_dict:
          xpath_expression_update_dict[base_xpath_expression] = \
                                   dict(xml=xupdated_node,
                                        object=context,
                                        xpath_expression=base_xpath_expression)
      elif 'block_data' in original_xpath_expression:
        """XXX Use Qualified Names for block_data nodes
        to avoid ambiguity
        """
        xpath_expression = original_xpath_expression
        context = self.getContextFromXpath(object, xpath_expression)
        base_xpath_expression = xpath_expression\
                                            [:xpath_expression.index('block_data')-1]
        xupdated_node_list = xupdated_tree.xpath(base_xpath_expression)
        if xupdated_node_list:
          xupdated_node = xupdated_node_list[0]
        else:
          ValueError('Wrong xpath expression:%r' % base_xpath_expression)
        if base_xpath_expression not in xpath_expression_update_dict:
          xpath_expression_update_dict[base_xpath_expression] = \
                                   dict(xml=xupdated_node,
                                        object=context,
                                        xpath_expression=base_xpath_expression)
      elif subnode.xpath('name()') in self.XUPDATE_INSERT_OR_ADD:
        conflict_list += self.addNode(xml=subnode, object=object,
                                      previous_xml=previous_xml,
                                      **kw)['conflict_list']
      elif subnode.xpath('name()') in self.XUPDATE_DEL:
        conflict_list += self.deleteNode(xml=subnode, object=object,
                                         previous_xml=previous_xml, **kw)
      elif subnode.xpath('name()') in self.XUPDATE_UPDATE:
        conflict_list += self.updateNode(xml=subnode, object=object,
                                         previous_xml=previous_xml, **kw)

    # Now apply collected xupdated_node
    for update_dict in xpath_expression_update_dict.itervalues():
      update_dict.update(kw)
      conflict_list += self.updateNode(previous_xml=previous_xml,
                                       **update_dict)
    return conflict_list

  def isWorkflowActionAddable(self, object=None, status=None, wf_tool=None,
                              wf_id=None, xml=None):
    """
    Some checking in order to check if we should add the workfow or not
    We should not returns a conflict list as we wanted before, we should
    instead go to a conflict state.
    """
    # We first test if the status in not already inside the workflow_history
    return 1
    # XXX Disable for now
    wf_history = object.workflow_history
    if wf_history.has_key(wf_id):
      action_list = wf_history[wf_id]
    else: action_list = []
    addable = True
    for action in action_list:
      this_one = True
      for key in action.keys():
        if status[key] != action[key]:
          this_one = False
          break
      if this_one:
        addable = False
        break
    return addable

  security.declareProtected(Permissions.ModifyPortalContent, 'constructContent')
  def constructContent(self, object, object_id, portal_type):
    """
    This allows to specify how to construct a new content.
    This is really usefull if you want to write your
    own Conduit.
    """
    #LOG('ERP5Conduit.addNode',0,'portal_type: |%s|' % str(portal_type))
    object.newContent(portal_type=portal_type, id=object_id)
    subobject = object._getOb(object_id)
    return subobject, True, True

  security.declareProtected(Permissions.ModifyPortalContent, 'addWorkflowNode')
  def addWorkflowNode(self, object, xml, simulate):
    """
    This allows to specify how to handle the workflow informations.
    This is really usefull if you want to write your own Conduit.
    """
    conflict_list = []
    # We want to add a workflow action
    wf_tool = getToolByName(object,'portal_workflow')
    wf_id = self.getAttribute(xml,'id')
    if wf_id is None: # History added by xupdate
      wf_id = self.getHistoryIdFromSelect(xml)
      xml = xml[0]
    #for action in self.getWorkflowActionFromXml(xml):
    status = self.getStatusFromXml(xml)
    #LOG('addNode, status:',0,status)
    add_action = self.isWorkflowActionAddable(object=object,
                                           status=status,wf_tool=wf_tool,
                                           wf_id=wf_id,xml=xml)
    if add_action and not simulate:
      wf_tool.setStatusOf(wf_id,object,status)

    # Specific CPS, try to remove duplicate lines in portal_repository._histories
    tool = getToolByName(self,'portal_repository',None)
    if tool is not None:
      if getattr(self, 'getDocid', None) is not None:
        docid = self.getDocid()
        history = tool.getHistory(docid)
        new_history = ()
        for history_line in history:
          if history_line not in new_history:
            new_history += (history_line,)
        tool.setHistory(docid,new_history)

    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'addLocalRoleNode')
  def addLocalRoleNode(self, object, xml):
    """
    This allows to specify how to handle the local role informations.
    This is really usefull if you want to write your own Conduit.
    """
    # We want to add a local role
    roles = self.convertXmlValue(xml, data_type='tokens')
    user = self.getAttribute(xml, 'id')
    roles = list(roles) # Needed for CPS, or we have a CPS error
    #LOG('local_role: ',0,'user: %s roles: %s' % (repr(user),repr(roles)))
    #user = roles[0]
    #roles = roles[1:]
    if xml.xpath('local-name()') == self.local_role_tag:
      object.manage_setLocalRoles(user, roles)
    elif xml.xpath('local-name()') == self.local_group_tag:
      object.manage_setLocalGroupRoles(user, roles)

  security.declareProtected(Permissions.ModifyPortalContent, 'addLocalPermissionNode')
  def addLocalPermissionNode(self, object, xml):
    """
    This allows to specify how to handle the local permision informations.
    This is really usefull if you want to write your own Conduit.
    """
    conflict_list = []
    # We want to add a local role
    #LOG('addLocalPermissionNode, xml',0,xml)
    roles = self.convertXmlValue(xml, data_type='tokens')

    permission = xml.get('id')
    #LOG('local_role: ',0,'permission: %s roles: %s' % (repr(permission),repr(roles)))
    #user = roles[0]
    #roles = roles[1:]
    if xml.xpath('local-name()') == self.local_permission_tag:
      object.manage_setLocalPermissions(permission, roles)
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'editDocument')
  def editDocument(self, object=None, **kw):
    """
    This is the default editDocument method. This method
    can easily be overwritten.
    """
    object._edit(**kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'getProperty')
  def getProperty(self, object, kw):
    """
    This is the default getProperty method. This method
    can easily be overwritten.
    """
    return object.getProperty(kw)

  def nodeToString(self, node):
    """
    return an xml string corresponding to the node
    """
    return etree.tostring(node, encoding='utf-8', pretty_print=True)

  def getGidFromObject(self, object):
    """
    return the Gid composed with the object informations
    """
    return object.getId()

  def _createContent(self, xml=None, object=None, object_id=None,
                     sub_object=None, reset_local_roles=False,
                     reset_workflow=False, simulate=False, **kw):
    """
      This is the method calling to create an object
    """
    if object_id is None:
      object_id = xml.get('id')
    if object_id is not None:
      if sub_object is None:
        try:
          sub_object = object._getOb(object_id)
        except (AttributeError, KeyError, TypeError):
          sub_object = None
      if sub_object is None: # If so, it doesn't exist
        portal_type = ''
        if xml.xpath('local-name()') == self.xml_object_tag:
          portal_type = self.getObjectType(xml)
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
                                                        object,
                                                        object_id,
                                                        portal_type)
      self.newObject(object=sub_object,
                     xml=xml,
                     simulate=simulate,
                     reset_local_roles=reset_local_roles,
                     reset_workflow=reset_workflow)
    return sub_object

  def _updateContent(self, object=None, **args):
    """
      This is the method for update the object
    """
    return self.editDocument(object=object, **args)

  def _deleteContent(self, object=None, object_id=None):
    """
      This is the method for delete the object
    """
    return self.deleteObject(object, object_id)


#  def getGidFromXML(self, xml, namespace, gid_from_xml_list):
#    """
#    return the Gid composed with xml informations
#    """
#    gid = xml.xpath('string(.//syncml:id)')
#    if gid in gid_from_xml_list or gid == ' ':
#      return False
#    return gid
