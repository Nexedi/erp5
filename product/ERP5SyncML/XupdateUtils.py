##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5SyncML.XMLSyncUtils import *
from xml.dom.ext.reader.Sax2 import FromXml
from zLOG import LOG

class XupdateUtils:
  """
  This class contains method specific to xupdate xml,
  this is the place where we should parse xupdate data.
  """

  def applyXupdate(self, object=None, xupdate=None, conduit=None, force=0, **kw):
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if type(xupdate) is type('a'):
      xupdate = FromXml(xupdate)

    # This is a list of selection with a fake tag
    fake_tag_list = ()

    for subnode in xupdate.childNodes:
      to_continue = 0
      selection_name = ''
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'xupdate:append':
        # Check if we do not have a fake tag somewhere
        for subnode1 in subnode.attributes:
          if subnode1.nodeType == subnode1.ATTRIBUTE_NODE and subnode1.nodeName=='select':
            selection_name = subnode1.nodeValue
            LOG('applyXupdate',0,'selection_name: %s' % str(selection_name))
        for subnode1 in subnode.childNodes:
          if subnode1.nodeType == subnode1.ELEMENT_NODE and subnode1.nodeName == 'xupdate:element':
            for subnode2 in subnode1.attributes:
              if subnode2.nodeName=='name' and subnode2.nodeValue == 'LogilabXMLDIFFFAKETag':
                fake_tag_list += (selection_name,)
                to_continue = 1
            if not to_continue:
              conduit.addNode(xml=subnode, object=object, force=force, **kw)
          if subnode1.nodeType == subnode.ELEMENT_NODE and subnode1.nodeName == 'xupdate:text':
            if selection_name in fake_tag_list: # This is the case where xmldiff do the crazy thing :
                                                # Adding a fake tag, modify and delete,
                                                # so we should only update.
              conflict_list += conduit.updateNode(xml=subnode, object=object, force=force, **kw)
            else:
              conflict_list += conduit.addNode(xml=subnode,object=object, force=force, **kw)
        #if to_continue:
        #  continue
      elif subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'xupdate:remove':
        for subnode1 in subnode.attributes:
          if subnode1.nodeType == subnode1.ATTRIBUTE_NODE and subnode1.nodeName=='select':
            selection_name = subnode1.nodeValue
            LOG('applyXupdate',0,'fake_tag_list: %s' % str(fake_tag_list))
            for fake_tag in fake_tag_list:
              if selection_name.find(fake_tag) == 0:
                LOG('applyXupdate',0,'selection ignored for delete: %s' % str(selection_name))
                to_continue = 1
            if not to_continue:
              conduit.deleteNode(xml=subnode, object=object)
      elif subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'xupdate:update':
        conflict_list += conduit.updateNode(xml=subnode, object=object, force=force, **kw)
      elif subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'xupdate:insert-after':
        conflict_list += conduit.addNode(xml=subnode, object=object, force=force, **kw)

    return conflict_list




  def old_applyXupdate(self, object=None, xupdate=None, conduit=None):
    """
    deprecated and should not be used
    """
    for subnode in xupdate.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'xupdate:modifications':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE:
            to_continue = 0
            select_list = ()
            # First check if we are not a sub-object
            for subnode3 in subnode2.attributes:
              if subnode3.nodeType == subnode3.ATTRIBUTE_NODE and subnode3.nodeName=='select':
                nodeValue = subnode3.nodeValue
                if nodeValue.find('/object[1]/object')==0:
                  to_continue = 1
                elif nodeValue.find('/object[1]/workflow_history')==0:
                  to_continue = 1
                elif nodeValue.find('/object[1]/security_info')==0:
                  to_continue = 1
                else:
                  select_list = subnode3.nodeValue.split('/') # Something like: ('','object[1]','sid[1]')
                  new_select_list = ()
                  for select_item in select_list:
                    new_select_list += (select_item[:select_item.find('[')],)
                  select_list = new_select_list # Something like : ('','object','sid')
            if to_continue:
              continue

            # Then we have to find the keyword, differents ways are needed
            # depending if we are inserting, updating, removing...
            keyword = None
            data = None
            if subnode2.nodeName == 'xupdate:insert-after': # We suppose the tag was empty before
                                                            # XXX this supposition could be WRONG
              for subnode3 in getElementNodeList(subnode2):
                if subnode3.nodeName=='xupdate:element':
                  for subnode4 in subnode3.attributes:
                    if subnode4.nodeName=='name':
                      keyword = subnode4.nodeValue
                      LOG('ApplyUpdate',0,'i-a, keyword: %s' % keyword)
                      if keyword=='object': # This is a subobject, we have to stop right now
                        to_continue = 1
                      elif keyword.find('element_')==0: # We are on a part of a list
                        keyword = select_list[len(select_list)-2]
                  if to_continue:
                    continue
                  if len(getElementNodeList(subnode3))==0:
                    data = str(subnode3.childNodes[0].data) # We assume the child is a text node
                  else: # We have many elements
                    data = []
                    for subnode4 in getElementNodeList(subnode3):
                      # In this case we should only have one childnode
                      LOG('ApplyUpdate',0,'subnode4: %s' % str(subnode4))
                      element_data = subnode4.childNodes[0].data
                      element_data = element_data[element_data.find('\n')+1:element_data.rfind('\n')]
                      data += [element_data]
            elif subnode2.nodeName == 'xupdate:append':
              keyword = select_list[len(select_list)-1]
              if len(getElementNodeList(subnode2))==0:
                data = subnode2.childNodes[0].data
                data = data[data.find('\n')+1:data.rfind('\n')]
              else:
                data=[]
                for subnode3 in getElementNodeList(subnode2):
                  element_data = subnode3.childNodes[0].data
                  element_data = element_data[element_data.find('\n')+1:element_data.rfind('\n')]
                  data += [element_data]
                if len(data) == 1: # This is probably because this is not a list but a string XXX may be not good
                  data = data[0]

            LOG('ERP5Conduit.ApplyUpdate',0,'args: %s' % str(args))
            if keyword is not None:
              if type(keyword) is type(u"a"):
                LOG('ERP5Conduit.ApplyUpdate',0,'keyword before encoding: %s' % str(type(keyword)))
                keyword = keyword.encode(self.getEncoding())
                LOG('ERP5Conduit.ApplyUpdate',0,'keyword after encoding: %s' % str(type(keyword)))
              if not(keyword in self.NOT_EDITABLE_PROPERTY):
                if type(data) is type([]) or type(data) is type(()):
                  new_data = []
                  for item in data:
                    if type(item) is type(u"a"):
                      item = item.encode(self.getEncoding())
                    new_data += [item]
                  data = new_data
                if type(data) is type(u"a"):
                  data = data.encode(self.getEncoding())
                # if we have already this keyword, then we may append to a list
                if args.has_key(keyword):
                  arg_type = type(args[keyword])
                  if arg_type is type(()) or arg_type is type([]):
                    if type(data) is not type(()) or type(data) is not type([]):
                      data = [data]
                    data = args[keyword] + data
                args[keyword] = data

    if len(args) > 0:
      object.edit(**args)

