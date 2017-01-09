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

import fnmatch, re, gc
import hashlib
import transaction
from copy import deepcopy
from collections import defaultdict
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Products.ERP5Type.Globals import Persistent, PersistentMapping
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules

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
      #self.setBuildingState('built')

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
    def export(self, path=None, local=0, bta=None):
      """
      Export the object
      """
      if not self.getBuildingState() == 'built':
        raise BusinessPackageException, 'Package not built properly'
      self._export(path, local, bta)

    def _export(self, path=None, local=0, bta=None):
      if bta is None:
        if local:
          # we export into a folder tree
          bta = BusinessTemplateFolder(path, creation=1)
        else:
          # We export BT into a tarball file
          if path is None:
            path = self.getTitle()
          bta = BusinessTemplateTarball(path, creation=1)

      # export bt
      for prop in self.propertyMap():
        prop_type = prop['type']
        id = prop['id']
        if id in ('id', 'uid', 'rid', 'sid', 'id_group', 'last_id', 'revision',
                  'install_object_list_list', 'id_generator', 'bt_for_diff'):
          continue
        value = self.getProperty(id)
        if not value:
          continue
        if prop_type in ('text', 'string', 'int', 'boolean'):
          bta.addObject(str(value), name=id, path='bt', ext='')
        elif prop_type in ('lines', 'tokens'):
          bta.addObject('\n'.join(value), name=id, path='bt', ext='')

      # Export each part
      for item_name in item_name_list:
        item = getattr(self, item_name, None)
        if item is not None:
          item.export(context=self, bta=bta)

      self._setRevision(bta.getRevision())
      return bta.finishCreation()

class BusinessPackageException(Exception):
  pass

class BusinessPackageArchive():
  """
  Keep saved the exported objects in Business Package in an archive
  """
  pass

