# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush-Tiwari <ayush.tiwari@nexedi.com>
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

import gc
import os
import posixpath
import transaction
import imghdr
import tarfile
import time
import hashlib
import fnmatch
import re
import threading
import pprint

from copy import deepcopy
from collections import defaultdict
from cStringIO import StringIO
from OFS.Image import Pdata
from lxml.etree import parse
from urllib import quote, unquote
from OFS import SimpleItem, XMLExportImport
from datetime import datetime
from itertools import chain
from operator import attrgetter
from persistent.list import PersistentList
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from zLOG import LOG, INFO, WARNING

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Core.Folder import Folder
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.PythonScript import PythonScript
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.Globals import Persistent, PersistentMapping
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.patches.ppml import importXML
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter

customImporters = {
    XMLExportImport.magic: importXML,
    }

CACHE_DATABASE_PATH = None
try:
  if int(os.getenv('ERP5_BT5_CACHE', 0)):
    from App.config import getConfiguration
    import gdbm
    instancehome = getConfiguration().instancehome
    CACHE_DATABASE_PATH = os.path.join(instancehome, 'bt5cache.db')
except TypeError:
  pass
cache_database = threading.local()
_MARKER = []

SEPARATELY_EXPORTED_PROPERTY_DICT = {
  # For objects whose class name is 'class_name', the 'property_name'
  # attribute is removed from the XML export, and the value is exported in a
  # separate file, with extension specified by 'extension'.
  # 'extension' must be None for auto-detection.
  #
  # class_name: (extension, unicode_data, property_name),
  "Document Component":  ("py",   0, "text_content"),
  "DTMLDocument":        (None,   0, "raw"),
  "DTMLMethod":          (None,   0, "raw"),
  "Extension Component": ("py",   0, "text_content"),
  "File":                (None,   0, "data"),
  "Image":               (None,   0, "data"),
  "OOoTemplate":         ("oot",  1, "_text"),
  "PDF":                 ("pdf",  0, "data"),
  "PDFForm":             ("pdf",  0, "data"),
  "Python Script":       ("py",   0, "_body"),
  "PythonScript":        ("py",   0, "_body"),
  "Spreadsheet":         (None,   0, "data"),
  "SQL":                 ("sql",  0, "src"),
  "SQL Method":          ("sql",  0, "src"),
  "Test Component":      ("py",   0, "text_content"),
  "Test Page":           (None,   0, "text_content"),
  "Web Page":            (None,   0, "text_content"),
  "Web Script":          (None,   0, "text_content"),
  "Web Style":           (None,   0, "text_content"),
  "ZopePageTemplate":    ("zpt",  1, "_text"),
}


def _delObjectWithoutHook(obj, id):
  """OFS.ObjectManager._delObject without calling manage_beforeDelete."""
  ob = obj._getOb(id)
  if obj._objects:
    obj._objects = tuple([i for i in obj._objects if i['id'] != id])
  obj._delOb(id)
  try:
    ob._v__object_deleted__ = 1
  except:
    pass


def _recursiveRemoveUid(obj):
  """Recusivly set uid to None, to prevent (un)indexing.
  This is used to prevent unindexing real objects when we delete subobjects on
  a copy of this object.
  """
  if getattr(aq_base(obj), 'uid', _MARKER) is not _MARKER:
    obj.uid = None
    # Make all objects and sub-object un-indexable
    # XXX: Should be moved into another function or change the name and desc
    # of this function
    obj.isIndexable = ConstantGetter('isIndexable', value=False)
  for subobj in obj.objectValues():
    _recursiveRemoveUid(subobj)


# New BusinessItem addition function
def manage_addBusinessItem(self, item_path='', item_sign=1, item_layer=0, *args, **kw):
  # Create BusinessItem object container
  c = BusinessItem(item_path, item_sign, item_layer)

  return c


# New BusinessPropertyItem addition function
def manage_addBusinessPropertyItem(self, item_path='', item_sign=1, item_layer=0, *args, **kw):
  # Create BusinessPathItem object container
  c = BusinessPropertyItem(item_path, item_sign, item_layer)

  return c

# New BusinessPatchItem addition function
def manage_addBusinessPatchItem(self, item_path='', item_sign=1, item_layer=0, *args, **kw):
  # Create BusinessPatchItem object container
  c = BusinessPatchItem(item_path, item_sign, item_layer)

  return c

