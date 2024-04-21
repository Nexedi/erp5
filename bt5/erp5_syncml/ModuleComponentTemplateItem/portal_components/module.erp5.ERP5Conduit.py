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

from erp5.component.module.XMLSyncUtils import XMLSyncUtilsMixin
from erp5.component.module.XMLSyncUtils import getXupdateObject
from Products.ERP5Type.Utils import deprecated
from Products.ERP5Type.XMLExportImport import MARSHALLER_NAMESPACE_URI
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Base import WorkflowMethod
from DateTime.DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import PersistentMapping

from xml.sax.saxutils import unescape
import re
from lxml import etree
from lxml.etree import Element
import six
parser = etree.XMLParser(remove_blank_text=True)
from xml_marshaller.xml_marshaller import Unmarshaller
from xupdate_processor import xuproc
from base64 import standard_b64decode
from zope.interface import implementer
from copy import deepcopy
from six import string_types as basestring

import logging
syncml_logger = logging.getLogger('ERP5SyncML')

from hashlib import sha1

from erp5.component.module.SyncMLConstant import XUPDATE_ELEMENT,\
     XUPDATE_INSERT_OR_ADD_LIST, XUPDATE_DEL, XUPDATE_UPDATE, XUPDATE_INSERT_LIST
from erp5.component.interface.IConduit import IConduit


class SafeUnmarshaller(Unmarshaller):
  def find_class(self, module, name):
    raise ValueError("Refusing to unmarshall {}.{}".format(module, name))

unmarshaller = SafeUnmarshaller().load_tree

# Constant
HISTORY_TAG = 'workflow_action'
XML_OBJECT_TAG = 'object'
LOCAL_ROLE_TAG = 'local_role'
LOCAL_PERMISSION_TAG = 'local_permission'
LOCAL_GROUP_TAG = 'local_group'
LOCAL_ROLE_LIST = (LOCAL_ROLE_TAG, LOCAL_GROUP_TAG,)

ADDABLE_PROPERTY_LIST = LOCAL_ROLE_LIST + (HISTORY_TAG,) + (LOCAL_PERMISSION_TAG,)
NOT_EDITABLE_PROPERTY_LIST = ('id', 'object', 'uid', 'attribute::type',) +\
                             (XUPDATE_ELEMENT,) + ADDABLE_PROPERTY_LIST

FORCE_CONFLICT_LIST = ('layout_and_schema', 'ModificationDate')

from Products.ERP5Type.Accessor.TypeDefinition import list_types
LIST_TYPE_LIST = list_types
TEXT_TYPE_LIST = ('text', 'string',)
NONE_TYPE = 'None'
DATE_TYPE = 'date'
DICT_TYPE = 'dict'
INT_TYPE = 'int'
DATA_TYPE_LIST = ('data', 'object',)
BOOLEAN_TYPE = 'boolean'

HISTORY_EXP = re.compile(r"/%s\[@id='.*'\]" % HISTORY_TAG)
BAD_HISTORY_EXP = re.compile(r"/%s\[@id='.*'\]/" % HISTORY_TAG)
EXTRACT_ID_FROM_XPATH = re.compile(
                            r"(?P<object_block>(?P<property>[^/]+)\[@"\
                            r"(?P<id_of_id>id|gid)='(?P<object_id>[^']+)'\])")

WORKFLOW_ACTION_NOT_ADDABLE = 0
WORKFLOW_ACTION_ADDABLE = 1
WORKFLOW_ACTION_INSERTABLE = 2

