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
from Products.ERP5SyncML.Subscription import Conflict
from Products.CMFCore.utils import getToolByName
from Products.ERP5SyncML.XupdateUtils import XupdateUtils
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from xml.dom.ext.reader.Sax2 import FromXml

from email.MIMEBase import MIMEBase
from email import Encoders

import sre

from zLOG import LOG

class ERP5Conduit(SyncCode):
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

  """

  NOT_EDITABLE_PROPERTY = ('id','object','workflow_history','security_info','uid'
                           'xupdate:element','xupdate:attribute')


  def getEncoding(self):
    """
    return the string corresponding to the local encoding
    """
    return "iso-8859-1"


  def __init__(self):
    self.args = {}

  def applyModification(object=None):
    """
    This will apply all updates
    """
    args = self.args



  def addNode(self, xml=None, object=None, previous_xml=None, force=0, **kw):
    """
    A node is added

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,remote_value]
    """
    conflict_list = []
    xml = self.convertToXML(xml)
    LOG('addNode',0,'xml_reconstitued: %s' % str(xml))
    # In the case where this new node is a object to add
    LOG('addNode',0,'object.id: %s' % object.getId())
    LOG('addNode',0,'xml.nodeName: %s' % xml.nodeName)
    LOG('addNode',0,'isSubObjectAdd: %i' % self.getSubObjectAddDepth(xml))
    if xml.nodeName == 'object' \
       or xml.nodeName == 'xupdate:insert-after' and self.getSubObjectAddDepth(xml)==1:
      object_id = self.getObjectId(xml)
      LOG('addNode',0,'object_id: %s' % object_id)
      if object_id is not None:
        subobject = None
        try:
          subobject = object[object_id]
        except KeyError:
          pass
        if subobject is None: # If so it does'nt exist yes
          portal_type = ''
          if xml.nodeName == 'object':
            portal_type = self.getObjectType(xml)
          elif xml.nodeName == 'xupdate:insert-after':
            portal_type = self.getXupdateObjectType(xml)
          portal_types = getToolByName(object,'portal_types')
          LOG('ERP5Conduit.addNode',0,'portal_type: |%s|' % str(portal_type))
          portal_types.constructContent(type_name = portal_type,
                                            container = object,
                                            id = object_id)
          subobject = object[object_id]
        self.newObject(object=subobject,xml=xml)
    elif xml.nodeName == 'xupdate:insert-after' \
         and self.getSubObjectAddDepth(xml)==2:
      # We should find the object corresponding to
      # this update, so we have to look in the previous_xml
      object_number = self.getSubObjectIndex(xml)
      LOG('addNode',0,'getSubObjectModification number: %i' % object_number)
      #LOG('updateNode',0,'isSubObjectModification previous: %s' % str(previous_xml))
      if previous_xml is not None and object_number is not None:
        LOG('addNode',0,'previous xml is not none and also object_number')
        if type(previous_xml) in (type('a'),type(u'a')):
          previous_xml = FromXml(previous_xml)
          previous_xml = previous_xml.childNodes[1] # Because we just created a new xml
          # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
        # Get the id of the previous object
        i = 0
        sub_previous_xml = None
        # Find the previous xml corresponding to this subobject
        for subnode in self.getElementNodeList(previous_xml):
          if subnode.nodeName=='object':
            for subnode1 in self.getElementNodeList(subnode):
              if subnode1.nodeName=='object':
                i += 1
                if i==object_number:
                  sub_previous_xml = subnode1
        LOG('addNode',0,'isSubObjectModification sub_p_xml: %s' % str(sub_previous_xml))
        if sub_previous_xml is not None:
          sub_object = None
          LOG('addNode',0,'getObjectId: %s' % self.getObjectId(sub_previous_xml) )
          # XXXXXXXXXXXX
          # The problem is actually that the sub_previous_xml doesn't correspong to the
          # xml, we have the xupdate of a subobject but we have the previous_xml
          # of the object
          try:
            sub_object = object[self.getObjectId(sub_previous_xml)]
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

  def deleteNode(self, xml=None, object=None, **kw):
    """
    A node is deleted
    """
    # In the case where this new node is a object to delete
    LOG('ERP5Conduit',0,'deleteNode')
    xml = self.convertToXML(xml)
    if xml.nodeName == 'object':
      object_id = self.getObjectId(xml)
      if object_id is not None:
        try:
          object._delObject(object_id)
        except KeyError:
          pass

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, **kw):
    """
    A node is updated with some xupdate
      - xml : the xml corresponding to the update, it should be xupdate
      - object : the object on wich we want to apply the xupdate
      - [previous_xml] : the previous xml of the object, it is mandatory
                         when we have sub objects
    """
    conflict_list = []
    xml = self.convertToXML(xml)
    LOG('updateNode',0,'xml.nodeName: %s' % xml.nodeName)
    # we have an xupdate xml
    if xml.nodeName == 'xupdate:modifications':
      xupdate_utils = XupdateUtils()
      conflict_list += xupdate_utils.applyXupdate(object=object,xupdate=xml,conduit=self,
                                 previous_xml=previous_xml, force=force)
    # we may have only the part of an xupdate
    else:
      args = {}
      if self.isProperty(xml) and not(self.isSubObjectModification(xml)):
        for subnode in xml.attributes:
          if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
            select_list = subnode.nodeValue.split('/') # Something like: ('','object[1]','sid[1]')
            new_select_list = ()
            for select_item in select_list:
              new_select_list += (select_item[:select_item.find('[')],)
            select_list = new_select_list # Something like : ('','object','sid')
            keyword = select_list[len(select_list)-1] # this will be 'sid'

        if xml.nodeName != 'xupdate:insert-after':
          for subnode in self.getElementNodeList(xml):
            if subnode.nodeName=='xupdate:element':
              for subnode1 in subnode.attributes:
                if subnode1.nodeName=='name':
                  keyword = subnode1.nodeValue
        i = 1
        while (keyword.find('()') > 0) and (i <= len(select_list)):
          keyword = select_list[len(select_list)-i] # we want description in :
                                                    # /object[1]/description[1]/text()[1]
          i += 1
        if not (keyword in self.NOT_EDITABLE_PROPERTY):
          # We will look for the data to enter
          if len(self.getElementNodeList(xml))==0:
            data = xml.childNodes[0].data
            data = self.convertXmlValue(data)
            #data = data[data.find('\n')+1:data.rfind('\n')]
            #data = data.replace('@@@','\n')
          else:
            data=[]
            for subnode in self.getElementNodeList(xml):
              element_data = subnode.childNodes[0].data
              #element_data = element_data[element_data.find('\n')+1:element_data.rfind('\n')]
              element_data = self.convertXmlValue(element_data)
              element_data = element_data.replace('@@@','\n')
              data += [element_data]
            if len(data) == 1: # This is probably because this is not a list but a string XXX may be not good
              data = data[0]
          #LOG('updateNode',0,'data: %s' % str(data))
          if keyword.find('_list') > 0:
            LOG('updateNode',0,'keyword is type list')
            if type(data) == type(u'a'): # Probably deprecated
              data = data.split('@@@') # XXX very bad hack, must find something better
            #if type(data) == type(u'a'):
            #  LOG('updateNode',0,'splitting it')
            #  data = data.split('\n')
          args[keyword] = data
          args = self.getFormatedArgs(args=args)
          # This is the place where we should look for conflicts
          # For that we need :
          #   - data : the data from the remote box
          #   - old_data : the data from this box but at the time of the last synchronization
          #   - current_data : the data actually on this box
          isConflict = 0
          if previous_xml is not None: # if no previous_xml, no conflict
            old_data = self.getObjectProperty(keyword,previous_xml)
            current_data = object.getProperty(keyword)
            LOG('updateNode',0,'Conflict data: %s' % str(data))
            LOG('updateNode',0,'Conflict old_data: %s' % str(old_data))
            LOG('updateNode',0,'Conflict current_data: %s' % str(current_data))
            if (old_data != current_data) and (data != current_data):
              # This is a conflict
              isConflict = 1
              conflict_list += [Conflict(object_path=object.getPhysicalPath(),keyword=keyword,\
                                local_value=current_data,remote_value=data)]
              #conflict_list += [[object.getPath(),keyword,current_data,data]]
          # We will now apply the argument with the method edit
          if args != {} and (isConflict==0 or force):
            LOG('updateNode',0,'object.edit, args: %s' % str(args))
            object.edit(**args)
        if keyword == 'object':
          # This is the case where we have to call addNode
          LOG('updateNode',0,'we will add sub-object')
          conflict_list += self.addNode(xml=subnode,object=object,force=force)
      elif self.isSubObjectModification(xml):
        # We should find the object corresponding to
        # this update, so we have to look in the previous_xml
        object_number = self.getSubObjectIndex(xml)
        LOG('updateNode',0,'getSubObjectModification number: %i' % object_number)
        #LOG('updateNode',0,'isSubObjectModification previous: %s' % str(previous_xml))
        if previous_xml is not None and object_number is not None:
          LOG('updateNode',0,'previous xml is not none and also object_number')
          if type(previous_xml) in (type('a'),type(u'a')):
            previous_xml = FromXml(previous_xml)
            previous_xml = previous_xml.childNodes[1] # Because we just created a new xml
            # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node

          # Get the id of the previous object
          i = 0
          sub_previous_xml = None
          # Find the previous xml corresponding to this subobject
          for subnode in self.getElementNodeList(previous_xml):
            if subnode.nodeName=='object':
              for subnode1 in self.getElementNodeList(subnode):
                if subnode1.nodeName=='object':
                  i += 1
                  if i==object_number:
                    sub_previous_xml = subnode1
          LOG('updateNode',0,'isSubObjectModification sub_p_xml: %s' % str(sub_previous_xml))
          if sub_previous_xml is not None:
            sub_object = None
            LOG('updateNode',0,'getObjectId: %s' % self.getObjectId(sub_previous_xml) )
            # XXXXXXXXXXXX
            # The problem is actually that the sub_previous_xml doesn't correspong to the
            # xml, we have the xupdate of a subobject but we have the previous_xml
            # of the object
            # I guess it was resolved with getSubObjectXupdate... so this comment may be removed XXX
            try:
              sub_object = object[self.getObjectId(sub_previous_xml)]
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
          new_data += [item]
        data = new_data
      if type(data) is type(u"a"):
        data = data.encode(self.getEncoding())
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
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
        value = subnode.nodeValue
        if sre.search("/object\[[0-9]*\]/object\[[0-9]*\]/.",value) is not None:
          try:
            new_value = ''
            new_value_list = (value.split('/')[1:2] + value.split('/')[3:])
            for s in new_value_list:
              new_value += '/' + s
          except KeyError:
            pass
          subnode.nodeValue = new_value
    element_node_list = self.getElementNodeList(xml)
    # This is when we have a sub_sub_object_add and we will want a sub_object_add
    LOG('getSubObjectXupdate',0,'xml.nodeName: %s' % xml.nodeName)
    #for j in range(0,len(xml.childNodes)):
    #  subnode = xml.childNodes[j]
    for subnode in self.getElementNodeList(xml):
      #if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName=='xupdate:element':
      if subnode.nodeName=='xupdate:element':
        LOG('getSubObjectXupdate',0,'subnode.nodeName: %s' % subnode.nodeName)
        for subnode1 in self.getElementNodeList(subnode):
          LOG('getSubObjectXupdate',0,'subnode1.nodeName: %s' % subnode1.nodeName)
          if subnode.nodeType == subnode.ELEMENT_NODE and \
            subnode1.nodeName=='object':
            #LOG('getSubObjectXupdate',0,'xml.childNodes[j].nodeName: %s' % xml.childNodes[j].nodeName)
            #xml.childNodes[j] = subnode1
            return subnode1
    return xml

  def isSubObjectModification(self, xml):
    """
    Check if it is a modification from an subobject
    """
    good_list = ('/object[1]/object',)
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
        value = subnode.nodeValue
        LOG('isSubObjectModification',0,'value: %s' % value)
        for good_string in good_list:
          if value.find(good_string)==0:
            return 1
    return 0

  def getSubObjectAddDepth(self, xml):
    """
    Check if this modification is in reality a new subobject to add
    """
    if xml.nodeName == 'xupdate:insert-after':
      for subnode in self.getElementNodeList(xml):
        if subnode.nodeName == 'xupdate:element':
          for attribute in subnode.attributes:
            if attribute.nodeName == 'name':
              is_sub_add = 0
              if attribute.nodeValue == 'object':
                is_sub_add = 1
              if not is_sub_add:
                return 0
              for subnode1 in self.getElementNodeList(subnode):
                if subnode1.nodeName == 'object': # In this particular case, this is sub_sub_add
                  return 2
              return 1
        if subnode.nodeName == 'object':
          return 1
    return 0

  def getSubObjectIndex(self, xml):
    """
    Return the number of the subobject in an xupdate modification
    """
    selection = None
    good_string = '/object[1]/object['
    for subnode in xml.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE and subnode.nodeName=='select':
        value = subnode.nodeValue
        if value.find(good_string)==0:
          string_number = value[len(good_string):]
          string_number = string_number.split(']')[0]
          selection = int(string_number)
    return selection

  def getObjectId(self, xml):
    """
    Retrieve the id
    """
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'id':
        data = subnode.childNodes[0].data
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


  def getObjectProperty(self, property, xml):
    """
    Retrieve the given property
    """
    if type(xml) in (type('a'),type(u'a')):
      xml = FromXml(xml)
      xml = xml.childNodes[1] # Because we just created a new xml
    # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
    for subnode in self.getElementNodeList(xml):
      LOG('getObjectProperty',0,'subnode.nodeName: %s' % subnode.nodeName)
      if subnode.nodeName == property:
        data = subnode.childNodes[0].data
        data =  self.convertXmlValue(data)
        if property[-5:]=='_list':
          data = data.split('@@@')
        return data
    return None

  def convertToXML(self,xml):
    """
    if xml is a string, convert it to a node
    """
    if type(xml) in (type('a'),type(u'a')):
      xml = FromXml(xml)
      xml = xml.childNodes[1] # Because we just created a new xml
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
          data = self.convertXmlValue(data)
          args[keyword]=data
        LOG('newObject',0,'keyword: %s' % str(keyword))
        LOG('newObject',0,'keywordtype: %s' % str(keyword_type))
        if args.has_key(keyword):
          LOG('newObject',0,'data: %s' % str(args[keyword]))
        if keyword_type in list_types:
          if args.has_key(keyword):
            if type(args[keyword]) in [type(u'a'),type('a')]:
              args[keyword] = args[keyword].split('@@@')
        elif keyword_type in ('text',):
          if args.has_key(keyword):
            args[keyword] = args[keyword].replace('@@@','\n')

    # We should first edit the object
    args = self.getFormatedArgs(args=args)
    LOG('newObject',0,"object.getpath: %s" % str(object.getPath()))
    LOG('newObject',0,"args: %s" % str(args))
    # edit the object with a dictionnary of arguments,
    # like {"telephone_number":"02-5648"}
    object.edit(**args)

    # Then we may create subobject
    for subnode in xml.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and \
                              subnode.nodeName=='object':
        self.addNode(object=object,xml=subnode)

  def convertXmlValue(self, data):
    """
    It is possible that the xml change the value, for example
    there is some too much '\n' and some spaces. We should correct it
    """
    # Theses two lines are not needed any more
    #if data.find('\n')>=0 and data[0]==' ': # We may suppose there is two '\n' in this case
    #  data = data[data.find('\n')+1:data.rfind('\n')]
    # Then we should remove every other \n
    # we doesn't want any of them on our synchronization, they have
    # to be all replaced by '@@@', this is really usefull in order to split
    # very long data
    data = data.replace('\n','')
    # Remove spaces at the beginning
    while data.find(' ')==0:
      data = data[1:]
    # Remove spaces at the end
    while data.rfind(' ')==(len(data)-1):
      data = data[:-1]
    if type(data) is type(u"a"):
      data = data.encode(self.getEncoding())
    return data

  def getElementNodeList(self, node):
    """
      Return childNodes that are ElementNode
    """
    subnode_list = []
    for subnode in node.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE:
        subnode_list += [subnode]
    LOG('getElementNodeList',0,'end...')
    return subnode_list