class BusinessManager(Folder):

  """Business Manager is responsible for saving objects and properties in
  an ERP5Site. Everything will be saved just via path"""

  meta_type = 'ERP5 Business Manager'
  portal_type = 'Business Manager'
  add_permission = Permissions.AddPortalContent
  allowed_types = ('Business Item',
                   'Business Property Item',
                   'Business Patch item',)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  template_format_version = 3

  # Factory Type Information
  factory_type_information = \
    {    'id'             : portal_type
       , 'meta_type'      : meta_type
       , 'icon'           : 'file_icon.gif'
       , 'product'        : 'ERP5Type'
       , 'factory'        : ''
       , 'type_class'     : 'BusinessManager'
       , 'immediate_view' : 'BusinessManager_view'
       , 'allow_discussion'     : 1
       , 'allowed_content_types': ('Business Item',
                                    'Business Property Item',
                                    )
       , 'filter_content_types' : 1
    }


  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
                      PropertySheet.Base,
                      PropertySheet.XMLObject,
                      PropertySheet.SimpleItem,
                      PropertySheet.CategoryCore,
                      PropertySheet.Version,
                    )

  def getShortRevision(self):
    return None

  def getVersion(self):
    # Override the getter because currently we don't migrate the version, and
    # this is used to find missing dependency list
    return '5.4.7'

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBuildingState')
  def getBuildingState(self, default=None, id_only=1):
    """
      Returns the current state in building
    """
    portal_workflow = getToolByName(self, 'portal_workflow')
    wf = portal_workflow.getWorkflowById(
                        'business_manager_building_workflow')
    return wf._getWorkflowStateOf(self, id_only=id_only )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInstallationState')
  def getInstallationState(self, default=None, id_only=1):
    """
      Returns the current state in installation
    """
    portal = self.getPortalObject()
    portal_workflow = portal.portal_workflow
    wf = portal_workflow.getWorkflowById(
                         'business_manager_installation_workflow')
    return wf._getWorkflowStateOf(self, id_only=id_only )

  def changeBuildingStatetoModified(self):
    """
    Change building_state to 'modified'. This is needed specifically as we want
    to update the building state even if we change any sub-objects(Business Item
    or Business Property Item) of Business Manager.
    """
    portal_workflow = self.getPortalObject().portal_workflow
    wf = portal_workflow._getOb('business_manager_building_workflow')

    wf._executeMetaTransition(self, 'modified')

  def applytoERP5(self, DB):
    """Apply the flattened/reduced Business Manager to the DB"""
    portal = self.getPortalObject()
    pass

  def _clean(self):
    """
      Clean built information.
      Remove all the built sub-objects from Business Item or Business Property
      Item.
    """
    for item in self.objectValues():
      if item.getPortalType() == 'Business Item':
        # Delete the sub-object
        id_list = [l for l in item.objectIds()]
        if id_list:
          item.manage_delObjects(ids=id_list)
      elif item.getPortalType() == 'Business Property Item':
        # Add empty property item_property_name, value and type
        # XXX: Shouldn't we check if the properties exist and then just delete
        # them ?
        item.setProperty('item_property_name', '')
        item.setProperty('item_property_value', '')
        item.setProperty('item_property_type', '')

  security.declareProtected(Permissions.ManagePortal, 'preinstall')
  def preinstall(self, check_dependencies=1, **kw):
    """
    Preinstall for Business Manager comapres the installation state and returns
    the changes in a manner which can keep up compatibilty with the view we use
    in Business Template installation.

    This function calls `portal_templates.updateInstallationState` to get the
    change_list.

    We don't care of check_dependencies here as this all would be taken care by
    `udpateInstallationState` iteself.
    """
    change_list = self.aq_parent.compareInstallationState([self])
    modified_object_list = {}
    for path in change_list:
      type_name = 'Business Item'
      if '#' in path[0]:
        type_name = 'Business Property Item'
        modified_object_list[path[0]] = [path[1], type_name]
    return modified_object_list

  security.declareProtected(Permissions.ManagePortal, 'clean')
  clean = _clean

  def _setTitle(self, value):
    """
    Override required due to bootstrap
    """
    self.title = value

  def getPathItemList(self):
    return self.objectValues()

  # XXX: Change into property
  security.declareProtected(Permissions.ManagePortal, 'getTemplateFormatVersion')
  def getTemplateFormatVersion(self):
    return self.template_format_version

  # XXX: Change into property
  def _setTemplateFormatVersion(self, value):
    self.template_format_version = int(value)

  def propertyMap(self):
    prop_map = super(BusinessManager, self).propertyMap()
    final_prop_map = prop_map+self._properties
    return final_prop_map

  def export(self, path=None, **kw):
    """
    Export the object as zexp file
    """
    if not self.getBuildingState() == 'built':
      raise ValueError, 'Manager not built properly'
    f = StringIO()

    self._p_jar.exportFile(self._p_oid, f)

    # XXX: Improve naming
    name = self.getTitle()
    name = posixpath.join(path, name)
    # XXX required due to overuse of os.path
    name = name.replace('\\', '/').replace(':', '/')
    name = quote(name + '.zexp')
    obj_path = name.replace('/', os.sep)

    f.seek(0)
    obj = f.read()

    object_path = os.path.join(path, obj_path)
    path = os.path.dirname(object_path)
    os.path.exists(path) or os.makedirs(path)
    f = open(object_path, 'wb')
    try:
      f.write(obj)
    finally:
      f.close()

  security.declareProtected(Permissions.ManagePortal, 'importFile')
  def importFile(self, path, connection=None):
    """
      Import Business Manager object and all attribute to current BM itself
    """
    if not connection:
      connection = self.aq_parent._p_jar
    file = open(path, 'rb')
    imported_manager = connection.importFile(file)
    self.title = imported_manager.title
    for obj in imported_manager.objectValues():
      delattr(obj, '__ac_local_roles__')
      # XXX: Donot merge this, needed just for migrated erp5_core
      try:
        self._setObject(obj.id, aq_base(obj))
      except Exception:
        pass
      obj.isIndexable = ConstantGetter('isIndexable', value=False)

  def __add__(self, other):
    """
    Adds the Business Item objects for the given Business Manager objects
    """
    # XXX: Still to define
    return self

  __radd__ = __add__

  def __sub__(self, other):
    """
    Override subtract to find difference b/w the values in different cases.
    """
    # Create the sha list for all path item list available in current object
    sha_list = [item.sha for item in self._path_item_list]
    # Reverse the sign of Business Item objects for the old Business Manager
    # Trying comparing/subtracting ZODB with old installed object
    for path_item in other._path_item_list:
      if path_item.sha in sha_list:
        self._path_item_list = [item for item
                                in self._path_item_list
                                if item.sha != path_item.sha]
      else:
        path_item.sign = -1
        self._path_item_list.append(path_item)

    return self

  __rsub__ = __sub__

  security.declareProtected(Permissions.ManagePortal, 'storeTemplateData')
  def storeTemplateData(self, isBuild=False, **kw):
    """
    Store data for objects in the ERP5.
    Create Business Item sub-objects after resolving the paths. Also, add
    layers to all Business Item objects
    """
    portal = self.getPortalObject()
    LOG('Business Manager', INFO, 'Storing Manager Data')

    to_delete_id_list = []
    for item in self.objectValues():

      # Only try to resolve the Business Item objects
      if item.getPortalType() != 'Business Item':
        continue

      item_path = item.getProperty('item_path')
      # Resolve the path and update sub-objects lists
      path_list = self._resolvePath(portal, [], item_path.split('/'))

      if len(path_list) == 1 and path_list[0] == item_path:
        continue
      else:
        item_sign = item.getProperty('item_sign')
        item_layer = item.getProperty('item_layer')
        # Create new Business Item objects with path in path_list and sign and
        # layer same as that of the path used for resolving to new paths.
        for path in path_list:
          path_item = self.newContent(portal_type='Business Item')
          path_item.edit(
            item_path=path,
            item_sign=item_sign,
            item_layer=item_layer
            )
        # Add Id of BusinessItem to be deleted as we do already have resolved
        # path and new sub-objects based on resolved paths
        to_delete_id_list.append(item.getId())

    # Now, delete the original Business Item(s) sub-object as we do have
    # Business Item created from resolved paths
    self.manage_delObjects(ids=to_delete_id_list)

  def _resolvePath(self, folder, relative_url_list, id_list):
    """
      For Business Manager, we expect to resolve the path incase we face
      paths which expect to include sub-objects.
      For example: 'portal_catalog/erp5_mysql_innodb/**' should only consider
      the sub-objects of the object mentioned, and create separate BusinessItem
      objects for all of them.

      This method calls itself recursively.

      The folder is the current object which contains sub-objects.
      The list of ids are path components. If the list is empty,
      the current folder is valid.
    """
    if len(id_list) == 0:
      return ['/'.join(relative_url_list)]
    id = id_list[0]
    if re.search('[\*\?\[\]]', id) is None:
      # If the id has no meta character, do not have to check all objects.
      obj = folder._getOb(id, None)
      if obj is None:
        raise AttributeError, "Could not resolve '%s' during business template processing." % id
      return self._resolvePath(obj, relative_url_list + [id], id_list[1:])
    path_list = []
    for object_id in fnmatch.filter(folder.objectIds(), id):
      if object_id != "":
        path_list.extend(self._resolvePath(
            folder._getOb(object_id),
            relative_url_list + [object_id], id_list[1:]))
    return path_list

  def getPathList(self):
    path_list = []
    for item in self.objectValues():
      path_list.append(item.getProperty('item_path'))
    return path_list

  def getPathItemDict(self):
    path_item_dict = {}
    # TODO: Handle error for BM with multiple items at same path
    for item in self.objectValues():
      path_item_dict[item.getProperty('item_path')] = item
    return path_item_dict

  def getBusinessItemByPath(self, path):
    path_item_dict = self.getPathItemDict()
    try:
      return path_item_dict[path]
    except KeyError:
      return

  def build(self, no_action=False, **kw):
    """Creates new values for business item from the values from
    OFS Database"""
    LOG('Business Manager', INFO, 'Building Business Manager')
    removable_sub_object_path_list = kw.get('removable_sub_object_path', [])
    removable_property_dict = kw.get('removable_property', {})
    # Now, we need to put a check here for returning whih objects should be
    # updated during rebuild of BM
    checkNeeded = kw.get('checkNeeded', False)
    # Build all paths if there is no check required(i.e, its a new build action)
    if not checkNeeded:
      if not no_action:
        self.storeTemplateData(isBuild=True, **kw)
        for path_item in self.objectValues():
          kwargs = {}
          item_path = path_item.getProperty('item_path')
          kwargs['removable_property_list'] = removable_property_dict.get(item_path, [])
          kwargs['remove_sub_objects'] = item_path in removable_sub_object_path_list
          path_item.build(self, **kwargs)
      return self
    else:
      item_path_list = kw.get('item_path_list', [])
      if item_path_list:
        for path in item_path_list:
          item = self.getBusinessItemByPath(path)
          item.build(self)
          return self

  def flattenBusinessManager(self):
    """
    Flattening a reduced Business Manager with two path p1 and p2 where p1 <> p2:

    flatten([(p1, s1, l1, v1), (p2, s2, l2, v2)]) = [(p1, s1, 0, v1), (p2, s2, 0, v2)]
    A reduced Business Manager BT is said to be flattened if and only if:
    flatten(BT) = BT
    """
    pass

  def reduceBusinessManager(self):
    """
    Reduction is a function that takes a Business Manager as input and returns
    a smaller Business Manager by taking out values with lower priority layers.

    After taking out BusinessItem(s) with lower priority layer, we also go
    through arithmetic in case there are multiple number of BI at the higher layer

    Two path on different layer are reduced as a single path with the highest layer:

    If l1 > l2,
    reduce([(p, s, l1, (a, b, c)), (p, s, l2, (d, e))]) = [(p, s, l1, merge(a, b, c))]

    A Business Manager BT is said to be reduced if and only if:
    reduce(BT) = BT
    """
    path_list = self.getPathList()

    reduced_path_item_list = []

    # We separate the path list in the ones which are repeated and the ones
    # which are unique for the installation
    seen_path_list = set()
    unique_path_list = [x for x
                        in path_list
                        if x not in seen_path_list
                        and not seen_path_list.add(x)]

    # Create an extra dict for values on path which are repeated in the path list
    seen_path_dict = {path: [] for path in seen_path_list}

    for item in self.objectValues():
      if item.getProperty('item_path') in seen_path_list:
        # In case the path is repeated keep the path_item in a separate dict
        # for further arithmetic
        seen_path_dict[item.getProperty('item_path')].append(item)
      else:
        # If the path is unique, add them in the list of reduced Business Item
        reduced_path_item_list.append(item)

    # Reduce the values and get the merged result out of it
    for path, path_item_list in seen_path_dict.items():

      # Create separate list of list items with highest priority
      higest_priority_layer = max(path_item_list, key=attrgetter('item_layer')).item_layer
      prioritized_path_item = [path_item for path_item
                               in path_item_list
                               if path_item.item_layer == higest_priority_layer]

      # Separate the positive and negative sign path_item
      if len(prioritized_path_item) > 1:

        path_item_list_add = [item for item
                              in prioritized_path_item
                              if item.getProperty('item_sign') > 0]

        path_item_list_subtract = [item for item
                                   in prioritized_path_item
                                   if item.getProperty('item_sign') < 0]

        # XXX: TODO: Look at the correct merge
        raise ValueErrror('Recheck how this is gonna work')

        combined_added_path_item = reduce(lambda x, y: x+y, path_item_list_add)
        combined_subtracted_path_item = reduce(lambda x, y: x+y, path_item_list_subtract)

        added_value = combined_added_path_item.objectValues()
        subtracted_value = combined_subtracted_path_item.objectValues()

        if added_value != subtracted_value:
          # Append the arithmetically combined path_item objects in the final
          # reduced list after removing the intersection
          added_value, subtracted_value = \
                  self._simplifyValueIntersection(added_value, subtracted_value)

          combined_added_path_item.value = added_value
          combined_subtracted_path_item.value = subtracted_value

          # Append the path_item to the final reduced path_item_list after
          # doing required arithmetic on it. Make sure to first append
          # subtracted item because while installation, we need to first
          # uninstall the old object and then install new object at same path
          reduced_path_item_list.append(combined_subtracted_path_item)
          reduced_path_item_list.append(combined_added_path_item)

      else:
        reduced_path_item_list.append(prioritized_path_item[0])

    id_list = [l for l in self.objectIds()]
    for l in id_list:
      try:
        self._delObject(l)
      except Exception:
        # XXX: REMOVE/RECHEK BEFORE MERGE
        # The reason for doing this horrible workaround is to delete object
        # for 'portal_memcached/persistent_memcached_plugin' as it is not getting
        # deleted in 1st attempt with failure :
        # AttributeError: 'NoneType' object has no attribute 'getUid'
        self._delObject(l)

    for item in reduced_path_item_list:
      item.isIndexable = ConstantGetter('isIndexable', value=False)
      new_id = self.generateNewId()
      self._setObject(new_id, aq_base(item),
                                        suppress_events=True)

  def _simplifyValueIntersection(self, added_value, subtracted_value):
    """
    Returns values for the Business Item having same path and layer after
    removing the intersection of the values

    Parameters:
    added_value - Value for the Business Item having sign = +1
    subtracted_value - Value for Busienss Item having sign = -1
    """
    built_in_number_type = (int, long, float, complex)
    built_in_container_type = (tuple, list, dict, set)
    built_in_type_list = built_in_number_type + built_in_container_type

    # For ERP5 objects, we should return the added and subtracted values as it is
    if type(added_value).__name__ not in built_in_type_list and \
        type(subtracted_value).__name__ not in built_in_type_list:
      return added_value, subtracted_value

    # For all the values of container type, we remove the intersection
    added_value = [x for x in added_value if x not in subtracted_value]
    subtracted_value = [x for x in subtracted_value if x not in added_value]

    return added_value, subtracted_value

  def mergeBusinessPatchItem(self, item1, item2):
    """
    Merge two BusinessPatchItem at same layer and same sign.

    XXX: This function shouldn't be used at reduction, rather than during
    updating the installation_state, because we need to know all the states to
    be able to find out which patch needs to be used.

    Cases:
    1. Shouldn't matter if both have same new_value as we give preference to
    the final result and try to remove conflict as much as possible.
    2. If both have different old_value and different new_value, merge should
    return both of them and let the updateInstallationState process decide
    which one to apply and if needed, raise a conflict
    """
    pass

