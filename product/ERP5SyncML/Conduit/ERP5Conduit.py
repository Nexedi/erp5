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
from Products.ERP5SyncML.Subscription import Conflict
from Products.CMFCore.utils import getToolByName
from Products.ERP5SyncML.XMLSyncUtils import Parse
from DateTime.DateTime import DateTime
from email.MIMEBase import MIMEBase
from email import Encoders
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, Interface
from Globals import PersistentMapping
import pickle
from cStringIO import StringIO
from xml.sax.saxutils import escape, unescape
import re
import cStringIO
from zLOG import LOG, INFO, DEBUG
try:
  from Ft.Xml.Domlette import Print, PrettyPrint
except ImportError:
  LOG('ERP5Conduit',0,"Can't import Print and PrettyPrint")
  class Print:
    def __init__(self, *args, **kw):
      raise ImportError, "Sorry, it was not possible to import Ft library"

  class PrettyPrint:
    def __init__(self, *args, **kw):
      raise ImportError, "Sorry, it was not possible to import Ft library"


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
  __implements__ = ( Interface.IConduit, )

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
  def addNode(self, xml=None, object=None, previous_xml=None,
              object_id=None, sub_object=None, force=0, simulate=0, **kw):
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
    reset_local_roles = 1
    reset_workflow = 1
    conflict_list = []
    xml = self.convertToXml(xml)
    if xml is None:
      return {'conflict_list':conflict_list, 'object':sub_object}
    # In the case where this new node is a object to add
    if xml.nodeName in self.XUPDATE_INSERT_OR_ADD and \
        self.getSubObjectDepth(xml)==0:
      if self.isHistoryAdd(xml)!=-1: # bad hack XXX to be removed
        for element in self.getXupdateElementList(xml):
          xml = self.getElementFromXupdate(element)
          conflict_list += self.addNode(xml=xml,object=object,
                          previous_xml=previous_xml, force=force,
                          simulate=simulate, **kw)['conflict_list']
    elif xml.nodeName == 'object':
      if object_id is None:
        object_id = self.getAttribute(xml,'id')
      docid = self.getObjectDocid(xml)
      if object_id is not None:
        if sub_object is None:
          try:
            sub_object = object._getOb(object_id)
          except (AttributeError, KeyError, TypeError):
            sub_object = None
        else:
          #We prevent reset_workflow an reset_local_roles
          reset_local_roles = 0
          reset_workflow = 0
        if sub_object is None: # If so, it doesn't exist
          portal_type = ''
          if xml.nodeName == 'object':
            portal_type = self.getObjectType(xml)
          elif xml.nodeName in self.XUPDATE_INSERT_OR_ADD: # Deprecated ???
            portal_type = self.getXupdateObjectType(xml) # Deprecated ???
          sub_object = self.constructContent(object, object_id, docid, 
              portal_type)
        self.newObject(
                  object=sub_object,
                  xml=xml,
                  simulate=simulate,
                  reset_local_roles=reset_local_roles,
                  reset_workflow=reset_workflow)
    elif xml.nodeName in self.XUPDATE_INSERT_OR_ADD \
         and self.getSubObjectDepth(xml)>=1:
      sub_object_id = self.getSubObjectId(xml)
      if previous_xml is not None and sub_object_id is not None:
        # Find the previous xml corresponding to this subobject
        sub_previous_xml = self.getSubObjectXml(sub_object_id, previous_xml)
        LOG('addNode', DEBUG,'isSubObjectModification sub_previous_xml: %s' % str(sub_previous_xml))
        if sub_previous_xml is not None:
          sub_object = None
          try:
            sub_object = object._getOb(sub_object_id)
          except (AttributeError, KeyError, TypeError):
            pass
          if sub_object is not None:
            LOG('addNode', DEBUG, 'subobject.id: %s' % sub_object.id)
            # Change the xml in order to directly apply
            # modifications to the subobject
            sub_xml = self.getSubObjectXupdate(xml)
            LOG('addNode', DEBUG, 'sub_xml: %s' % str(sub_xml))
            # Then do the udpate
            conflict_list += self.addNode(xml=sub_xml,object=sub_object,
                            previous_xml=sub_previous_xml, force=force,
                            simulate=simulate, **kw)['conflict_list']
    elif xml.nodeName == self.history_tag or self.isHistoryAdd(xml)>0:
      conflict_list += self.addWorkflowNode(object, xml, simulate)
    #elif xml.nodeName in self.local_role_list or self.isLocalRole(xml)>0 and not simulate:
    elif xml.nodeName in self.local_role_list:
      conflict_list += self.addLocalRoleNode(object, xml)
    elif xml.nodeName in self.local_permission_list:
      conflict_list += self.addLocalPermissionNode(object, xml)
    else:
      conflict_list += self.updateNode(xml=xml,object=object, force=force,
                                       simulate=simulate,  **kw)
    # We must returns the object created
    return {'conflict_list':conflict_list, 'object': sub_object}

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteNode')
  def deleteNode(self, xml=None, object=None, object_id=None, force=None,
                 simulate=0, **kw):
    """
    A node is deleted
    """
    # In the case where we have to delete an object
    LOG('ERP5Conduit.deleteNode', DEBUG, 'deleteNode, object path: %s' % repr(object.getPhysicalPath()))
    conflict_list = []
    if xml is not None:
      xml = self.convertToXml(xml)
    if object_id is None:
      LOG('ERP5Conduit.deleteNode', DEBUG, 'deleteNode, SubObjectDepth: %i' % self.getSubObjectDepth(xml))
      if xml.nodeName == self.xml_object_tag:
        object_id = self.getAttribute(xml,'id')
      elif self.getSubObjectDepth(xml)==1:
        object_id = self.getSubObjectId(xml)
      elif self.getSubObjectDepth(xml)==2:
        # we have to call delete node on a subsubobject
        sub_object_id = self.getSubObjectId(xml)
        try:
          sub_object = object._getOb(sub_object_id)
          sub_xml = self.getSubObjectXupdate(xml)
          conflict_list += self.deleteNode(xml=sub_xml,object=sub_object,
                                       force=force, simulate=simulate, **kw)
        except (KeyError, AttributeError, TypeError):
          LOG('ERP5Conduit.deleteNode', DEBUG, 'deleteNode, Unable to delete SubObject: %s' % str(sub_object_id))
          pass
    if object_id is not None: # We do have an object_id
      self.deleteObject(object, object_id)
    # In the case where we have to delete an user role
    # If we are still there, this means the delete is for this node
    elif xml.nodeName in self.XUPDATE_DEL:
      xml = self.getElementFromXupdate(xml)
      if xml.nodeName in self.local_role_list and not simulate:
        # We want to del a local role
        user = self.getAttribute(xml,'id')
        LOG('ERP5Conduit.deleteNode local_role: ', DEBUG, 'user: %s' % repr(user))
        if xml.nodeName.find(self.local_role_tag)>=0:
          object.manage_delLocalRoles([user])
        elif xml.nodeName.find(self.local_group_tag)>=0:
          object.manage_delLocalGroupRoles([user])
      if xml.nodeName in self.local_permission_list and not simulate:
        permission = self.getAttribute(xml,'id')
        object.manage_setLocalPermissions(permission)
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'deleteObject')
  def deleteObject(self, object, object_id):
    try:
      object._delObject(object_id)
    except (AttributeError, KeyError):
      LOG('ERP5Conduit.deleteObject', DEBUG, 'Unable to delete: %s' % str(object_id))
      pass

  security.declareProtected(Permissions.ModifyPortalContent, 'updateNode')
  def updateNode(self, xml=None, object=None, previous_xml=None, force=0,
                 simulate=0,  **kw):
    """
    A node is updated with some xupdate
      - xml : the xml corresponding to the update, it should be xupdate
      - object : the object on wich we want to apply the xupdate
      - [previous_xml] : the previous xml of the object, it is mandatory
                         when we have sub objects
    """
    conflict_list = []
    xml = self.convertToXml(xml)
    LOG('ERP5Conduit.updateNode', DEBUG, 'xml.nodeName: %s' % xml.nodeName)
    LOG('ERP5Conduit.updateNode, force: ', DEBUG, force)
    # we have an xupdate xml
    if xml.nodeName == 'xupdate:modifications':
      conflict_list += self.applyXupdate(object=object, xupdate=xml, 
          conduit=self,previous_xml=previous_xml, force=force, 
          simulate=simulate, **kw)
    # we may have only the part of an xupdate
    else:
      args = {}
      if self.isProperty(xml) and not(self.isSubObjectModification(xml)):
        keyword = None
        for subnode in self.getAttributeNodeList(xml):
          if subnode.nodeName=='select':
            select_list = subnode.nodeValue.split('/') # Something like:
                                                       #('','object[1]','sid[1]')
            new_select_list = ()
            for select_item in select_list:
              if select_item.find('[')>=0:
                select_item = select_item[:select_item.find('[')]
              new_select_list += (select_item,)
            select_list = new_select_list # Something like : ('','object','sid')
            keyword = select_list[len(select_list)-1] # this will be 'sid'
        data_xml = xml
        data = None
        if xml.nodeName not in self.XUPDATE_INSERT_OR_ADD:
          for subnode in self.getElementNodeList(xml):
            if subnode.nodeName=='xupdate:element':
              for subnode1 in subnode.attributes:
                if subnode1.nodeName=='name':
                  keyword = subnode1.nodeValue
              data_xml = subnode
        else:
          #We can call add node
          conflict_list += self.addNode(xml=xml,
                                        object=object,
                                        force=force,
                                        simulate=simulate,
                                        **kw)
          return conflict_list

        if xml.nodeName in self.XUPDATE_DEL:
          conflict_list += self.deleteNode(xml=xml,
                                           object=object,
                                           force=force,
                                           simulate=simulate,
                                           **kw)
          return conflict_list
        if keyword is None: # This is not a selection, directly the property
          keyword = xml.nodeName
        if len(self.getElementNodeList(data_xml))==0:
          try:
            data = data_xml.childNodes[0].data
          except IndexError: # There is no data
            data = None
        if not (keyword in self.NOT_EDITABLE_PROPERTY):
          # We will look for the data to enter
          data_type = object.getPropertyType(keyword)
          LOG('ERP5Conduit.updateNode', DEBUG, 'data_type: %s for keyword: %s' % (str(data_type), keyword))
          data = self.convertXmlValue(data,data_type=data_type)
          args[keyword] = data
          args = self.getFormatedArgs(args=args)
          # This is the place where we should look for conflicts
          # For that we need :
          #   - data : the data from the remote box
          #   - old_data : the data from this box but at the time of the i
          #last synchronization
          #   - current_data : the data actually on this box
          isConflict = 0
          if (previous_xml is not None) and (not force): 
          # if no previous_xml, no conflict
            old_data = self.getObjectProperty(keyword, previous_xml, 
                data_type=data_type)
            #current_data = object.getProperty(keyword)
            current_data = self.getProperty(object, keyword)
            LOG('ERP5Conduit.updateNode', DEBUG, 'Conflict data: %s' % str(data))
            LOG('ERP5Conduit.updateNode', DEBUG, 'Conflict old_data: %s' % str(old_data))
            LOG('ERP5Conduit.updateNode', DEBUG, 'Conflict current_data: %s' % str(current_data))
            if (old_data != current_data) and (data != current_data) \
                and keyword not in self.force_conflict_list:
              LOG('ERP5Conduit.updateNode', DEBUG, 'Conflict on : %s' % keyword)
              # Hack in order to get the synchronization working for demo
              # XXX this have to be removed after
              #if not (data_type in self.binary_type_list):
              if 1:
                # This is a conflict
                isConflict = 1
                string_io = StringIO()
                PrettyPrint(xml,stream=string_io)
                conflict = Conflict(object_path=object.getPhysicalPath(),
                                    keyword=keyword)
                conflict.setXupdate(string_io.getvalue())
                if not (data_type in self.binary_type_list):
                  conflict.setLocalValue(current_data)
                  conflict.setRemoteValue(data)
                conflict_list += [conflict]
          # We will now apply the argument with the method edit
          if args != {} and (isConflict==0 or force) and (not simulate):
            self.editDocument(object=object,**args)
            # It is sometimes required to do something after an edit
            if hasattr(object,'manage_afterEdit'):
              object.manage_afterEdit()

        if keyword == 'object':
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=xml, object=object, force=force, 
              simulate=simulate, **kw)['conflict_list']
        elif keyword == self.history_tag and not simulate:
          # This is the case where we have to call addNode
          conflict_list += self.addNode(xml=subnode,object=object,force=force,
              simulate=simulate,**kw)['conflict_list']
        elif keyword in (self.local_role_tag, self.local_permission_tag) and not simulate:
          # This is the case where we have to update Roles or update permission
          #LOG('ERP5Conduit.updateNode', DEBUG, 'we will add a local role')
          #user = self.getSubObjectId(xml)
          #roles = self.convertXmlValue(data,data_type='tokens')
          #object.manage_setLocalRoles(user,roles)
          xml = self.getElementFromXupdate(xml)
          conflict_list += self.addNode(xml=xml, object=object, force=force, 
              simulate=simulate,**kw)['conflict_list']
      elif self.isSubObjectModification(xml):
        # We should find the object corresponding to
        # this update, so we have to look in the previous_xml
        sub_object_id = self.getSubObjectId(xml)
        LOG('ERP5Conduit.updateNode', DEBUG,'isSubObjectModification sub_object_id: %s' % sub_object_id)
        if previous_xml is not None and sub_object_id is not None:
          sub_previous_xml = self.getSubObjectXml(sub_object_id,previous_xml)
          LOG('ERP5Conduit.updateNode', DEBUG, 'isSubObjectModification sub_previous_xml: %s' % str(sub_previous_xml))
          if sub_previous_xml is not None:
            sub_object = None
            try:
              sub_object = object[sub_object_id]
            except KeyError:
              pass
            if sub_object is not None:
              LOG('ERP5Conduit.updateNode', DEBUG, 'subobject.id: %s' % sub_object.id)
              # Change the xml in order to directly apply
              # modifications to the subobject
              sub_xml = self.getSubObjectXupdate(xml)
              LOG('ERP5Conduit.updateNode', DEBUG, 'sub_xml: %s' % str(sub_xml))
              # Then do the udpate
              conflict_list += self.updateNode(xml=sub_xml, object=sub_object, 
                  force=force, previous_xml=sub_previous_xml, 
                  simulate=simulate, **kw)
        elif previous_xml is None and xml is not None and sub_object_id is not None:
          sub_object = None
          try:
            sub_object = object[sub_object_id]
          except KeyError:
            pass
          if sub_object is not None:
            sub_xml = self.getSubObjectXupdate(xml)
            conflict_list += self.updateNode(xml=sub_xml,
                                             object=sub_object,
                                             force=force,
                                             simulate=simulate,
                                             **kw)
        elif previous_xml is None and xml is not None and sub_object_id is not None:
          sub_object = None
          try:
            sub_object = object[sub_object_id]
          except KeyError:
            pass
          if sub_object is not None:
            sub_xml = self.getSubObjectXupdate(xml)
            conflict_list += self.updateNode(xml=sub_xml,
                                             object=sub_object,
                                             force=force,
                                             simulate=simulate,
                                             **kw)
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
      if type(keyword) is type(u"a"):
        keyword = keyword.encode(self.getEncoding())
      if type(data) is type([]) or type(data) is type(()):
        new_data = []
        for item in data:
          if type(item) is type(u"a"):
            item = item.encode(self.getEncoding())
            item = item.replace('@@@','\n')
          new_data += [item]
        data = new_data
      if type(data) is type(u"a"):
        data = data.encode(self.getEncoding())
        data = data.replace('@@@','\n')
      if keyword == 'binary_data':
        LOG('ERP5Conduit.getFormatedArgs', DEBUG, 'binary_data keyword: %s' % str(keyword))
        msg = MIMEBase('application','octet-stream')
        Encoders.encode_base64(msg)
        msg.set_payload(data)
        data = msg.get_payload(decode=1)
      new_args[keyword] = data
    return new_args

  security.declareProtected(Permissions.AccessContentsInformation,'isProperty')
  def isProperty(self, xml):
    """
    Check if it is a simple property
    """
    bad_list = (self.sub_object_exp,self.history_exp)
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        for bad_string in bad_list:
          if re.search(bad_string,value) is not None:
            return 0
    return 1

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubObjectXupdate')
  def getSubObjectXupdate(self, xml):
    """
    This will change the xml in order to change the update
    from the object to the subobject
    """
    xml_copy = xml.cloneNode(True) #make a deepcopy of the node xml
    for subnode in self.getAttributeNodeList(xml_copy):
      if subnode.nodeName=='select':
        subnode.nodeValue = self.getSubObjectSelect(subnode.nodeValue)
    return xml_copy

  security.declareProtected(Permissions.AccessContentsInformation, 
      'isHistoryAdd')
  def isHistoryAdd(self, xml):
    bad_list = (self.history_exp,)
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        for bad_string in bad_list:
          if re.search(bad_string,value) is not None:
            if re.search(self.bad_history_exp,value) is None:
              return 1
            else:
              return -1
    return 0

  security.declareProtected(Permissions.AccessContentsInformation, 
      'isSubObjectModification')
  def isSubObjectModification(self, xml):
    """
    Check if it is a modification from an subobject
    """
    good_list = (self.sub_object_exp,)
    for subnode in self.getAttributeNodeList(xml) :
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        for good_string in good_list:
          if re.search(good_string,value) is not None:
            return 1
    return 0

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubObjectDepth')
  def getSubObjectDepth(self, xml):
    """
    Give the Depth of a subobject modification
    0 means, no depth
    1 means it is a subobject
    2 means it is more depth than subobject
    """
    #LOG('getSubObjectDepth',0,'xml.nodeName: %s' % xml.nodeName)
    if xml.nodeName in self.XUPDATE_TAG:
      i = 0
      if xml.nodeName in self.XUPDATE_INSERT:
        i = 1
      #LOG('getSubObjectDepth',0,'xml2.nodeName: %s' % xml.nodeName)
      for subnode in self.getAttributeNodeList(xml):
        #LOG('getSubObjectDepth',0,'subnode.nodeName: %s' % subnode.nodeName)
        if subnode.nodeName == 'select':
          value = subnode.nodeValue
          #LOG('getSubObjectDepth',0,'subnode.nodeValue: %s' % subnode.nodeValue)
          if re.search(self.sub_sub_object_exp,value) is not None:
            return 2 # This is sure in all cases
          elif re.search(self.sub_object_exp,value) is not None:
            #new_select = self.getSubObjectSelect(value) # Still needed ???
            #if self.getSubObjectSelect(new_select) != new_select:
            #  return (2 - i)
            #return (1 - i)
            return (2 - i)
          elif re.search(self.object_exp,value) is not None:
            return (1 - i)
    return 0

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubObjectSelect')
  def getSubObjectSelect(self, select):
    """
    Return a string wich is the selection for the subobject
    ex: for "/object[@id='161']/object[@id='default_address']/street_address"
    it returns "/object[@id='default_address']/street_address"
    """
    if re.search(self.object_exp,select) is not None:
      s = '/'
      if re.search('/.*/',select) is not None: # This means we have more than just object
        new_value = select[select.find(s,select.find(s)+1):]
      else:
        new_value = '/'
      select = new_value
    return select

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubObjectId')
  def getSubObjectId(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        if re.search(self.object_exp,value) is not None:
          s = "'"
          first = value.find(s)+1
          object_id = value[first:value.find(s,first)]
          return object_id
    return object_id

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getHistoryIdFromSelect')
  def getHistoryIdFromSelect(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        if re.search(self.history_exp,value) is not None:
          s = self.history_tag
          object_id = value[value.find(s):]
          object_id = object_id[object_id.find("'")+1:]
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
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName==self.xml_object_tag:
        if object_id == self.getAttribute(subnode,'id'):
          return subnode
    return None

  security.declareProtected(Permissions.AccessContentsInformation,'getAttribute')
  def getAttribute(self, xml, param):
    """
    Retrieve the given parameter from the xml
    """
    for attribute in self.getAttributeNodeList(xml):
      if attribute.nodeName == param:
        data = attribute.value
        return self.convertXmlValue(data,data_type='string')
    return None

  security.declareProtected(Permissions.AccessContentsInformation,'getObjectDocid')
  def getObjectDocid(self, xml):
    """
    Retrieve the docid
    """
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'docid':
        data = subnode.childNodes[0].value
        return self.convertXmlValue(data)
    return None

  security.declareProtected(Permissions.AccessContentsInformation,'getObjectProperty')
  def getObjectProperty(self, property, xml, data_type=None):
    """
    Retrieve the given property
    """
    xml = self.convertToXml(xml)
    # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == property:
        if data_type is None:
          data_type = self.getPropertyType(subnode)
        try:
          data = subnode.childNodes[0].data
        except IndexError: # There is no data
          data = None
        data =  self.convertXmlValue(data, data_type=data_type)
        return data
    return None

  security.declareProtected(Permissions.AccessContentsInformation,'convertToXml')
  def convertToXml(self,xml):
    """
    if xml is a string, convert it to a node
    """
    if xml is None:
      return
    if type(xml) in (type('a'),type(u'a')):
      if type(xml) is type(u'a'):
        xml = xml.encode('utf-8')
      xml = Parse(xml)
      #LOG('Conduit.convertToXml not failed',0,'ok')
      xml = xml.childNodes[0] # Because we just created a new xml
    # If we have the xml from the node erp5, we just take the subnode
    if xml.nodeName=='erp5':
      xml = self.getElementNodeList(xml)[0]
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,'getObjectType')
  def getObjectType(self, xml):
    """
    Retrieve the portal type from an xml
    """
    portal_type = None
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='portal_type':
        portal_type = subnode.nodeValue
        portal_type = self.convertXmlValue(portal_type)
        return portal_type
    return portal_type

  security.declareProtected(Permissions.AccessContentsInformation,'getPropertyType')
  def getPropertyType(self, xml):
    """
    Retrieve the portal type from an xml
    """
    p_type = None # use getElementsByTagName !!!! XXX
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='type':
        p_type = subnode.nodeValue
        p_type = self.convertXmlValue(p_type,data_type='string')
        return p_type
    return p_type

  security.declareProtected(Permissions.AccessContentsInformation,'getXupdateObjectType')
  def getXupdateObjectType(self, xml):
    """
    Retrieve the portal type from an xupdate
    XXXX  This should not be used any more !!! XXXXXXXXXXX
    """
    if xml.nodeName.find('xupdate')>=0:
      for subnode in self.getElementNodeList(xml):
        if subnode.nodeName == 'xupdate:element':
          for subnode1 in self.getElementNodeList(subnode):
            if subnode1.nodeName == 'xupdate:attribute':
              for attribute in subnode1.attributes:
                if attribute.nodeName == 'name':
                  if attribute.nodeValue == 'portal_type':
                    data = subnode1.childNodes[0].data
                    data = self.convertXmlValue(data)
                    return data
    return None


  security.declareProtected(Permissions.ModifyPortalContent, 'newObject')
  def newObject(self, object=None, xml=None, simulate=0, reset_local_roles=1, reset_workflow=1):
    """
      modify the object with datas from
      the xml (action section)
    """
    args = {}
    if simulate:
      return
    # Retrieve the list of users with a role and delete default roles
    if reset_local_roles:
      user_role_list = map(lambda x:x[0],object.get_local_roles())
      object.manage_delLocalRoles(user_role_list)
    if hasattr(object,'workflow_history') and reset_workflow:
      object.workflow_history = PersistentMapping()
    if xml.nodeName.find('xupdate')>= 0:
      xml = self.getElementNodeList(xml)[0]
    for subnode in self.getElementNodeList(xml):
      if not(subnode.nodeName in self.NOT_EDITABLE_PROPERTY):
        keyword_type = self.getPropertyType(subnode)
        # This is the case where the property is a list
        keyword=str(subnode.nodeName)
        if len(subnode.childNodes) > 0: # We check that this tag is not empty
          data = subnode.childNodes[0].data
          args[keyword]=data
        #if args.has_key(keyword):
        #  LOG('newObject',0,'data: %s' % str(args[keyword]))
        if args.has_key(keyword):
          args[keyword] = self.convertXmlValue(args[keyword],keyword_type)
      elif subnode.nodeName in self.ADDABLE_PROPERTY:
        self.addNode(object=object,xml=subnode, force=1)
    # We should first edit the object
    args = self.getFormatedArgs(args=args)
    # edit the object with a dictionnary of arguments,
    # like {"telephone_number":"02-5648"}
    self.editDocument(object=object,**args)
    if hasattr(object,'manage_afterEdit'):
      object.manage_afterEdit()
    self.afterNewObject(object = object)

    # Then we may create subobject
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName in (self.xml_object_tag,): #,self.history_tag):
        self.addNode(object=object,xml=subnode)

  security.declareProtected(Permissions.AccessContentsInformation,'afterNewObject')
  def afterNewObject(self, object):
    pass

  security.declareProtected(Permissions.AccessContentsInformation,'getStatusFromXml')
  def getStatusFromXml(self, xml):
    """
    Return a worklow status from xml
    """
    status = {}
    for subnode in self.getElementNodeList(xml):
      keyword = self.convertXmlValue(subnode.nodeName)
      value = self.getObjectProperty(keyword,xml)
      status[keyword] = value
    return status

  security.declareProtected(Permissions.AccessContentsInformation,'getXupdateElementList')
  def getXupdateElementList(self, xml):
    """
    Retrieve the list of xupdate:element subnodes
    """
    e_list = []
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName in self.XUPDATE_EL:
        e_list += [subnode]
    #LOG('getXupdateElementList, e_list:',0,e_list)
    return e_list

  security.declareProtected(Permissions.AccessContentsInformation,'getElementFromXupdate')
  def getElementFromXupdate(self, xml):
    """
    from a xupdate:element returns the element as xml
    """
    if xml.nodeName in self.XUPDATE_EL:
      result = unicode('<',encoding='utf-8')
      result += xml.attributes.values()[0].nodeValue
      for subnode in self.getElementNodeList(xml):  #getElementNodeList
        if subnode.nodeName == 'xupdate:attribute':
          result += ' ' + subnode.attributes.values()[0].nodeValue + '='
          result += '"' + subnode.childNodes[0].nodeValue + '"'
      result += '>'
      # Then dumps the xml and remove what we does'nt want
      #xml_string = StringIO()
      #PrettyPrint(xml,xml_string)
      #xml_string = xml_string.getvalue()
      #xml_string = unicode(xml_string,encoding='utf-8')
      xml_string = self.nodeToString(xml)
      xml_string = unicode(xml_string,encoding='utf-8')
      #if type(xml_string) is type (u'a'):
      #  xml_string = xml_string.encode('utf-8')
      maxi = max(xml_string.find('>')+1,\
                 xml_string.rfind('</xupdate:attribute>')+len('</xupdate:attribute>'))
      result += xml_string[maxi:xml_string.find('</xupdate:element>')]
      result += '</' + xml.attributes.values()[0].nodeValue + '>'
      return self.convertToXml(result.encode('utf-8'))
    if xml.nodeName in (self.XUPDATE_UPDATE+self.XUPDATE_DEL):
      result = u'<'
      for subnode in self.getAttributeNodeList(xml):
        if subnode.nodeName == 'select':
          attribute = subnode.nodeValue
      s = '[@id='
      s_place = attribute.find(s)
      select_id = None
      if (s_place > 0):
        select_id = attribute[s_place+len(s):]
        select_id = select_id[:select_id.find("'",1)+1]
      else:
        s_place = len(attribute)
      property = attribute[:s_place]
      if property.find('/')==0:
        property = property[1:]
      result += property
      if select_id is not None:
        result += ' id=%s' % select_id
      result +=  '>'
      xml_string = self.nodeToString(xml)
      xml_string = unicode(xml_string,encoding='utf-8')
      maxi = xml_string.find('>')+1
      result += xml_string[maxi:xml_string.find('</%s>' % xml.nodeName)]
      result += '</' + property + '>'
      #LOG('getElementFromXupdate, result:',0,repr(result))
      return self.convertToXml(result)
    return xml

  security.declareProtected(Permissions.AccessContentsInformation,'getWorkflowActionFromXml')
  def getWorkflowActionFromXml(self, xml):
    """
    Return the list of workflow actions
    """
    action_list = []
    if xml.nodeName in self.XUPDATE_EL:
      action_list += [xml]
      return action_list
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == self.action_tag:
        action_list += [subnode]
    return action_list

  security.declareProtected(Permissions.AccessContentsInformation,'convertXmlValue')
  def convertXmlValue(self, data, data_type=None):
    """
    It is possible that the xml change the value, for example
    there is some too much '\n' and some spaces. We have to do some extra
    things so that we convert correctly the vlalue
    """
    if data is None:
      if data_type in self.list_type_list:
        data = ()
      if data_type in self.text_type_list:
        data = ''
      return data
    data = data.replace('\n','')
    if type(data) is type(u"a"):
      data = data.encode(self.getEncoding())
    if data=='None':
      return None
    # We can now convert string in tuple, dict, binary...
    if data_type in self.list_type_list:
      if type(data) is type('a'):
        data = tuple(data.split('@@@'))
    elif data_type in self.text_type_list:
      data = data.replace('@@@','\n')
#     elif data_type in self.binary_type_list:
#       data = data.replace('@@@','\n')
#       msg = MIMEBase('application','octet-stream')
#       Encoders.encode_base64(msg)
#       msg.set_payload(data)
#       data = msg.get_payload(decode=1)
      data = unescape(data)
    elif data_type in self.pickle_type_list:
      data = data.replace('@@@','\n')
      msg = MIMEBase('application','octet-stream')
      Encoders.encode_base64(msg)
      msg.set_payload(data)
      data = msg.get_payload(decode=1)
      data = pickle.loads(data)
    elif data_type in self.date_type_list:
      data = DateTime(data)
    elif data_type in self.int_type_list:
      data = int(data)
    elif data_type in self.dict_type_list: # only usefull for CPS, with data = '{fr:1}'
      if data == '{}':
        data = {}
      else:
        dict_list = map(lambda x:x.split(':'),data[1:-1].split(','))
        data = map(lambda (x,y):(x.replace(' ','').replace("'",''),int(y)),dict_list)
        data = dict(data)
    return data

  # XXX is it the right place ? It should be in XupdateUtils, but here we
  # have some specific things to do
  security.declareProtected(Permissions.ModifyPortalContent, 'applyXupdate')
  def applyXupdate(self, object=None, xupdate=None, conduit=None, force=0,
                   simulate=0, **kw):
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if type(xupdate) in (type('a'),type(u'a')):
      xupdate = Parse(xupdate)
    #When xupdate mix different object, (like object and his subobject) we need to treat them separatly
    if self.isMixedXupdate(xupdate):
      #return to updateNode with only one line
      #del all sub_element
      sub_node_list = self.getElementNodeList(xupdate)
      #clean the node
      for subnode in sub_node_list:
        #Create one xupdate:modification per update node
        conflict_list += self.updateNode(xml=subnode,
                                         object=object,
                                         force=force,
                                         simulate=simulate,
                                         **kw)
      return conflict_list
    for subnode in self.getElementNodeList(xupdate):
      sub_xupdate = self.getSubObjectXupdate(subnode)
      selection_name = ''
      if subnode.nodeName in self.XUPDATE_INSERT_OR_ADD:
        conflict_list += conduit.addNode(xml=sub_xupdate,object=object, \
                                         force=force, simulate=simulate, **kw)['conflict_list']
      elif subnode.nodeName in self.XUPDATE_DEL:
        conflict_list += conduit.deleteNode(xml=sub_xupdate, object=object, \
                                      force=force, simulate=simulate, **kw)
      elif subnode.nodeName in self.XUPDATE_UPDATE:
        conflict_list += conduit.updateNode(xml=sub_xupdate, object=object, \
                                         force=force, simulate=simulate, **kw)
      #elif subnode.nodeName in self.XUPDATE_INSERT:
      #  conflict_list += conduit.addNode(xml=subnode, object=object, force=force, **kw)

    return conflict_list

  def isMixedXupdate(self, xml):
    #If an xupdate:modifications contains modification which concerns different objects
    subnode_list = self.getElementNodeList(xml)
    nb_sub = len(subnode_list)
    comp = 0
    for subnode in subnode_list:
      value = self.getAttribute(subnode, 'select')
      if re.search(self.object_exp, value):
        comp += 1
    if nb_sub == comp:
      return 0
    return 1

  def isWorkflowActionAddable(self, object=None,status=None,wf_tool=None,
                              wf_id=None,xml=None):
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
    addable = 1
    for action in action_list:
      this_one = 1
      for key in action.keys():
        if status[key] != action[key]:
          this_one = 0
          break
      if this_one:
        addable = 0
        break
    return addable

  security.declareProtected(Permissions.ModifyPortalContent, 'constructContent')
  def constructContent(self, object, object_id, docid, portal_type):
    """
    This allows to specify how to construct a new content.
    This is really usefull if you want to write your
    own Conduit.
    """
    portal_types = getToolByName(object,'portal_types')
    #LOG('ERP5Conduit.addNode',0,'portal_type: |%s|' % str(portal_type))
    if docid==None: # ERP5 content
      object.newContent(portal_type=portal_type,id=object_id)
    else: # CPS content
      # This is specific to CPS, we will call the proxy tool
      px_tool= getToolByName(object,'portal_proxies')
      trees_tool= getToolByName(object,'portal_trees')
      proxy_type = 'document'
      if portal_type in ('Workspace','Section'):
        proxy_type = 'folder'
      proxy = px_tool.createEmptyProxy(proxy_type,
                                object,portal_type,object_id,docid=docid)
      proxy.isIndexable = 0 # So it will not be reindexed, this prevent errors
      # Calculate rpath
      utool = getToolByName(object, 'portal_url')
      rpath = utool.getRelativeUrl(proxy)
      px_tool._modifyProxy(proxy,rpath)
      trees_tool.notify_tree('sys_modify_object',proxy,rpath)
    subobject = object._getOb(object_id)
    return subobject

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
      xml = self.getElementNodeList(xml)[0]
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
      if hasattr(self,'getDocid'):
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
    conflict_list = []
    # We want to add a local role
    roles = self.convertXmlValue(xml.childNodes[0].data,data_type='tokens')
    user = self.getAttribute(xml,'id')
    roles = list(roles) # Needed for CPS, or we have a CPS error
    #LOG('local_role: ',0,'user: %s roles: %s' % (repr(user),repr(roles)))
    #user = roles[0]
    #roles = roles[1:]
    if xml.nodeName.find(self.local_role_tag)>=0:
      object.manage_setLocalRoles(user,roles)
    elif xml.nodeName.find(self.local_group_tag)>=0:
      object.manage_setLocalGroupRoles(user,roles)
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'addLocalPermissionNode')
  def addLocalPermissionNode(self, object, xml):
    """
    This allows to specify how to handle the local permision informations.
    This is really usefull if you want to write your own Conduit.
    """
    conflict_list = []
    # We want to add a local role
    #LOG('addLocalPermissionNode, xml',0,xml)
    if len(xml.childNodes)>0:
      roles = self.convertXmlValue(xml.childNodes[0].data,data_type='tokens')
      roles = list(roles) # Needed for CPS, or we have a CPS error
    else:
      roles = ()
    permission = self.getAttribute(xml,'id')
    #LOG('local_role: ',0,'permission: %s roles: %s' % (repr(permission),repr(roles)))
    #user = roles[0]
    #roles = roles[1:]
    if xml.nodeName.find(self.local_permission_tag)>=0:
      object.manage_setLocalPermissions(permission,roles)
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


    # This doesn't works fine because all workflows variables
    # are not set the same way
#    if status.has_key('action'):
#      action_name = status['action']
#      authorized = 0
#      authorized_actions = wf_tool.getActionsFor(object)
#      LOG('isWorkflowActionAddable, status:',0,status)
#      LOG('isWorkflowActionAddable, authorized_actions:',0,authorized_actions)
#      for action in authorized_actions:
#        if action['id']==action_name:
#          authorized = 1
#      if not authorized:
#        string_io = StringIO()
#        PrettyPrint(xml,stream=string_io)
#        conflict = Conflict(object_path=object.getPhysicalPath(),
#                            keyword=self.history_tag)
#        conflict.setXupdate(string_io.getvalue())
#        conflict.setRemoteValue(status)
#        conflict_list += [conflict]
#    return conflict_list

  def nodeToString(self, node):
    """
    return an xml string corresponding to the node
    """
    buf = cStringIO.StringIO()
    Print(node, stream=buf, encoding='utf-8')
    xml_string = buf.getvalue()
    buf.close() 
    return xml_string

  def getGidFromObject(self, object):
    """
    return the Gid composed with the object informations
    """
    return object.getId()

  def getGidFromXML(self, xml, gid_from_xml_list):
    """
    return the Gid composed with xml informations
    """
    return None

