# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Acquisition import aq_base, aq_inner

from cStringIO import StringIO
from pickle import Pickler, EMPTY_DICT, MARK, DICT, PyStringMap, DictionaryType
from xml.sax.saxutils import escape, unescape
from lxml import etree
from lxml.etree import Element, SubElement
from xml_marshaller.xml_marshaller import Marshaller
from OFS.Image import Pdata
from zLOG import LOG
from base64 import standard_b64encode

from hashlib import sha1

MARSHALLER_NAMESPACE_URI = 'http://www.erp5.org/namespaces/marshaller'
marshaller = Marshaller(namespace_uri=MARSHALLER_NAMESPACE_URI,
                                                            as_tree=True).dumps

class OrderedPickler(Pickler):

    dispatch = Pickler.dispatch.copy()

    def save_dict(self, obj):
        write = self.write
        if self.bin:
            write(EMPTY_DICT)
        else:   # proto 0 -- can't use EMPTY_DICT
            write(MARK + DICT)
        self.memoize(obj)
        item_list = obj.items()
        item_list.sort()
        self._batch_setitems(iter(item_list))

    dispatch[DictionaryType] = save_dict
    if not PyStringMap is None:
        dispatch[PyStringMap] = save_dict

# ERP5 specific pickle function - produces ordered pickles
def dumps(obj, protocol=None):
    file = StringIO()
    OrderedPickler(file, protocol).dump(obj)
    return file.getvalue()

def Base_asXML(object, root=None):
  """
      Generate an xml text corresponding to the content of this object
  """
  self = object
  return_as_object = True
  if root is None:
    return_as_object = False
    root = Element('erp5')
  #LOG('asXML',0,'Working on: %s' % str(self.getPhysicalPath()))

  object = SubElement(root, 'object',
                      attrib=dict(id=self.getId(),
                      portal_type=self.getPortalType()))

  # We have to find every property
  for prop_id in set(self.propertyIds()):
    # In most case, we should not synchronize acquired properties
    if prop_id not in ('uid', 'workflow_history', 'id', 'portal_type') and (prop_id != 'user_id' or 'ERP5User' not in getattr(
      getattr(
        self.getPortalObject().portal_types,
        self.getPortalType(),
        None,
      ),
      'getTypePropertySheetList',
      lambda: (),
    )()):
      value = self.getProperty(prop_id)
      if value is None:
        prop_type = 'None'
      else:
        prop_type = self.getPropertyType(prop_id)
      sub_object = SubElement(object, prop_id, attrib=dict(type=prop_type))
      if prop_type in ('object',):
        # We may have very long lines, so we should split
        value = aq_base(value)
        value = dumps(value)
        sub_object.text = standard_b64encode(value)
      elif prop_type in ('data',):
        # Create blocks to represent data
        # <data><block>ZERD</block><block>OEJJM</block></data>
        size_block = 60
        if isinstance(value, str):
          for index in xrange(0, len(value), size_block):
            content = value[index:index + size_block]
            data_encoded = standard_b64encode(content)
            block = SubElement(sub_object, 'block_data')
            block.text = data_encoded
        else:
          raise ValueError("XMLExportImport failed, the data is undefined")
      elif prop_type in ('lines', 'tokens',):
        value = [word.decode('utf-8').encode('ascii','xmlcharrefreplace')\
            for word in value]
        sub_object.append(marshaller(value))
      elif prop_type in ('text', 'string',):
        sub_object.text = unicode(escape(value), 'utf-8')
      elif prop_type != 'None':
        sub_object.text = str(value)

  # We have to describe the workflow history
  if getattr(self, 'workflow_history', None) is not None:
    workflow_list = self.workflow_history
    workflow_list_keys = workflow_list.keys()
    workflow_list_keys.sort() # Make sure it is sorted

    for workflow_id in workflow_list_keys:
      for workflow_action in workflow_list[workflow_id]:
        workflow_node = SubElement(object, 'workflow_action',
                                   attrib=dict(workflow_id=workflow_id))
        workflow_variable_list = workflow_action.keys()
        workflow_variable_list.sort()
        for workflow_variable in workflow_variable_list:
          variable_type = "string" # Somewhat bad, should find a better way
          if workflow_variable.find('time') >= 0:
            variable_type = "date"
          if workflow_variable.find('language_revs') >= 0: # XXX specific to cps
            variable_type = "dict"
          if workflow_action[workflow_variable] is None:
            variable_type = 'None'
          variable_node = SubElement(workflow_node, workflow_variable,
                                     attrib=dict(type=variable_type))
          if variable_type != 'None':
            variable_node_text = str(workflow_action[workflow_variable])
            variable_node.text = unicode(variable_node_text, 'utf-8')

            if workflow_variable == 'time':
              time = variable_node.text
            elif workflow_variable == 'actor':
              actor = variable_node.text

        workflow_node.attrib['id'] = sha1(workflow_id + time +
                                             str(actor.encode('utf-8'))).hexdigest()

  # We should now describe security settings
  for user_role in self.get_local_roles():
    local_role_node = SubElement(object, 'local_role',
                                 attrib=dict(id=user_role[0], type='tokens'))
    #convert local_roles in string because marshaller can't do it
    role_list = []
    for role in user_role[1]:
      if isinstance(role, unicode):
        role = role.encode('utf-8')
      role_list.append(role)
    local_role_node.append(marshaller(tuple(role_list)))
  if getattr(self, 'get_local_permissions', None) is not None:
    for user_permission in self.get_local_permissions():
      local_permission_node = SubElement(object, 'local_permission',
                              attrib=dict(id=user_permission[0], type='tokens'))
      local_permission_node.append(marshaller(user_permission[1]))
  # Sometimes theres is roles specified for groups, like with CPS
  if getattr(self, 'get_local_group_roles', None) is not None:
    for group_role in self.get_local_group_roles():
      local_group_node = SubElement(object, 'local_group',
                                    attrib=dict(id=group_role[0], type='tokens'))
      local_group_node.append(marshaller(group_role[1]))
  if return_as_object:
    return root
  return etree.tostring(root, encoding='utf-8',
                        xml_declaration=True, pretty_print=True)

def Folder_asXML(object, omit_xml_declaration=True, root=None):
  """
      Generate an xml text corresponding to the content of this object
  """
  xml_declaration = not omit_xml_declaration
  from Products.ERP5Type.Base import Base
  self = object
  if root is None:
    root = Element('erp5')
  Base_asXML(self, root=root)
  root_node = root.find('object')
  # Make sure the list of sub objects is ordered
  id_list = sorted(self.objectIds())
  # Append to the xml the xml of subobjects
  for id in id_list:
    o = self._getOb(id)
    if issubclass(o.__class__, Base):
      o.asXML(root=root_node)

  return etree.tostring(root, encoding='utf-8',
                        xml_declaration=xml_declaration, pretty_print=True)