class BusinessItem(XMLObject):

  """Saves the path and values for objects, properties, etc, the
    attributes for a path configuration being:

    - item_path  (similar to an xpath expression)
        Examples of path :
          portal_type/Person
          portal_type/Person#title
          portal_type/Person#property_sheet?ancestor=DublinCore
          portal_type/Person#property_sheet?position=2
    - item_sign  (+1/-1)
    - item_layer (0, 1, 2, 3, etc.)
    - item_value (a set of pickable value in python)"""

  add_permission = Permissions.AddPortalContent
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  constructors = (manage_addBusinessItem,)
  portal_type = 'Business Item'
  meta_type = 'Business Item'
  icon = None
  isProperty = False
  isIndexable = False

  def _edit(self, item_path='', item_sign=1, item_layer=0, *args, **kw):
    """
    Overriden function so that we can update attributes for BusinessItem objects
    """

    super(BusinessItem, self)._edit(item_path=item_path,
                                    item_sign=item_sign,
                                    item_layer=item_layer,
                                    **kw)

    # Build the object here, if the item_path has been added/updated
    # XXX: We also need to add attribute to ensure that this doesn't happen
    # while in tests or while creating them on the fly
    if 'item_path' in self._v_modified_property_dict:
      self.build(self.aq_parent)

  def build(self, context, **kw):
    """
    Extract value for the given path from the OFS

    Three different situations to extract value:
    1. For paths which point directly to an object in OFS
    2. For paths which point to multiple objects inside a folder
    3. For paths which point to property of an object in OFS : In this case,
    we can have URL delimiters like ?, #, = in the path
    """
    LOG('Business Manager', INFO, 'Building Business Item')

    # Remove the old sub-objects if exisiting before building
    id_list = [l for l in self.objectIds()]
    if id_list:
      self.manage_delObjects(ids=id_list)

    p = context.getPortalObject()
    path = self.getProperty('item_path')
    obj = p.unrestrictedTraverse(path)
    obj = obj._getCopy(context)

    # We should remove the extra properties of object so that there
    # shouldn't be redundancy of the proeprties
    removable_property_list = kw.get('removable_property_list', [])

    # We should also add extra parameter to remove sub-objects by removing
    # `_tree` for any erp5 object. This way we can have control over adding
    # sub-objects as new Business Item objects
    remove_sub_objects = kw.get('remove_sub_objects', False)
    if remove_sub_objects:
      removable_property_list.append('_tree')
    keep_workflow_history = False
    # For portal_components object, we need validation_history
    if self.getProperty('item_path').startswith('portal_components'):
      keep_workflow_history = True
    obj = self.removeProperties(obj,
                                1,
                                properties=removable_property_list,
                                keep_workflow_history=keep_workflow_history,
                                )
    obj = obj.__of__(context)
    # XXX: '_recursiveRemoveUid' is not working as expected
    _recursiveRemoveUid(obj)
    obj = aq_base(obj)
    obj.isIndexable = ConstantGetter('isIndexable', value=False)
    new_id = self.generateNewId()
    self._setObject(new_id, obj, suppress_events=True)

  def _resolvePath(self, folder, relative_url_list, id_list):
    """
    We go through 3 types of paths:

    1. General path we find in erp5 for objects
    Ex: portal_type/Person
    In this case, we import/export the object on the path

    2. Path where we consider saving sub-objects also, in that case we create
    new BusinessItem for those objects
    Ex: portal_catalog/erp5_mysql_innodb/**
    This should create BI for the catalog methods sub-objects present in the
    erp5_catalog.

    This method calls itself recursively.

    The folder is the current object which contains sub-objects.
    The list of ids are path components. If the list is empty,
    the current folder is valid.
    """
    if len(id_list) == 0:
      return ['/'.join(relative_url_list)]
    id = id_list[0]
    if re.search('[\*\?\[\]]', id) is None:
      # If the id has no meta character, do not have to check all objects.
      obj = folder._getOb(id, None)
      if obj is None:
        raise AttributeError, "Could not resolve '%s' during BusinessItem processing." % id
      return self._resolvePath(obj, relative_url_list + [id], id_list[1:])
    path_list = []
    for object_id in fnmatch.filter(folder.objectIds(), id):
      if object_id != "":
        path_list.extend(self._resolvePath(
            folder._getOb(object_id),
            relative_url_list + [object_id], id_list[1:]))
    return path_list

  def install(self, context, *args):
    """
    Set the value to the defined path.
    """
    # In case the path denotes property, we create separate object for
    # ObjectTemplateItem and handle the installation there.
    try:
      portal = context.getPortalObject()
    except AttributeError:
      # This is a possibility during bootstrap where the context is not an
      # erp5 object but a dynamic class
      if args:
        portal = args[0]
      else:
        raise AttributeError('No portal object found')

    path = self.getProperty('item_path')
    path_list = path.split('/')
    container_path = path_list[:-1]
    object_id = path_list[-1]
    try:
      container = self.unrestrictedResolveValue(portal, container_path)
    except KeyError:
      # parent object can be set to nothing, in this case just go on
      container_url = '/'.join(container_path)
    old_obj = container._getOb(object_id, None)
    # delete the old object before installing a new object
    if old_obj:
      container._delObject(object_id)
    # Create a new object only if sign is +1
    # If sign is +1, set the new object on the container
    if int(self.getProperty('item_sign')) == 1:
      # install object
      obj = self.objectValues()[0]
      obj = obj._getCopy(container)

      # Update the type_provider_list if needed
      # XXX: Find a way to fiter and do this check only for tool, so that we
      # don't lose on perfomance in checking this everytime
      if interfaces.ITypeProvider.providedBy(obj):
        type_container_id = obj.id
        types_tool = portal.portal_types
        if type_container_id not in types_tool.type_provider_list:
          types_tool.type_provider_list = tuple(types_tool.type_provider_list) + \
                                          (type_container_id,)

      # Before making `obj` a sub-object of `container`, we should the acquired
      # roles on obj
      obj.isIndexable = ConstantGetter('isIndexable', value=False)
      delattr(obj, '__ac_local_roles__')
      container._setObject(object_id, obj, suppress_events=True)
      obj = container._getOb(object_id)
      skin_tool = portal.portal_skins
      if obj.aq_parent.meta_type == 'CMF Skins Tool':
        registerSkinFolder(skin_tool, obj)

  def unrestrictedResolveValue(self, context=None, path='', default=_MARKER,
                               restricted=0):
    """
      Get the value without checking the security.
      This method does not acquire the parent.
    """
    if isinstance(path, basestring):
      stack = path.split('/')
    else:
      stack = list(path)
    stack.reverse()
    if stack:
      if context is None:
        portal = aq_inner(self.getPortalObject())
        container = portal
      else:
        container = context

      if restricted:
        validate = getSecurityManager().validate

      while stack:
        key = stack.pop()
        try:
          value = container[key]
        except KeyError:
          LOG('BusinessManager', WARNING,
              'Could not access object %s' % (path,))
          if default is _MARKER:
            raise
          return default

        if restricted:
          try:
            if not validate(container, container, key, value):
              raise Unauthorized('unauthorized access to element %s' % key)
          except Unauthorized:
            LOG('BusinessManager', WARNING,
                'access to %s is forbidden' % (path,))
          if default is _MARKER:
            raise
          return default

        container = value

      return value
    else:
      return context

  def __add__(self, other):
    """
    Add the values from the path when the path is same for 2 objects
    """
    if self.path != other.path:
      raise ValueError, "BusinessItem are incommensurable, have different path"
    elif self.sign != other.sign:
      raise ValueError, "BusinessItem are incommensurable, have different sign"
    else:
      self.value = self._mergeValue(value_list=[self.value, other.value])
      return self

  __radd__ = __add__

  def _mergeValue(self, value_list):
    """
    Merge value in value list

    merge(a, b, c) : A monotonic commutative function that depends on the
    type of a, b and c:

    if a, b and c are sets, merge = union
    if a, b and c are lists, merge = ordered concatenation
    if a, b and c are objects, merge = the object created the last
    else merge = MAX
    """
    builtin_number_type = (int, long, float, complex)

    # Now, consider the type of both values
    if all(isinstance(x, builtin_number_type) for x in value_list):
      merged_value = max(value_list)
    elif all(isinstance(x, set) for x in value_list):
      merged_value = set(chain.from_iterable(value_list))
    elif all(isinstance(x, list) for x in value_list):
      merged_value = list(chain.from_iterable(value_list))
    elif all(isinstance(x, tuple) for x in value_list):
      merged_value = tuple(chain.from_iterable(value_list))
    else:
      # In all other case, check if the values are objects and then take the
      # objects created last.

      # XXX: Should we go with creation date or modification_date ??
      # TODO:
      # 1. Add check that the values are ERP5 objects
      # 2. In case 2 maximum values are created at same time, prefer one with
      # higher priority layer
      merged_value = max([max(value, key=attrgetter('creation_date'))
                         for value in value_list],
                         key=attrgetter('creation_date'))

    return merged_value

  def removeProperties(self,
                       obj,
                       export,
                       properties=[],
                       keep_workflow_history=False,
                       keep_workflow_history_last_history_only=False):
    """
    Remove unneeded properties for export
    """
    obj._p_activate()
    klass = obj.__class__
    classname = klass.__name__
    attr_set = {'_dav_writelocks', '_filepath', '_owner', '_related_index',
                'last_id', 'uid',
                '__ac_local_roles__', '__ac_local_roles_group_id_dict__'}
    if properties:
      for prop in properties:
        if prop.endswith('_list'):
          prop = prop[:-5]
        attr_set.add(prop)
    if export:
      if keep_workflow_history_last_history_only:
        self._removeAllButLastWorkflowHistory(obj)
      elif not keep_workflow_history:
        attr_set.add('workflow_history')
      # PythonScript covers both Zope Python scripts
      # and ERP5 Python Scripts
      if isinstance(obj, PythonScript):
        attr_set.update(('func_code', 'func_defaults', '_code',
                         '_lazy_compilation', 'Python_magic'))
        for attr in 'errors', 'warnings', '_proxy_roles':
          if not obj.__dict__.get(attr, 1):
            delattr(obj, attr)
      elif classname in ('File', 'Image'):
        attr_set.update(('_EtagSupport__etag', 'size'))
      elif classname == 'SQL' and klass.__module__ == 'Products.ZSQLMethods.SQL':
        attr_set.update(('_arg', 'template'))
      elif interfaces.IIdGenerator.providedBy(obj):
        attr_set.update(('last_max_id_dict', 'last_id_dict'))
      elif classname == 'Types Tool' and klass.__module__ == 'erp5.portal_type':
        attr_set.add('type_provider_list')

    for attr in obj.__dict__.keys():
      if attr in attr_set or attr.startswith('_cache_cookie_'):
        try:
          delattr(obj, attr)
        except AttributeError:
          # XXX: Continue in cases where we want to delete some properties which
          # are not in attribute list
          # Raise an error
          continue

    if classname == 'PDFForm':
      if not obj.getProperty('business_template_include_content', 1):
        obj.deletePdfContent()
    return obj

  def getBusinessPath(self):
    return self.getProperty('item_path')

  def getBusinessPathSign(self):
    return self.getProperty('item_sign', 1)

  def getBusinessPathLayer(self):
    return self.getProperty('item_layer', 1)

  def getParentBusinessManager(self):
    return self.aq_parent