class PathTemplatePackageItem(Implicit, Persistent):

  def __init__(self, id_list, tool_id=None, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    self._hash = PersistentMapping()
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
    hash_func = hashlib.sha1
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
          for id_ in list(id_list):
            _delObjectWithoutHook(obj, id_)
        self._objects[relative_url] = obj
        self._hash[relative_url] = hash_func(obj.asXML()).hexdigest()
        obj.wl_clearLocks()

  def export(self, context, bta, catalog_method_template_item = 0, **kw):
    """
      Export the business template : fill the BusinessTemplateArchive with
      objects exported as XML, hierarchicaly organised.
    """
    if len(self._objects.keys()) == 0:
      return
    path = self.__class__.__name__ + '/'

    # We now will add the XML object and its sha hash while exporting the object
    # to Business package itself
    for key, obj in self._objects.iteritems():
      # Back compatibility with filesystem Documents
      if isinstance(obj, str):
        if not key.startswith(path):
          key = path + key
        bta.addObject(obj, name=key, ext='.py')
      else:
        try:
          extension, unicode_data, record_id = \
            SEPARATELY_EXPORTED_PROPERTY_DICT[obj.__class__.__name__]
        except KeyError:
          pass
        else:
          while 1: # not a loop
            obj = obj._getCopy(context)
            data = getattr(aq_base(obj), record_id, None)
            if unicode_data:
              if type(data) is not unicode:
                break
              try:
                data = data.encode(aq_base(obj).output_encoding)
              except (AttributeError, UnicodeEncodeError):
                break
            elif type(data) is not bytes:
              if not isinstance(data, Pdata):
                break
              data = bytes(data)
            try:
              # Delete this attribute from the object.
              # in case the related Portal Type does not exist, the object may be broken.
              # So we cannot delattr, but we can delete the key of its its broken state
              if isinstance(obj, ERP5BaseBroken):
                del obj.__Broken_state__[record_id]
                obj._p_changed = 1
              else:
                delattr(obj, record_id)
            except (AttributeError, KeyError):
              # property was acquired on a class,
              # do nothing, only .xml metadata will be exported
              break
            # export a separate file with the data
            if not extension:
              extension = self.guessExtensionOfDocument(obj, key,
                data if record_id == 'data' else None)
            bta.addObject(StringIO(data), key, path=path,
              ext='._xml' if extension == 'xml' else '.' + extension)
            break
          # since we get the obj from context we should
          # again remove useless properties
          obj = self.removeProperties(obj, 1, keep_workflow_history = True)
          transaction.savepoint(optimistic=True)

        f = StringIO()
        XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
        bta.addObject(f, key, path=path)

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
          LOG('BusinessTemplate', WARNING,
              'Could not access object %s' % (path,))
          if default is _MARKER:
            raise
          return default

        if restricted:
          try:
            if not validate(container, container, key, value):
              raise Unauthorized('unauthorized access to element %s' % key)
          except Unauthorized:
            LOG('BusinessTemplate', WARNING,
                'access to %s is forbidden' % (path,))
          if default is _MARKER:
            raise
          return default

        container = value

      return value
    else:
      return context

  def _resetDynamicModules(self):
    # before any import, flush all ZODB caches to force a DB reload
    # otherwise we could have objects trying to get commited while
    # holding reference to a class that is no longer the same one as
    # the class in its import location and pickle doesn't tolerate it.
    # First we do a savepoint to dump dirty objects to temporary
    # storage, so that all references to them can be freed.
    transaction.savepoint(optimistic=True)
    # Then we need to flush from all caches, not only the one from this
    # connection
    portal = self.getPortalObject()
    portal._p_jar.db().cacheMinimize()
    synchronizeDynamicModules(portal, force=True)
    gc.collect()

  def fixBrokenObject(self, obj):
    if isinstance(obj, ERP5BaseBroken):
      self._resetDynamicModules()

  def _getObjectKeyList(self):
    # sort to add objects before their subobjects
    keys = self._objects.keys()
    keys.sort()
    return keys

  def install(self, context, *args, **kw):
    force = 1
    update_dict = {}
    portal = context.getPortalObject()
    object_key_list = self._getObjectKeyList()
    for path in object_key_list:
      __traceback_info__ = path
      # We do not need to perform any backup because the object was
      # created during the Business Template installation
      if update_dict.get(path) == 'migrate':
        continue

      if update_dict.has_key(path) or force:
        # get action for the oject
        action = 'backup'
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        # get subobjects in path
        path_list = path.split('/')
        container_path = path_list[:-1]
        object_id = path_list[-1]
        try:
          container = self.unrestrictedResolveValue(portal, container_path)
        except KeyError:
          # parent object can be set to nothing, in this case just go on
          container_url = '/'.join(container_path)
        old_obj = container._getOb(object_id, None)
        # install object
        obj = self._objects[path]
        self.fixBrokenObject(obj)
        obj = obj._getCopy(container)
        #self.removeProperties(obj, 0)
        __traceback_info__ = (container, object_id, obj)
        container._setObject(object_id, obj)
        obj = container._getOb(object_id)

# The reason to keep createInstallationData as separate function is to
# not need to initialize an InstallationTree object everytime when we want
# to create some installation data
def createInstallationData(package_list):
  """
  Create installation object as well as add new node on the installation tree
  from the installed state
  """
  path_list = []
  final_data = {}
  conflicted_data = {}

  # Create path_list of all the objects to be installed by the installation
  for package in package_list:
    path_list.extend(package.getTemplatePathList())
    path_list = list(set(path_list))

  for package in package_list:
    obj_dict = package._path_item._objects
    hash_dict = package._path_item._hash
    for path in path_list:
      object_metadata = {}
      object_metadata['obj'] = obj_dict[path]
      object_metadata['sha'] = hash_dict[path]

      # If the path already exists in conflicted_data, add the metadata in the
      # conflicted_data itself
      if conflicted_data.has_key(path):
        conflicted_data[path].append(object_metadata)

      # If the path is new, add the metadata to final_data
      elif not data.has_key(path):
        final_data[path] = object_metadata

      # If the object is neither in conflicted_data already in final_data,
      # compare hash of the objects
      else:
        # Leave the metadata in final_data in case the hash matches,
        # else add it to conflicted_data
        if final_data[path]['sha'] ==  object_metadata['sha']
          continue
        else:
          conflicted_data[path] = [object_metadata]

  return final_data, conflicted_data

class InstallationTree(object):
  """
  Tree implemetation to manage install/update/remove between states.
  This is a very rough code to explain what can be achieved. In real case,
  this class should be a well defined ERP5 object and most possibly act as a
  portal tool, cause there should be one installation tree per site(agree ??)

  Data at every node:
  ('_path_item': PathTemplateItem, }

  State Number:
  1)  ERP5Site
  2)  ERP5Site + BP1 : BP1 installed on ERP5Site
  3)  Install state BP2 + BP3 on state 2

  Initially:(Each node is a state)
  Leaf node: OFS State(with some default BP installed)
  Trying to install a new BT5 should be like adding new node to the tree

  Will show if faced by any conflict between states, but mostly will try to
  solve by itself

  How to pickle:
  http://stackoverflow.com/questions/2134706/hitting-maximum-recursion-depth-using-pythons-pickle-cpickle

  How to version control the states:
  https://github.com/gitpython-developers/GitPython/tree/master/git

  """

  def __init__(self, data):
    self.data = data          # To be installed/update/deleted list of packages
    self.children = []        # List of child nodes

  def addNewState(self, state):
    """
    In tree language, should act as set next node to the tree

    This should add package list after comparing the states of
    packages with the installed state. So even if we try to install multiple
    packages at a time, it should be counted as one state being implented on
    another installed state, i.e, the state of ERP5Site
    """
    self.children.append(state)

  def mapToERP5Site(self):
    """
    Create a new state by comparing all BP combined built and the ERP5Site,
    then calls setNewState to update the state
    While mapping we compare between installed_item of BT, if exisits as well
    as ZODB. The Installation Tree should be smart enough to take us nearest to
    the installed state. If any conflict whatsoever arise, it should raise it.
    """
    # No need to create sha here, save it in business package itself
    pass
