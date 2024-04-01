# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001,2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
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

## The code below was initially in ERP5Type/XMLExportImport.py
from Acquisition import aq_base, aq_inner
from collections import OrderedDict
from io import BytesIO
# XXX-zope4py3: Python3 C implementation does not have Unpickler.dispatch
# attribute. dispatch_table should be used instead.
from zodbpickle.slowpickle import Pickler
from xml.sax.saxutils import escape, unescape
from lxml import etree
from lxml.etree import Element, SubElement
from xml_marshaller.xml_marshaller import Marshaller
from OFS.Image import Pdata
import six
if six.PY2:
  from base64 import standard_b64encode, encodestring as encodebytes
else:
  from base64 import standard_b64encode, encodebytes

from hashlib import sha1
from Products.ERP5Type.Utils import bytes2str
#from zLOG import LOG

try:
  long_ = long
except NameError: # six.PY3
  long_ = int

MARSHALLER_NAMESPACE_URI = 'http://www.erp5.org/namespaces/marshaller'
marshaller = Marshaller(namespace_uri=MARSHALLER_NAMESPACE_URI,
                                                            as_tree=True).dumps

class OrderedPickler(Pickler):
    """Pickler producing consistent output by saving dicts in order
    """
    dispatch = Pickler.dispatch.copy()

    def save_dict(self, obj):
        return Pickler.save_dict(
            self,
            OrderedDict(sorted(obj.items())))

    dispatch[dict] = save_dict

# ERP5 specific pickle function - produces ordered pickles
def dumps(obj, protocol=None):
    file = BytesIO()
    OrderedPickler(file, protocol).dump(obj)
    return file.getvalue()

from six.moves import xrange
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
  for prop_id in sorted(set(self.propertyIds())):
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
        if isinstance(value, bytes):
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
        value = escape(value)
        if six.PY2:
          value = six.text_type(value, 'utf-8')
        sub_object.text = value
      elif prop_type != 'None':
        sub_object.text = str(value)

  # We have to describe the workflow history
  if getattr(self, 'workflow_history', None) is not None:
    workflow_list = self.workflow_history

    for workflow_id, workflow_action_list in sorted(six.iteritems(workflow_list)):  # Make sure it is sorted
      for workflow_action in workflow_action_list:
        workflow_node = SubElement(object, 'workflow_action',
                                   attrib=dict(workflow_id=workflow_id))
        workflow_variable_list = workflow_action.keys()
        for workflow_variable, variable_node_text in sorted(six.iteritems(workflow_action)):
          variable_type = "string" # Somewhat bad, should find a better way
          if workflow_variable.find('time') >= 0:
            variable_type = "date"
          if workflow_variable.find('language_revs') >= 0: # XXX specific to cps
            variable_type = "dict"
          if variable_node_text is None:
            variable_type = 'None'
          variable_node = SubElement(workflow_node, workflow_variable,
                                     attrib=dict(type=variable_type))
          if variable_type != 'None':
            variable_node_text = str(variable_node_text)
            if six.PY2:
              variable_node_text = six.text_type(str(variable_node_text), 'utf-8')
            variable_node.text = variable_node_text

            if workflow_variable == 'time':
              time = variable_node.text
            elif workflow_variable == 'actor':
              actor = variable_node.text

        if six.PY2 and isinstance(actor, six.text_type):
          actor = actor.encode('utf-8')
        workflow_transition_id = workflow_id + time + actor
        if six.PY3:
          workflow_transition_id = workflow_transition_id.encode()
        workflow_node.attrib['id'] = sha1(workflow_transition_id).hexdigest()

  # We should now describe security settings
  for user_role in self.get_local_roles():
    local_role_node = SubElement(object, 'local_role',
                                 attrib=dict(id=user_role[0], type='tokens'))
    #convert local_roles in string because marshaller can't do it
    role_list = []
    for role in user_role[1]:
      if six.PY2 and isinstance(role, six.text_type):
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
  return bytes2str(etree.tostring(root, encoding='utf-8',
                        xml_declaration=True, pretty_print=True))

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

  return bytes2str(etree.tostring(root, encoding='utf-8',
                        xml_declaration=xml_declaration, pretty_print=True))

## The code below was initially from OFS.XMLExportImport
from six import string_types as basestring
from ZODB.serialize import referencesf
from ZODB.ExportImport import TemporaryFile, export_end_marker
from ZODB.utils import p64
from ZODB.utils import u64
from functools import partial
from inspect import getargspec
from OFS import ObjectManager
from . import ppml

magic=b'<?xm' # importXML(jar, file, clue)}

def reorderPickle(jar, p):
    try:
        from ZODB._compat import Unpickler, Pickler
    except ImportError: # BBB: ZODB 3.10
        from ZODB.ExportImport import Unpickler, Pickler
    from ZODB.ExportImport import Ghost, persistent_id

    oids = {}
    storage = jar._storage
    new_oid = storage.new_oid
    store = storage.store

    def persistent_load(ooid,
                        Ghost=Ghost,
                        oids=oids, wrote_oid=oids.__contains__,
                        new_oid=storage.new_oid):

        "Remap a persistent id to an existing ID and create a ghost for it."
        if isinstance(ooid, tuple): ooid, klass = ooid
        else: klass=None

        try:
          Ghost=Ghost()
          Ghost.oid=ooid
        except TypeError:
          Ghost=Ghost(ooid)
        return Ghost

    # Reorder pickle by doing I/O
    pfile = BytesIO(p)
    unpickler=Unpickler(pfile)
    unpickler.persistent_load=persistent_load

    newp=BytesIO()
    pickler = OrderedPickler(newp, 3)
    pickler.persistent_id=persistent_id

    classdef = unpickler.load()
    obj = unpickler.load()
    pickler.dump(classdef)
    pickler.dump(obj)

    if 0: # debug
      debugp = BytesIO()
      debugpickler = OrderedPickler(debugp, 3)
      debugpickler.persistent_id = persistent_id
      debugpickler.dump(obj)
      import pickletools
      print(debugp.getvalue())
      print(pickletools.dis(debugp.getvalue()))

    p=newp.getvalue()
    return obj, p