class BusinessPropertyItem(XMLObject):

  """Class to deal with path(s) which refer to property of an ERP5 object.
  Used to store property name, type and value for a given object and property"""

  add_permission = Permissions.AddPortalContent
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  portal_type = 'Business Property Item'
  meta_type = 'Business Property Item'
  icon = None
  isIndexable = False
  isProperty = True
  constructors = (manage_addBusinessPropertyItem,)

  def _edit(self, item_path='', item_sign=1, item_layer=0, *args, **kw):
    """
    Overriden function so that we can update attributes for BusinessItem objects
    """
    return super(BusinessPropertyItem, self)._edit(item_path=item_path,
                                                   item_sign=item_sign,
                                                   item_layer=item_layer,
                                                   **kw)

  def build(self, context, **kw):
    p = context.getPortalObject()
    path = self.getProperty('item_path')
    relative_url, property_id = path.split('#')
    obj = p.unrestrictedTraverse(relative_url)
    property_value = obj.getProperty(property_id)
    property_type = obj.getPropertyType(property_id)
    self.setProperty('item_property_name', property_id)
    self.setProperty('item_property_type', property_type)
    self.setProperty('item_property_value', property_value)

  def install(self, context, *args):
    # Get portal object
    try:
      portal = context.getPortalObject()
    except AttributeError:
      # This is a possibility during bootstrap where the context is not an
      # erp5 object but a dynamic class
      if args:
        portal = args[0]
      else:
        raise AttributeError('No portal object found')

    path = self.getProperty('item_path')
    relative_url, property_id = path.split('#')
    obj = portal.unrestrictedTraverse(relative_url)
    property_name = self.getProperty('item_property_name')
    property_type = self.getProperty('item_property_type')
    property_value = self.getProperty('item_property_value')
    # First remove the property from the existing path and keep the default
    # empty, and update only if the sign is +1
    obj._delPropValue(property_name)
    # Remove the '_list' from the end of property_name. This is required because
    # of the way _setProperty is defined where if the type is list_type, it
    # explicitly adds '_list' at the end of property_name before trying to call
    # the accessor
    if property_name.endswith('_list'):
      property_name = property_name[:-5]

    # XXX: Explicit addition of property_type for 'type_workflow' property on
    # 'ERP5Type' objects. This is required as we have created an explicit
    # property outside of property sheet for ERP5Type objects, but at the same
    # time, the object(s) also have property sheet for them. Since, there is no
    # functions like _setProperty, hasProperty, etc to combine both of them
    # we have to end up using explicit mention of 'list' property_value here
    # 1. Other option can be to override hasProperty or _setProperty for ERP5Type
    # object and write it so that it can handle both _properties attribute as
    # well as accessor holders generated from property sheet(s).
    # 2. After that we can use hasProperty here for objects to check their
    # property_type and then just use the generic '_setProperty' function.
    # XXX: For now, we just put this explicitly/hard-code
    if property_name == 'type_workflow':
      property_type = 'multiple selection'

    if int(self.getProperty('item_sign')) == 1:
      obj._setProperty(property_name, property_value, property_type)

  def getBusinessPath(self):
    return self.getProperty('item_path')

  def getBusinessPathSign(self):
    return self.getProperty('item_sign', 1)

  def getBusinessPathLayer(self):
    return self.getProperty('item_layer', 1)

  def getParentBusinessManager(self):
    return self.aq_parent

  def getBusinessItemPropertyName(self):
    return self.getProperty('item_property_name')

  def getBusinessItemPropertyType(self):
    return self.getProperty('item_property_type')

  def getBusinessItemPropertyValue(self):
    return self.getProperty('item_property_value')

