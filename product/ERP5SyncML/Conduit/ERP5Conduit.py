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

from Products.ERP5SyncML.SyncCode import SyncCode
from Products.ERP5SyncML.XMLSyncUtils import XMLSyncUtilsMixin
from Products.ERP5SyncML.Subscription import Conflict
from Products.CMFCore.utils import getToolByName
from Products.ERP5SyncML.XupdateUtils import XupdateUtils
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from xml.dom.ext.reader.Sax2 import FromXml
from DateTime.DateTime import DateTime
from email.MIMEBase import MIMEBase
from email import Encoders

import re, copy

from zLOG import LOG

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


  def getEncoding(self):
    """
    return the string corresponding to the local encoding
    """
    return "iso-8859-1"

  def __init__(self):
    self.args = {}

  def addNode(self, xml=None, object=None, previous_xml=None, force=0, **kw):
    """
    A node is added

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,remote_value]
    """
    conflict_list = []
    xml = self.convertToXml(xml)
    LOG('addNode',0,'xml_reconstitued: %s' % str(xml))
    # In the case where this new node is a object to add
    LOG('addNode',0,'object.id: %s' % object.getId())
    LOG('addNode',0,'xml.nodeName: %s' % xml.nodeName)
    LOG('addNode',0,'isSubObjectAdd: %i' % self.getSubObjectDepth(xml))
    if xml.nodeName == 'object' \
       or xml.nodeName in self.XUPDATE_INSERT_OR_ADD and self.getSubObjectDepth(xml)==1:
      object_id = self.getObjectId(xml)
      docid = self.getObjectDocid(xml)
      LOG('addNode',0,'object_id: %s' % object_id)
      if object_id is not None:
        try:
          subobject = object._getOb(object_id)
        except (AttributeError, KeyError):
          subobject = None
        #subobject = None
        #try:
        #  subobject = object[object_id]
        #except KeyError:
        #  pass
        if subobject is None: # If so it does'nt exist yes
          portal_type = ''
          if xml.nodeName == 'object':
            portal_type = self.getObjectType(xml)
          elif xml.nodeName in self.XUPDATE_INSERT_OR_ADD:
            portal_type = self.getXupdateObjectType(xml)
          portal_types = getToolByName(object,'portal_types')
          LOG('ERP5Conduit.addNode',0,'portal_type: |%s|' % str(portal_type))
          if docid==None: # ERP5 content
            portal_types.constructContent(type_name = portal_type,
                                              container = object,
                                              id = object_id)
          else: # CPS content
            # This is specific to CPS, we will call the proxy tool
            px_tool= getToolByName(object,'portal_proxies')
            proxy_type = 'document'
            if portal_type == 'Workspace':
              proxy_type = 'folder'
            proxy = px_tool.createEmptyProxy(proxy_type,
                                   object,portal_type,object_id,docid)
            #px_tool.createRevision(proxy,px_tool.getDefaultLanguage()) # Doesn't works well
            # px_tool._addProxy(proxy,None) # Doesn't works well
          #object.newContent(portal_type=portal_type, id=object_id) # Doesn't works with CPS
          #subobject = object[object_id] # Doesn't works with CPS
          subobject = object._getOb(object_id)
          # Again for CPS proxy XXX May be not needed
          #if docid is not None:
          #  subobject.proxyChanged()
        self.newObject(object=subobject,xml=xml)
    elif xml.nodeName in self.XUPDATE_INSERT_OR_ADD \
         and self.getSubObjectDepth(xml)==2:
      # We should find the object corresponding to
      # this update, so we have to look in the previous_xml
      sub_object_id = self.getSubObjectId(xml)
      LOG('addNode',0,'getSubObjectModification number: %s' % sub_object_id)
      #LOG('updateNode',0,'isSubObjectModification previous: %s' % str(previous_xml))
      if previous_xml is not None and sub_object_id is not None:
        LOG('addNode',0,'previous xml is not none and also sub_object_id')
        previous_xml = self.getSubObjectXml(sub_object_id,previous_xml)
        # Get the id of the previous object
        i = 0
        sub_previous_xml = None
        # Find the previous xml corresponding to this subobject
        sub_previous_xml == self.getSubObjectXml(sub_object_id,previous_xml)
        LOG('addNode',0,'isSubObjectModification sub_p_xml: %s' % str(sub_previous_xml))
        if sub_previous_xml is not None:
          sub_object = None
          try:
            sub_object = object[sub_object_id]
          except KeyError:
            pass
          if sub_object is not None:
            LOG('addNode',0,'subobject.id: %s' % sub_object.id)
            # Change the xml in order to directly apply
            # modifications to the subobject
            sub_xml = self.getSubObjectXupdate(xml)
            LOG('addNode',0,'sub_xml: %s' % str(sub_xml))
            # Then do the udpate
            conflict_list += self.addNode(xml=sub_xml,object=sub_object,
                            previous_xml=sub_previous_xml, force=force)
    else:
      conflict_list += self.updateNode(xml=xml,object=object, force=force, **kw)
    return conflict_list

  def deleteNode(self, xml=None, object=None, object_id=None, force=None, **kw):
    """
    A node is deleted
    """
    # In the case where this new node is a object to delete
    LOG('ERP5Conduit',0,'deleteNode')
    LOG('ERP5Conduit',0,'deleteNode, object.id: %s' % object.getId())
    conflict_list = []
    xml = self.convertToXml(xml)
    if object_id is None:
      LOG('ERP5Conduit',0,'deleteNode, SubObjectDepth: %i' % self.getSubObjectDepth(xml))
      if xml.nodeName == self.xml_object_tag:
        object_id = self.getObjectId(xml)
      elif self.getSubObjectDepth(xml)==1:
        object_id = self.getSubObjectId(xml)
      elif self.getSubObjectDepth(xml)==2:
        # we have to call delete node on a subsubobject
        sub_object_id = self.getSubObjectId(xml)
        try:
          sub_object = object._getOb(sub_object_id)
          sub_xml = self.getSubObjectXupdate(xml)
          conflict_list += self.deleteNode(xml=sub_xml,object=sub_object,
                                           force=force)
        except KeyError:
          pass
    else: # We do have an object_id
      try:
        object._delObject(object_id)
      except (AttributeError, KeyError):
        pass
    return conflict_list

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, **kw):
    """
    A node is updated with some xupdate
      - xml : the xml corresponding to the update, it should be xupdate
      - object : the object on wich we want to apply the xupdate
      - [previous_xml] : the previous xml of the object, it is mandatory
                         when we have sub objects
    """
    conflict_list = []
    xml = self.convertToXml(xml)
    LOG('updateNode',0,'xml.nodeName: %s' % xml.nodeName)
    # we have an xupdate xml
    if xml.nodeName == 'xupdate:modifications':
      xupdate_utils = XupdateUtils()
      conflict_list += xupdate_utils.applyXupdate(object=object,xupdate=xml,conduit=self,
                                 previous_xml=previous_xml, force=force)
    # we may have only the part of an xupdate
    else:
      args = {}
      LOG('isSubObjectModification',0,'result: %s' % str(self.isSubObjectModification(xml)))
      if self.isProperty(xml) and not(self.isSubObjectModification(xml)):
        for subnode in xml.attributes:
          if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
            LOG('updateNode',0,'selection: %s' % str(subnode.nodeValue))
            select_list = subnode.nodeValue.split('/') # Something like:
                                                       #('','object[1]','sid[1]')
            new_select_list = ()
            for select_item in select_list:
              if select_item.find('[')>=0:
                select_item = select_item[:select_item.find('[')]
              new_select_list += (select_item,)
            select_list = new_select_list # Something like : ('','object','sid')
            keyword = select_list[len(select_list)-1] # this will be 'sid'

        LOG('updateNode',0,'keyword: %s' % str(keyword))
        if not (xml.nodeName in self.XUPDATE_INSERT_OR_ADD):
          for subnode in self.getElementNodeList(xml):
            if subnode.nodeName=='xupdate:element':
              for subnode1 in subnode.attributes:
                if subnode1.nodeName=='name':
                  keyword = subnode1.nodeValue
        if not (keyword in self.NOT_EDITABLE_PROPERTY):
          # We will look for the data to enter
          if len(self.getElementNodeList(xml))==0:
            try:
              data = xml.childNodes[0].data
            except IndexError: # There is no data
              data = None
          # XXX may be not needed any more
          #else:
          #  data=()
          #  for subnode in self.getElementNodeList(xml):
          #    element_data = subnode.childNodes[0].data
          #    element_data = self.convertXmlValue(element_data)
          #    data += (element_data,)
          #  if len(data) == 1: # This is probably because this is not a list
                               # but a string XXX may be not good
          #    data = data[0]
          data_type = object.getPropertyType(keyword)
          LOG('updateNode',0,'data_type: %s' % str(data_type))
          data = self.convertXmlValue(data,data_type=data_type)
          args[keyword] = data
          args = self.getFormatedArgs(args=args)
          # This is the place where we should look for conflicts
          # For that we need :
          #   - data : the data from the remote box
          #   - old_data : the data from this box but at the time of the last synchronization
          #   - current_data : the data actually on this box
          isConflict = 0
          if previous_xml is not None: # if no previous_xml, no conflict
            old_data = self.getObjectProperty(keyword,previous_xml,data_type=data_type)
            current_data = object.getProperty(keyword)
            LOG('updateNode',0,'Conflict data: %s' % str(data))
            LOG('updateNode',0,'Conflict old_data: %s' % str(old_data))
            LOG('updateNode',0,'Conflict current_data: %s' % str(current_data))
            if (old_data != current_data) and (data != current_data):
              LOG('updateNode',0,'Conflict on : %s' % keyword)
              # Hack in order to get the synchronization working for demo
              # XXX this have to be removed after
              if not (data_type in self.binary_type_list):
                # This is a conflict
                isConflict = 1
                conflict_list += [Conflict(object_path=object.getPhysicalPath(),
                                           keyword=keyword,
                                           local_value=current_data,
                                           remote_value=data)]
          # We will now apply the argument with the method edit
          if args != {} and (isConflict==0 or force):
            LOG('updateNode',0,'object._edit, args: %s' % str(args))
            object._edit(**args)
        if keyword == 'object':
          # This is the case where we have to call addNode
          LOG('updateNode',0,'we will add sub-object')
          conflict_list += self.addNode(xml=subnode,object=object,force=force)
      elif self.isSubObjectModification(xml):
        # We should find the object corresponding to
        # this update, so we have to look in the previous_xml
        sub_object_id = self.getSubObjectId(xml)
        LOG('updateNode',0,'getSubObjectModification number: %s' % sub_object_id)
        if previous_xml is not None and sub_object_id is not None:
          LOG('updateNode',0,'previous xml is not none and also sub_object_id')
          sub_previous_xml = self.getSubObjectXml(sub_object_id,previous_xml)
          LOG('updateNode',0,'isSubObjectModification sub_p_xml: %s' % str(sub_previous_xml))
          if sub_previous_xml is not None:
            sub_object = None
            try:
              sub_object = object[sub_object_id]
            except KeyError:
              pass
            if sub_object is not None:
              LOG('updateNode',0,'subobject.id: %s' % sub_object.id)
              # Change the xml in order to directly apply
              # modifications to the subobject
              sub_xml = self.getSubObjectXupdate(xml)
              LOG('updateNode',0,'sub_xml: %s' % str(sub_xml))
              # Then do the udpate
              conflict_list += self.updateNode(xml=sub_xml,object=sub_object, force=force,
                              previous_xml=sub_previous_xml)
    return conflict_list

  def getFormatedArgs(self, args=None):
    """
    This lookd inside the args dictionnary and then
    convert any unicode string to string
    """
    LOG('ERP5Conduit.getFormatedArgs',0,'args: %s' % str(args))
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
        LOG('ERP5Conduit.getFormatedArgs',0,'binary_data keyword: %s' % str(keyword))
        msg = MIMEBase('application','octet-stream')
        Encoders.encode_base64(msg)
        msg.set_payload(data)
        data = msg.get_payload(decode=1)
      new_args[keyword] = data
    return new_args

  def isProperty(self, xml):
    """
    Check if it is a simple property
    """
    bad_list = ('/object[1]/object','/object[1]/workflow_history','/object[1]/security_info')
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
        value = subnode.nodeValue
        for bad_string in bad_list:
          if value.find(bad_string)==0:
            return 0
    return 1

  def getSubObjectXupdate(self, xml):
    """
    This will change the xml in order to change the update
    from the object to the subobject
    """
    xml = copy.deepcopy(xml)
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        subnode.nodeValue = self.getSubObjectSelect(subnode.nodeValue)
    element_node_list = self.getElementNodeList(xml)
    # This is when we have a sub_sub_object_add and we will want a sub_object_add
    LOG('getSubObjectXupdate',0,'xml.nodeName: %s' % xml.nodeName)
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName=='xupdate:element':
        LOG('getSubObjectXupdate',0,'subnode.nodeName: %s' % subnode.nodeName)
        for subnode1 in self.getElementNodeList(subnode):
          LOG('getSubObjectXupdate',0,'subnode1.nodeName: %s' % subnode1.nodeName)
          if subnode1.nodeName=='object':
            return subnode1
    return xml

  def isSubObjectModification(self, xml):
    """
    Check if it is a modification from an subobject
    """
    good_list = (self.sub_object_exp,)
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
        value = subnode.nodeValue
        LOG('isSubObjectModification',0,'value: %s' % value)
        for good_string in good_list:
          if re.search(good_string,value) is not None:
            return 1
    return 0

  def getSubObjectDepth(self, xml):
    """
    Give the Depth of a subobject modification
    0 means, no depth
    1 means it is a subobject
    2 means it is more depth than subobject
    """
    LOG('getSubObjectDepth',0,'xml.nodeName: %s' % xml.nodeName)
    if xml.nodeName in self.XUPDATE_TAG:
      LOG('getSubObjectDepth',0,'xml2.nodeName: %s' % xml.nodeName)
      if xml.nodeName == self.xml_object_tag:
        return 1
      for subnode in self.getAttributeNodeList(xml):
        LOG('getSubObjectDepth',0,'subnode.nodeName: %s' % subnode.nodeName)
        if subnode.nodeName == 'select':
          value = subnode.nodeValue
          LOG('getSubObjectDepth',0,'subnode.nodeValue: %s' % subnode.nodeValue)
          if re.search(self.sub_object_exp,value) is not None:
            new_select = self.getSubObjectSelect(value)
            if self.getSubObjectSelect(new_select) != new_select:
              return 2
            return 1
      for subnode in self.getElementNodeList(xml):
        # One part of this is specific to xmldiff, may be need to rewrite
        if subnode.nodeName == 'xupdate:element':
          for attribute in subnode.attributes:
            if attribute.nodeName == 'name':
              is_sub_add = 0
              if attribute.nodeValue == self.xml_object_tag:
                is_sub_add = 1
              if not is_sub_add:
                return 0
              for subnode1 in self.getElementNodeList(subnode):
                if subnode1.nodeName == self.xml_object_tag: # In this particular case, this is sub_sub_add
                  return 2
              return 1
    return 0

  def getSubObjectSelect(self, select):
    """
    Return a string wich is the selection for the subobject
    ex: for "/object[@id='161']/object[@id='default_address']/street_address"
    if returns "/object[@id='default_address']/street_address"
    """
    if re.search(self.sub_object_exp,select) is not None:
      s = self.xml_object_tag
      new_value = '/' + select[select.find(s,select.find(s)+1):]
      select = new_value
    return select

  def getSubObjectId(self, xml):
    """
    Return the id of the subobject in an xupdate modification
    """
    object_id = None
    for subnode in self.getAttributeNodeList(xml):
      if subnode.nodeName=='select':
        value = subnode.nodeValue
        if re.search(self.sub_object_exp,value) is not None:
          s = self.xml_object_tag
          object_id = value[value.find(s,value.find(s)+1):]
          object_id = object_id[object_id.find("'")+1:]
          object_id = object_id[:object_id.find("'")]
          return object_id
    return object_id

  def getSubObjectXml(self, object_id, xml):
    """
    Return the xml of the subobject which as the id object_id
    """
    xml = self.convertToXml(xml)
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName==self.xml_object_tag:
        LOG('getSub0bjectXml: object_id:',0,object_id)
        if object_id == self.getObjectId(subnode):
          return subnode
    return None

  def getObjectId(self, xml):
    """
    Retrieve the id
    """
    #for subnode in self.getElementNodeList(xml):
    #  if subnode.nodeName == 'id':
    #    data = subnode.childNodes[0].data
    #    return self.convertXmlValue(data)
    for attribute in self.getAttributeNodeList(xml):
      if attribute.nodeName == 'id':
        data = attribute.childNodes[0].data
        return self.convertXmlValue(data)
    # In the case where the new object is inside an xupdate
    if xml.nodeName.find('xupdate')>=0:
      for subnode in self.getElementNodeList(xml):
        if subnode.nodeName == 'xupdate:element':
          for subnode1 in self.getElementNodeList(subnode):
            if subnode1.nodeName == 'id':
              data = subnode1.childNodes[0].data
              return self.convertXmlValue(data)
    return None

  def getObjectDocid(self, xml):
    """
    Retrieve the docid
    """
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'docid':
        data = subnode.childNodes[0].data
        return self.convertXmlValue(data)
    return None

  def getObjectProperty(self, property, xml, data_type=None):
    """
    Retrieve the given property
    """
    xml = self.convertToXml(xml)
    # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == property:
        try:
          data = subnode.childNodes[0].data
          data =  self.convertXmlValue(data, data_type=data_type)
        except IndexError: # There is no data
          data = None
        return data
    return None

  def convertToXml(self,xml):
    """
    if xml is a string, convert it to a node
    """
    if type(xml) in (type('a'),type(u'a')):
      xml = FromXml(xml)
      xml = xml.childNodes[1] # Because we just created a new xml
    # If we have the xml from the node erp5, we just take the subnode
    if xml.nodeName=='erp5':
      xml = self.getElementNodeList(xml)[0]
    return xml

  def getObjectType(self, xml):
    """
    Retrieve the portal type from an xml
    """
    portal_type = None
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE:
        if subnode.nodeName=='portal_type':
          portal_type = subnode.nodeValue
          portal_type = self.convertXmlValue(portal_type)
          return portal_type
    return portal_type

  def getXupdateObjectType(self, xml):
    """
    Retrieve the portal type from an xupdate
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


  def newObject(self, object=None, xml=None):
    """
      modify the object with datas from
      the xml (action section)
    """
    args = {}
    if xml.nodeName.find('xupdate')>= 0:
      xml = self.getElementNodeList(xml)[0]
    for subnode in self.getElementNodeList(xml):
      if not(subnode.nodeName in self.NOT_EDITABLE_PROPERTY):
        keyword_type = None
        for subnode1 in subnode.attributes:
          if subnode1.nodeType == subnode1.ATTRIBUTE_NODE:
            if subnode1.nodeName=='type':
              keyword_type = subnode1.nodeValue

        LOG('newObject',0,str(subnode.childNodes))
        # This is the case where the property is a list
        keyword=str(subnode.nodeName)
        if len(subnode.childNodes) > 0: # We check that this tag is not empty
          data = subnode.childNodes[0].data
          args[keyword]=data
        LOG('newObject',0,'keyword: %s' % str(keyword))
        LOG('newObject',0,'keywordtype: %s' % str(keyword_type))
        #if args.has_key(keyword):
        #  LOG('newObject',0,'data: %s' % str(args[keyword]))
        if args.has_key(keyword):
          args[keyword] = self.convertXmlValue(args[keyword],keyword_type)
    # We should first edit the object
    args = self.getFormatedArgs(args=args)
    LOG('newObject',0,"object.getpath: %s" % str(object.getPath()))
    LOG('newObject',0,"args: %s" % str(args))
    # edit the object with a dictionnary of arguments,
    # like {"telephone_number":"02-5648"}
    object._edit(**args)

    # Then we may create subobject
    for subnode in xml.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and \
                              subnode.nodeName=='object':
        self.addNode(object=object,xml=subnode)

  def convertXmlValue(self, data, data_type=None):
    """
    It is possible that the xml change the value, for example
    there is some too much '\n' and some spaces. We have to do some extra
    things so that we convert correctly the vlalue
    """
    if data is None:
      if data_type in self.list_type_list:
        data = ()
      return data
    data = data.replace('\n','')
    if type(data) is type(u"a"):
      data = data.encode(self.getEncoding())
    # We can now convert string in tuple, dict, binary...
    if data_type in self.list_type_list:
      if type(data) is type('a'):
        data = tuple(data.split('@@@'))
    elif data_type in self.text_type_list:
      data = data.replace('@@@','\n')
    elif data_type in self.binary_type_list:
      data = data.replace('@@@','\n')
      msg = MIMEBase('application','octet-stream')
      Encoders.encode_base64(msg)
      msg.set_payload(data)
      data = msg.get_payload(decode=1)
    elif data_type in self.date_type_list:
      data = DateTime(data)
    elif data_type in self.dict_type_list:
      dict_list = map(lambda x:x.split(':'),data[1:-1].split(','))
      data = map(lambda (x,y):(x.replace(' ','').replace("'",''),int(y)),dict_list)
      data = dict(data)
    LOG('convertXmlValue',0,'data: %s' % str(data))
    return data