def _mapOid(id_mapping, oid):
    idprefix = str(u64(oid))
    id = id_mapping[idprefix]
    old_aka = encodebytes(oid)[:-1]
    aka=encodebytes(p64(long_(id)))[:-1]  # Rebuild oid based on mapped id
    id_mapping.setConvertedAka(old_aka, aka)
    return idprefix+'.', id, aka

def XMLrecord(oid, plen, p, id_mapping):
    # Proceed as usual
    f = BytesIO(p)
    u = ppml.ToXMLUnpickler(f)
    u.idprefix, id, aka = _mapOid(id_mapping, oid)
    p = u.load(id_mapping=id_mapping).__str__(4)
    if f.tell() < plen:
        p=p+u.load(id_mapping=id_mapping).__str__(4)
    String='  <record id="%s" aka="%s">\n%s  </record>\n' % (id, bytes2str(aka), p)
    return String

def exportXML(jar, oid, file=None):
    # For performance reasons, exportXML does not use 'XMLrecord' anymore to map
    # oids. This requires to initialize MinimalMapping.marked_reference before
    # any string output, i.e. in ppml.Reference.__init__
    # This also fixed random failures when DemoStorage is used, because oids
    # can have values that have a shorter representation in 'repr' instead of
    # 'base64' (see ppml.convert) and ppml.String does not support this.
    load = jar._storage.load
    if 'version' in getargspec(load).args: # BBB: ZODB<5 (TmpStore)
        load = partial(load, version='')
    pickle_dict = {oid: None}
    max_cache = [1e7] # do not cache more than 10MB of pickle data
    def getReorderedPickle(oid):
        p = pickle_dict[oid]
        if p is None:
            p = load(oid)[0]
            p = reorderPickle(jar, p)[1]
            if len(p) < max_cache[0]:
                max_cache[0] -= len(p)
                pickle_dict[oid] = p
        return p

    # Sort records and initialize id_mapping
    id_mapping = ppml.MinimalMapping()
    reordered_oid_list = [oid]
    for oid in reordered_oid_list:
        _mapOid(id_mapping, oid)
        for oid in referencesf(getReorderedPickle(oid)):
            if oid not in pickle_dict:
                pickle_dict[oid] = None
                reordered_oid_list.append(oid)

    # Do real export
    if file is None:
        file = TemporaryFile(mode='w')
    elif isinstance(file, basestring):
        file = open(file, 'w')
    write = file.write
    write('<?xml version="1.0"?>\n<ZopeData>\n')
    for oid in reordered_oid_list:
        p = getReorderedPickle(oid)
        write(XMLrecord(oid, len(p), p, id_mapping))
    write('</ZopeData>\n')
    return file

class zopedata:
    def __init__(self, parser, tag, attrs):
        self.file=parser.file
        write=self.file.write
        write(b'ZEXP')

    def append(self, data):
        file=self.file
        write=file.write
        pos=file.tell()
        file.seek(pos)
        write(data)

def start_zopedata(parser, tag, data):
    return zopedata(parser, tag, data)

def save_zopedata(parser, tag, data):
    file=parser.file
    write=file.write
    pos=file.tell()
    file.seek(pos)
    write(export_end_marker)

def save_record(parser, tag, data):
    file=parser.file
    write=file.write
    pos=file.tell()
    file.seek(pos)
    a=data[1]
    if 'id' in a: oid=a['id']
    oid=p64(int(oid))
    v=b''
    for x in data[2:]:
        v=v+x
    l=p64(len(v))
    v=oid+l+v
    return v

import xml.parsers.expat
def importXML(jar, file, clue=''):
    if isinstance(file, str):
        with open(file, 'rb') as f:
          data = f.read()
    else:
        data = file.read()
    with TemporaryFile() as outfile:
        F=ppml.xmlPickler()
        F.end_handlers['record'] = save_record
        F.end_handlers['ZopeData'] = save_zopedata
        F.start_handlers['ZopeData'] = start_zopedata
        F.file=outfile
        # <patch>
        # Our BTs XML files don't declare encoding but have accented chars in them
        # So we have to declare an encoding but not use unicode, so the unpickler
        # can deal with the utf-8 strings directly
        p=xml.parsers.expat.ParserCreate('utf-8')
        if six.PY2:
          p.returns_unicode = False
        # </patch>
        p.CharacterDataHandler=F.handle_data
        p.StartElementHandler=F.unknown_starttag
        p.EndElementHandler=F.unknown_endtag
        r=p.Parse(data)
        outfile.seek(0)
        return jar.importFile(outfile, clue)

customImporters = {
  magic: importXML
}