class BusinessPatchItem(XMLObject):

  """
  Business Item for saving patch and diff. This will help us to create a diff or
  patch between the old value and current value.

  item_sign -- +1 or -1
  item_path -- extended OFS path (equivalent to deepdiff path)
    ex. a/b/c#x/y/z:int/w
  item_layer -- layer
  old -- old value
  new -- new value
  dependency_list -- a list of bt5 identifiers useful to rebuild the
                    BusinesTemplatePatchItem instance
  preserved_list -- a list of bt5 identifiers useful to rebuild the
                    BusinesTemplatePatchItem instance
                    (XXX: We don't use `preserved_list` for now)

  Business Patch Item can be both PathItem or PropertyItem, but both of them are
  quite distinguishable, so we prefer not to use them as base class for it.
  """
  # CMF Type definition
  portal_type = 'Business Patch Item'
  meta_type = 'Business Patch Item'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  icon = None
  isIndexable = False
  isProperty = False
  constructors = (manage_addBusinessPatchItem,)
  allowed_types = ('Business Item', 'Business Property Item',)

  def _edit(self, **kw):
    """
    Override _edit to create Business Item and BusinessPropertyItem for old and
    new value
    """
    dependency_list = kw.get('dependency_list', self.getProperty('dependency_list'))

    # Raise error if no dependency_list, this way we ensure there are no useless
    # patch_item objects
    if not dependency_list:
      raise ValueError('Please add dependency to the Business Patch Item')

    super(BusinessPatchItem, self)._edit(**kw)

  def build(self, context, **kw):
    """
    Build should update the old and new value
    """
    portal = self.getPortalObject()
    portal_templates = portal.portal_templates

    item_path = self.getProperty('item_path')
    item_layer = self.getProperty('item_layer')
    item_sign = self.getProperty('item_sign')

    # Remove old objects if it exists
    old_id_list = [l for l in self.objectIds()]
    if old_id_list:
      self.manage_delObjects(ids=old_id_list)

    # Get the dependency Business Manager
    dependency_list = self.getProperty('dependency_list')
    if dependency_list:
      dependency_title = dependency_list[0]
      dependency_bm = portal_templates.getInstalledBusinessManager(dependency_title)
      if not dependency_bm:
        raise ValueError('Missing Installed Business Manager for dependecy_list \
                          which is required to build')

    # Use item_path to determine if we need to create Business Item or
    # Business Property Item for storing old and new values
    if '#' in item_path:
      # Create new_prop_item and build it from ZODB
      new_item = self.newContent(portal_type='Business Property Item',
                                      item_path=item_path,
                                      item_layer=item_layer,
                                      item_sign=item_sign,
                                      id='new_item')
      new_item.build(self)

    else:
      # Create new_item and build it from ZODB
      new_item = self.newContent(portal_type='Business Item',
                                item_path=item_path,
                                item_layer=item_layer,
                                item_sign=item_sign,
                                id='new_item')
      new_item.build(self)

    updated_id = 'old_item'
    # Copy old item/property item from the item at similar path in dependency_bm
    dependency_item = dependency_bm.getBusinessItemByPath(item_path)

    # Raise if there is no item exisiting in dependency Business Manager
    if not dependency_item:

      raise ValueError('No %s exist at path %s in installed version of %s'
                          % ( new_item.getPortalType(),
                              item_path,
                              dependency_title,))

    cp_data = dependency_bm.manage_copyObjects([dependency_item.getId()])
    new_id = self.manage_pasteObjects(cp_data)[0]['new_id']
    self.manage_renameObject(id=new_id, new_id=updated_id)

    # Get the copied object and update the properties
    old_item = self._getOb(updated_id)
    old_item.setProperty('item_layer', item_layer)
    old_item.setProperty('item_sign', item_sign)

    # Commit the transaction
    transaction.commit()

  def getOldValue(self):
    """
    Returns old value for the BusinessPatchItem
    """
    old_item = self._getOb('old_item')[0]
    if old_item.getPortalType() == 'Business Item':
      return old_item.objectValues()
    else:
      return old_item.getProperty('item_property_value')

  def getNewValue(self, build=False):
    """
    Returns new value for the given BusinessPatchItem
    """
    old_item = self._getOb('new_item')
    if old_item.getPortalType() == 'Business Item':
      return old_item.objectValues()[0]
    else:
      return old_item.getProperty('item_property_value')

  def getDiff(self, patch_format='deepdiff'):
    """
    Use diff tool to find the diff between two values

    XXX: For now we display the json format of the patched diff
    """
    patch = self.getPatchObject(patch_format)
    if patch_format == 'deepdiff':
      return patch.asDeepDiffPatch().json
    else:
      # For json-patch object
      return patch.asJSONPatch().to_string()

  def getPatchObject(self, patch_format='deepdiff'):
    portal = self.getPortalObject()
    diff_tool = portal.portal_diff

    old_item = self._getOb('old_item')
    new_item = self._getOb('new_item')

    if (old_item.getPortalType() == new_item.getPortalType() == 'Business Item'):
      old = old_item.objectValues()[0]
      new = new_item.objectValues()[0]
    else:
      old = old_item.getProperty('item_property_value')
      new = new_item.getProperty('item_property_value')
    patch = diff_tool.diffPortalObject(old=old,
                                       new=new,
                                       patch_format=patch_format
                                       )
    return patch

  def install(self, context, *args):
    """
    Install will call the apply function which puts the new value at the
    path mentioned while checking if the old value exists.
    """
    # Installation is basically running installation on the new_value
    self.new_value.install(context)

  def applyPatch(self):
    """
    Apply the new value by removing the old value. Also, show conflict in case
    the value at old_installation_state is not same as the old value.
    """
    pass

