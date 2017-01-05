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

import fnmatch, re
import transaction
from copy import deepcopy
from collections import defaultdict
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.BusinessTemplate import ObjectTemplateItem
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Products.ERP5Type.Globals import Persistent, PersistentMapping

_MARKER = []

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
  for subobj in obj.objectValues():
    _recursiveRemoveUid(subobj)

class BusinessPackage(XMLObject):
    """
    New implementation of Business Templates
    """

    meta_type = 'ERP5 Business Package'
    portal_type = 'Business Package'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.BusinessPackage
                      )

    def _install(self):
      self._path_item.install(self)

    security.declareProtected(Permissions.ManagePortal, 'install')
    install = _install

    security.declareProtected(Permissions.ManagePortal, 'build')
    def build(self):
      """
      Should also export the objects from PathTemplateItem to their xml format
      """
      self.storePathData()
      self._path_item.build(self)

    security.declareProtected(Permissions.ManagePortal, 'storePathData')
    def storePathData(self):
      self._path_item = PathTemplatePackageItem(self._getTemplatePathList())

    security.declareProtected(Permissions.ManagePortal, 'getTemplatePathList')
    def _getTemplatePathList(self):
      result = tuple(self.getTemplatePathList())
      if result is None:
        result = ()
      return result

    security.declareProtected(Permissions.ManagePortal, 'export')
    def export(self):
      """
      Export the object
      """
      pass

class PathTemplatePackageItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id=None, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    for id in id_list:
      if id is not None and id != '':
        self._archive[id] = None
    id_list = self._archive.keys()
    self._archive.clear()
    self._path_archive = PersistentMapping()
    for id in id_list:
      self._path_archive[id] = None

  def _resolvePath(self, folder, relative_url_list, id_list):
    """
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

  def build(self, context, **kw):
    p = context.getPortalObject()
    keys = self._path_archive.keys()
    keys.sort()
    for path in keys:
      include_subobjects = 0
      if path.endswith("**"):
        include_subobjects = 1
      for relative_url in self._resolvePath(p, [], path.split('/')):
        obj = p.unrestrictedTraverse(relative_url)
        obj = obj._getCopy(context)
        obj = obj.__of__(context)
        _recursiveRemoveUid(obj)
        id_list = obj.objectIds()
        if hasattr(aq_base(obj), 'groups'):
          # we must keep groups because it's ereased when we delete subobjects
          groups = deepcopy(obj.groups)
        if len(id_list) > 0:
          if include_subobjects:
            self.build_sub_objects(obj, id_list, relative_url)
          for id_ in list(id_list):
            _delObjectWithoutHook(obj, id_)
        if hasattr(aq_base(obj), 'groups'):
          obj.groups = groups
        self._objects[relative_url] = obj
        obj.wl_clearLocks()

  def install(self, context, *args, **kw):
    kw['object_to_update'] = {}
    kw['force'] = 1
    super(PathTemplatePackageItem, self).install(context, trashbin=None, *args, **kw)

    # Regenerate local roles for all paths in this business template
    p = context.getPortalObject()
    portal_type_role_list_len_dict = {}
    update_dict = defaultdict(list)
    for path in self._objects:
      obj = p.unrestrictedTraverse(path, None)
      # Ignore any object without PortalType (non-ERP5 objects)
      try:
        portal_type = aq_base(obj).getPortalType()
      except Exception, e:
        pass
      else:
        if portal_type not in p.portal_types:
          LOG("BusinessTemplate", WARNING,
              "Could not update Local Roles as Portal Type '%s' could not "
              "be found" % portal_type)

          continue

        if portal_type not in portal_type_role_list_len_dict:
          portal_type_role_list_len_dict[portal_type] = \
              len(p.portal_types[portal_type].getRoleInformationList())

        if portal_type_role_list_len_dict[portal_type]:
          update_dict[portal_type].append(obj)

    if update_dict:
      def updateLocalRolesOnDocument():
        for portal_type, obj_list in update_dict.iteritems():
          update = p.portal_types[portal_type].updateLocalRolesOnDocument
          for obj in obj_list:
            update(obj)
            LOG("BusinessTemplate", INFO,
                "Updated Local Roles for '%s' (%s)"
                % (portal_type, obj.getRelativeUrl()))
      transaction.get().addBeforeCommitHook(updateLocalRolesOnDocument)