@implementer( IConduit,)
class ERP5Conduit(XMLSyncUtilsMixin):
  """
    A conduit is a piece of code in charge of

    - updating an object attributes from an XUpdate XML stream

    (Conduits are not in charge of creating new objects which
    are eventually missing in a synchronization process)

    If an object has be created during a synchronization process,
    the way to proceed consists in:

    1- creating an empty instance of the appropriate class
      in the appropriate directory

    2- updating that empty instance with the conduit

    The first implementation of ERP5 synchronization
    will define a default location to create new objects and
    a default class. This will be defined at the level of the synchronization
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

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,'getEncoding')
  def getEncoding(self):
    """
    return the string corresponding to the local encoding
    """
    #return "iso-8859-1"
    return "utf-8"

  #security.declareProtected(Permissions.ModifyPortalContent, '__init__')
  #def __init__(self):
    #self.args = {}

  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, xml=None, object=None, sub_object=None, reset=None, # pylint: disable=redefined-builtin
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
    if xml is None:
      return {'conflict_list': conflict_list, 'object': sub_object}
    # In the case where this new node is a object to add
    xpath_expression = xml.get('select')
    if xml.xpath('local-name()') == HISTORY_TAG and not reset:
      conflict_list += self.addWorkflowNode(object, xml, simulate)
    elif xml.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST and\
                            MARSHALLER_NAMESPACE_URI not in xml.nsmap.values():
      # change the context according select expression
      get_target_parent = xml.xpath('name()') in XUPDATE_INSERT_LIST
      context = self.getContextFromXpath(object, xpath_expression,
                                         get_target_parent=get_target_parent)
      for element in xml.findall('{%s}element' % xml.nsmap['xupdate']):
        xml = self.getElementFromXupdate(element)
        conflict_list += self.addNode(xml=xml, object=context, **kw)\
                                                              ['conflict_list']
    elif xml.xpath('local-name()') == XML_OBJECT_TAG:
      sub_object = self._createContent(xml=xml,
                                      object=object,
                                      sub_object=sub_object,
                                      reset_local_roles=reset_local_roles,
                                      reset_workflow=reset_workflow,
                                      reset=reset,
                                      simulate=simulate,
                                      **kw)
    elif xml.xpath('local-name()') in LOCAL_ROLE_LIST:
      self.addLocalRoleNode(object, xml)
    elif xml.xpath('local-name()') == LOCAL_PERMISSION_TAG:
      conflict_list += self.addLocalPermissionNode(object, xml)
    else:
      conflict_list += self.updateNode(xml=xml, object=object, reset=reset,
                                                       simulate=simulate, **kw)
    # We must returns the object created
    return {'conflict_list':conflict_list, 'object': sub_object}

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteNode')
  def deleteNode(self, xml=None, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """
    This method manage the deletion of a node as well as the deletion
    of one property
    """
    #LOG('ERP5Conduit.deleteNode', INFO, 'object path:%s' % object.getPath())
    #LOG('ERP5Conduit deleteNode', INFO, 'object_id:%r' % object_id)
    if object_id is not None:
      self._deleteContent(object=object, object_id=object_id, **kw)
      return []
    xml = self.convertToXml(xml)
    #LOG('ERP5Conduit deleteNode', INFO, etree.tostring(xml, pretty_print=True))
    xpath_expression = xml.get('select')
    #LOG('ERP5Conduit xpath_expression', INFO, xpath_expression)
    context_to_delete = self.getContextFromXpath(object, xpath_expression)
    if 'workflow_action' in xpath_expression:
      # /erp5/object[@gid='313730']/../workflow_action[@id=SHA(TIME + ACTOR)]
      wf_action_id = EXTRACT_ID_FROM_XPATH.findall(xpath_expression)[-1][-1]
      def deleteWorkflowNode():
        for wf_id, wf_history_tuple in six.iteritems(object.workflow_history):
          for wf_history_index, wf_history in enumerate(wf_history_tuple):
            if sha1((wf_id + str(wf_history['time']) +
                       wf_history['actor']).encode('utf-8')).hexdigest() == wf_action_id:
              object.workflow_history[wf_id] = (
                object.workflow_history[wf_id][:wf_history_index] +
                object.workflow_history[wf_id][wf_history_index + 1:])

              return True

        return False

      deleteWorkflowNode()

    elif context_to_delete != object:
      self._deleteContent(object=context_to_delete.getParentValue(),
                                           object_id=context_to_delete.getId(),
                          **kw)
    else:
      #same context
      if [role for role in LOCAL_ROLE_LIST if role in xpath_expression]:
        user = EXTRACT_ID_FROM_XPATH.findall(xpath_expression)[-1][3]
        #LOG('ERP5Conduit.deleteNode local_role: ', INFO, 'user: %r' % user)
        if LOCAL_ROLE_TAG in xpath_expression:
          object.manage_delLocalRoles([user])
        elif LOCAL_GROUP_TAG in xpath_expression:
          object.manage_delLocalGroupRoles([user])
      if LOCAL_PERMISSION_TAG in xpath_expression:
        permission = EXTRACT_ID_FROM_XPATH.findall(xpath_expression)[-1][3]
        #LOG('ERP5Conduit.deleteNode permission: ', INFO,
                                                 #'permission: %r' % permission)
        object.manage_setLocalPermissions(permission)
    return []

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteObject')
  def deleteObject(self, object, object_id, **kw): # pylint: disable=redefined-builtin
    try:
      object._delObject(object_id)
    except (AttributeError, KeyError):
      #LOG('ERP5Conduit.deleteObject', DEBUG, 'Unable to delete: %s' % str(object_id))
      pass

  security.declareProtected(Permissions.ModifyPortalContent, 'updateNode')
  def updateNode(self, xml=None, object=None, previous_xml=None, force=False, # pylint: disable=redefined-builtin
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
      return []
    xml = self.convertToXml(xml)
    syncml_logger.debug("updateNode with xml %s",
                        etree.tostring(xml, pretty_print=True))
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
        if xml.xpath('name()') not in XUPDATE_INSERT_OR_ADD_LIST:
          for subnode in xml:
            if subnode.xpath('name()') == XUPDATE_ELEMENT:
              keyword = subnode.get('name')
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
        if xml.xpath('name()') in XUPDATE_DEL:
          conflict_list += self.deleteNode(xml=xml,
                                           object=object,
                                           force=force,
                                           simulate=simulate,
                                           reset=reset,
                                           **kw)
          return conflict_list
        if keyword is None: # This is not a selection, directly the property
          keyword = xml.xpath('name()')
        if keyword not in NOT_EDITABLE_PROPERTY_LIST:
          # We will look for the data to enter
          xpath_expression = xml.get('select', xpath_expression)
          get_target_parent = xml.xpath('name()') in XUPDATE_INSERT_LIST
          context = self.getContextFromXpath(object,
                                           xpath_expression,
                                           get_target_parent=get_target_parent)
          data_type = context.getPropertyType(keyword)
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
          if previous_xml and not force:
            previous_xml_tree = self.convertToXml(previous_xml)
            old_result = previous_xml_tree.xpath(xpath_expression)
            if old_result:
              old_data = self.convertXmlValue(old_result[0])
            else:
              raise ValueError('Xpath expression does not apply on previous'\
                                                  ' xml:%r' % xpath_expression)
            current_data = self.getProperty(context, keyword)
            if (old_data != current_data) and (data != current_data) and\
                                            keyword not in FORCE_CONFLICT_LIST:
              # This is a conflict
              isConflict = True
              xml_string = etree.tostring(xml, encoding='utf-8')
              # unattach diff from its parent once copy has been
              # stored on signature
              xml.getparent().remove(xml)
              conflict = kw['signature'].newContent(portal_type='SyncML Conflict',
                                                    origin_value=context,
                                                    property_id=keyword,
                                                    diff_chunk=xml_string)
              if data_type not in DATA_TYPE_LIST:
                conflict.edit(local_value=current_data,
                              remote_value=data)
              syncml_logger.info("Generated a conflict for %s", keyword)
              conflict_list += [conflict]
          else:
            syncml_logger.info("UpdateNode : no previous xml founds or force")
          # We will now apply the argument with the method edit
          if args and (not isConflict or force) and (not simulate or reset):
            syncml_logger.info("calling updateContent : %s", args)
            self._updateContent(object=context, **args)
            # It is sometimes required to do something after an edit
            if getattr(context, 'manage_afterEdit', None) is not None:
              context.manage_afterEdit()
          else:
            syncml_logger.warning("did not call updateContent on %s", context)
        else:
          syncml_logger.info("UpdateNode : not editable property %s", keyword)

        # Specific cases of update
        if keyword == 'object':
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=xml,
                                        object=object,
                                        force=force,
                                        simulate=simulate,
                                        reset=reset,
                                        **kw)['conflict_list']
        elif keyword == HISTORY_TAG and not simulate:
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=subnode, object=object,
                                        force=force, simulate=simulate,
                                        reset=reset, **kw)['conflict_list']
        elif keyword in (LOCAL_ROLE_TAG, LOCAL_PERMISSION_TAG) and not simulate:
          # This is the case where we have to update Roles or update permission
          #LOG('ERP5Conduit.updateNode', DEBUG, 'we will add a local role')
          #user = self.getSubObjectId(xml)
          #roles = self.convertXmlValue(data,data_type='tokens')
          #object.manage_setLocalRoles(user,roles)
          conflict_list += self.addNode(xml=xml, object=object,
                                       force=force, simulate=simulate,
                                       reset=reset, **kw)['conflict_list']
      else:
        syncml_logger.warning("UpdateNode : not a property %s", etree.tostring(xml, pretty_print=True))
    return conflict_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getFormatedArgs')
  def getFormatedArgs(self, args=None):
    """
    This lookd inside the args dictionnary and then
    convert any unicode string to string ( on python 2 )
    """
    new_args = {}
    for keyword in args.keys():
      data = args[keyword]
      if six.PY2 and isinstance(keyword, six.text_type):
        keyword = keyword.encode(self.getEncoding())
      if isinstance(data, (tuple, list)):
        new_data = []
        for item in data:
          if six.PY2 and isinstance(item, six.text_type):
            item = item.encode(self.getEncoding())
          new_data.append(item)
        data = new_data
      if six.PY2 and isinstance(data, six.text_type):
        data = data.encode(self.getEncoding())
      new_args[keyword] = data
    return new_args

  security.declareProtected(Permissions.AccessContentsInformation, 'isProperty')
  def isProperty(self, xml):
    """
    Check if it is a simple property
    not an attribute @type it's a metadata
    """
    bad_list = (HISTORY_EXP,)
    value = xml.get('select')
    if value is not None:
      for bad_string in bad_list:
        if bad_string.search(value) is not None:
          return False
    return True

  def getContextFromXpath(self, context, xpath, get_target_parent=False):
    """Return the last object from xpath expression
    /object[@gid='foo']/object[@id='bar']/object[@id='freak']/property
    will return object.getId() == 'freak'
    - We ignore the first object_block /object[@gid='foo'] intentionaly
    because the targeted context is already actual context.
      context: object in acquisition context
      xpath: string which is xpath expression to fetch the object
      get_target_parent: boolean to get the parent of targetted object
    """
    if xpath is None:
      return context
    result_list = EXTRACT_ID_FROM_XPATH.findall(xpath)
    if get_target_parent:
      result_list = result_list[:-1]
    first_object = True
    sub_context = None
    while result_list:
      object_block = result_list[0][0]
      sub_context_id = result_list[0][3]
      _get_ob_accessor = getattr(context, '_getOb', None)
      if _get_ob_accessor is not None:
        # Some ERP5 objects doe not implement Folder
        # like coordinates objects
        sub_context = _get_ob_accessor(sub_context_id, None)
      if first_object:
        first_object = False
      elif sub_context is not None:
        context = sub_context
      # else:
        # Ignore non existing objects
        #LOG('ERP5Conduit', INFO, 'sub document of %s not found with id:%r'%\
                                         #(context.getPath(), sub_context_id))
      xpath = xpath.replace(object_block, '', 1)
      result_list = EXTRACT_ID_FROM_XPATH.findall(xpath)
      if get_target_parent:
        result_list = result_list[:-1]
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
    bad_list = (HISTORY_EXP,)
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
      'getHistoryIdFromSelect')
  def getHistoryIdFromSelect(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    value = xml.get('select')
    if value is not None:
      if HISTORY_EXP.search(value) is not None:
        s = HISTORY_TAG
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
      if subnode.xpath('local-name()') == XML_OBJECT_TAG:
        if object_id == subnode.get('id'):
          return subnode
    return None

  security.declareProtected(Permissions.ModifyPortalContent,
                            'replaceIdFromXML')
  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    """XXX argument old_attribute_name is missing
    XXX name of method is not good, because content is not necessarily XML
    return a xml with id replaced by a new id
    """
    if isinstance(xml, (str, bytes)):
      xml = etree.XML(xml, parser=parser)
    else:
      # copy of xml object for modification
      xml = deepcopy(xml)
    object_element = xml.find('object')
    try:
      del object_element.attrib['gid']
    except KeyError:
      pass
    try:
      del object_element.attrib['id']
    except KeyError:
      pass
    object_element.attrib[attribute_name] = new_id
    if as_string:
      return etree.tostring(xml, encoding="utf-8")
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getXMLFromObjectWithId')
  def getXMLFromObjectWithId(self, object, xml_mapping, context_document=None): # pylint: disable=redefined-builtin
    """
      return the xml with Id of Object
    """
    xml = ''
    if xml_mapping is None:
      return xml
    func = getattr(object, xml_mapping, None)
    if func is not None:
      try:
        xml = func(context_document=context_document)
      except TypeError:
        # The method does not accept parameters
        xml = func()
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getXMLFromObjectWithGid')
  def getXMLFromObjectWithGid(self, object, gid, xml_mapping, as_string=True, context_document=None): # pylint: disable=redefined-builtin
    """
      return the xml with Gid of Object
    """
    xml_with_id = self.getXMLFromObjectWithId(object, xml_mapping, context_document=context_document)
    return self.replaceIdFromXML(xml_with_id, 'gid', gid, as_string=as_string)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getXMLFromObjectWithRid')
  def getXMLFromObjectWithRid(self, object, rid, xml_mapping, as_string=True, context_document=None): # pylint: disable=redefined-builtin
    """
      return the xml with Rid of Object
    """
    xml_id = self.getXMLFromObjectWithId(object, xml_mapping, context_document=context_document)
    xml_rid = self.replaceIdFromXML(xml_id, 'rid', rid, as_string=as_string)
    return xml_rid

  security.declareProtected(Permissions.AccessContentsInformation,'convertToXml')
  def convertToXml(self, xml):
    """
    if xml is a string, convert it to a node
    """
    if xml is None:
      return None
    if isinstance(xml, six.string_types + (bytes, )):
      if six.PY2 and isinstance(xml, six.text_type):
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

  security.declareProtected(Permissions.ModifyPortalContent, 'newObject')
  def newObject(self, object=None, xml=None, simulate=False, # pylint: disable=redefined-builtin
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
      if subnode.xpath('name()') not in NOT_EDITABLE_PROPERTY_LIST:
        keyword_type = self.getPropertyType(subnode)
        # This is the case where the property is a list
        keyword = subnode.xpath('name()')
        args[keyword] = self.convertXmlValue(subnode, keyword_type)
      elif subnode.xpath('local-name()') in ADDABLE_PROPERTY_LIST\
                                                           + (XML_OBJECT_TAG,):
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
  def afterNewObject(self, object): # pylint: disable=redefined-builtin
    """Overloadable method
    """

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
                                                       'getElementFromXupdate')
  def getElementFromXupdate(self, xml):
    """
    return a fragment node with applied xupdate
    This method simulate an xupdate transformation on given XML.
    It transform the xupdate into node handleable by Conduit
    """
    if xml.xpath('name()') == XUPDATE_ELEMENT:
      new_node = Element(xml.get('name'), nsmap=xml.nsmap)
      for subnode in xml.findall('{%s}attribute' % xml.nsmap['xupdate']):
        new_node.attrib.update({subnode.get('name'): subnode.text})
      ## Then dumps the xml and remove xupdate:attribute nodes
      new_node.extend(deepcopy(child) for child in\
                                 xml.xpath('*[name() != "xupdate:attribute"]'))
      new_node.text = xml.text
      new_node.tail = xml.tail
      return new_node
    if xml.xpath('name()') == XUPDATE_UPDATE:
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
      property_ = attribute[:s_place].strip('/')
      result += property_
      if select_id is not None:
        result += ' id=%s' % select_id
      result +=  '>'
      xml_string = self.nodeToString(xml)
      maxi = xml_string.find('>')+1
      result += xml_string[maxi:xml_string.find('</%s>' % xml.xpath('name()'))]
      result += '</%s>' % (property_)
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
    if xml.xpath('name()') == XUPDATE_ELEMENT:
      action_list.append(xml)
      return action_list
    # XXX not sure code bellow is still used ?
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
    if data_type == NONE_TYPE:
      return None
    data = node.text
    if data is not None and six.PY2 and isinstance(data, six.text_type):
      data = data.encode('utf-8')
    elif data is None and data_type in TEXT_TYPE_LIST:
      return ''
    # We can now convert string in tuple, dict, binary...
    if data_type in LIST_TYPE_LIST:
      data = unmarshaller(node[0])
    elif data_type in TEXT_TYPE_LIST:
      data = unescape(data)
    elif data_type == BOOLEAN_TYPE:
      if data == 'False':
        data = False
      elif data == 'True':
        data = True
      else:
        raise TypeError('Boolean type not expected:%r' % (data,))
    elif data_type in DATA_TYPE_LIST:
      if data is None:
        # data is splitted inside  block_data nodes
        data = b''.join([standard_b64decode(block.text) for\
                                                 block in node.iterchildren()])
    elif data_type == DATE_TYPE:
      data = DateTime(data)
    elif data_type == INT_TYPE :
      data = int(data)
    return data


  security.declareProtected(Permissions.ModifyPortalContent, 'applyXupdate')
  def applyXupdate(self, object=None, xupdate=None, previous_xml=None, **kw): # pylint: disable=redefined-builtin
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if isinstance(xupdate, six.string_types + (bytes, )):
      xupdate = etree.XML(xupdate, parser=parser)
    #LOG("applyXupdate", INFO, etree.tostring(xupdate, pretty_print=True))
    xupdate_builded = False
    xpath_expression_update_dict = {}
    for subnode in xupdate:
      original_xpath_expression = subnode.get('select', '')
      if not xupdate_builded and \
          MARSHALLER_NAMESPACE_URI in subnode.nsmap.values() \
          or 'block_data' in original_xpath_expression:
        # It means that the xpath expression is targetting
        # marshalled values or data nodes. We need to rebuild the original xml
        # in its own context in order to retrieve original value

        # We are insde a loop build the XUpdated tree only once
        xupdate_builded = True

        # Find the prefix used by marshaller.
        for prefix, namespace_uri in six.iteritems(subnode.nsmap):
          if namespace_uri == MARSHALLER_NAMESPACE_URI:
            break
        # TODO add support of etree objects for xuproc to avoid
        # serializing tree into string
        if isinstance(previous_xml, bytes):
          previous_xml = previous_xml.decode('utf-8')
        if not isinstance(previous_xml, six.text_type):
          previous_xml = etree.tostring(previous_xml, encoding='unicode')
        xupdated_tree = xuproc.applyXUpdate(xml_xu_string=etree.tostring(xupdate, encoding='unicode'),
                                            xml_doc_string=previous_xml)
      if MARSHALLER_NAMESPACE_URI in subnode.nsmap.values():
        xpath_expression = original_xpath_expression
        get_target_parent = subnode.xpath('name()') in XUPDATE_INSERT_LIST
        context = self.getContextFromXpath(object, xpath_expression,
                                           get_target_parent=get_target_parent)
        base_xpath_expression = xpath_expression\
                                            [:xpath_expression.index(prefix)-1]
        xupdated_node_list = xupdated_tree.xpath(base_xpath_expression)
        if xupdated_node_list:
          xupdated_node = xupdated_node_list[0]
        else:
          raise ValueError('Wrong xpath expression:%r' % base_xpath_expression)
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
        get_target_parent = subnode.xpath('name()') in XUPDATE_INSERT_LIST
        context = self.getContextFromXpath(object, xpath_expression,
                                           get_target_parent=get_target_parent)
        base_xpath_expression = xpath_expression\
                                            [:xpath_expression.index('block_data')-1]
        xupdated_node_list = xupdated_tree.xpath(base_xpath_expression)
        if xupdated_node_list:
          xupdated_node = xupdated_node_list[0]
        else:
          raise ValueError('Wrong xpath expression:%r' % base_xpath_expression)
        if base_xpath_expression not in xpath_expression_update_dict:
          xpath_expression_update_dict[base_xpath_expression] = \
                                   dict(xml=xupdated_node,
                                        object=context,
                                        xpath_expression=base_xpath_expression)
      elif subnode.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST:
        conflict_list += self.addNode(xml=subnode, object=object,
                                      previous_xml=previous_xml,
                                      **kw)['conflict_list']
      elif subnode.xpath('name()') == XUPDATE_DEL:
        conflict_list += self.deleteNode(xml=subnode, object=object,
                                         previous_xml=previous_xml, **kw)
      elif subnode.xpath('name()') == XUPDATE_UPDATE:
        conflict_list += self.updateNode(xml=subnode, object=object,
                                         previous_xml=previous_xml, **kw)

    # Now apply collected xupdated_node
    for update_dict in six.itervalues(xpath_expression_update_dict):
      update_dict.update(kw)
      conflict_list += self.updateNode(previous_xml=previous_xml,
                                       **update_dict)
    return conflict_list

  def isWorkflowActionAddable(self, document, status, wf_id):
    """
    Some checking in order to check if we should add the workfow or not
    We should not returns a conflict list as we wanted before, we should
    instead go to a conflict state.
    """
    # We first test if the status in not already inside the workflow_history
    wf_history = document.workflow_history
    if wf_id in wf_history:
      action_list = wf_history[wf_id]
    else:
      return WORKFLOW_ACTION_ADDABLE
    addable = WORKFLOW_ACTION_ADDABLE
    time = status.get('time')
    for action in action_list:
      this_one = WORKFLOW_ACTION_ADDABLE
      if time <= action.get('time'):
        # action in the past are not appended
        addable = WORKFLOW_ACTION_INSERTABLE
      key_list = list(action.keys())
      key_list.remove("time")
      for key in key_list:
        if status[key] != action[key]:
          this_one = WORKFLOW_ACTION_NOT_ADDABLE
          break
      if this_one:
        addable = WORKFLOW_ACTION_NOT_ADDABLE
        break
    return addable

  security.declareProtected(Permissions.ModifyPortalContent, 'constructContent')
  def constructContent(self, object, object_id, portal_type): # pylint: disable=redefined-builtin
    """
    This allows to specify how to construct a new content.
    This is really usefull if you want to write your
    own Conduit.
    """
    from zLOG import LOG
    LOG('ERP5Conduit.addNode',0,'portal_type: |%s|' % str(portal_type))
    subobject = object.newContent(portal_type=portal_type, id=object_id)
    return subobject, True, True

  security.declareProtected(Permissions.ModifyPortalContent, 'addWorkflowNode')
  def addWorkflowNode(self, object, xml, simulate): # pylint: disable=redefined-builtin
    """
    This allows to specify how to handle the workflow information.
    This is really usefull if you want to write your own Conduit.
    """
    conflict_list = []
    # We want to add a workflow action
    wf_tool = getToolByName(object.getPortalObject(), 'portal_workflow')
    wf_id = xml.get('workflow_id')
    if wf_id is None: # History added by xupdate
      wf_id = self.getHistoryIdFromSelect(xml)
      xml = xml[0]
    #for action in self.getWorkflowActionFromXml(xml):
    status = self.getStatusFromXml(xml)
    #LOG('addNode, status:',0,status)
    add_action = self.isWorkflowActionAddable(document=object,
                                              status=status,
                                              wf_id=wf_id,)
    if not simulate:
      if add_action == WORKFLOW_ACTION_ADDABLE:
        wf_tool.setStatusOf(wf_id, object, status)
      elif add_action == WORKFLOW_ACTION_INSERTABLE:
        wf_history_list = list(object.workflow_history[wf_id])
        for wf_history_index, wf_history in enumerate(wf_history_list):
          if wf_history['time'] > status['time']:
            wf_history_list.insert(wf_history_index, status)
            break

        object.workflow_history[wf_id] = tuple(wf_history_list)

    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'addLocalRoleNode')
  def addLocalRoleNode(self, object, xml): # pylint: disable=redefined-builtin
    """
    This allows to specify how to handle the local role information.
    This is really usefull if you want to write your own Conduit.
    """
    # We want to add a local role
    roles = self.convertXmlValue(xml, data_type='tokens')
    user = xml.get('id')
    #LOG('local_role: %s' % object.getPath(), INFO,
                                          #'user:%r | roles:%r' % (user, roles))
    #user = roles[0]
    #roles = roles[1:]
    if xml.xpath('local-name()') == LOCAL_ROLE_TAG:
      object.manage_setLocalRoles(user, roles)
    elif xml.xpath('local-name()') == LOCAL_GROUP_TAG:
      object.manage_setLocalGroupRoles(user, roles)

  security.declareProtected(Permissions.ModifyPortalContent, 'addLocalPermissionNode')
  def addLocalPermissionNode(self, object, xml): # pylint: disable=redefined-builtin
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
    if xml.xpath('local-name()') == LOCAL_PERMISSION_TAG:
      object.manage_setLocalPermissions(permission, roles)
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'editDocument')

  # XXX Ugly hack to avoid calling interaction workflow when synchronizing
  # objects with ERP5SyncML as it leads to unwanted side-effects on the object
  # being synchronized, such as undesirable workflow history being added (for
  # example edit_workflow) and double conversion for OOo documents (for
  # example document_conversion_interaction_workflow defined for _setData())
  # making the source and destination XML representation different.
  @WorkflowMethod.disable
  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """
    This is the default editDocument method. This method
    can easily be overwritten.
    """
    syncml_logger.debug("editing document %s with %s", object, kw)
    object._edit(**kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'getProperty')
  def getProperty(self, object, kw): # pylint: disable=redefined-builtin
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

  def getGidFromObject(self, object): # pylint: disable=redefined-builtin
    """
    return the Gid composed with the object informations
    """
    return object.getId()

  def _createContent(self, xml=None, object=None, object_id=None, # pylint: disable=redefined-builtin
                     sub_object=None, reset_local_roles=False,
                     reset_workflow=False, simulate=False, **kw):
    """
      This is the method calling to create an object
    """
    # XXX We can not find an object with remote id
    if object_id is None:
      # XXX object must be retrieved by their GID, id must not be synchronised
      # This hack is wrong, unfortunately all units are based on it so I can
      # not remove it, all must be reviewed before
      object_id = xml.get('id')
    if object_id is not None:
      if sub_object is None:
        sub_object = object._getOb(object_id, None)
    if sub_object is None: # If so, it doesn't exist
      portal_type = ''
      if xml.xpath('local-name()') == XML_OBJECT_TAG:
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

  def _updateContent(self, object=None, **args): # pylint: disable=redefined-builtin
    """
      This is the method for update the object
    """
    return self.editDocument(object=object, **args)

  def _deleteContent(self, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """
      This is the method for delete the object
    """
    return self.deleteObject(object, object_id, **kw)

  def getContentType(self):
    """Content-Type of binded data
    """
    return 'text/xml'

  def generateDiff(self, new_data, former_data):
    """return xupdate node
    """
    return getXupdateObject(new_data, former_data)

  def applyDiff(self, original_data, diff):
    """Use xuproc for computing patched content
    """
    # XXX xuproc does not support passing
    # etree objetcs
    if isinstance(diff, bytes):
      diff = diff.decode('utf-8')
    elif not isinstance(diff, basestring):
      diff = etree.tostring(diff, encoding='unicode')
    if not isinstance(original_data, six.text_type):
      original_data = six.text_type(original_data, 'utf-8')
    return etree.tostring(xuproc.applyXUpdate(xml_xu_string=diff,
                                              xml_doc_string=original_data),
                                              encoding='utf-8')

#  def getGidFromXML(self, xml, namespace, gid_from_xml_list):
#    """
#    return the Gid composed with xml informations
#    """
#    gid = xml.xpath('string(.//syncml:id)')
#    if gid in gid_from_xml_list or gid == ' ':
#      return False
#    return gid