def registerSkinFolder(skin_tool, skin_folder):
  request = skin_tool.REQUEST
  # XXX: Getting parameter from request instead of dialog is bad
  # XXX: This is even non consistent with rest of parameters selected by user
  #      (like update_translation or update_catalog)
  register_skin_selection = request.get('your_register_skin_selection', 1)
  reorder_skin_selection = request.get('your_reorder_skin_selection', 1)
  skin_layer_list = request.get('your_skin_layer_list',
                                skin_tool.getSkinSelections())

  skin_folder_id = skin_folder.getId()

  try:
    skin_selection_list = skin_folder.getProperty(
                 'business_template_registered_skin_selections',
                 skin_tool.getSkinSelections()
                 )
  except AttributeError:
    skin_selection_list = skin_tool.getSkinSelections()

  if isinstance(skin_selection_list, basestring):
    skin_selection_list = skin_selection_list.split()

  def skin_sort_key(skin_folder_id):
    obj = skin_tool._getOb(skin_folder_id, None)
    if obj is None:
      return 0, skin_folder_id
    return -obj.getProperty('business_template_skin_layer_priority',
      obj.meta_type == 'Filesystem Directory View' and -1 or 0), skin_folder_id

  for skin_name in skin_selection_list:

    if (skin_name not in skin_tool.getSkinSelections()) and \
                                          register_skin_selection:
      createSkinSelection(skin_tool, skin_name)
      # add newly created skins to list of skins we care for
      skin_layer_list.append(skin_name)

    selection = skin_tool.getSkinPath(skin_name) or ''
    selection_list = selection.split(',')
    if (skin_folder_id not in selection_list):
      selection_list.insert(0, skin_folder_id)
    if reorder_skin_selection:
      # Sort by skin priority and ID
      selection_list.sort(key=skin_sort_key)
    if (skin_name in skin_layer_list):
      skin_tool.manage_skinLayers(skinpath=selection_list,
                                  skinname=skin_name, add_skin=1)
      skin_tool.getPortalObject().changeSkin(None)

def createSkinSelection(skin_tool, skin_name):
  # This skin selection does not exist, so we create a new one.
  # We'll initialize it with all skin folders, unless:
  #  - they explictly define a list of
  #    "business_template_registered_skin_selections", and we
  #    are not in this list.
  #  - they are not registered in the default skin selection
  skin_path = ''
  for skin_folder in skin_tool.objectValues():
    if skin_name in skin_folder.getProperty(
             'business_template_registered_skin_selections',
             (skin_name, )):
      if skin_folder.getId() in \
          skin_tool.getSkinPath(skin_tool.getDefaultSkin()):
        if skin_path:
          skin_path = '%s,%s' % (skin_path, skin_folder.getId())
        else:
          skin_path= skin_folder.getId()
  # add newly created skins to list of skins we care for
  skin_tool.addSkinSelection(skin_name, skin_path)
  skin_tool.getPortalObject().changeSkin(None)

def deleteSkinSelection(skin_tool, skin_name):
  # Do not delete default skin
  if skin_tool.getDefaultSkin() != skin_name:
    for skin_folder in skin_tool.objectValues():
      try:
        if skin_name in skin_folder.getProperty(
               'business_template_registered_skin_selections', ()):
          break
      except AttributeError:
        pass
    else:
      skin_tool.manage_skinLayers(chosen=[skin_name], del_skin=1)
      skin_tool.getPortalObject().changeSkin(None)

def unregisterSkinFolderId(skin_tool, skin_folder_id, skin_selection_list):
  for skin_selection in skin_selection_list:
    selection = skin_tool.getSkinPath(skin_selection)
    selection = selection.split(',')
    if (skin_folder_id in selection):
      selection.remove(skin_folder_id)
      skin_tool.manage_skinLayers(skinpath=tuple(selection),
                                  skinname=skin_selection, add_skin=1)
      deleteSkinSelection(skin_tool, skin_selection)
      skin_tool.getPortalObject().changeSkin(None)
