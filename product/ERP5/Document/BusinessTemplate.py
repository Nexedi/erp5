# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import fnmatch, gc, glob, imp, os, re, shutil, sys, time, tarfile
from collections import defaultdict
from Shared.DC.ZRDB import Aqueduct
from Shared.DC.ZRDB.Connection import Connection as RDBConnection
from Products.ERP5Type.DiffUtils import DiffFile
from Products.ERP5Type.Globals import Persistent, PersistentMapping
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.PythonScript import PythonScript
from Products.ZSQLMethods.SQL import SQL
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Utils import readLocalDocument, \
                                    writeLocalDocument, \
                                    importLocalDocument, \
                                    removeLocalDocument
from Products.ERP5Type.Utils import readLocalPropertySheet, \
                                    writeLocalPropertySheet, \
                                    importLocalPropertySheet, \
                                    removeLocalPropertySheet
from Products.ERP5Type.Utils import readLocalConstraint, \
                                    writeLocalConstraint, \
                                    importLocalConstraint, \
                                    removeLocalConstraint
from Products.ERP5Type.Utils import readLocalExtension, \
                                    writeLocalExtension, \
                                    removeLocalExtension
from Products.ERP5Type.Utils import readLocalTest, \
                                    writeLocalTest, \
                                    removeLocalTest
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
from Products.ERP5Type.Core.PropertySheet import PropertySheet as PropertySheetDocument
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5.Document.File import File
from OFS.Traversable import NotFound
from OFS import SimpleItem, XMLExportImport
from OFS.Image import Pdata
from cStringIO import StringIO
from copy import deepcopy
from zExceptions import BadRequest
import OFS.XMLExportImport
from Products.ERP5Type.patches.ppml import importXML
customImporters={
    XMLExportImport.magic: importXML,
    }
from Products.ERP5Type.Workflow import WorkflowHistoryList
from zLOG import LOG, WARNING, INFO
from warnings import warn
from lxml.etree import parse
from xml.sax.saxutils import escape
from Products.CMFCore.Expression import Expression
from urllib import quote, unquote
from difflib import unified_diff
import posixpath
import transaction
import inspect

import threading
from ZODB.broken import Broken, BrokenModified
from Products.ERP5.genbt5list import BusinessTemplateRevision, \
  item_name_list, item_set
from OFS.Image import File as OFSFile

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
from Products.MimetypesRegistry.common import MimeTypeException
import imghdr

# those attributes from CatalogMethodTemplateItem are kept for
# backward compatibility
catalog_method_list = ('_is_catalog_list_method_archive',
                       '_is_uncatalog_method_archive',
                       '_is_clear_method_archive',
                       '_is_filtered_archive',)

catalog_method_filter_list = ('_filter_expression_archive',
                              '_filter_expression_cache_key_archive',
                              '_filter_type_archive',)

INSTALLED_BT_FOR_DIFF = 'installed_bt_for_diff'
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
  "Interface Component": ("py",   0, "text_content"),
  "OOoTemplate":         ("oot",  1, "_text"),
  "Mixin Component":     ("py",   0, "text_content"),
  "Module Component":    ("py",   0, "text_content"),
  "PDF":                 ("pdf",  0, "data"),
  "PDFForm":             ("pdf",  0, "data"),
  "PyData Script":       ("py",   0, "_body"),
  "Python Script":       ("py",   0, "_body"),
  "PythonScript":        ("py",   0, "_body"),
  "Spreadsheet":         (None,   0, "data"),
  "SQL":                 ("sql",  0, "src"),
  "SQL Method":          ("sql",  0, "src"),
  "Test Component":      ("py",   0, "text_content"),
  "Test Page":           (None,   0, "text_content"),
  "Tool Component":      ("py",   0, "text_content"),
  "Web Page":            (None,   0, "text_content"),
  "Web Script":          (None,   0, "text_content"),
  "Web Style":           (None,   0, "text_content"),
  "ZopePageTemplate":    ("zpt",  1, "_text"),
}

def _getCatalog(acquisition_context):
  """
    Return the id of the Catalog which correspond to the current BT.
  """
  catalog_method_id_list = acquisition_context.getTemplateCatalogMethodIdList()
  if len(catalog_method_id_list) == 0:
    try:
      return acquisition_context.getPortalObject().portal_catalog.objectIds()[0]
    except IndexError:
      return None
  catalog_method_id = catalog_method_id_list[0]
  return catalog_method_id.split('/')[0]

def _getCatalogValue(acquisition_context):
  """
    Returns the catalog object which correspond to the ZSQLMethods
    stored/to store in the business template.

    NB: acquisition_context must make possible to reach portal object
        and getTemplateCatalogMethodIdList.
  """
  catalog_id = _getCatalog(acquisition_context)
  if catalog_id is None:
    return None
  try:
    return acquisition_context.getPortalObject().portal_catalog[catalog_id]
  except KeyError:
    return None

def _recursiveRemoveUid(obj):
  """Recusivly set uid to None, to prevent (un)indexing.
  This is used to prevent unindexing real objects when we delete subobjects on
  a copy of this object.
  """
  if getattr(aq_base(obj), 'uid', _MARKER) is not _MARKER:
    obj.uid = None
  for subobj in obj.objectValues():
    _recursiveRemoveUid(subobj)

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

def removeAll(entry):
  warn('removeAll is deprecated; use shutil.rmtree instead.',
       DeprecationWarning)
  shutil.rmtree(entry, True)

def getChainByType(context):
  """
  This is used in order to construct the full list
  of mapping between type and list of workflow associated
  This is only useful in order to use
  portal_workflow.manage_changeWorkflows
  """
  pw = context.getPortalObject().portal_workflow
  cbt = pw._chains_by_type
  ti = pw._listTypeInfo()
  types_info = []
  for t in ti:
    id = t.getId()
    title = t.Title()
    if title == id:
      title = None
    if cbt is not None and cbt.has_key(id):
      chain = ', '.join(cbt[id])
    else:
      chain = '(Default)'
    types_info.append({'id': id,
                      'title': title,
                      'chain': chain})
  new_dict = {}
  for item in types_info:
    new_dict['chain_%s' % item['id']] = item['chain']
  default_chain=', '.join(pw._default_chain)
  return (default_chain, new_dict)

def fixZSQLMethod(portal, method):
  """Make sure the ZSQLMethod uses a valid connection.
  """
  if not isinstance(getattr(portal, method.connection_id, None),
                      RDBConnection):
    # if not valid, we assign to the first valid connection found
    sql_connection_list = portal.objectIds(
                          spec=('Z MySQL Database Connection',))
    if (method.connection_id not in sql_connection_list) and \
       (len(sql_connection_list) != 0):
      LOG('BusinessTemplate', WARNING,
          'connection_id for Z SQL Method %s is invalid, using %s' % (
                    method.getId(), sql_connection_list[0]))
      method.connection_id = sql_connection_list[0]
  # recompile the method
  method._arg = Aqueduct.parse(method.arguments_src)
  method.template = method.template_class(method.src)

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

class BusinessTemplateArchive(object):
  """
    This is the base class for all Business Template archives
  """
  def __init__(self, path, **kw):
    self.path = path
    self.revision = BusinessTemplateRevision()

  def addObject(self, obj, name, path=None, ext='.xml'):
    if path:
      name = posixpath.join(path, name)
    # XXX required due to overuse of os.path
    name = name.replace('\\', '/').replace(':', '/')
    name = quote(name + ext)
    path = name.replace('/', os.sep)
    try:
      write = self._writeFile
    except AttributeError:
      if not isinstance(obj, str):
        obj.seek(0)
        obj = obj.read()
      self.revision.hash(path, obj)
      self._writeString(obj, path)
    else:
      if isinstance(obj, str):
        self.revision.hash(path, obj)
        obj = StringIO(obj)
      else:
        obj.seek(0)
        self.revision.hash(path, obj.read())
      write(obj, path)

  def finishCreation(self):
    pass

  def getRevision(self):
    return self.revision.digest()

class BusinessTemplateFolder(BusinessTemplateArchive):
  """
    Class archiving business template into a folder tree
  """
  def _writeString(self, obj, path):
    object_path = os.path.join(self.path, path)
    path = os.path.dirname(object_path)
    os.path.exists(path) or os.makedirs(path)
    f = open(object_path, 'wb')
    try:
      f.write(obj)
    finally:
      f.close()

  def importFiles(self, item):
    """
      Import file from a local folder
    """
    join = os.path.join
    item_name = item.__class__.__name__
    root = join(os.path.normpath(self.path), item_name, '')
    root_path_len = len(root)
    if CACHE_DATABASE_PATH:
      try:
        cache_database.db = gdbm.open(CACHE_DATABASE_PATH, 'cf')
      except gdbm.error:
        cache_database.db = gdbm.open(CACHE_DATABASE_PATH, 'nf')
    try:
      for root, dirs, files in os.walk(root):
        for file_name in files:
          file_name = join(root, file_name)
          with open(file_name, 'rb') as f:
            file_name = posixpath.normpath(file_name[root_path_len:])
            if '%' in file_name:
              file_name = unquote(file_name)
            elif item_name == 'bt' and file_name == 'revision':
              continue
            self.revision.hash(item_name + '/' + file_name, f.read())
            f.seek(0)
            item._importFile(file_name, f)
    finally:
      if hasattr(cache_database, 'db'):
        cache_database.db.close()
        del cache_database.db

class BusinessTemplateTarball(BusinessTemplateArchive):
  """
    Class archiving businnes template into a tarball file
  """

  def __init__(self, path, creation=0, importing=0, **kw):
    super(BusinessTemplateTarball, self).__init__(path, **kw)
    if creation:
      self.fobj = StringIO()
      self.tar = tarfile.open('', 'w:gz', self.fobj)
      self.time = time.time()
    elif importing:
      self.tar = tarfile.open(path, 'r:gz')
      self.item_dict = item_dict = defaultdict(list)
      for info in self.tar.getmembers():
        if info.isreg():
          path = info.name.split('/')
          if path[0] == '.':
            del path[0]
          item_dict[path[1]].append(('/'.join(path[2:]), info))

  def _writeFile(self, obj, path):
    if self.path:
      path = posixpath.join(self.path, path)
    info = tarfile.TarInfo(path)
    info.mtime = self.time
    obj.seek(0, 2)
    info.size = obj.tell()
    obj.seek(0)
    self.tar.addfile(info, obj)

  def finishCreation(self):
    self.tar.close()
    return self.fobj

  def importFiles(self, item):
    """
      Import all file from the archive to the site
    """
    extractfile = self.tar.extractfile
    item_name = item.__class__.__name__
    for file_name, info in self.item_dict.get(item_name, ()):
      if '%' in file_name:
        file_name = unquote(file_name)
      elif item_name == 'bt' and file_name == 'revision':
        continue
      f = extractfile(info)
      self.revision.hash(item_name + '/' + file_name, f.read())
      f.seek(0)
      item._importFile(file_name, f)

class TemplateConditionError(Exception): pass
class TemplateConflictError(Exception): pass
class BusinessTemplateMissingDependency(Exception): pass

ModuleSecurityInfo(__name__).declarePublic('BusinessTemplateMissingDependency',
  'TemplateConditionError', 'TemplateConflictError')

class BaseTemplateItem(Implicit, Persistent):
  """
    This class is the base class for all template items.
    is_bt_for_diff means This BT is used to compare self temporary BT with installed BT
  """
  is_bt_for_diff = None

  def __init__(self, id_list, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    for id in id_list:
      if id is not None and id != '':
        self._archive[id] = None

  def build(self, context, **kw):
    pass

  def preinstall(self, context, installed_item, **kw):
    """
      Build a list of added/removed/changed files between the BusinessTemplate
      being installed (self) and the installed one (installed_item).
      Note : we compare files between BTs, *not* between the installed BT and
      the objects in the DataFS.

      XXX: -12 used here is -len('TemplateItem')
    """
    modified_object_list = {}
    for path in self._objects:
      if installed_item._objects.has_key(path):
        # compare objects to see it there are changes
        new_obj_xml = self.generateXml(path=path)
        old_obj_xml = installed_item.generateXml(path=path)
        if new_obj_xml != old_obj_xml:
          modified_object_list[path] = 'Modified', self.__class__.__name__[:-12]
        # else, compared versions are identical, don't overwrite the old one
      else: # new object
        modified_object_list[path] = 'New', self.__class__.__name__[:-12]
    # list removed objects
    old_keys = installed_item._objects.keys()
    for path in old_keys:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', self.__class__.__name__[:-12]
    return modified_object_list

  def install(self, context, trashbin, **kw):
    pass

  def uninstall(self, context, **kw):
    pass

  def remove(self, context, **kw):
    """
      If 'remove' is chosen on an object containing subobjects, all the
      subobjects will be removed too, even if 'backup' or 'keep' was chosen for
      the subobjects.
      Likewise, for 'save_and_remove' : subobjects will get saved too.
    """
    remove_dict = kw.get('remove_object_dict', {})
    keys = self._objects.keys()
    keys.sort()
    keys.reverse()
    # if you choose remove, the object and all its subobjects will be removed
    # even if you choose backup or keep for subobjects
    # it is same behaviour for backup_and_remove, all we be save
    for path in keys:
      if remove_dict.has_key(path):
        action = remove_dict[path]
        if action == 'save_and_remove':
          # like trash
          self.uninstall(context, trash=1, object_path=path, **kw)
        elif action == 'remove':
          self.uninstall(context, trash=0, object_path=path, **kw)
        else:
          # As the list of available actions is not strictly defined,
          # prevent mistake if an action is not handled
          raise ValueError, 'Unknown action "%s"' % action


  def trash(self, context, new_item, **kw):
    # trash is quite similar to uninstall.
    return self.uninstall(context, new_item=new_item, trash=1, **kw)

  def export(self, context, bta, **kw):
    pass

  def getKeys(self):
    return self._objects.keys()

  def importFile(self, bta, **kw):
    bta.importFiles(self)

  def _removeAllButLastWorkflowHistory(self, obj):
    workflow_history = getattr(obj, 'workflow_history', None)
    if workflow_history is None:
      return
    for workflow_id in workflow_history.keys():
      workflow_history[workflow_id] = WorkflowHistoryList(
        [workflow_history[workflow_id][-1]])

  def removeProperties(self,
                       obj,
                       export,
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
    if export:
      if keep_workflow_history_last_history_only:
        self._removeAllButLastWorkflowHistory(obj)
      elif not keep_workflow_history:
        attr_set.add('workflow_history')
      # PythonScript covers both Zope Python scripts
      # and ERP5 Python Scripts
      if isinstance(obj, PythonScript):
        # `expression_instance` is included so as to add compatibility for
        # exporting older catalog methods which might have them as their
        # properties or in their attribute dict.
        attr_set.update(('func_code', 'func_defaults', '_code',
                         '_lazy_compilation', 'Python_magic',
                         'expression_instance'))
        for attr in 'errors', 'warnings', '_proxy_roles':
          if not obj.__dict__.get(attr, 1):
            delattr(obj, attr)
      elif classname in ('File', 'Image'):
        attr_set.update(('_EtagSupport__etag', 'size'))
      # SQL covers both ZSQL Methods and ERP5 SQL Methods
      elif isinstance(obj, SQL):
        # `expression_instance` is included so as to add compatibility for
        # exporting older catalog methods which might have them as their
        # properties or in their attribute dict.
        attr_set.update(('_arg', 'template', 'expression_instance'))
      elif interfaces.IIdGenerator.providedBy(obj):
        attr_set.update(('last_max_id_dict', 'last_id_dict'))
      elif classname == 'Types Tool' and klass.__module__ == 'erp5.portal_type':
        attr_set.add('type_provider_list')

    for attr in obj.__dict__.keys():
      if attr in attr_set or attr.startswith('_cache_cookie_'):
        delattr(obj, attr)

    if classname == 'PDFForm':
      if not obj.getProperty('business_template_include_content', 1):
        obj.deletePdfContent()
    return obj

  def getTemplateTypeName(self):
    """
     Get a meaningfull class Name without 'TemplateItem'. Used to
     present to the user.

     XXX: -12 used here is -len('TemplateItem')
    """
    return self.__class__.__name__[:-12]

  def restrictedResolveValue(self, context=None, path='', default=_MARKER):
    """
      Get the value with checking the security.
      This method does not acquire the parent.
    """
    return self.unrestrictedResolveValue(context, path, default=default,
                                         restricted=1)

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

class ObjectTemplateItem(BaseTemplateItem):
  """
    This class is used for generic objects and as a subclass.
  """

  def __init__(self, id_list, tool_id=None, **kw):
    BaseTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    if tool_id is not None:
      id_list = self._archive.keys()
      self._archive.clear()
      for id in id_list :
        if id != '':
          self._archive["%s/%s" % (tool_id, id)] = None

  def _guessFilename(self, document, key, data):
    # Try to guess the extension based on the id of the document
    yield key
    document_base = aq_base(document)
    # Try to guess the extension based on the reference of the document
    if hasattr(document_base, 'getReference'):
      yield document.getReference()
    elif isinstance(document_base, ERP5BaseBroken):
      yield getattr(document_base, "reference", None)
    # Try to guess the extension based on the title of the document
    yield getattr(document_base, "title", None)
    # Try to guess from content
    if data:
      for test in imghdr.tests:
        extension = test(data, None)
        if extension:
          yield 'x.' + extension

  def guessExtensionOfDocument(self, document, key, data=None):
    """Guesses and returns the extension of an ERP5 document.

    The process followed is:
    1. Try to guess extension by the id of the document
    2. Try to guess extension by the title of the document
    3. Try to guess extension by the reference of the document
    4. Try to guess from content (only image data is tested)

    If there's a content type, we only return an extension that matches.

    In case everything fails then:
    - '.bin' is returned for binary files
    - '.txt' is returned for text
    """
    document_base = aq_base(document)
    # XXX Zope items like DTMLMethod would not implement getContentType method
    mime = None
    if hasattr(document_base, 'getContentType'):
      content_type = document.getContentType()
    elif isinstance(document_base, ERP5BaseBroken):
      content_type = getattr(document_base, "content_type", None)
    else:
      content_type = None
    # For stable export, people must have a MimeTypes Registry, so do not
    # fallback on mimetypes. We prefer the mimetypes_registry because there
    # are more extensions and we can have preferred extensions.
    # See also https://bugs.python.org/issue1043134
    mimetypes_registry = self.getPortalObject()['mimetypes_registry']
    if content_type:
      try:
        mime = mimetypes_registry.lookup(content_type)[0]
      except (IndexError, MimeTypeException):
        pass

    for key in self._guessFilename(document, key, data):
      if key:
        ext = os.path.splitext(key)[1][1:].lower()
        if ext and (mimetypes_registry.lookupExtension(ext) is mime if mime
               else mimetypes_registry.lookupExtension(ext)):
          return ext

    if mime:
      # return first registered extension (if any)
      if mime.extensions:
        return mime.extensions[0]
      for ext in mime.globs:
        if ext[0] == "*" and ext.count(".") == 1:
          return ext[2:].encode("utf-8")

    # in case we could not read binary flag from mimetypes_registry then return
    # '.bin' for all the Portal Types where exported_property_type is data
    # (File, Image, Spreadsheet). Otherwise, return .bin if binary was returned
    # as 1.
    binary = getattr(mime, 'binary', None)
    if binary or binary is None is not data:
      return 'bin'
    # in all other cases return .txt
    return 'txt'

  def export(self, context, bta, catalog_method_template_item = 0, **kw):
    """
      Export the business template : fill the BusinessTemplateArchive with
      objects exported as XML, hierarchicaly organised.
    """
    if len(self._objects.keys()) == 0:
      return
    path = self.__class__.__name__ + '/'
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
        
      if catalog_method_template_item:
        # add all datas specific to catalog inside one file
        xml_data = self.generateXml(key)
        bta.addObject(xml_data, key + '.catalog_keys', path=path)

  def _restoreSeparatelyExportedProperty(self, obj, data):
    unicode_data, property_name = SEPARATELY_EXPORTED_PROPERTY_DICT[
      obj.__class__.__name__][1:]
    if unicode_data:
      data = data.decode(obj.output_encoding)
    if isinstance(obj, OFSFile) and property_name == "data":
      data = obj._read_data(data)[0]
    try:
      setattr(obj, property_name, data)
    except BrokenModified:
      obj.__Broken_state__[property_name] = data
      obj._p_changed = 1
    else:
      # Revert any work done by __setstate__.
      # XXX: This is enough for all objects we currently split in 2 files,
      #      but __setstate__ could behave badly with the missing attribute
      #      and newly added types may require more than this.
      self.removeProperties(obj, 1, keep_workflow_history=True)

  def _importFile(self, file_name, file_obj, catalog_method_template_item = 0):
    obj_key, file_ext = os.path.splitext(file_name)
    # id() for installing several bt5 in the same transaction
    transactional_variable_obj_key = "%s-%s" % (id(self), obj_key)
    if file_ext != '.xml':
      # if the document has not been migrated yet (its class is file and
      # it is not in portal_components) use legacy importer
      if issubclass(self.__class__, FilesystemDocumentTemplateItem) and file_obj.name.rsplit(os.path.sep, 2)[-2] != 'portal_components':
        FilesystemDocumentTemplateItem._importFile(self, file_name, file_obj)
      else:
        # For ZODB Components: if .xml have been processed before, set the
        # source code property, otherwise store it in a transactional variable
        # so that it can be set once the .xml has been processed
        data = file_obj.read()
        try:
          obj = self._objects[obj_key]
        except KeyError:
          getTransactionalVariable()[transactional_variable_obj_key] = data
        else:
          self._restoreSeparatelyExportedProperty(obj, data)
    else:
      connection = self.getConnection(self.aq_parent)
      __traceback_info__ = 'Importing %s' % file_name
      if hasattr(cache_database, 'db') and isinstance(file_obj, file):
        obj = connection.importFile(self._compileXML(file_obj))
      else:
        # FIXME: Why not use the importXML function directly? Are there any BT5s
        # with actual .zexp files on the wild?
        obj = connection.importFile(file_obj, customImporters=customImporters)
      self._objects[obj_key] = obj

      data = getTransactionalVariable().get(transactional_variable_obj_key)
      if data is not None:
        self._restoreSeparatelyExportedProperty(obj, data)

      # When importing a Business Template, there is no way to determine if it
      # has been already migrated or not in __init__() when it does not
      # already exist, therefore BaseTemplateItem.__init__() is called which
      # does not set _archive with portal_components/ like
      # ObjectTemplateItem.__init__()
      # XXX - the above comment is a bit unclear, 
      # still not sure if this is handled correctly
      if file_obj.name.rsplit(os.path.sep, 2)[-2] == 'portal_components':
        self._archive[obj_key] = None
        try:
          del self._archive[obj_key[len('portal_components/'):]]
        except KeyError:
          pass
      if catalog_method_template_item:
        self.removeProperties(obj, 0)

  def build_sub_objects(self, context, id_list, url, **kw):
    # XXX duplicates code from build
    for id in id_list:
      relative_url = '/'.join([url,id])
      obj = context._getOb(id)
      obj = self.removeProperties(obj, 1,
                                  self.isKeepWorkflowObject(relative_url),
                                  self.isKeepWorkflowObjectLastHistoryOnly(relative_url))
      id_list = obj.objectIds() # FIXME duplicated variable name
      if hasattr(aq_base(obj), 'groups'): # XXX should check metatype instead
        # we must keep groups because they are deleted along with subobjects
        groups = deepcopy(obj.groups)
      if id_list:
        self.build_sub_objects(obj, id_list, relative_url, copied=True)
        for id_ in list(id_list):
          _delObjectWithoutHook(obj, id_)
      if hasattr(aq_base(obj), 'groups'):
        obj.groups = groups
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      try:
        obj = p.unrestrictedTraverse(relative_url)
      except ValueError:
        raise ValueError, "Can not access to %s" % relative_url
      try:
        obj = obj._getCopy(context)
      except AttributeError:
        raise AttributeError, "Could not find object '%s' during business template processing." % relative_url
      _recursiveRemoveUid(obj)
      obj = self.removeProperties(obj, 1,
                                  self.isKeepWorkflowObject(relative_url),
                                  self.isKeepWorkflowObjectLastHistoryOnly(relative_url))
      id_list = obj.objectIds()
      if hasattr(aq_base(obj), 'groups'): # XXX should check metatype instead
        # we must keep groups because they are deleted along with subobjects
        groups = deepcopy(obj.groups)
      if len(id_list) > 0:
        self.build_sub_objects(obj, id_list, relative_url)
        for id_ in list(id_list):
          _delObjectWithoutHook(obj, id_)
      if hasattr(aq_base(obj), 'groups'):
        obj.groups = groups
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def _compileXML(self, file):
    # This method converts XML to ZEXP. Because the conversion
    # is quite heavy, a persistent cache database is used to
    # store ZEXP, so the second run wouldn't have to re-generate
    # identical data again.
    #
    # For now, a pair of the path to an XML file and its modification time
    # are used as a unique key. In theory, a checksum of the content could
    # be used instead, and it could be more reliable, as modification time
    # might not be updated in some insane filesystems correctly. However,
    # in practice, checksums consume a lot of CPU time, so when the cache
    # does not hit, the increased overhead is significant. In addition, it
    # does rarely happen that two XML files in Business Templates contain
    # the same data, so it may not be expected to have more cache hits
    # with this approach.
    #
    # The disadvantage is that this wouldn't work with the archive format,
    # because each entry in an archive does not have a mtime in itself.
    # However, the plan is to have an archive to retain ZEXP directly
    # instead of XML, so the idea of caching would be completely useless
    # with the archive format.
    name = file.name
    mtime = os.path.getmtime(file.name)
    key = '%s:%s' % (name, mtime)

    try:
      return StringIO(cache_database.db[key])
    except:
      pass

    #LOG('Business Template', 0, 'Compiling %s...' % (name,))
    from Shared.DC.xml import ppml
    from OFS.XMLExportImport import start_zopedata, save_record, save_zopedata
    import xml.parsers.expat
    outfile=StringIO()
    try:
      data=file.read()
      F=ppml.xmlPickler()
      F.end_handlers['record'] = save_record
      F.end_handlers['ZopeData'] = save_zopedata
      F.start_handlers['ZopeData'] = start_zopedata
      F.binary=1
      F.file=outfile
      p=xml.parsers.expat.ParserCreate('utf-8')
      p.returns_unicode = False
      p.CharacterDataHandler=F.handle_data
      p.StartElementHandler=F.unknown_starttag
      p.EndElementHandler=F.unknown_endtag
      p.Parse(data)

      try:
        cache_database.db[key] = outfile.getvalue()
      except:
        pass

      outfile.seek(0)
      return outfile
    except:
      outfile.close()
      raise

  def getConnection(self, obj):
    while True:
      connection = obj._p_jar
      if connection is not None:
        return connection
      obj = obj.aq_parent

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    upgrade_list = []
    type_name = self.__class__.__name__.split('TemplateItem')[-2]
    for path, obj in self._objects.iteritems():
      if installed_item._objects.has_key(path):
        upgrade_list.append((path, installed_item._objects[path]))
      else: # new object
        modified_object_list[path] = 'New', type_name

    # update _p_jar property of objects cleaned by removeProperties
    transaction.savepoint(optimistic=True)
    for path, old_object in upgrade_list:
      # compare object to see it there is changes
      new_object = self._objects[path]
      new_io = StringIO()
      old_io = StringIO()
      OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, new_io)
      new_obj_xml = new_io.getvalue()
      try:
        OFS.XMLExportImport.exportXML(old_object._p_jar, old_object._p_oid, old_io)
        old_obj_xml = old_io.getvalue()
      except (ImportError, UnicodeDecodeError), e: # module is already
                                                   # removed etc.
        old_obj_xml = '(%s: %s)' % (e.__class__.__name__, e)
      new_io.close()
      old_io.close()
      if new_obj_xml != old_obj_xml:
        if context.isKeepObject(path):
          modified_object_list[path] = 'Modified but should be kept', type_name
        else:
          modified_object_list[path] = 'Modified', type_name
    # get removed object
    for path in set(installed_item._objects) - set(self._objects):
      if context.isKeepObject(path):
        modified_object_list[path] = 'Removed but should be kept', type_name
      else:
        modified_object_list[path] = 'Removed', type_name
    return modified_object_list

  def _backupObject(self, action, trashbin, container_path, object_id, **kw):
    """
      Backup the object in portal trash if necessery and return its subobjects
    """
    if "portal_integrations" in container_path and "module" in object_id:
      # XXX It is impossible to backup integration module as
      # it will call the request and try to get remote data
      return
    p = self.getPortalObject()
    if trashbin is None: # must return subobjects
      subobject_dict = {}
      obj = p.unrestrictedTraverse(container_path)[object_id]
      for subobject_id in obj.objectIds():
        subobject = obj[subobject_id]
        subobject_dict[subobject_id] = subobject._p_jar.exportFile(
            subobject._p_oid, StringIO())
      return subobject_dict
    # XXX btsave is for backward compatibility
    if action in ('backup', 'btsave', 'save_and_remove',):
      save = 1
    elif action in ('install', 'remove'):
      save = 0
    else:
      # As the list of available actions is not strictly defined,
      # prevent mistake if an action is not handled
      raise NotImplementedError, 'Unknown action "%s"' % action
    return p.portal_trash.backupObject(trashbin, container_path, object_id,
                                       save=save, **kw)


  def beforeInstall(self):
    """
      Installation hook.
      Called right at the begining of "install" method.
      Can be overridden by subclasses.
    """
    pass

  def afterInstall(self):
    """
      Installation hook.
      Called right before returning in "install" method.
      Can be overridden by subclasses.
    """
    pass

  def afterUninstall(self):
    """
      Uninstallation hook.
      Called right before returning in "uninstall" method.
      Can be overridden by subclasses.
    """
    pass

  def onNewObject(self, obj):
    """
      Installation hook.
      Called when installation process determined that object to install is
      new on current site (it's not replacing an existing object).
      `obj` parameter is the newly created object in its acquisition context.
      Can be overridden by subclasses.
    """
    pass

  def setSafeReindexationMode(self, context):
    """
      Postpone indexations after unindexations.
      This avoids alarming error messages about a single uid being used
      by "deleted" path and reindexed object. This can happen here for
      objects on which the uid was restored: previous object was deleted,
      hence the "deleted" path, and new object does have the same uid.
    """
    kw = context.getPlacelessDefaultReindexParameters()
    if kw is None:
      kw = {}
    context.setPlacelessDefaultReindexParameters(**dict(kw,
      activate_kw=dict(kw.get('activate_kw', ()),
                       after_method_id='unindexObject')))
    return kw

  def _getObjectKeyList(self):
    # sort to add objects before their subobjects
    keys = self._objects.keys()
    keys.sort()
    return keys

  def unindexBrokenObject(self, item_path):
    """
      Unindex broken objects.

      Corresponding catalog record is not unindexed even after a broken object
      is removed, since the broken object does not implement 'CopySupport'.
      This situation triggers a FATAL problem on SQLCatalog.catalogObjectList
      when upgrading a broken path by ObjectTemplateItem with BusinessTemplate.
      We often get this problem when we are upgrading a quite old ERP5 site
      to new one, as several old classes may be already removed/replaced
      in the file system, thus several objects tend to be broken.

      Keyword arguments:
      item_path -- the path specified by the ObjectTemplateItem
    """
    def flushActivity(obj, invoke=0, **kw):
      try:
        activity_tool = self.getPortalObject().portal_activities
      except AttributeError:
        return # Do nothing if no portal_activities
      # flush all activities related to this object
      activity_tool.flush(obj, invoke=invoke, **kw)

    class fakeobject:
       def __init__(self, path):
         self._physical_path = tuple(path.split('/'))
       def getPhysicalPath(self):
         return self._physical_path

    def recursiveUnindex(catalog, item_path, root_document_path):
      # search the object + sub-objects
      result = catalog(relative_url=(item_path,
                                     item_path.replace('_', r'\_') + '/%'))
      for x in result:
        uid = x.uid
        path = x.path
        unindex(root_document_path, path, uid)

    def unindex(root_document_path, path, uid):
      LOG('Products.ERP5.Document.BusinessTemplate', WARNING,
          'Unindex Broken object at %r.' % (path,))
      # Make sure there is not activity for this object
      flushActivity(fakeobject(path))
      # Set the path as deleted without lock
      catalog.beforeUnindexObject(None,path=path,uid=uid)
      # Then start activity in order to remove lines in catalog,
      # sql wich generate locks
      catalog.activate(activity='SQLQueue',
                       tag='%s' % uid,
                       group_method_id='portal_catalog/uncatalogObjectList',
                       serialization_tag=root_document_path
                       ).unindexObject(uid=uid)

    portal = self.getPortalObject()
    try:
      catalog = portal.portal_catalog
    except AttributeError:
      pass
    else:
      # given item_path is a relative_url in reality
      root_path = "/".join(item_path.split('/')[:2])
      root_document_path = '/%s/%s' % (portal.getId(), root_path)
      recursiveUnindex(catalog, item_path, root_document_path)

  def fixBrokenObject(self, obj):
    if isinstance(obj, ERP5BaseBroken):
      self._resetDynamicModules()

  def install(self, context, trashbin, **kw):
    self.beforeInstall()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')

    def recurse(hook, document, prefix=''):
      my_prefix = '%s/%s' % (prefix, document.id)
      if (hook(document, my_prefix)):
        for subdocument in document.objectValues():
          recurse(hook, subdocument, my_prefix)
    def saveHook(document, prefix):
      uid = getattr(aq_base(document), 'uid', None)
      if uid is None:
        return 0
      else:
        saved_uid_dict[prefix] = uid
        return 1
    def restoreHook(document, prefix):
      uid = saved_uid_dict.get(prefix)
      if uid is None:
        return 0
      else:
        document.uid = uid
        return 1
    groups = {}
    old_groups = {}
    portal = context.getPortalObject()
    # set safe activities execution order
    original_reindex_parameters = self.setSafeReindexationMode(context)
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
          if update_dict.get(container_url) == 'nothing':
            continue
          # If container's container is portal_catalog,
          # then automatically create the container.
          elif len(container_path) > 1 and container_path[-2] == 'portal_catalog':
            # The id match, but better double check with the meta type
            # while avoiding the impact of systematic check
            container_container = portal.unrestrictedTraverse(container_path[:-1])
            # Check for meta_type of container before creating Catalog
            if container_container.meta_type == 'Catalog Tool':
              container_container.newContent(portal_type='Catalog', id=container_path[-1], title='')
            elif container_container.meta_type == 'ERP5 Catalog':
              container_container.manage_addProduct['ZSQLCatalog'].manage_addSQLCatalog(id=container_path[-1], title='')
            else:
              # Raise in case meta_type don't match
              raise ValueError(
                'No meta_type exists for %r during Catalog installation' % (
                container_container.title,
                ),
              )

            # Update default catalog ID
            if len(container_container.objectIds()) == 1:
              # Set the default catalog. Here, thanks to consistency between
              # ERP5CatalogTool and ZSQLCatalog, we can use the explicit accessor
              # `_setDefaultSqlCatalogId` to update both `default_sql_catalog_id`
              # and `default_erp5_catalog_id`
              container_container._setDefaultSqlCatalogId(container_path[-1])
            container = portal.unrestrictedTraverse(container_path)
          else:
            raise
        saved_uid_dict = {}
        subobjects_dict = {}
        portal_type_dict = {}
        old_obj = container._getOb(object_id, None)
        object_existed = old_obj is not None
        if object_existed:
          if context.isKeepObject(path) and force:
            # do nothing if the object is specified in keep list in
            # force mode.
            continue
          # Object already exists
          recurse(saveHook, old_obj)
          if getattr(aq_base(old_obj), 'groups', None) is not None:
            # we must keep original order groups
            # from old form in case we keep some
            # old widget, thus we can readd them in
            # the right order group
            old_groups[path] = deepcopy(old_obj.groups)
          # we force backup since it was an existing object
          subobjects_dict = self._backupObject('backup', trashbin,
                                               container_path, object_id)
          # in case of portal types, we want to keep some properties
          if interfaces.ITypeProvider.providedBy(container):
            for attr in ('allowed_content_types',
                         'hidden_content_type_list',
                         'property_sheet_list',
                         'base_category_list'):
              portal_type_dict[attr] = getattr(old_obj, attr, ())
            portal_type_dict['workflow_chain'] = \
              getChainByType(context)[1].get('chain_' + object_id, '')
          container.manage_delObjects([object_id])
          # unindex here when it is a broken object
          if isinstance(old_obj, Broken):
            new_obj = self._objects[path]
            # check isIndexable with new one, because the old one is broken
            if new_obj.isIndexable():
              self.unindexBrokenObject(path)

        # install object
        obj = self._objects[path]
        self.fixBrokenObject(obj)
        # XXX Following code make Python Scripts compile twice, because
        #     _getCopy returns a copy without the result of the compilation.
        #     A solution could be to add a specific _getCopy method to
        #     Python Scripts.
        if getattr(aq_base(obj), 'groups', None) is not None:
          # we must keep original order groups
          # because they change when we add subobjects
          groups[path] = deepcopy(obj.groups)
        # copy the object
        if (getattr(aq_base(obj), '_mt_index', None) is not None and
            obj._count() == 0):
          # some btrees were exported in a corrupted state. They're empty but
          # their metadata-index (._mt_index) contains entries which in
          # Zope 2.12 are used for .objectIds(), .objectValues() and
          # .objectItems(). In these cases, force the
          LOG('Products.ERP5.Document.BusinessTemplate', WARNING,
              'Cleaning corrupted BTreeFolder2 object at %r.' % (path,))
          obj._initBTrees()
        obj = obj._getCopy(container)
        self.removeProperties(obj, 0)
        __traceback_info__ = (container, object_id, obj)
        container._setObject(object_id, obj)
        obj = container._getOb(object_id)

        if not object_existed:
          # A new object was added, call the hook
          self.onNewObject(obj)

        # mark a business template installation so in 'PortalType_afterClone' scripts
        # we can implement logical for reseting or not attributes (i.e reference).
        self.REQUEST.set('is_business_template_installation', 1)
        # We set isIndexable to 0 before calling
        # manage_afterClone in order to not call recursiveReindex, this is
        # useless because we will already reindex every created object, so
        # we avoid duplication of reindexation
        obj.isIndexable = ConstantGetter('isIndexable', value=False)
        # START:part of ERP5Type.CopySupport.manage_afterClone
        # * reset uid
        # * reset owner
        # * do not reset workflow
        # * do not call recursively
        # * do not call type-based afterClone script
        #
        # Change uid attribute so that Catalog thinks object was not yet catalogued
        aq_base(obj).uid = portal.portal_catalog.newUid()
        # Give the Owner local role to the current user, zope only does this if no
        # local role has been defined on the object, which breaks ERP5Security
        if getattr(aq_base(obj), '__ac_local_roles__', None) is not None:
          user=getSecurityManager().getUser()
          if user is not None:
            userid=user.getId()
            if userid is not None:
              #remove previous owners
              local_role_dict = obj.__ac_local_roles__
              removable_role_key_list = []
              for key, value in local_role_dict.items():
                if 'Owner' in value:
                  value.remove('Owner')
                if len(value) == 0:
                  removable_role_key_list.append(key)
              # there is no need to keep emptied keys after cloning, it makes
              # unstable local roles -- if object is cloned it can be different when
              # after being just added
              for key in removable_role_key_list:
                local_role_dict.pop(key)
              #add new owner
              l=local_role_dict.setdefault(userid, [])
              l.append('Owner')
        # END:part of ERP5Type.CopySupport.manage_afterClone
        del obj.isIndexable
        if getattr(aq_base(obj), 'reindexObject', None) is not None:
          obj.reindexObject()
        obj.wl_clearLocks()
        if portal_type_dict:
          # set workflow chain
          wf_chain = portal_type_dict.pop('workflow_chain')
          chain_dict = getChainByType(context)[1]
          default_chain = ''
          chain_dict['chain_%s' % (object_id)] = wf_chain
          context.portal_workflow.manage_changeWorkflows(default_chain, props=chain_dict)
          # restore some other properties
          obj.__dict__.update(portal_type_dict)
        # import sub objects if there is
        if subobjects_dict:
          # get a jar
          connection = self.getConnection(obj)
          # import subobjects
          for subobject_id, subobject_data in subobjects_dict.iteritems():
            try:
              if obj._getOb(subobject_id, None) is None:
                subobject_data.seek(0)
                subobject = connection.importFile(subobject_data)
                obj._setObject(subobject_id, subobject)
            except AttributeError:
              # XXX this may happen when an object which can contain
              # sub-objects (e.g. ERP5 Form) has been replaced with
              # an object which cannot (e.g. External Method).
              LOG('BusinessTemplate', WARNING,
                  'could not restore %r in %r' % (subobject_id, obj))
        if obj.meta_type in ('Z SQL Method', 'ERP5 SQL Method'):
          fixZSQLMethod(portal, obj)
        # portal transforms specific initialization
        elif obj.meta_type in ('Transform', 'TransformsChain'):
          assert container.meta_type == 'Portal Transforms'
          # skip transforms that couldn't have been initialized
          if obj.title != 'BROKEN':
            container._mapTransform(obj)
        elif obj.meta_type in ('ERP5 Ram Cache',
                               'ERP5 Distributed Ram Cache',):
          assert container.meta_type in ('ERP5 Cache Factory',
                                         'ERP5 Cache Bag')
          container.getParentValue().updateCache()
        elif obj.__class__.__name__ in ('File', 'Image'):
          if "data" in obj.__dict__:
            File._setData.__func__(obj, obj.data)
        elif (container.meta_type == 'CMF Skins Tool') and \
            (old_obj is not None):
          # Keep compatibility with previous export format of
          # business_template_registered_skin_selections
          # and do not modify exported value
          if obj.getProperty('business_template_registered_skin_selections',
                             None) is None:
            # Keep previous value of register skin selection for skin folder
            skin_selection_list = old_obj.getProperty(
                'business_template_registered_skin_selections', None)
            if skin_selection_list is not None:
              if isinstance(skin_selection_list, basestring):
                skin_selection_list = skin_selection_list.split(' ')
              obj._setProperty(
                  'business_template_registered_skin_selections',
                  skin_selection_list, type='tokens')
        # in case the portal ids, we want keep the property dict
        elif interfaces.IIdGenerator.providedBy(obj) and \
          old_obj is not None:
          for dict_name in ('last_max_id_dict', 'last_id_dict'):
            # Keep previous last id dict
            if getattr(old_obj, dict_name, None) is not None:
              old_dict = getattr(old_obj, dict_name, None)
              setattr(obj, dict_name, old_dict)

        recurse(restoreHook, obj)
    # now put original order group
    # we remove object not added in forms
    # we put old objects we have kept
    for path, new_groups_dict in groups.iteritems():
      if not old_groups.has_key(path):
        # installation of a new form
        obj = portal.unrestrictedTraverse(path)
        obj.groups = new_groups_dict
      else:
        # upgrade of a form
        old_groups_dict = old_groups[path]
        obj = portal.unrestrictedTraverse(path)
        # first check that all widgets are in new order
        # excetp the one that had to be removed
        widget_id_list = obj.objectIds()
        for widget_id in widget_id_list:
          widget_path = path+'/'+widget_id
          if update_dict.has_key(widget_path) and update_dict[widget_path] in ('remove', 'save_and_remove'):
            continue
          widget_in_form = 0
          for group_id, group_value_list in new_groups_dict.iteritems():
            if widget_id in group_value_list:
              widget_in_form = 1
              break
          # if not, add it in the same groups
          # defined on the former form
          previous_group_id = None
          if not widget_in_form:
            for old_group_id, old_group_values in old_groups_dict.iteritems():
              if widget_id in old_group_values:
                previous_group_id = old_group_id
            # if we find same group in new one, add widget to it
            if previous_group_id is not None and new_groups_dict.has_key(previous_group_id):
              new_groups_dict[previous_group_id].append(widget_id)
            # otherwise use a specific group
            else:
              if new_groups_dict.has_key('not_assigned'):
                new_groups_dict['not_assigned'].append(widget_id)
              else:
                new_groups_dict['not_assigned'] = [widget_id,]
                obj.group_list = list(obj.group_list) + ['not_assigned']
        # second check all widget_id in order are in form
        for group_id, group_value_list in new_groups_dict.iteritems():
          for widget_id in tuple(group_value_list):
            if widget_id not in widget_id_list:
              # if we don't find the widget id in the form
              # remove it fro the group
              group_value_list.remove(widget_id)
        # now set new group object
        obj.groups = new_groups_dict
    # restore previous activities execution order
    context.setPlacelessDefaultReindexParameters(**original_reindex_parameters)
    to_delete_dict = {}
    # XXX: it is not clear why update_dict would contain subojects of any
    # element of object_key_list, and not just these objects themselves.
    # XXX: why does update_dict contain the path of documents not managed
    # by current instance ?
    for path, action in update_dict.iteritems():
      if action not in ('remove', 'save_and_remove'):
        continue
      path_match = path + '/'
      for object_key in object_key_list:
        if path_match.startswith(object_key + '/'):
          to_delete_dict[path] = action
    # Sort by path so that, for example, form is created before its fields.
    for path, action in sorted(to_delete_dict.iteritems()):
      document = self.unrestrictedResolveValue(portal, path, None)
      if document is None:
        continue
      if getattr(aq_base(document), 'getParentValue', None) is None:
        parent = document.aq_parent
      else:
        parent = document.getParentValue()
      document_id = document.getId()
      self._backupObject(action, trashbin, path.split('/')[:-1],
                         document_id)
      try:
        parent.manage_delObjects([document_id])
      except BadRequest:
        pass # removed manually

    self.afterInstall()

  def uninstall(self, context, **kw):
    portal = context.getPortalObject()
    trash = kw.get('trash', 0)
    trashbin = kw.get('trashbin', None)
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for relative_url in object_keys:
      container_path = relative_url.split('/')[0:-1]
      object_id = relative_url.split('/')[-1]
      try:
        container = self.unrestrictedResolveValue(portal, container_path)
        container._getOb(object_id) # We force access to the object to be sure
                                        # that appropriate exception is thrown
                                        # in case object is already backup and/or removed
        if trash and trashbin is not None:
          self.portal_trash.backupObject(trashbin, container_path, object_id, save=1, keep_subobjects=1)
        if container.meta_type == 'CMF Skins Tool':
          # we are removing a skin folder, check and
          # remove if registered skin selection
          unregisterSkinFolderId(container, object_id,
              container.getSkinSelections())

        container.manage_delObjects([object_id])
        if container.aq_parent.meta_type == 'ERP5 Catalog' and not len(container):
          # We are removing a ZSQLMethod, remove the SQLCatalog if empty
          container.getParentValue().manage_delObjects([container.id])
      except (NotFound, KeyError, BadRequest, AttributeError):
        # object is already backup and/or removed
        pass
    BaseTemplateItem.uninstall(self, context, **kw)
    self.afterUninstall()

class PathTemplateItem(ObjectTemplateItem):
  """
    This class is used to store objects with wildcards supported.
  """
  def __init__(self, id_list, tool_id=None, **kw):
    BaseTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    id_list = self._archive.keys()
    self._archive.clear()
    self._path_archive = PersistentMapping()
    for id in id_list:
      self._path_archive[id] = None

  def uninstall(self, context, **kw):
    portal = context.getPortalObject()
    trash = kw.get('trash', 0)
    trashbin = kw.get('trashbin', None)
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._path_archive.keys()
    object_keys.sort()
    object_keys.reverse()
    p = context.getPortalObject()
    for path in object_keys:
      try:
        path_list = self._resolvePath(p, [], path.split('/'))
      except AttributeError:
        # path seems to not exist anymore
        continue
      path_list.sort()
      path_list.reverse()
      for relative_url in path_list:
        try:
          container_path = relative_url.split('/')[0:-1]
          object_id = relative_url.split('/')[-1]
          container = self.unrestrictedResolveValue(portal, container_path)
          if trash and trashbin is not None:
            self.portal_trash.backupObject(trashbin, container_path,
                                           object_id, save=1,
                                           keep_subobjects=1)
          container.manage_delObjects([object_id])
        except (NotFound, KeyError):
          # object is already backup and/or removed
          pass
    BaseTemplateItem.uninstall(self, context, **kw)

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
    BaseTemplateItem.build(self, context, **kw)
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
        obj = self.removeProperties(obj, 1,
                                    self.isKeepWorkflowObject(relative_url),
                                    self.isKeepWorkflowObjectLastHistoryOnly(relative_url))
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
    super(PathTemplateItem, self).install(context, *args, **kw)

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

class ToolTemplateItem(PathTemplateItem):
  """This class is used only for making a distinction between other objects
  and tools, because tools may not be backed up."""
  def _backupObject(self, action, trashbin, container_path, object_id, **kw):
    """Fake as if a trashbin is not available."""
    return PathTemplateItem._backupObject(self, action, None, container_path,
                                          object_id, **kw)

  def install(self, context, trashbin, **kw):
    """ When we install a tool that is a type provider not
    registered on types tool, register it into the type provider.
    """
    PathTemplateItem.install(self, context, trashbin, **kw)
    portal = context.getPortalObject()
    types_tool = portal.portal_types
    for type_container_id, obj in self._objects.iteritems():
      if (interfaces.ITypeProvider.providedBy(obj) and
          type_container_id != types_tool.id and
          type_container_id not in types_tool.type_provider_list):
        types_tool.type_provider_list = tuple(types_tool.type_provider_list) + \
                                        (type_container_id,)

  def uninstall(self, context, **kw):
    """ When we uninstall a tool, unregister it from the type provider. """
    portal = context.getPortalObject()
    types_tool = portal.portal_types
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._path_archive.keys()
    for tool_id in object_keys:
      types_tool.type_provider_list = tuple([ \
        x for x in types_tool.type_provider_list \
        if x != tool_id])
    PathTemplateItem.uninstall(self, context, **kw)

  def remove(self, context, **kw):
    """ When we remove a tool, unregister it from the type provider. """
    portal = context.getPortalObject()
    types_tool = portal.portal_types
    remove_dict = kw.get('remove_object_dict', {})
    keys = self._objects.keys()
    for tool_id in keys:
      if remove_dict.has_key(tool_id):
        action = remove_dict[tool_id]
        if 'remove' in action:
          types_tool.type_provider_list = tuple([ \
            x for x in types_tool.type_provider_list \
            if x != tool_id])
    PathTemplateItem.remove(self, context, **kw)

class PreferenceTemplateItem(PathTemplateItem):
  """
  This class is used to store preference objects
  """
  def _resolvePath(self, folder, relative_url_list, id_list):
    """
    This method calls itself recursively.

    The folder is the current object which contains sub-objects.
    The list of ids are path components. If the list is empty,
    the current folder is valid.
    """
    if relative_url_list != []:
      LOG("PreferenceTemplateItem, _resolvePath", WARNING,
          "Should be empty")
    if len(id_list) != 1:
      LOG("PreferenceTemplateItem, _resolvePath", WARNING,
          "Should contain only one element")
    # XXX hardcoded
    return ['portal_preferences/%s' % id_list[0]]

  def install(self, context, trashbin, **kw):
    """
    Enable Preference
    """
    PathTemplateItem.install(self, context, trashbin, **kw)
    portal = context.getPortalObject()
    for object_path in self._objects.keys():
      pref = portal.unrestrictedTraverse(object_path)
      # XXX getPreferenceState is a bad name
      if pref.getPreferenceState() == 'disabled':
        # set safe activities execution order
        original_reindex_parameters = self.setSafeReindexationMode(context)
        portal.portal_workflow.doActionFor(
                      pref,
                      'enable_action',
                      comment="Initialized during Business Template " \
                              "installation.")
        # restore previous activities execution order
        context.setPlacelessDefaultReindexParameters(**original_reindex_parameters)

class CategoryTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_categories', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def build_sub_objects(self, context, id_list, url, **kw):
    for id in id_list:
      relative_url = '/'.join([url,id])
      obj = context._getOb(id)
      obj = self.removeProperties(obj, 1,
                                  self.isKeepWorkflowObject(relative_url),
                                  self.isKeepWorkflowObjectLastHistoryOnly(relative_url))
      id_list = obj.objectIds()
      if id_list:
        self.build_sub_objects(obj, id_list, relative_url)
        for id_ in list(id_list):
          _delObjectWithoutHook(obj, id_)
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      try:
        obj = p.unrestrictedTraverse(relative_url)
        obj = obj._getCopy(context)
      except (KeyError, AttributeError):
        if self.is_bt_for_diff:
          continue
        else:
          raise ValueError, "%s not found" % relative_url
      _recursiveRemoveUid(obj)
      obj = self.removeProperties(obj, 1,
                                  self.isKeepWorkflowObject(relative_url),
                                  self.isKeepWorkflowObjectLastHistoryOnly(relative_url))
      include_sub_categories = obj.__of__(context).getProperty('business_template_include_sub_categories', 0)
      id_list = obj.objectIds()
      if len(id_list) > 0 and include_sub_categories:
        self.build_sub_objects(obj, id_list, relative_url)
      for id_ in list(id_list):
        _delObjectWithoutHook(obj, id_)
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def beforeInstall(self):
    self._installed_new_category = False

  def onNewObject(self, obj):
    self._installed_new_category = True

  def afterInstall(self):
    if self._installed_new_category:
      # reset accessors if we installed a new category
      self.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()

class SkinTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_skins', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def build(self, context, **kw):
    ObjectTemplateItem.build(self, context, **kw)
    for relative_url in self._objects.keys():
      obj = self._objects[relative_url]
      if (getattr(obj, 'meta_type', None) == 'Folder') and \
        (obj.getProperty('business_template_registered_skin_selections', None) \
            is not None):
          obj._delProperty(
              'business_template_registered_skin_selections')

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = ObjectTemplateItem.preinstall(self, context, installed_item, **kw)
    # We must install/update an ERP5 Form if one of its widget is modified.
    # This allow to keep the widget order and the form layout after an update
    #   from a BT to another one.
    for (bt_obj_path, bt_obj) in self._objects.items():
      if getattr(bt_obj, 'meta_type', None) == 'ERP5 Form':
        # search sub-objects of ERP5 Forms that are marked as "modified"
        for upd_obj_path in modified_object_list.keys():
          if upd_obj_path.startswith(bt_obj_path):
            # a child of the ERP5 Form must be updated, so the form too
            if not modified_object_list.has_key(bt_obj_path):
              modified_object_list[bt_obj_path] = 'Modified', self.__class__.__name__[:-12]
    return modified_object_list

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    skin_tool = p.portal_skins
    for relative_url in self._objects.keys():
      # Do not register skin which were explicitely ask not to be installed
      if not force and update_dict.get(relative_url)  == 'nothing':
        continue
      folder = self.unrestrictedResolveValue(p, relative_url)
      for obj in folder.objectValues(spec=('Z SQL Method', 'ERP5 SQL Method')):
        fixZSQLMethod(p, obj)
      if folder.aq_parent.meta_type == 'CMF Skins Tool':
        registerSkinFolder(skin_tool, folder)

class RegisteredSkinSelectionTemplateItem(BaseTemplateItem):
  # BUG: Let's suppose old BT defines
  #         some_skin | Skin1
  #         some_skin | Skin2
  #      and new BT has:
  #         some_skin | Skin1
  #      Because 'some_skin' is still defined, it will be updated (actually
  #      'install') and not removed ('uninstall'). But we don't compare with
  #      old BT so we don't know we must unregister Skin2.

  def build(self, context, **kw):
    portal = context.getPortalObject()
    skin_tool = getToolByName(portal, 'portal_skins')

    for key in self._archive.keys():
      skin_folder_id, skin_selection_id = key.split(' | ')

      skin_folder = skin_tool[skin_folder_id]
      selection_list = skin_folder.getProperty(
          'business_template_registered_skin_selections',
          [])
      # Backward compatibility, some values can be string
      if isinstance(selection_list, str):
        selection_list = selection_list.replace(',', ' ').split(' ')
      if skin_selection_id in selection_list:
        self._objects.setdefault(skin_folder_id, []).append(skin_selection_id)
      else:
        raise NotFound, 'No skin selection %s found for skin folder %s.' \
                          % (skin_selection_id, skin_folder_id)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    xml_data = '<registered_skin_selection>'
    keys = self._objects.keys()
    keys.sort()
    for key in keys:
      skin_selection_list = self._objects[key]
      xml_data += '\n <skin_folder_selection>'
      xml_data += '\n  <skin_folder>%s</skin_folder>' % key
      xml_data += '\n  <skin_selection>%s</skin_selection>' \
                      % ','.join(sorted(skin_selection_list))
      xml_data += '\n </skin_folder_selection>'
    xml_data += '\n</registered_skin_selection>'
    return xml_data

  def export(self, context, bta, **kw):
    if not self._objects:
      return
    # export workflow chain
    bta.addObject(self.generateXml(),
                  name='registered_skin_selection',
                  path=self.__class__.__name__)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    portal = context.getPortalObject()
    skin_tool = getToolByName(portal, 'portal_skins')

    for skin_folder_id in self._objects.keys():

      if update_dict.has_key(skin_folder_id) or force:
        if not force:
          action = update_dict[skin_folder_id]
          if action == 'nothing':
            continue
        skin_folder = skin_tool[skin_folder_id]
        default_value = []
        selection_list = skin_folder.getProperty(
          'business_template_registered_skin_selections', default_value)

        if selection_list is default_value:
          create_property = True
          selection_list = self._objects[skin_folder_id]
        else:
          create_property = False
          if isinstance(selection_list, basestring):
            selection_list = selection_list.replace(',', ' ').split(' ')
          elif isinstance(selection_list, tuple):
            selection_list = list(selection_list)
          selection_list.extend(self._objects[skin_folder_id])

        # Remove duplicate
        selection_list = list(set(selection_list))
        if create_property:
          skin_folder._setProperty(
              'business_template_registered_skin_selections',
              selection_list, type='tokens')
        else:
          skin_folder._updateProperty(
              'business_template_registered_skin_selections',
              selection_list)

        unregisterSkinFolderId(skin_tool, skin_folder_id,
                               skin_tool.getSkinSelections())
        registerSkinFolder(skin_tool, skin_folder)

  def uninstall(self, context, **kw):
    portal = context.getPortalObject()
    skin_tool = getToolByName(portal, 'portal_skins')
    object_path = kw.get('object_path')
    for skin_folder_id in (object_path,) if object_path else self._objects:
      skin_selection_list = self._objects[skin_folder_id]
      if isinstance(skin_selection_list, str):
        skin_selection_list = skin_selection_list.replace(',', ' ').split(' ')
      skin_folder = skin_tool.get(skin_folder_id)
      if skin_folder is not None:
        current_selection_set = set(skin_folder.getProperty(
          'business_template_registered_skin_selections', ()))
        current_selection_set.difference_update(skin_selection_list)
        if current_selection_set:
          skin_folder._updateProperty(
            'business_template_registered_skin_selections',
            list(current_selection_set))
          # Unregister skin folder from skin selection
          unregisterSkinFolderId(skin_tool, skin_folder_id, skin_selection_list)
          continue
      # Delete all skin selection
      for skin_selection in skin_selection_list:
        deleteSkinSelection(skin_tool, skin_selection)
      if skin_folder is not None:
        del skin_folder.business_template_registered_skin_selections
        # Register to all other skin selection
        registerSkinFolder(skin_tool, skin_folder)

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    for path in self._objects:
      if installed_item._objects.has_key(path):
        # compare object to see it there is changes
        new_object = self._objects[path]
        old_object = installed_item._objects[path]
        if new_object != old_object:
          modified_object_list[path] = 'Modified', self.__class__.__name__[:-12]
      else: # new object
        modified_object_list[path] = 'New', self.__class__.__name__[:-12]
    # get removed object
    old_keys = installed_item._objects.keys()
    for path in old_keys:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', self.__class__.__name__[:-12]
    return modified_object_list

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    # import workflow chain for portal_type
    skin_selection_dict = {}
    xml = parse(file)
    for skin_folder_selection in xml.getroot():
      skin_folder_id = skin_folder_selection.find('skin_folder').text
      selection_string = skin_folder_selection.find('skin_selection').text
      if not selection_string:
        selection_list = []
      else:
        selection_list = selection_string.split(',')
      skin_selection_dict[skin_folder_id] = selection_list
    self._objects = skin_selection_dict

class RegisteredVersionPrioritySelectionTemplateItem(BaseTemplateItem):
  def _fillObjectDictFromArchive(self):
    for version_priority in self._archive:
      try:
        version, priority = version_priority.split('|')
        priority = float(priority)
      except ValueError:
        version = version_priority
        priority = 0.

      self._objects[version.strip()] = priority

  def build(self, context, **kw):
    self._fillObjectDictFromArchive()

  def beforeInstall(self):
    self.__is_new_version_priority_installed = False

  def install(self, context, trashbin, **kw):
    if not self._objects:
      return

    self.beforeInstall()

    portal = context.getPortalObject()
    registered_tuple_list = []
    for value in portal.getVersionPriorityList():
      try:
        version, priority = value.split('|')
        priority = float(priority)
      except ValueError:
        version = value
        priority = 0.

      registered_tuple_list.append((version.strip(), priority))

    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    registered_name_list = set(portal.getVersionPriorityNameList())
    for new_version, new_priority in self._objects.iteritems():
      action = update_dict.get(new_version)
      if (not action or action == 'nothing') and not force:
        continue

      # Merge version and priority defined on this bt and already registered
      # version and priority
      inserted = False
      index = 0
      for (version, priority) in registered_tuple_list:
        if new_version == version:
          if new_priority == priority:
            inserted = True
            break
          else:
            del registered_tuple_list[index]
            continue
        elif not inserted:
          if new_priority > priority:
            registered_tuple_list.insert(index, (new_version, new_priority))
            inserted = True
          elif new_priority == priority and new_version >= version:
            registered_tuple_list.insert(index, (new_version, new_priority))
            inserted = True

        index += 1

      if not inserted:
        registered_tuple_list.append((new_version, new_priority))

      self.__is_new_version_priority_installed = True

    portal.setVersionPriorityList(('%s | %s' % (version, priority)
                                   for version, priority in registered_tuple_list))

    self.afterInstall()

  def afterInstall(self):
    if self.__is_new_version_priority_installed:
      self.portal_components.reset(force=True,
                                   reset_portal_type_at_transaction_boundary=True)

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    class_name_prefix = self.__class__.__name__[:-12]
    for path, new_object in self._objects.iteritems():
      old_object = installed_item._objects.get(path)
      if old_object is not None:
        # Compare object to see it there is any change
        if new_object != old_object:
          modified_object_list[path] = 'Modified', class_name_prefix
      else:
        modified_object_list[path] = 'New', class_name_prefix

    # Get removed objects
    for path in installed_item._objects:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', class_name_prefix

    return modified_object_list

  def importFile(self, bta, **kw):
    super(RegisteredVersionPrioritySelectionTemplateItem,
          self).importFile(bta, **kw)

    self._objects.clear()
    self._fillObjectDictFromArchive()

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path')
    object_list = object_path and (object_path,) or self._objects

    portal = context.getPortalObject()
    registered_list = list(portal.getVersionPriorityList())
    index = 0
    for version in portal.getVersionPriorityNameList():
      if version in object_list:
        del registered_list[index]
      else:
        index += 1

    portal.setVersionPriorityList(registered_list)

class WorkflowTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_workflow', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  # When the root object of a workflow is modified, the entire workflow is
  # recreated: all subobjects are discarded and must be reinstalled.
  # So we hide modified subobjects to the user and we always reinstall
  # (or remove) everything.

  def preinstall(self, context, installed_item, installed_bt, **kw):
    modified_object_dict = ObjectTemplateItem.preinstall(self, context,
                                                         installed_item, **kw)
    modified_workflow_dict = {}
    for modified_object, state in modified_object_dict.iteritems():
      path = modified_object.split('/')
      if len(path) > 2:
        modified_workflow_dict.setdefault('/'.join(path[:2]), ('Modified', state[1]))
      else:
        modified_workflow_dict[modified_object] = state
    removed_workflow_id_list = [x[0].split('/', 1)[1] \
                                for x in modified_workflow_dict.iteritems() \
                                if x[1][0] == 'Removed']
    if len(removed_workflow_id_list) > 0:
      installed_chain_list = [[y.strip() for y in x.split('|')] for x in \
                                installed_bt.getTemplatePortalTypeWorkflowChainList()]
      new_chain_list = [[y.strip() for y in x.split('|')] for x in \
                          context.getTemplatePortalTypeWorkflowChainList()]
      chain_dict = getChainByType(context)[1]
      for workflow_id in removed_workflow_id_list:
        affected_portal_type_set = {x[6:] for x, y in chain_dict.iteritems()
          if any(workflow_id == y.strip() for y in y.split(','))}
        safe_portal_type_set = {x for x, y in installed_chain_list
                                  if y == workflow_id}
        safe_portal_type_set.difference_update(x for x, y in new_chain_list
                                                 if y == workflow_id)
        if affected_portal_type_set - safe_portal_type_set:
          value = modified_workflow_dict['portal_workflow/%s' % workflow_id]
          modified_workflow_dict['portal_workflow/%s' % workflow_id] = \
              ('Removed but used', value[1])
    return modified_workflow_dict

  def install(self, context, trashbin, **kw):
    portal = context.getPortalObject()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # sort to add objects before their subobjects
    for path in sorted(self._objects):
        if force:
          action = 'backup'
        else:
          action = update_dict.get('/'.join(path.split('/')[:2]))
          if action in (None, 'nothing'):
            continue
        container_path = path.split('/')[:-1]
        object_id = path.split('/')[-1]
        try:
          container = self.unrestrictedResolveValue(portal, container_path)
        except KeyError:
          # parent object can be set to nothing, in this case just go on
          container_url = '/'.join(container_path)
          if update_dict.has_key(container_url):
            if update_dict[container_url] == 'nothing':
              continue
          raise
        container_ids = container.objectIds()
        if object_id in container_ids:    # Object already exists
          self._backupObject(action, trashbin, container_path, object_id, keep_subobjects=1)
          container.manage_delObjects([object_id])
        obj = self._objects[path]
        obj = obj._getCopy(container)
        self.removeProperties(obj, 0)
        container._setObject(object_id, obj)
        obj = container._getOb(object_id)
        obj.manage_afterClone(obj)
        obj.wl_clearLocks()

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    removed_workflow_id_list = {x.split('/', 1)[1] for x in object_keys}
    (default_chain, chain_dict) = getChainByType(context)
    for portal_type, workflow_ids in chain_dict.iteritems():
      workflow_ids = {x.strip() for x in workflow_ids.split(',')} - \
                     removed_workflow_id_list
      chain_dict[portal_type] = ', '.join(workflow_ids)
    context.portal_workflow.manage_changeWorkflows(default_chain,
                                                   props=chain_dict)
    ObjectTemplateItem.uninstall(self, context, **kw)

class PortalTypeTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_types', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    # XXX : this statement can be removed once all bt5 have separated
    # workflow-chain information
    self._workflow_chain_archive = PersistentMapping()

  def build(self, context, **kw):
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse(relative_url)
      # normalize relative_url, not all type informations are stored in
      # "portal_types"
      relative_url = '%s/%s' % (obj.getPhysicalPath()[-2:])

      obj = obj._getCopy(context)
      obj._p_activate()
      for attr in obj.__dict__.keys():
        if attr == '_property_domain_dict':
          continue
        if attr[0] == '_' or attr in ('allowed_content_types',
                                      'hidden_content_type_list',
                                      'property_sheet_list',
                                      'base_category_list',
                                      'last_id', 'uid') or \
            (attr == 'workflow_history' and
             not self.isKeepWorkflowObject(relative_url)):
          delattr(obj, attr)
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def _getObjectKeyList(self):
    # Sort portal types to install according to their dependencies
    object_key_list = self._objects.keys()
    path_dict = dict(x.split('/')[1:] + [x] for x in object_key_list)
    cache = {}
    def solveDependency(path):
      score = cache.get(path)
      if score is None:
        obj = self._objects[path]
        klass = obj.__class__
        if klass.__module__ != 'erp5.portal_type':
          portal_type = obj.portal_type
        else:
          portal_type = klass.__name__
        depend = path_dict.get(portal_type)
        # Prevent infinite recursion for 'portal_types/Base Type',
        # only relevant with Portal Types classes because 'Base Type'
        # is an 'erp5.portal_type.Base Type' class
        if depend == path:
          assert depend == 'portal_types/Base Type'
          return 0, path
        cache[path] = score = depend and 1 + solveDependency(depend)[0] or 0
      return score, path
    object_key_list.sort(key=solveDependency)
    return object_key_list

  # XXX : this method is kept temporarily, but can be removed once all bt5 are
  # re-exported with separated workflow-chain information
  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # We now need to setup the list of workflows corresponding to
    # each portal type
    (default_chain, chain_dict) = getChainByType(context)
    # Set the default chain to the empty string is probably the
    # best solution, by default it is 'default_workflow', which is
    # not very usefull
    default_chain = ''
    for path, obj in self._objects.iteritems():
      if update_dict.has_key(path) or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        portal_type = obj.id
        if self._workflow_chain_archive.has_key(portal_type):
          chain_dict['chain_%s' % portal_type] = \
              self._workflow_chain_archive[portal_type]
    context.portal_workflow.manage_changeWorkflows(default_chain,
                                                   props=chain_dict)
  # XXX : this method is kept temporarily, but can be removed once all bt5 are
  # re-exported with separated workflow-chain information
  def _importFile(self, file_name, file):
    if 'workflow_chain_type.xml' in file_name:
      # import workflow chain for portal_type
      result_dict = {}
      xml = parse(file)
      chain_list = xml.findall('//chain')
      for chain in chain_list:
        portal_type = chain.find('type').text
        workflow = chain.find('workflow').text or ''
        result_dict[portal_type] = workflow
      self._workflow_chain_archive = result_dict
    else:
      ObjectTemplateItem._importFile(self, file_name, file)

class PortalTypeWorkflowChainTemplateItem(BaseTemplateItem):

  _chain_string_prefix = 'chain_'
  _chain_string_separator = ', '

  def build(self, context, **kw):
    # we can either specify nothing, +, - or = before the chain
    # this is used to know how to manage the chain
    # if nothing or +, chain is added to the existing one
    # if - chain is removed from the exisiting one
    # if = chain replaced the existing one
    (default_chain, chain_dict) = getChainByType(context)
    for key in self._archive.keys():
      wflist = key.split(' | ')
      if len(wflist) == 2:
        portal_type = wflist[0]
        workflow = wflist[1]
      else:
        # portal type with no workflow defined
        portal_type = wflist[0][:-2]
        workflow = ''
      portal_type_key = '%s%s' % (self._chain_string_prefix, portal_type)
      if portal_type_key in chain_dict:
        workflow_name = workflow.lstrip('+-=')
        if workflow[0] != '-' and workflow_name not in \
           chain_dict[portal_type_key].split(self._chain_string_separator):
          if not self.is_bt_for_diff:
            # here, we use 'LOG' instead of 'raise', because it can
            # happen when a workflow is removed from the chain by
            # another business template.
            LOG('BusinessTemplate', WARNING, 'workflow %s not found '\
                       'in chain for portal_type %s' % (workflow_name, portal_type))
        self._objects.setdefault(portal_type, []).append(workflow)
      elif not self.is_bt_for_diff:
        raise NotFound, 'No workflow chain found for portal type %s. This '\
                        'is probably a sign of a missing dependency.'\
                                                    % portal_type

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    xml_data = '<workflow_chain>'
    key_list = self._objects.keys()
    key_list.sort()
    for key in key_list:
      workflow_list = self._objects[key]
      xml_data += '\n <chain>'
      xml_data += '\n  <type>%s</type>' %(key,)
      xml_data += '\n  <workflow>%s</workflow>' %(
        self._chain_string_separator.join(sorted(workflow_list)))
      xml_data += '\n </chain>'
    xml_data += '\n</workflow_chain>'
    return xml_data

  def export(self, context, bta, **kw):
    if not self._objects:
      return
    # 'portal_type_workflow_chain/' is added in _importFile
    # and if the template is not built,
    # it should be removed here from the key
    new_objects = PersistentMapping()
    for key, value in self._objects.iteritems():
      new_key = deepcopy(key)
      if 'portal_type_workflow_chain/' in key:
        new_key = new_key.replace('portal_type_workflow_chain/', '')
      new_objects[new_key] = value
    self._objects = new_objects
    # export workflow chain
    xml_data = self.generateXml()
    bta.addObject(xml_data, name='workflow_chain_type',
                  path=self.__class__.__name__)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    installed_bt = kw.get('installed_bt')
    if installed_bt is not None:
      previous_portal_type_workflow_chain_list = list(installed_bt\
          .getTemplatePortalTypeWorkflowChainList())
    else:
      previous_portal_type_workflow_chain_list = []
    # We now need to setup the list of workflows corresponding to
    # each portal type
    (default_chain, chain_dict) = getChainByType(context)
    # First convert all workflow_ids into list.
    for key, value in chain_dict.iteritems():
      chain_dict[key] = value.split(self._chain_string_separator)
    orig_chain_dict = chain_dict.copy()
    # Set the default chain to the empty string is probably the
    # best solution, by default it is 'default_workflow', which is
    # not very usefull
    default_chain = ''
    for path in self._objects:
      if path in update_dict or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        path_splitted = path.split('/', 1)
        # XXX: to avoid crashing when no portal_type
        if not path_splitted:
          continue
        portal_type = path_splitted[-1]
        chain_key = '%s%s' % (self._chain_string_prefix, portal_type)
        if chain_key in chain_dict:
          # XXX we don't use the chain (Default) in erp5 so don't keep it
          old_chain_list = [workflow_id for workflow_id in\
                            chain_dict[chain_key] if workflow_id not in\
                            ('(Default)', '',)]
          old_chain_workflow_id_set = set(old_chain_list)
          # get new workflow id list
          workflow_id_list = self._objects[path]
          # fetch list of new workflows which shall be added to chains
          addative_workflow_id_list = [q.lstrip('+') for q in workflow_id_list\
              if not q.startswith('-') and not q.startswith('=')]
          for previous_line in [q for q in \
              previous_portal_type_workflow_chain_list \
              if q.startswith(portal_type)]:
            previous_portal_type, previous_workflow_id = previous_line.split(
                '|')
            previous_portal_type = previous_portal_type.strip()
            previous_workflow_id = previous_workflow_id.strip()
            if not previous_workflow_id.startswith('-') \
                and not previous_workflow_id.startswith('='):
              # else: nothing can be done if previously workflow was removed
              # or replaced as this requires introspection on global system
              previous_workflow_id = previous_workflow_id.lstrip('+')
              if previous_workflow_id not in addative_workflow_id_list:
                # In previous Business Template workflow was chained with
                # portal type, but current Business Template cancels this
                # so it shall be removed
                workflow_id_list.append('-%s' % previous_workflow_id)
          for wf_id in workflow_id_list:
            if wf_id[0] == '-':
              # remove wf id if already present
              if wf_id[1:] in old_chain_workflow_id_set:
                old_chain_workflow_id_set.remove(wf_id[1:])
            elif wf_id[0] == '=':
              # replace existing chain by this one
              old_chain_workflow_id_set = set()
              old_chain_workflow_id_set.add(wf_id[1:])
            # then either '+' or nothing, add wf id to the list
            else:
              wf_id = wf_id.lstrip('+')
              old_chain_workflow_id_set.add(wf_id)
            # create the new chain
            chain_dict[chain_key] = list(old_chain_workflow_id_set)
          if not workflow_id_list:
            # Check if it has normally to remove a workflow chain, in order to
            # improve the error message
            for wf_id in self._objects[path]:
              if wf_id.startswith('-'):
                raise ValueError, '"%s" is not a workflow ID for %s' % \
                                  (wf_id, portal_type)
            chain_dict[chain_key] = self._objects[path]
        else:
          if context.portal_types.getTypeInfo(portal_type) is None:
            raise ValueError('Cannot chain workflow %r to non existing '
                           'portal type %r' % (self._chain_string_separator\
                                                     .join(self._objects[path])
                                               , portal_type))
          chain_dict[chain_key] = self._objects[path]
    if orig_chain_dict == chain_dict:
      return
    self._resetDynamicModules()
    # convert workflow list into string only at the end.
    for key, value in chain_dict.iteritems():
      chain_dict[key] =  self._chain_string_separator.join(value)
    context.portal_workflow.manage_changeWorkflows(default_chain,
                                                   props=chain_dict)

  def uninstall(self, context, **kw):
    (default_chain, chain_dict) = getChainByType(context)
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_key_list = [object_path]
    else:
      object_key_list = self._objects.keys()
    for object_key in object_key_list:
      path_splitted = object_key.split('/', 1)
      if len(path_splitted) < 2:
        continue
      portal_type = path_splitted[1]
      path = '%s%s' % (self._chain_string_prefix, portal_type)
      if path in chain_dict:
        workflow_id_list = chain_dict[path].\
                                            split(self._chain_string_separator)
        removed_workflow_id_list = self._objects[object_key]
        for workflow_id in removed_workflow_id_list:
          for i in range(workflow_id_list.count(workflow_id)):
            workflow_id_list.remove(workflow_id)
        if not workflow_id_list:
          del chain_dict[path]
        else:
          chain_dict[path] = self._chain_string_separator.\
                                                  join(workflow_id_list)
    context.getPortalObject().portal_workflow.\
                                   manage_changeWorkflows('', props=chain_dict)

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    new_dict = PersistentMapping()
    # Fix key from installed bt if necessary
    for key, value in installed_item._objects.iteritems():
      if not 'portal_type_workflow_chain/' in key:
        key = 'portal_type_workflow_chain/%s' % (key)
      new_dict[key] = value
    if new_dict:
      installed_item._objects = new_dict
    for path in self._objects:
      if path in installed_item._objects:
        # compare object to see it there is changes
        new_object = self._objects[path]
        old_object = installed_item._objects[path]
        if isinstance(new_object, str):
          new_object = new_object.split(self._chain_string_separator)
        if isinstance(old_object, str):
          old_object = old_object.split(self._chain_string_separator)
        new_object.sort()
        old_object.sort()
        if new_object != old_object:
          modified_object_list[path] = 'Modified', self.getTemplateTypeName()
      else: # new object
        modified_object_list[path] = 'New', self.getTemplateTypeName()
    # get removed object
    for path in installed_item._objects:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', self.getTemplateTypeName()
    return modified_object_list

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    # import workflow chain for portal_type
    result_dict = {}
    xml = parse(file)
    chain_list = xml.findall('chain')
    for chain in chain_list:
      portal_type = chain.find('type').text
      workflow_chain = chain.find('workflow').text or ''
      if 'portal_type_workflow_chain/' not in portal_type:
        key = 'portal_type_workflow_chain/%s' % (portal_type,)
      else:
        key = portal_type
      result_dict[key] = workflow_chain.split(self._chain_string_separator)
    self._objects = result_dict

# just for backward compatibility
PortalTypeTemplateWorkflowChainItem = PortalTypeWorkflowChainTemplateItem

class PortalTypeAllowedContentTypeTemplateItem(BaseTemplateItem):
  # XXX This class is subclassed for hidden types, propertysheets, base
  # categories ...
  name = 'Allowed Content Type'
  xml_tag = 'allowed_content_type_list'
  class_property = 'allowed_content_types'
  business_template_class_property = '_portal_type_allowed_content_type_item'

  def build(self, context, **kw):
    types_tool = getToolByName(self.getPortalObject(), 'portal_types')
    for key in self._archive.keys():
      try:
        portal_type, allowed_type = key.split(' | ')
      except ValueError:
        raise ValueError('Invalid item %r in %s' % (key, self.name))
      ob = types_tool.getTypeInfo(portal_type)
      # check properties corresponds to what is defined in site
      if ob is None:
        raise ValueError, "Portal Type %r not found in site" %(portal_type,)
      prop_value = getattr(ob, self.class_property, ())
      if allowed_type in prop_value:
        if self.class_property not in portal_type:
          key = '%s/%s' % (self.class_property, portal_type)
        else:
          key = portal_type
        self._objects.setdefault(key, []).append(allowed_type)
      elif not self.is_bt_for_diff:
        raise ValueError, "%s %s not found in portal type %s" % (
                             getattr(self, 'name', self.__class__.__name__),
                             allowed_type, portal_type)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    xml_data = '<%s>' %(self.xml_tag,)
    key_list = self._objects.keys()
    key_list.sort()
    for key in key_list:
      id_value = key.replace('%s/' % self.class_property, '')
      allowed_item_list = sorted(self._objects[key])
      xml_data += '\n <portal_type id="%s">' % (id_value)
      for allowed_item in allowed_item_list:
        xml_data += '\n  <item>%s</item>' %(allowed_item,)
      xml_data += '\n </portal_type>'
    xml_data += '\n</%s>' %(self.xml_tag,)
    return xml_data

  def export(self, context, bta, **kw):
    if not self._objects:
      return
    xml_data = self.generateXml(path=None)
    bta.addObject(xml_data, name=self.class_property,
                  path=self.__class__.__name__)

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    new_dict = PersistentMapping()
    # fix key if necessary in installed bt for diff
    for key, value in installed_item._objects.iteritems():
      if self.class_property not in key:
        key = '%s/%s' % (self.class_property, key)
      new_dict[key] = value
    if new_dict:
      installed_item._objects = new_dict
    for path in self._objects:
      if path in installed_item._objects:
        # compare object to see it there is changes
        new_object = self._objects[path]
        old_object = installed_item._objects[path]
        new_object.sort()
        old_object.sort()
        if new_object != old_object:
          modified_object_list[path] = 'Modified', self.getTemplateTypeName()
      else: # new object
        modified_object_list[path] = 'New', self.getTemplateTypeName()
    # get removed object
    for path in installed_item._objects:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', self.getTemplateTypeName()
    return modified_object_list

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    path, name = posixpath.split(file_name)
    xml = parse(file)
    portal_type_list = xml.findall('portal_type')
    for portal_type in portal_type_list:
      id = portal_type.get('id')
      item_type_list = [item.text for item in portal_type.findall('item')]
      if self.class_property not in id:
        key = '%s/%s' % (self.class_property, id,)
      else:
        key = id
      self._objects[key] = item_type_list

  def install(self, context, trashbin, **kw):
    portal = context.getPortalObject()
    types_tool = getToolByName(portal, 'portal_types')
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    installed_bt = kw.get('installed_bt')
    if installed_bt is not None:
      item = getattr(installed_bt, self.business_template_class_property, None)
      if item is not None:
        old_objects = item._objects
      else:
        old_objects = {}
    else:
      old_objects = {}
    for key in set(self._objects.keys()).union(old_objects.keys()):
      if key in update_dict or force:
        if not force:
          action = update_dict[key]
          if action == 'nothing':
            continue
        portal_id = key.split('/')[-1]
        property_list = self._objects.get(key, [])
        type_information = types_tool.getTypeInfo(portal_id)
        if type_information is None:
          if not property_list:
            continue
          raise AttributeError, "Portal type '%s' not found while " \
              "installing %s" % (portal_id, self.getTitle())
        old_property_list = old_objects.get(key, ())
        object_property_list = getattr(type_information, self.class_property, ())
        # merge differences between portal types properties
        # for example:
        # * current value : [A,B,C]
        # * in new BT : [A,D]
        # * in old BT : [A,B]
        # -> [A,D,C] i.e. C is merged but B is not merged
        for id in object_property_list:
          if id not in property_list and id not in old_property_list:
            property_list.append(id)
        setattr(type_information, self.class_property, tuple(property_list))

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path', None)
    portal = context.getPortalObject()
    types_tool = getToolByName(portal, 'portal_types')
    if object_path is not None:
      object_key_list = [object_path]
    else:
      object_key_list = self._objects.keys()
    for key in object_key_list:
      portal_id = key.split('/')[-1]
      type_information = types_tool.getTypeInfo(portal_id)
      if type_information is None:
        LOG("BusinessTemplate", WARNING,
            "Portal type %r not found while uninstalling" % (portal_id,))
        continue
      property_list = self._objects[key]
      original_property_list = list(getattr(type_information,
                                    self.class_property, ()))
      for id in property_list:
        if id in original_property_list:
          original_property_list.remove(id)
      setattr(type_information, self.class_property, tuple(original_property_list))


class PortalTypeHiddenContentTypeTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  name = 'Hidden Content Type'
  xml_tag = 'hidden_content_type_list'
  class_property = 'hidden_content_type_list'
  business_template_class_property = '_portal_type_hidden_content_type_item'


class PortalTypePropertySheetTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  name = 'Property Sheet'
  xml_tag = 'property_sheet_list'
  class_property = 'property_sheet_list'
  business_template_class_property = '_portal_type_property_sheet_item'


class PortalTypeBaseCategoryTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  name = 'Base Category'
  xml_tag = 'base_category_list'
  class_property = 'base_category_list'
  business_template_class_property = '_portal_type_base_category_item'


class CatalogMethodTemplateItem(ObjectTemplateItem):
  """Template Item for catalog methods.

    This template item stores catalog method and install them in the
    default catalog.
    The use Catalog makes for methods is saved as well and recreated on
    installation.
  """

  def __init__(self, id_list, tool_id='portal_catalog', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    # a mapping to store properties of methods.
    # the mapping contains an entry for each method, and this entry is
    # another mapping having the id of the catalog property as key and a
    # boolean value to say wether the method is part of this catalog
    # configuration property.
    self._method_properties = PersistentMapping()

    self._is_filtered_archive = PersistentMapping()
    for method in catalog_method_filter_list:
      setattr(self, method, PersistentMapping())

  def _extractMethodProperties(self, catalog, method_id):
    """Extracts properties for a given method in the catalog.
    Returns a mapping of property name -> boolean """
    method_properties = PersistentMapping()

    if catalog.meta_type == 'ERP5 Catalog':
      property_list = list(catalog.propertyMap())
    else:
      property_list = list(catalog._properties)

    for prop in property_list:
      if prop.get('select_variable') == 'getCatalogMethodIds':

        # In case the properties are defined via property sheet 'Catalog', the
        # object would have two IDs if it is of type 'selection' or
        # 'multiple_selection': 'id' and 'base_id', usage of base_id is preferred
        # while building objects as it maintains consistency between the old
        # catalog and new erp5 catalog
        prop_id = prop.get('base_id', prop['id'])

        # IMPORTANT: After migration of Catalog, the properties which were of
        # 'selection' type in ZSQL Catalog made more sense to be of 'string'
        # type as they only contained one value. Also, putting them in
        # 'selection' type, we would've ended up having to deal with accessors
        # which end with '_list' which would've made no sense. So, we decided
        # to move them to 'string' type
        if prop['type'] in ('string', 'selection') and \
            getattr(catalog, prop_id, None) == method_id:
          method_properties[prop_id] = 1

        elif prop['type'] == 'multiple selection' and \
            method_id in getattr(catalog, prop_id, ()):
          method_properties[prop_id] = 1

    return method_properties

  def build(self, context, **kw):
    ObjectTemplateItem.build(self, context, **kw)

    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate build', 0, 'catalog not found')
      return

    # upgrade old
    if not hasattr(self, '_method_properties'):
      self._method_properties = PersistentMapping()

    for obj in self._objects.values():
      method_id = obj.id
      # Check if the method is sub-object of Catalog
      if method_id in catalog.objectIds():
        self._method_properties[method_id] = self._extractMethodProperties(
                                                            catalog, method_id)

  def generateXml(self, path):
    obj = self._objects[path]
    method_id = obj.id
    xml_data = '<catalog_method>'
    if self._method_properties.has_key(method_id):
      for method_property, value in self._method_properties[method_id].items():
        xml_data += '\n <item key="%s" type="int">' %(method_property,)
        xml_data += '\n  <value>%s</value>' %(value,)
        xml_data += '\n </item>'

    xml_data += '\n</catalog_method>\n'
    return xml_data

  def preinstall(self, context, installed_item, **kw):
    """Compute diffs from catalog methods metadata and objects.

    To support `template_keep_path_list`, we give priority to
    ObjectTemplateItem.preinstall which may return 'Removed but should be kept'
    """
    # from catalog methods properies (from generateXML)
    modified_object_dict = BaseTemplateItem.preinstall(self, context, installed_item, **kw)
    # diffs from actual objects
    modified_object_dict.update(ObjectTemplateItem.preinstall(self, context, installed_item, **kw))
    return modified_object_dict

  def export(self, context, bta, **kw):
    ObjectTemplateItem.export(self, context, bta, catalog_method_template_item=1)

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    # Make copies of attributes of the default catalog of portal_catalog.
    sql_catalog_object_list = list(catalog.sql_catalog_object_list)
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_clear_catalog = list(catalog.sql_clear_catalog)

    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    values = []

    # When the default catalog is of 'ERP5 Catalog' meta_type, its better to ..
    # convert all the CatalogMethodTemplateItems in the current BT to the
    # allowed types for ERP5 Catalog, i.e, to ERP5 SQLMethod and ERP5 Python Script
    # and update the self._objects dict accordingly
    if catalog.meta_type == 'ERP5 Catalog':
      import erp5
      from Products.ERP5.Extensions.CheckPortalTypes import changeObjectClass

      # We need the dynamic portal_type classes for changing object classes
      sql_class = getattr(erp5.portal_type, 'SQL Method')
      script_class = getattr(erp5.portal_type, 'Python Script')

      portal = self.getPortalObject()
      # Will be modifying dict, so better to use .items()
      # XXX: In python3 it should be .copy.items().
      for path, obj in self._objects.items():
        method = self.unrestrictedResolveValue(portal, path)
        method_id = path.split('/')[-1]
        if method.meta_type == 'Z SQL Method':
          method = changeObjectClass(catalog, method_id, sql_class)
        if method.meta_type == 'Script (Python)':
          method = changeObjectClass(catalog, method_id, script_class)
        new_obj  = method.aq_base
        self._objects[path] = new_obj

    if force: # get all objects
      values = self._objects.values()
    else: # get only selected object
      for key, value in self._objects.iteritems():
        if update_dict.has_key(key) or force:
          if not force:
            action = update_dict[key]
            if action == 'nothing':
              continue
          values.append(value)

    for obj in values:
      method_id = obj.id

      # Restore catalog properties for methods
      if hasattr(self, '_method_properties'):
        for key in self._method_properties.get(method_id, {}).keys():
          old_value = getattr(catalog, key, None)
          if isinstance(old_value, str):
            setattr(catalog, key, method_id)
          elif isinstance(old_value, (list, tuple)):
            if method_id not in old_value:
              new_value = list(old_value) + [method_id]
              new_value.sort()
              setattr(catalog, key, tuple(new_value))

      method = catalog._getOb(method_id)

      # Restore filter:
      #
      # Here we have to handle two cases:
      # 1. CatalogMethodTemplateItem with _is_filtered_archive (possible for
      #    methods who still have filter attributes in `_catalog_keys.xml` file).
      # 2. CatalogMethodTemplateItem where methods have filter properties
      #    directly on xml file of method rather than in `_catalog_keys.xml`.
      #    This would be case for BT which have been exported after catalog
      #    migration.
      if self._is_filtered_archive.get(method_id, 0):
        expression = self._filter_expression_archive[method_id]
        method.setFiltered(1)
        method.setExpression(expression)
        method.setExpressionCacheKey(
          self._filter_expression_cache_key_archive.get(method_id, ()))
        method.setTypeList(self._filter_type_archive.get(method_id, ()))
      # If there is no filter archive and the the meta_type of the catalog
      # method isn't one of the ERP5-ified Catalog Method Document, then
      # set the filter to 0
      elif method.meta_type not in ('ERP5 SQL Method', 'ERP5 Python Script'):
        method.setFiltered(0)

      # backward compatibility
      if hasattr(self, '_is_catalog_list_method_archive'):
        LOG("BusinessTemplate.CatalogMethodTemplateItem", 0,
            "installing old style catalog method configuration")
        is_catalog_list_method = int(
                  self._is_catalog_list_method_archive[method_id])
        is_uncatalog_method = int(
                  self._is_uncatalog_method_archive[method_id])
        is_clear_method = int(
                  self._is_clear_method_archive[method_id])

        if is_catalog_list_method and method_id not in sql_catalog_object_list:
          sql_catalog_object_list.append(method_id)
        elif not is_catalog_list_method and\
                        method_id in sql_catalog_object_list:
          sql_catalog_object_list.remove(method_id)

        if is_uncatalog_method and method_id not in sql_uncatalog_object:
          sql_uncatalog_object.append(method_id)
        elif not is_uncatalog_method and method_id in sql_uncatalog_object:
          sql_uncatalog_object.remove(method_id)

        if is_clear_method and method_id not in sql_clear_catalog:
          sql_clear_catalog.append(method_id)
        elif not is_clear_method and method_id in sql_clear_catalog:
          sql_clear_catalog.remove(method_id)

        sql_catalog_object_list.sort()
        catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
        sql_uncatalog_object.sort()
        catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
        sql_clear_catalog.sort()
        catalog.sql_clear_catalog = tuple(sql_clear_catalog)

  def uninstall(self, context, **kw):
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    values = []
    object_path = kw.get('object_path', None)
    # get required values
    if object_path is None:
      values = self._objects.values()
    else:
      try:
        value = self._objects[object_path]
      except KeyError:
        value = None
      if value is not None:
        values.append(value)
    for obj in values:
      method_id = obj.id
      if catalog.meta_type == 'ERP5 Catalog':
        property_list = list(catalog.propertyMap())
      else:
        property_list = list(catalog._properties)

      # remove method references in portal_catalog
      for catalog_prop in property_list:
        if catalog_prop.get('select_variable') == 'getCatalogMethodIds'\
            and catalog_prop['type'] == 'multiple selection':
          # In case the properties are defined via property sheet 'Catalog', the
          # object would have two IDs if it is of type 'selection' or
          # 'multiple_selection': 'id' and 'base_id', usage of base_id is preferred
          # while building objects as it maintains consistency between the old
          # catalog and new erp5 catalog
          catalog_prop_id = catalog_prop.get('base_id', catalog_prop['id'])
          old_value = getattr(catalog, catalog_prop_id, ())
          if method_id in old_value:
            new_value = list(old_value)
            new_value.remove(method_id)
            # Better to set the attribute value as tuple as it would be consistent
            # with both SQL Catalog and ERP5 Catalog.
            setattr(catalog, catalog_prop_id, tuple(new_value))

      filter_dict = catalog._getFilterDict()
      try:
        del filter_dict[method_id]
      except KeyError:
        pass

    # uninstall objects
    ObjectTemplateItem.uninstall(self, context, **kw)

  def _importFile(self, file_name, file):
    if file_name.endswith('.catalog_keys.xml'):
      # recreate data mapping specific to catalog method
      name = os.path.basename(file_name)
      id = name.split('.', 1)[0]
      xml = parse(file)
      method_list = xml.findall('item')
      for method in method_list:
        key = method.get('key')
        key_type = method.get('type')
        value_node = method.find('value')
        if key_type == "str":
          value = value_node.text or ''
        elif key_type == "int":
          value = int(value_node.text)
        elif key_type == "tuple":
          value = tuple([value_node.text for value_node in method.findall('value')])
        else:
          LOG('BusinessTemplate import CatalogMethod, type unknown', 0, key_type)
          continue
        if key in catalog_method_list or key in catalog_method_filter_list:
          getattr(self, key)[id] = value
        else:
          # new style key
          self._method_properties.setdefault(id, PersistentMapping())[key] = 1
    else:
      ObjectTemplateItem._importFile(self, file_name, file, catalog_method_template_item=1)


class ActionTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, **kw):
    # XXX It's look like ObjectTemplateItem __init__
    BaseTemplateItem.__init__(self, id_list, **kw)
    id_list = self._archive.keys()
    self._archive.clear()
    for id in id_list:
      self._archive["%s/%s" % ('portal_types', id)] = None

  def _splitPath(self, path):
    """
      Split path tries to split a complex path such as:

      "foo/bar[id=zoo]"

      into

      "foo/bar", "id", "zoo"

      This is used mostly for generic objects
    """
    # Add error checking here
    if path.find('[') >= 0 and path.find(']') > path.find('=') and path.find('=') > path.find('['):
      relative_url = path[0:path.find('[')]
      id_block = path[path.find('[')+1:path.find(']')]
      key = id_block.split('=')[0]
      value = id_block.split('=')[1]
      return relative_url, key, value
    return path, None, None

  def _getPortalTypeActionCopy(self, obj, value):
    id_id = 'reference'
    for action in obj.getActionInformationList():
      if getattr(action, id_id, None) == value:
        return obj._exportOldAction(action)

  def _getPortalToolActionCopy(self, obj, context, value):
    from Products.CMFCore.interfaces import IActionProvider
    if not IActionProvider.providedBy(obj):
      # look for the action in portal_actions, instead of the original object
      LOG('Products.ERP5.Document.BusinessTemplate', WARNING,
          'Redirected action export',
          'Attempted to retrieve action %r from %r which is no longer an '
          'IActionProvider. Retrieving action from portal_actions instead' %
          (value, obj.getId()))
      obj = context.getPortalObject().portal_actions
    id_id = 'id'
    for action in obj.listActions():
      if getattr(action, id_id, None) == value:
        return action._getCopy(context)

  def _getActionCopy(self, obj, context, value):
    """
    Gets action copy from action provider given the action id or reference
    """
    # Several tools still use CMF actions
    if interfaces.ITypeProvider.providedBy(obj.getParentValue()):
      return self._getPortalTypeActionCopy(obj, value)
    else:
      return self._getPortalToolActionCopy(obj, context, value)

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      url, value = id.split(' | ')
      url = posixpath.split(url)
      obj = p.unrestrictedTraverse(url)
      # normalize url
      url = p.portal_url.getRelativeContentPath(obj)
      if len(url) == 1:
        # global actions are stored under 'portal_types', mostly for
        # compatibility
        url = 'portal_types', url[0]
      action = self._getActionCopy(obj, context, value)
      if action is None:
        if self.is_bt_for_diff:
          continue
        raise NotFound('Action %r not found' % id)
      key = posixpath.join(url[-2], url[-1], value)
      self._objects[key] = self.removeProperties(
        action, 1,
        self.isKeepWorkflowObject(key),
        self.isKeepWorkflowObjectLastHistoryOnly(key))

      self._objects[key].wl_clearLocks()

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    portal_type_dict = {}
    p = context.getPortalObject()
    for id in self._objects.keys():
      if update_dict.has_key(id) or force:
        if not force:
          action = update_dict[id]
          if action == 'nothing':
            continue
        obj = self._objects[id]
        path, id = id.rsplit('/', 1)
        container = p.unrestrictedTraverse(path)

        if interfaces.ITypeProvider.providedBy(aq_parent(aq_inner(container))):
          # XXX future BT should use 'reference' instead of 'id'
          reference = getattr(obj, 'reference', None) or obj.id
          portal_type_dict.setdefault(path, {})[reference] = obj
          continue

        # Following code is for actions outside Types Tool.
        # It will be removed when they are also converted to ERP5 actions.
        from Products.CMFCore.interfaces import IActionProvider
        if not IActionProvider.providedBy(container):
          # some tools stopped being ActionProviders in CMF 2.x. Drop the
          # action into portal_actions.
          LOG('Products.ERP5.Document.BusinessTemplate', WARNING,
              'Redirected action import',
              'Attempted to store action %r in %r which is no longer an '
              'IActionProvider. Storing action on portal_actions instead' %
              (id, path))
          container = p.portal_actions
        obj, action = container, obj
        action_list = obj.listActions()
        for index in range(len(action_list)):
          if action_list[index].id == id:
            # remove previous action
            obj.deleteActions(selections=(index,))
        action_text = action.action
        if isinstance(action_text, Expression):
          action_text = action_text.text
        obj.addAction(
                      id = action.id
                    , name = action.title
                    , action = action_text
                    , condition = action.getCondition()
                    , permission = action.permissions
                    , category = action.category
                    , visible = action.visible
                    , icon = getattr(action, 'icon', None)\
                              and action.icon.text or ''
                    , priority = action.priority
                    , description = action.description
                  )
        # sort action based on the priority define on it
        # XXX suppose that priority are properly on actions
        new_priority = action.priority
        action_list = obj.listActions()
        move_down_list = []
        for index in range(len(action_list)):
          action = action_list[index]
          if action.priority > new_priority:
            move_down_list.append(str(index))
        obj.moveDownActions(selections=tuple(move_down_list))
    for path, action_dict in portal_type_dict.iteritems():
      container = p.unrestrictedTraverse(path)
      container.manage_delObjects([obj.id
        for obj in container.getActionInformationList()
        if obj.getReference() in action_dict])
      for name, obj in action_dict.iteritems():
        container._importOldAction(obj).aq_base

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    object_path = kw.get("object_path", None)
    if object_path is not None:
      if '/' in object_path:
        # here object_path is the path of the actions, something like
        # portal_type/Person/view
        ti, action_id = object_path.rsplit('/', 1)
        keys = ['%s | %s' % (ti, action_id)]
      else:
        # compatibility ?
        keys = [object_path]
    else:
      keys = self._archive.keys()
    for id in keys:
      if  '|' in id:
        relative_url, value = id.split(' | ')
        obj = p.unrestrictedTraverse(relative_url, None)
        # Several tools still use CMF actions
        if obj is not None:
          is_new_action = interfaces.ITypeProvider.providedBy(obj.getParentValue())
          key = is_new_action and 'reference' or 'id'
      else:
        relative_url, key, value = self._splitPath(id)
        obj = p.unrestrictedTraverse(relative_url, None)
      if obj is not None:
        action_list = obj.listActions()
        for index in range(len(action_list)):
          if getattr(action_list[index], key, None) == value:
            obj.deleteActions(selections=(index,))
            break
      LOG('BusinessTemplate', WARNING,
          'Unable to uninstall action at %s, ignoring' % relative_url )
    BaseTemplateItem.uninstall(self, context, **kw)

class PortalTypeRolesTemplateItem(BaseTemplateItem):

  def __init__(self, id_list, **kw):
    id_list = ['portal_type_roles/%s' % id for id in id_list if id != '']
    BaseTemplateItem.__init__(self, id_list, **kw)

  def build(self, context, **kw):
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse("portal_types/%s" %
          relative_url.split('/', 1)[1])
      # normalize url
      relative_url = '%s/%s' % (obj.getPhysicalPath()[-2:])
      self._objects[relative_url] = type_role_list = []
      for role in obj.getRoleInformationList():
        type_role_dict = {}
        for k, v in aq_base(role).__getstate__().iteritems():
          if k == 'condition':
            if not v:
              continue
            v = v.text
          elif k in ('role_base_category', 'role_category'):
            k = k[5:]
          elif k == 'role_name':
            k, v = 'id', '; '.join(v)
          elif k not in ('title', 'description', 'categories'):
            k = {'id': 'object_id', # for stable sort
                 'role_base_category': 'base_category',
                 'role_base_category_script_id': 'base_category_script',
                 'role_category': 'category',
                 'local_roles_group_id': 'local_roles_group_id'}.get(k)
            if not k:
              continue
          type_role_dict[k] = v
        if 'id' in type_role_dict:
          type_role_list.append(type_role_dict)
      type_role_list.sort(key=lambda x: (x.get('title'), x['object_id'],))

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    type_role_list = self._objects[path]
    xml_data = '<type_roles>'
    for role in type_role_list:
      xml_data += "\n  <role id='%s'>" % role['id']
      # uniq
      for property in ('title', 'description', 'condition',
          'base_category_script'):
        prop_value = role.get(property)
        if prop_value:
          if isinstance(prop_value, str):
            prop_value = escape(prop_value.decode('utf-8'))
          xml_data += "\n   <property id='%s'>%s</property>" % \
              (property, prop_value)
      # multi
      for property in ('categories', 'category', 'base_category'):
        for prop_value in role.get(property, []):
          if isinstance(prop_value, str):
            prop_value = escape(prop_value.decode('utf-8'))
          xml_data += "\n   <multi_property "\
          "id='%s'>%s</multi_property>" % (property, prop_value)
      xml_data += "\n  </role>"
    xml_data += '\n</type_roles>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = self.__class__.__name__
    for key in self._objects.keys():
      xml_data = self.generateXml(key)
      if isinstance(xml_data, unicode):
        xml_data = xml_data.encode('utf-8')
      name = key.split('/', 1)[1]
      bta.addObject(xml_data, name=name, path=path)

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    type_roles_list = []
    xml = parse(file)
    xml_type_roles_list = xml.findall('role')
    for role in xml_type_roles_list:
      id = role.get('id')
      if isinstance(id, unicode):
        id = id.encode('utf_8', 'backslashreplace')
      type_role_property_dict = {'id': id}
      # uniq
      property_list = role.findall('property')
      for property_node in property_list:
        property_id = property_node.get('id')
        if property_node.text:
          value = property_node.text
          if isinstance(value, unicode):
            value = value.encode('utf_8', 'backslashreplace')
          type_role_property_dict[property_id] = value
      # multi
      multi_property_list = role.findall('multi_property')
      for property_node in multi_property_list:
        property_id = property_node.get('id')
        if property_node.text:
          value = property_node.text
          if isinstance(value, unicode):
            value = value.encode('utf_8', 'backslashreplace')
          type_role_property_dict.setdefault(property_id, []).append(value)
      type_roles_list.append(type_role_property_dict)
    self._objects['portal_type_roles/%s' % (file_name[:-4],)] = type_roles_list

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    for roles_path in self._objects.keys():
      if update_dict.has_key(roles_path) or force:
        if not force:
          action = update_dict[roles_path]
          if action == 'nothing':
            continue
        path = 'portal_types/%s' % roles_path.split('/', 1)[1]
        obj = p.unrestrictedTraverse(path, None)
        if obj is not None:
          # reset roles before applying
          obj.manage_delObjects([x.id for x in obj.getRoleInformationList()])
          type_roles_list = self._objects[roles_path] or []
          for role_property_dict in type_roles_list:
            obj._importRole(role_property_dict)
        else:
          raise AttributeError("Path %r not found while "
                               "installing roles" % (path, ))

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    object_path = kw.get('object_path', None)
    if object_path is not None:
      keys = [object_path]
    else:
      keys = self._objects.keys()
    for roles_path in keys:
      path = 'portal_types/%s' % roles_path.split('/', 1)[1]
      try:
        obj = p.unrestrictedTraverse(path)
        obj.manage_delObjects([x.id for x in obj.getRoleInformationList()])
      except (NotFound, KeyError):
        pass

class SitePropertyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      for property in p.propertyMap():
        if property['id'] == id:
          obj = p.getProperty(id)
          prop_type = property['type']
          break
      else:
        obj = None
      if obj is None and not self.is_bt_for_diff:
        raise NotFound, 'the property %s is not found' % id
      self._objects[id] = (prop_type, obj)

  def _importFile(self, file_name, file):
    # recreate list of site property from xml file
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    xml = parse(file)
    for property_node in xml.getroot().findall('property'):
      property_id = property_node.find('id').text
      prop_type = property_node.find('type').text
      value_node = property_node.find('value')
      if prop_type in ('lines', 'tokens'):
        value = [item.text for item in value_node.findall('item')]
      else:
        value = value_node.text
      self._objects[property_id] = (prop_type, value)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    for path in self._objects.keys():
      if update_dict.has_key(path) or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        dir, id = posixpath.split(path)
        prop_type, property = self._objects[path]
        if p.hasProperty(id):
          if p.getPropertyType(id) != prop_type:
            p._delProperty(id)
            p._setProperty(id, property, type=prop_type)
          else:
            p._updateProperty(id, property)
        else:
          p._setProperty(id, property, type=prop_type)

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    object_path = kw.get('object_path', None)
    if object_path is not None:
      keys = [object_path]
    else:
      keys = self._archive.keys()
    for id in keys:
      if p.hasProperty(id):
        p._delProperty(id)
    BaseTemplateItem.uninstall(self, context, **kw)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    xml_data = ''
    prop_type, obj = self._objects[path]
    xml_data += '\n <property>'
    xml_data += '\n  <id>%s</id>' % escape(str(path))
    xml_data += '\n  <type>%s</type>' % escape(str(prop_type))
    if prop_type in ('lines', 'tokens'):
      xml_data += '\n  <value>'
      for item in obj:
        if item != '':
          xml_data += '\n   <item>%s</item>' % escape(str(item))
      xml_data += '\n  </value>'
    else:
      xml_data += '\n  <value>%s</value>' % escape(str(obj))
    xml_data += '\n </property>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    xml_data = '<site_property>'
    keys = self._objects.keys()
    keys.sort()
    for path in keys:
      xml_data += self.generateXml(path)
    xml_data += '\n</site_property>'
    bta.addObject(xml_data, name='properties', path=self.__class__.__name__)

class ModuleTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for module_id in self._archive.keys():
      module = p.unrestrictedTraverse(module_id)
      mapping = {}
      mapping['id'] = module.getId()
      mapping['title'] = module.getTitle()
      mapping['portal_type'] = module.getPortalType()
      mapping['permission_list'] = module.showPermissions()
      mapping['category_list'] = module.getCategoryList()
      self._objects[module_id] = mapping

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    mapping = self._objects[path]
    xml_data = ['<module>']
    keys = mapping.keys()
    for key in sorted(keys):
      if key == 'permission_list':
        # separe permission dict into xml
        xml_data.append(' <%s>' % (key, ))
        permission_list = mapping[key]
        for perm in permission_list:
          # the type of the permission defined if we use acquired or not
          if isinstance(perm[1], list):
            ptype = "list"
          else:
            ptype = "tuple"
          role_list = list(perm[1])
          # Skip if permission is not configured (i.e. no role at all
          # with acquire permission, or Manager only without acquire
          # permission).
          if (len(role_list) == 0 and ptype == 'list') or \
                 (role_list == ['Manager'] and ptype == 'tuple'):
            continue
          role_list.sort()
          xml_data.append("  <permission type='%s'>" % (ptype, ))
          xml_data.append('   <name>%s</name>' % (perm[0], ))
          for role in role_list:
            xml_data.append('   <role>%s</role>' % (role, ))
          xml_data.append('  </permission>')
        xml_data.append(' </%s>' % (key, ))
      elif key == 'category_list':
        category_list = mapping[key]
        if not category_list:
          continue
        xml_data.append(' <%s>' % (key, ))
        for category in category_list:
          xml_data.append('  <category>%s</category>' % (category, ))
        xml_data.append(' </%s>' % (key, ))
      else:
        xml_data.append(' <%s>%s</%s>' % (key, mapping[key], key))
    xml_data.append('</module>')
    return '\n'.join(xml_data)

  def export(self, context, bta, **kw):
    if len(self._objects) == 0:
      return
    path = self.__class__.__name__
    keys = self._objects.keys()
    keys.sort()
    for key in keys:
      # export modules one by one
      xml_data = self.generateXml(path=key)
      bta.addObject(xml_data, name=key, path=path)

  def install(self, context, trashbin, **kw):
    portal = context.getPortalObject()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    valid_permissions = dict.fromkeys([x[0] for x in
                                       context.ac_inherited_permissions(all=1)])
    for path, mapping in self._objects.iteritems():
      if update_dict.has_key(path) or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        path, module_id = posixpath.split(path)
        portal_type = str(mapping['portal_type'])
        module = portal._getOb(module_id, None)
        if module is not None:
          module.portal_type = portal_type
        else:
          module = portal.newContent(id=module_id, portal_type=portal_type)
        module.setTitle(str(mapping['title']))
        permission_dict = dict(mapping['permission_list'])
        for name in valid_permissions.iterkeys():
          # By default, Manager only without acquire permission
          role_list = permission_dict.get(name, ('Manager',))
          acquire = isinstance(role_list, list)
          module.manage_permission(name, roles=role_list, acquire=acquire)
        if 'category_list' in mapping:
          module.setCategoryList(mapping['category_list'])

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    mapping = {}
    xml = parse(file)
    for key in ('portal_type', 'id', 'title', 'permission_list'):
      key_node = xml.find(key)
      if key == 'permission_list':
        permission_list = []
        for permission in key_node:
          permission_type = permission.get('type', None)
          name = permission.find('name').text
          role_list = [role.text for role in permission.findall('role')]
          if permission_type in ('list', None):
            perm_tuple = (name, list(role_list))
          else:
            perm_tuple = (name, tuple(role_list))
          permission_list.append(perm_tuple)
        mapping[key] = permission_list
      else:
        mapping[key] = key_node.text or ''

    category_list = []
    category_list_node = xml.find('category_list')
    if category_list_node is not None:
      category_list.extend(node.text for node\
                            in category_list_node.findall('category'))
    mapping['category_list'] = category_list

    self._objects[file_name[:-4]] = mapping

  def uninstall(self, context, **kw):
    trash = kw.get('trash', 0)
    if trash:
      return
    object_path = kw.get('object_path', None)
    trashbin = kw.get('trashbin', None)
    if object_path is None:
      keys = self._archive.keys()
    else:
      keys = [object_path]
    p = context.getPortalObject()
    id_list = p.objectIds()
    for key in keys:
      if key in id_list:
        try:
          if trash and trashbin is not None:
            container_path = key.split('/')
            self.portal_trash.backupObject(trashbin, container_path,
                                           key, save=1, keep_subobjects=1)
          p.manage_delObjects([key])
        except NotFound:
          pass
    BaseTemplateItem.uninstall(self, context, **kw)

  def trash(self, context, new_item, **kw):
    # Do not remove any module for safety.
    pass

# XXX-arnau: when everything has been migrated to Components, this class
# should be removed and only _ZodbComponentTemplateItem should remain
class FilesystemDocumentTemplateItem(BaseTemplateItem):
  local_file_reader_name = staticmethod(readLocalDocument)
  local_file_writer_name = staticmethod(writeLocalDocument)
  local_file_importer_name = staticmethod(importLocalDocument)
  local_file_remover_name = staticmethod(removeLocalDocument)

  def _getKey(self, path):
    """Magical method to generate dynamic unique path"""
    return '/'.join((self.getTemplateTypeName(), path))

  def _getPath(self, key):
    """Magical method to extract real path"""
    if '/' in key:
      return key.split('/')[1]
    return key

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for key in self._archive.iterkeys():
      self._objects[key] = self.local_file_reader_name(key)

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    # fix key if necessary in installed bt for diff
    extra_prefix = self.__class__.__name__ + '/'
    for key in installed_item._objects.keys():
      if key.startswith(extra_prefix):
        new_key = key[len(extra_prefix):]
        installed_item._objects[new_key] = installed_item._objects[key]
        del installed_item._objects[key]
    for path in self._objects:
      if installed_item._objects.has_key(path):
        # compare object to see if there is changes
        new_obj_code = self._objects[path]
        old_obj_code = installed_item._objects[path]
        if new_obj_code != old_obj_code:
          # Note: Magical way to have unique paths
          modified_object_list[self._getKey(path)] = 'Modified', self.__class__.__name__[:-12]
      else: # new object
        # Note: Magical way to have unique paths
        modified_object_list[self._getKey(path)] = 'New', self.__class__.__name__[:-12]
        # get removed object
    old_keys = installed_item._objects.keys()
    for path in old_keys:
      if path not in self._objects:
        # Note: Magical way to have unique paths
        modified_object_list[self._getKey(path)] = 'Removed', self.__class__.__name__[:-12]
    return modified_object_list

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    need_reset = isinstance(self, FilesystemDocumentTemplateItem)
    for key in self._objects.keys():
      # to achieve non data migration fresh installation parameters
      # differ from upgrade parameteres, so here the check have to be
      # care of both cases
      upgraded_key = self._getKey(key)
      if update_dict.has_key(key) or update_dict.has_key(upgraded_key) \
          or force:
        if not force:
          action = update_dict.get(key, update_dict.get(upgraded_key))
          if action == 'nothing':
            continue
        text = self._objects[key]
        path, name = posixpath.split(key)
        try:
          self.local_file_writer_name(name, text, create=0)
        except IOError, error:
          LOG(self.__class__.__name__, WARNING,
              "Cannot install class %r on file system" % name)
          if error.errno:
            raise
          continue
        if self.local_file_importer_name is None:
          continue
        if need_reset:
          self._resetDynamicModules()
          need_reset = False
        self.local_file_importer_name(name)

  def remove(self, context, **kw):
    """Conversion of magically uniqued paths to real ones"""
    remove_object_dict = kw.get('remove_object_dict', {})
    kw['remove_object_dict'] = {self._getPath(k): v
      for k, v in remove_object_dict.iteritems()
      if k.startswith(self.getTemplateTypeName()+'/')}
    BaseTemplateItem.remove(self, context, **kw)

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    if object_keys:
      if isinstance(self, FilesystemDocumentTemplateItem):
        self._resetDynamicModules()
      for key in object_keys:
        self.local_file_remover_name(key)
    BaseTemplateItem.uninstall(self, context, **kw)

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    extra_prefix = self.__class__.__name__ + '/'
    for key in self._objects.keys():
      obj = self._objects[key]
      # BBB the prefix was put into each key in the previous implementation.
      if not key.startswith(extra_prefix):
        key = extra_prefix + key
      bta.addObject(obj, name=key, ext='.py')

  def _importFile(self, file_name, file):
    if not file_name.endswith('.py'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    text = file.read()
    self._objects[file_name[:-3]] = text

class FilesystemToZodbTemplateItem(FilesystemDocumentTemplateItem,
                                   ObjectTemplateItem):
  """
  Abstract class to allow migration from FilesystemDocumentTemplateItem to
  ObjectTemplateItem, this is useful for migration from filesystem to ZODB for
  PropertySheets and Components
  """
  # If set to False, then the migration from filesystem to ZODB will be
  # performed, meaningful only until the code is stable
  _perform_migration = True

  _tool_id = None

  @staticmethod
  def _getZodbObjectId(id):
    return id

  def __init__(self, id_list, tool_id=None, context=None, **kw):
    if tool_id is None:
      tool_id = self._tool_id

    tool = None
    if context is not None and len(id_list):
      # XXX looking up a tool early in the install process might
      # cause issues. If it does, we'll have to consider moving this
      # to build()
      tool = getattr(context.getPortalObject(), self._tool_id, None)
    if tool is not None:
      existing_set = set(tool.objectIds())
      for i, id in enumerate(id_list):
        if id in existing_set:
          # if the object is on ZODB, use it.
          id_list[i] = "%s/%s" % (self._tool_id, self._getZodbObjectId(id))

    BaseTemplateItem.__init__(self, id_list, **kw)

  def _is_already_migrated(self, object_key_list):
    """
    Objects have already been migrated if any keys within the given
    object_key_list (either '_objects.keys()' or '_archive.keys()') contains a
    key starting by 'tool_id/'
    """
    return len(object_key_list) != 0 and \
        object_key_list[0].startswith(self._tool_id + '/')

  def _filesystemCompatibilityWrapper(method_name, object_dict_name):
    """
    Call ObjectTemplateItem method when the objects have already been
    migrated, otherwise fallback on FilesystemDocumentTemplateItem method for
    backward-compatibility
    """
    def inner(self, *args, **kw):
      if self._is_already_migrated(getattr(self, object_dict_name).keys()):
        result = getattr(ObjectTemplateItem, method_name)(self, *args, **kw)
      else:
        result = getattr(FilesystemDocumentTemplateItem,
                         method_name)(self, *args, **kw)

      if method_name == 'preinstall':
        old_result = result.copy()
        for k, v in old_result.iteritems():
          # Magical way to have unique path (without duplicating the prefix
          # neither) in case of not yet migrated property sheets available on
          # preinstall list
          if not (k.startswith(self._tool_id + '/') or
                  k.startswith(self.getTemplateTypeName())):
            result.pop(k)
            k = self._getKey(k)
          result[k] = v
      return result
    return inner

  export = _filesystemCompatibilityWrapper('export', '_objects')
  build = _filesystemCompatibilityWrapper('build', '_archive')
  preinstall = _filesystemCompatibilityWrapper('preinstall', '_objects')

  def _importFile(self, file_name, *args, **kw):
    """
    Import file by calling the appropriate base class according to the file
    name extensions
    """
    if file_name.endswith('.xml'):
      return ObjectTemplateItem._importFile(self, file_name, *args, **kw)
    else:
      return FilesystemDocumentTemplateItem._importFile(self, file_name,
                                                        *args, **kw)

  def uninstall(self, *args, **kw):
    # Only for uninstall, the path of objects can be given as a
    # parameter, otherwise it fallbacks on '_archive'
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()

    if self._is_already_migrated(object_keys):
      ObjectTemplateItem.uninstall(self, *args, **kw)
    else:
      FilesystemDocumentTemplateItem.uninstall(self, *args, **kw)

  def remove(self, context, **kw):
    """
    Conversion of magically uniqued paths to real ones
    """
    remove_object_dict = kw.get('remove_object_dict', {})
    kw['remove_object_dict'] = {self._getPath(k): v
      for k, v in remove_object_dict.iteritems()
      if k.startswith(self.getTemplateTypeName()+'/')}
    ObjectTemplateItem.remove(self, context, **kw)

  @staticmethod
  def _getFilesystemPath(class_id):
    raise NotImplementedError

  @staticmethod
  def _migrateFromFilesystem(tool, filesystem_path, filesystem_file, class_id):
    raise NotImplementedError

  def _migrateAllFromFilesystem(self,
                                context,
                                migrate_object_dict,
                                object_dict,
                                update_parameter_dict):
    """
    Migrate all Property Sheets from 'migrate_object_dict' and, if
    necessary, remove old references in 'object_dict' too (with format
    version 1 of Business Template, the former would be '_objects' and
    the latter '_archive'), and finally removing the useless Property
    Sheet on the filesystem
    """
    # Migrate all the filesystem classes of the Business Template if any
    tool = getattr(context.getPortalObject(), self._tool_id)
    id_set = set(tool.objectIds())

    # careful, that dictionary will change
    class_id_list = migrate_object_dict.keys()
    for class_id in class_id_list:
      # If the Property Sheet already exists in ZODB, then skip it,
      # otherwise it should not be needed anymore once the deletion
      # code of the filesystem Property Sheets is enabled
      if class_id in id_set:
        # XXX a Conduit must be able to merge modifications
        # from FS PropertySheets into ZODB PropertySheets
        warn('Conflict when migrating classes %s: already exists in %s and '\
               'cannot be updated automatically for now.' % (class_id,
                                                             self._tool_id),
             UserWarning)
        del migrate_object_dict[class_id]
        if class_id in object_dict:
          del object_dict[class_id]
        continue

      filesystem_path = self._getFilesystemPath(class_id)

      # A filesystem Property Sheet may already exist in the instance
      # home if the Business Template has been previously installed,
      # otherwise it is created
      if os.path.exists(filesystem_path):
        filesystem_file = open(filesystem_path)
      else:
        filesystem_file = open(filesystem_path, 'w+')
        filesystem_file.write(migrate_object_dict[class_id])
        filesystem_file.seek(0)

      try:
        migrated_object = self._migrateFromFilesystem(tool,
                                                      filesystem_path,
                                                      filesystem_file,
                                                      class_id).aq_base
      finally:
        filesystem_file.close()

      # Delete the file only if there was no error encountered during
      # migration
      os.remove(filesystem_path)

      # Update 'migrate_object_dict' with the new path
      key = '%s/%s' % (self._tool_id, migrated_object.getId())

      migrate_object_dict[key] = migrated_object
      del migrate_object_dict[class_id]

      # Remove old reference in 'object_dict' as it does not make
      # sense to keep it anymore
      if class_id in object_dict:
        object_dict[key] = None
        del object_dict[class_id]

      # Skip meaningless backup of the object as it has just been
      # migrated
      update_parameter_dict[key] = 'migrate'

  def install(self, context, **kw):
    """
    Install Business Template items and perform migration
    automatically only if the tool is available
    """
    if (not self._perform_migration or
        getattr(context.getPortalObject(), self._tool_id, None) is None):
      return FilesystemDocumentTemplateItem.install(self, context, **kw)

    if not self._is_already_migrated(self._objects.keys()):
      self._migrateAllFromFilesystem(context,
                                     self._objects,
                                     self._archive,
                                     kw.get('object_to_update'))

    return ObjectTemplateItem.install(self, context, **kw)

class PropertySheetTemplateItem(FilesystemToZodbTemplateItem):
  """
  Property Sheets are now stored in ZODB rather than the filesystem.
  However, some Business Templates may still have filesystem Property
  Sheets, which need to be migrated to the ZODB.

  This migration is performed in two steps:

  1/ Specify explicitly in the web user interface that the Property
     Sheets should be migrated.

  2/ The Property Sheets will all be migrated when installing the
     Business Template.

  Therefore, this is an all or nothing migration, meaning that only methods of
  FilesystemDocumentTemplateItem will be called before the migration has been
  performed, then ObjectTemplateItem methods afterwards.
  """
  # Only meaningful for filesystem Property Sheets
  local_file_reader_name = staticmethod(readLocalPropertySheet)
  local_file_writer_name = staticmethod(writeLocalPropertySheet)
  local_file_importer_name = staticmethod(importLocalPropertySheet)
  local_file_remover_name = staticmethod(removeLocalPropertySheet)

  _tool_id = 'portal_property_sheets'

  @staticmethod
  def _getFilesystemPath(class_id):
    """
    From the given class identifier, return the complete path of the
    filesystem Property Sheet class. Only meaningful when the Business
    Template has already been installed previously, otherwise the
    """
    from App.config import getConfiguration
    return os.path.join(getConfiguration().instancehome,
                        "PropertySheet",
                        class_id + ".py")

  @staticmethod
  def _migrateFromFilesystem(tool,
                             filesystem_path,
                             filesystem_file,
                             class_id):
    """
    Migration of a filesystem Property Sheet involves loading the
    class from 'instancehome/PropertySheet/<class_id>', then create
    the ZODB Property Sheets in portal_property_sheets from its
    filesystem definition
    """
    # The first parameter of 'load_source' is the module name where
    # the class will be stored, thus don't only use the class name as
    # it may clash with already loaded module, such as
    # BusinessTemplate.
    module = imp.load_source('Migrate%sFilesystemPropertySheet' % class_id,
                             filesystem_path,
                             filesystem_file)

    try:
      klass = getattr(module, class_id)
    except AttributeError:
      raise AttributeError("filesystem Property Sheet '%s' should " \
                           "contain a class with the same name" % \
                           class_id)

    return PropertySheetDocument.importFromFilesystemDefinition(tool, klass)

class ConstraintTemplateItem(FilesystemDocumentTemplateItem):
  local_file_reader_name = staticmethod(readLocalConstraint)
  local_file_writer_name = staticmethod(writeLocalConstraint)
  local_file_importer_name = staticmethod(importLocalConstraint)
  local_file_remover_name = staticmethod(removeLocalConstraint)

class _ZodbComponentTemplateItem(ObjectTemplateItem):
  @staticmethod
  def _getZodbObjectId(id):
    raise NotImplementedError

  def __init__(self, id_list, tool_id='portal_components', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def isKeepWorkflowObjectLastHistoryOnly(self, path):
    """
    Component Validation Workflow last History of ZODB Components must always be
    kept, without explicitly adding them to the field which requires an extra
    action for developers
    """
    return True

  def _removeAllButLastWorkflowHistory(self, obj):
    """
    Only export the last state of component_validation_workflow, because only
    the source code and its state to load it is necessary for ZODB Components
    and too much history would be exported (edit_workflow)
    """
    for wf_id in obj.workflow_history.keys():
      if wf_id != 'component_validation_workflow':
        del obj.workflow_history[wf_id]
        continue

      wf_history = obj.workflow_history[wf_id][-1]
      # Remove useless modifcation 'time' and 'actor' (conflicts with VCSs)
      wf_history.pop('time', None)
      wf_history.pop('actor', None)
      wf_history.pop('comment', None)

      obj.workflow_history[wf_id] = WorkflowHistoryList([wf_history])

  def afterInstall(self):
    """
    Reset component on the fly, because it is possible that those components
    are required in the middle of the transaction. For example:
      - A method in a component is called while installing.
      - A document component is used in a different business template, and
        those business templates are installed in a single transaction by
        upgrader.

    This reset is called at most 3 times in one business template
    installation. (for Document, Test, Extension)
    """
    self.portal_components.reset(force=True)

  def afterUninstall(self):
    self.portal_components.reset(force=True,
                                 reset_portal_type_at_transaction_boundary=True)

from Products.ERP5Type.Core.ModuleComponent import ModuleComponent
class ModuleComponentTemplateItem(_ZodbComponentTemplateItem):
  @staticmethod
  def _getZodbObjectId(id):
    return ModuleComponent.getIdPrefix() + '.' + id

from Products.ERP5Type.Core.InterfaceComponent import InterfaceComponent
class InterfaceTemplateItem(_ZodbComponentTemplateItem):
  @staticmethod
  def _getZodbObjectId(id):
    return InterfaceComponent.getIdPrefix() + '.' + id

from Products.ERP5Type.Core.MixinComponent import MixinComponent
class MixinTemplateItem(_ZodbComponentTemplateItem):
  @staticmethod
  def _getZodbObjectId(id):
    return MixinComponent.getIdPrefix() + '.' + id

from Products.ERP5Type.Core.ToolComponent import ToolComponent
class ToolComponentTemplateItem(_ZodbComponentTemplateItem):
  @staticmethod
  def _getZodbObjectId(id):
    return ToolComponent.getIdPrefix() + '.' + id

from Products.ERP5Type.Core.DocumentComponent import DocumentComponent
class DocumentTemplateItem(FilesystemToZodbTemplateItem,
                           _ZodbComponentTemplateItem):
  """
  Documents are now stored in ZODB rather than on the filesystem. However,
  some Business Templates may still have filesystem Documents which need to be
  migrated to the ZODB.

  The migration is performed in two steps:

    1/ Copy the Business Template to be migrated;

    2/ Run the migration script which will update properly the Document IDs in
       the Business Template.

  Upon import or export, two files will be created:

    - XML file: contains metadata
    - Python file: contains the source code itself

  This allows to keep Git history and having readable source code instead of
  being crippled into an XML file
  """
  @staticmethod
  def _getZodbObjectId(id):
    return DocumentComponent.getIdPrefix() + '.' + id

  ## All the methods/attributes below are for FS compatibility *only* and
  ## should be removed when all bt5s have been migrated
  _tool_id = 'portal_components'

  @staticmethod
  def _getFilesystemPath(class_id):
    from App.config import getConfiguration
    return os.path.join(getConfiguration().instancehome,
                        "Document",
                        class_id + ".py")

  def isKeepWorkflowObjectLastHistoryOnly(self, path):
    """
    Component Validation Workflow last History of ZODB Components must always be
    kept, without explicitly adding them to the field which requires an extra
    action for developers
    """
    return path.startswith(self._tool_id + '/')
  
  # XXX temporary should be eliminated from here
  def _importFile(self, file_name, file_obj):
    ObjectTemplateItem._importFile(self, file_name, file_obj)
  
  # XXX temporary should be eliminated from here
  def export(self, context, bta, **kw):
    ObjectTemplateItem.export(self, context, bta, **kw)  

  def getTemplateIdList(self):
    """
    Getter for Document property on the Business Template, must be overriden
    in children classes (e.g. ExtensionDocumentTemplateItem for example)
    """
    return self.getTemplateDocumentIdList()

  def build(self, context, **kw):
    if not self._archive:
      return

    # After running the migration script, update bt5 property accordingly
    if not self._is_already_migrated(self._archive.keys()):
      document_id_list = self.getTemplateIdList()
      if document_id_list[0] not in getattr(context.getPortalObject(),
                                            'portal_components', ()):
        return FilesystemDocumentTemplateItem.build(self, context, **kw)
      self._archive.clear()
      for name in document_id_list:
        self._archive['portal_components/' + name] = None

    return ObjectTemplateItem.build(self, context, **kw)

  def install(self, context, **kw):
    """
    In contrary to ZODB Property Sheets, Components are not migrated
    automatically as the version must be set manually. This should not be an
    issue as there are not so many Documents in bt5...
    """
    if self._is_already_migrated(self._objects.keys()):
      _ZodbComponentTemplateItem.install(self, context, **kw)
    else:
      FilesystemDocumentTemplateItem.install(self, context, **kw)

  _removeAllButLastWorkflowHistory = _ZodbComponentTemplateItem._removeAllButLastWorkflowHistory

  # Only for ObjectTemplateItem (ZODB Components) and thus no need to check
  # whether they have already been migrated or not
  afterInstall = _ZodbComponentTemplateItem.afterInstall
  afterUninstall = _ZodbComponentTemplateItem.afterUninstall

from Products.ERP5Type.Core.ExtensionComponent import ExtensionComponent
class ExtensionTemplateItem(DocumentTemplateItem):
  """
  Extensions are now stored in ZODB rather than on the filesystem. However,
  some Business Templates may still have filesystem Extensions which need to
  be migrated to the ZODB.
  """
  # Only meaningful for filesystem Extensions
  local_file_reader_name = staticmethod(readLocalExtension)
  local_file_writer_name = staticmethod(writeLocalExtension)
  # Extension needs no import
  local_file_importer_name = None
  local_file_remover_name = staticmethod(removeLocalExtension)

  @staticmethod
  def _getZodbObjectId(id):
    return ExtensionComponent.getIdPrefix() + '.' + id

  def getTemplateIdList(self):
    return self.getTemplateExtensionIdList()

from Products.ERP5Type.Core.TestComponent import TestComponent

class TestTemplateItem(DocumentTemplateItem):
  """
  Live Tests are now stored in ZODB rather than on the filesystem. However,
  some Business Templates may still have filesystem Live Tests which need to
  be migrated to the ZODB.
  """
  local_file_reader_name = staticmethod(readLocalTest)
  local_file_writer_name = staticmethod(writeLocalTest)
  # Test needs no import
  local_file_importer_name = None
  local_file_remover_name = staticmethod(removeLocalTest)

  @staticmethod
  def _getZodbObjectId(id):
    return TestComponent.getIdPrefix() + '.' + id

  def getTemplateIdList(self):
    return self.getTemplateTestIdList()

class ProductTemplateItem(BaseTemplateItem):
  # XXX Not implemented yet
  pass

class RoleTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    for key in self._archive.iterkeys():
      self._objects[key] = 1

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    # BBB it might be necessary to change the data structure.
    obsolete_key = self.__class__.__name__ + '/role_list'
    if obsolete_key in installed_item._objects:
      for role in installed_item._objects[obsolete_key]:
        installed_item._objects[role] = 1
      del installed_item._objects[obsolete_key]
    for role in self._objects:
      if installed_item._objects.has_key(role):
        continue
      else: # only show new roles
        modified_object_list[role] = 'New', 'Role'
    # get removed roles
    old_roles = installed_item._objects.keys()
    for role in old_roles:
      if role not in self._objects:
        modified_object_list[role] = 'Removed', self.__class__.__name__[:-12]
    return modified_object_list

  def install(self, context, trashbin, **kw):
    p = context.getPortalObject()
    # get roles
    role_set = set(self._objects)
    # set roles in PAS
    if p.acl_users.meta_type == 'Pluggable Auth Service':
      role_manager_list = p.acl_users.objectValues('ZODB Role Manager')
      for role_manager in role_manager_list:
        for role in role_set.difference(role_manager.listRoleIds()):
          role_manager.addRole(role)
    # set roles on portal
    p.__ac_roles__ = tuple(role_set.union(p.__ac_roles__))

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    xml = parse(file)
    for role in xml.getroot():
      value = role.text
      self._objects[value] = 1

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    roles = {}
    for role in p.__ac_roles__:
      roles[role] = 1
    for role in self._archive.keys():
      if role in roles:
        del roles[role]
    p.__ac_roles__ = tuple(roles.keys())
    BaseTemplateItem.uninstall(self, context, **kw)

  def trash(self, context, new_item, **kw):
    p = context.getPortalObject()
    new_roles = {}
    for role in new_item._archive.keys():
      new_roles[role] = 1
    roles = {}
    for role in p.__ac_roles__:
      roles[role] = 1
    for role in self._archive.keys():
      if role in roles and role not in new_roles:
        del roles[role]
    p.__ac_roles__ = tuple(roles.keys())

  # Function to generate XML Code Manually
  def generateXml(self):
    role_list = self._objects.keys()
    xml_data = '<role_list>'
    for role in sorted(role_list):
      xml_data += '\n <role>%s</role>' % (role,)
    xml_data += '\n</role_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects) == 0:
      return
    # BBB it might be necessary to change the data structure.
    obsolete_key = self.__class__.__name__ + '/role_list'
    if obsolete_key in self._objects:
      for role in self._objects[obsolete_key]:
        self._objects[role] = 1
      del self._objects[obsolete_key]
    xml_data = self.generateXml()
    path = obsolete_key
    bta.addObject(xml_data, name=path)

class CatalogKeyTemplateItemBase(BaseTemplateItem):

  def build(self, context, **kw):
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    catalog_key_list = list(getattr(catalog, self.key_list_attr, []))
    key_list = []
    for key in self._archive.keys():
      if key in catalog_key_list:
        key_list.append(key)
      elif not self.is_bt_for_diff:
        raise NotFound, '%s %r not found in catalog' %(self.key_title, key)
    if len(key_list) > 0:
      self._objects[self.key_list_title] = key_list

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    xml = parse(file)
    key_list = [key.text for key in xml.getroot()]
    self._objects[file_name[:-4]] = key_list

  def _getUpdateDictAction(self, update_dict):
    action = update_dict.get(self.key_list_title, 'nothing')
    return action

  def install(self, context, trashbin, **kw):
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    catalog_key_list = list(getattr(catalog, self.key_list_attr, []))
    if len(self._objects.keys()) == 0: # needed because of pop()
      return
    keys = []
    for k in self._objects.values().pop(): # because of list of list
      keys.append(k)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if force or self._getUpdateDictAction(update_dict) != 'nothing':
      catalog_key_list = self._getUpdatedCatalogKeyList(catalog_key_list, keys)
      setattr(catalog, self.key_list_attr, catalog_key_list)

  def _getUpdatedCatalogKeyList(self, catalog_key_list, new_key_list):
    catalog_key_set = set(catalog_key_list) # copy
    catalog_key_set.update(new_key_list)
    return sorted(catalog_key_set)

  def uninstall(self, context, **kw):
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    catalog_key_list = list(getattr(catalog, self.key_list_attr, []))
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in catalog_key_list:
        catalog_key_list.remove(key)
    setattr(catalog, self.key_list_attr, catalog_key_list)
    BaseTemplateItem.uninstall(self, context, **kw)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += '\n <key>%s</key>' %(key)
    xml_data += '\n</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    for name in self._objects.keys():
      path = self.__class__.__name__
      xml_data = self.generateXml(path=name)
      bta.addObject(xml_data, name=name, path=path)

class CatalogUniqueKeyTemplateItemBase(CatalogKeyTemplateItemBase):
  # like CatalogKeyTemplateItemBase, but for keys which use
  # "key | value" syntax to configure dictionaries.
  # The keys (part before the pipe) must be unique.

  def _getMapFromKeyList(self, key_list):
    # in case of duplicates, only the last installed entry will survive
    return dict(tuple(part.strip() for part in key.split('|', 1))
                for key in key_list)

  def _getListFromKeyMap(self, key_map):
    return [" | ".join(item) for item in sorted(key_map.items())]

  def _getUpdatedCatalogKeyList(self, catalog_key_list, new_key_list):
    # treat key lists as dictionaries, parse and update:
    catalog_key_map = self._getMapFromKeyList(catalog_key_list)
    catalog_key_map.update(self._getMapFromKeyList(new_key_list))
    return self._getListFromKeyMap(catalog_key_map)

class CatalogSearchKeyTemplateItem(CatalogUniqueKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_search_keys'
  key_list_title = 'search_key_list'
  key_title = 'Search key'

class CatalogResultKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_search_result_keys'
  key_list_title = 'result_key_list'
  key_title = 'Result key'

class CatalogRelatedKeyTemplateItem(CatalogUniqueKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_related_keys'
  key_list_title = 'related_key_list'
  key_title = 'Related key'

  # override this method to support 'key_list' for backward compatibility.
  def _getUpdateDictAction(self, update_dict):
    action = update_dict.get(self.key_list_title, _MARKER)
    if action is _MARKER:
      action = update_dict.get('key_list', 'nothing')
    return action

class CatalogResultTableTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_search_tables'
  key_list_title = 'result_table_list'
  key_title = 'Result table'

# keyword
class CatalogKeywordKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_keyword_search_keys'
  key_list_title = 'keyword_key_list'
  key_title = 'Keyword key'

# datetime
class CatalogDateTimeKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_datetime_search_keys'
  key_list_title = 'datetime_key_list'
  key_title = 'DateTime key'

# full text
class CatalogFullTextKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_full_text_search_keys'
  key_list_title = 'full_text_key_list'
  key_title = 'Fulltext key'

# request
class CatalogRequestKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_request_keys'
  key_list_title = 'request_key_list'
  key_title = 'Request key'

# multivalue
class CatalogMultivalueKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_multivalue_keys'
  key_list_title = 'multivalue_key_list'
  key_title = 'Multivalue key'

# topic
class CatalogTopicKeyTemplateItem(CatalogKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_topic_search_keys'
  key_list_title = 'topic_key_list'
  key_title = 'Topic key'

class CatalogScriptableKeyTemplateItem(CatalogUniqueKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_scriptable_keys'
  key_list_title = 'scriptable_key_list'
  key_title = 'Scriptable key'

class CatalogRoleKeyTemplateItem(CatalogUniqueKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_role_keys'
  key_list_title = 'role_key_list'
  key_title = 'Role key'

class CatalogLocalRoleKeyTemplateItem(CatalogUniqueKeyTemplateItemBase):
  key_list_attr = 'sql_catalog_local_role_keys'
  key_list_title = 'local_role_key_list'
  key_title = 'LocalRole key'

class CatalogSecurityUidColumnTemplateItem(CatalogSearchKeyTemplateItem):
  key_list_attr = 'sql_catalog_security_uid_columns'
  key_list_title = 'security_uid_column_list'
  key_title = 'Security Uid Columns'


class MessageTranslationTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    localizer = context.getPortalObject().Localizer
    for lang_key in self._archive.keys():
      if '|' in lang_key:
        lang, catalog = lang_key.split(' | ')
      else: # XXX backward compatibility
        lang = lang_key
        catalog = 'erp5_ui'
      path = posixpath.join(lang, catalog)
      mc = localizer._getOb(catalog)
      self._objects[path] = mc.manage_export(lang)
      if lang not in self._objects:
        name = localizer.get_language_name(lang)
        self._objects[lang] = name

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    for path in self._objects:
      if installed_item._objects.has_key(path):
        # compare object to see if there is changes
        new_obj_code = self._objects[path]
        old_obj_code = installed_item._objects[path]
        if new_obj_code != old_obj_code:
          modified_object_list[path] = 'Modified', self.__class__.__name__[:-12]
      else: # new object
        modified_object_list[path] = 'New', self.__class__.__name__[:-12]
    # get removed object
    old_keys = installed_item._objects.keys()
    for path in old_keys:
      if path not in self._objects:
        modified_object_list[path] = 'Removed', self.__class__.__name__[:-12]
    return modified_object_list

  def _splitKey(self,key):
    path = key.split('/')
    if len(path) == 1:
      lang = path[0]
      catalog = None
    elif len(path) == 2:
      lang = path[0]
      catalog = path[1]
    else:
      lang = path[-3]
      catalog = path[-2]
    return lang, catalog

  def _importCatalogLanguage(self, localizer, catalog, lang, po):
    if catalog not in localizer.objectIds():
      dispatcher = localizer.manage_addProduct['Localizer']
      dispatcher.manage_addMessageCatalog(id=catalog,
                                          title='Message Catalog',
                                          languages=['en'])
    mc = localizer._getOb(catalog)
    if lang not in mc.get_languages():
      mc.manage_addLanguage(lang)
    mc.manage_import(lang, po)

  def install(self, context, trashbin, localizer=None, **kw):
    if localizer is None:
      localizer = context.getPortalObject().Localizer
    update_dict = kw.get('object_to_update', {})
    force = kw.get('force')
    for key in sorted(self._objects.keys()):
      if update_dict.has_key(key) or force:
        if not force:
          action = update_dict[key]
          if action == 'nothing':
            continue
        lang, catalog = self._splitKey(key)

        if catalog is None:
          name = self._objects[key]
          for lang_dict in localizer.get_all_languages():
            if lang_dict['code'] == lang:
              # When the Localizer has the language as a user-defined
              # language, make sure that the name is updated.
              old_name = localizer.get_user_defined_language_name(lang)
              if old_name is not None and old_name != name:
                localizer._del_user_defined_language(lang)
                localizer._add_user_defined_language(name, lang)
              break
          else:
            # if the Localizer does not know the language code, it must be
            # defined as a user-defined language.
            localizer._add_user_defined_language(name, lang)
          if lang not in localizer.get_languages():
            localizer.manage_addLanguage(lang)
        else:
          po = self._objects[key]
          if lang not in localizer.get_languages():
            localizer.manage_addLanguage(lang)
          self._importCatalogLanguage(localizer, catalog, lang, po)

  def uninstall(self, context, remove_translations=False, **kw):
    if not remove_translations:
      return
    portal = context.getPortalObject()
    localizer = portal.Localizer
    from Products.Localizer.Localizer import Localizer
    fake_localizer = Localizer('Fake Localizer',
                               languages=['en']).__of__(portal)
    # roundabout way of keeping BW compatibility, allow install() to do the
    # heavy lifting so we can extract the original catalogs and messages:
    self.install(context, None, localizer=fake_localizer, force=True, **kw)
    # now scan the actual message_catalog to remove messages present in the
    # fake one.
    for fake_message_catalog in fake_localizer.objectValues():
      message_catalog = localizer._getOb(fake_message_catalog.getId())
      # get list of messages present in both the fake and the real catalog
      # UGH! direct attribute access... but there is no real API to access
      # all messages here.
      messages = set(fake_message_catalog._messages.keys())
      messages.intersection_update(message_catalog._messages.keys())
      for message in messages:
        # delete translations from the real catalog that are present in the
        # fake one
        fake_translations = fake_message_catalog.get_translations(message)
        translations = message_catalog.get_translations(message)
        for lang in fake_translations.keys():
          # XXX: should we check they're still the same before removing?
          translations.pop(lang, None)

  def export(self, context, bta, **kw):
    if len(self._objects) == 0:
      return
    root_path = self.__class__.__name__
    for key, obj in self._objects.iteritems():
      path = os.path.join(root_path, key)
      if '/' in key:
        bta.addObject(obj, 'translation', ext='.po', path=path)
      else:
        xml_data = ['<language>']
        xml_data.append(' <code>%s</code>' % (escape(key), ))
        xml_data.append(' <name>%s</name>' % (escape(obj), ))
        xml_data.append('</language>')
        bta.addObject('\n'.join(xml_data), 'language', path=path)

  def _importFile(self, file_name, file):
    name = posixpath.split(file_name)[1]
    if name == 'translation.po':
      text = file.read()
      self._objects[file_name[:-len(name)]] = text
    elif name == 'language.xml':
      xml = parse(file)
      name = xml.find('name').text
      code = xml.find('code').text
      self._objects[code] = name

class LocalRolesTemplateItem(BaseTemplateItem):

  def __init__(self, id_list, **kw):
    id_list = ['local_roles/%s' % id for id in id_list if id != '']
    BaseTemplateItem.__init__(self, id_list, **kw)

  def build(self, context, **kw):
    p = context.getPortalObject()
    for path in self._archive.keys():
      obj = p.unrestrictedTraverse(path.split('/', 1)[1])
      local_roles_dict = getattr(obj, '__ac_local_roles__',
                                        {}) or {}
      local_roles_group_id_dict = getattr(
        obj, '__ac_local_roles_group_id_dict__', {}) or {}
      self._objects[path] = (local_roles_dict, local_roles_group_id_dict)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    # With local roles groups id, self._object contains for each path a tuple
    # containing the dict of local roles and the dict of local roles group ids.
    # Before it was only containing the dict of local roles. This method is
    # also used on installed business templates to show a diff during
    # installation, so it might be called on old format objects.
    if len(self._objects[path]) == 2:
      # new format
      local_roles_dict, local_roles_group_id_dict = self._objects[path]
    else:
      # old format, before local roles group id
      local_roles_group_id_dict = None
      local_roles_dict, = self._objects[path]

    xml_data = '<local_roles_item>'
    # local roles
    xml_data += '\n <local_roles>'
    for user_id, role_list in sorted(local_roles_dict.items()):
      if 'Owner' in role_list:
        # We don't export Owner role as it set automatically when installing business template.
        role_list.remove('Owner')
      if role_list:
        xml_data += "\n  <role id='%s'>" %(user_id,)
        for role in role_list:
          xml_data += "\n   <item>%s</item>" %(role,)
        xml_data += '\n  </role>'
    xml_data += '\n </local_roles>'

    if local_roles_group_id_dict:
      # local roles group id dict (not included by default to be stable with
      # old bts)
      xml_data += '\n <local_role_group_ids>'
      for local_role_group_id, local_roles_group_id_list in sorted(local_roles_group_id_dict.items()):
        xml_data += "\n  <local_role_group_id id='%s'>" % escape(local_role_group_id)
        for principal, role in sorted(local_roles_group_id_list):
          xml_data += "\n    <principal id='%s'>%s</principal>" % \
                (escape(principal), escape(role))
        xml_data += "\n  </local_role_group_id>"
      xml_data += '\n </local_role_group_ids>'

    xml_data += '\n</local_roles_item>'
    if isinstance(xml_data, unicode):
      xml_data = xml_data.encode('utf8')
    return xml_data

  def export(self, context, bta, **kw):
    path = self.__class__.__name__
    for key in self._objects:
      xml_data = self.generateXml(key)
      assert key[:12] == 'local_roles/'
      bta.addObject(xml_data, key[12:], path=path)

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    xml = parse(file)
    # local roles
    local_roles_list = xml.findall('//role')
    local_roles_dict = {}
    for role in local_roles_list:
      id = role.get('id')
      item_type_list = [item.text for item in role]
      local_roles_dict[id] = item_type_list

    # local roles group id
    local_roles_group_id_dict = {}
    for local_role_group_id in xml.findall('//local_role_group_id'):
      role_set = set()
      for principal in local_role_group_id.findall('./principal'):
        role_set.add((principal.get('id'), principal.text))
      local_roles_group_id_dict[local_role_group_id.get('id')] = role_set
    self._objects['local_roles/%s' % (file_name[:-4],)] = (
      local_roles_dict, local_roles_group_id_dict)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    for roles_path in self._objects.keys():
      if update_dict.has_key(roles_path) or force:
        if not force:
          action = update_dict[roles_path]
          if action == 'nothing':
            continue
        path = roles_path.split('/')[1:]
        obj = p.unrestrictedTraverse(path)
        # again we might be installing an business template in format before
        # existance of local roles group id.
        if len(self._objects[roles_path]) == 2:
          local_roles_dict, local_roles_group_id_dict = self._objects[roles_path]
        else:
          local_roles_group_id_dict = None
          local_roles_dict, = self._objects[roles_path]

        # We ignore the owner defined in local_roles_dict and set it to the user installing that business template.
        local_roles_dict = deepcopy(local_roles_dict)
        for user_id, group_list in list(local_roles_dict.items()):
          if group_list == ["Owner"]:
            del local_roles_dict[user_id]
        current_user = getSecurityManager().getUser()
        if current_user is not None:
          current_user_id = current_user.getId()
          if current_user_id is not None:
            local_roles_dict.setdefault(current_user_id, []).append('Owner')

        obj.__ac_local_roles__ = local_roles_dict
        if local_roles_group_id_dict:
          obj.__ac_local_roles_group_id_dict__ = local_roles_group_id_dict
          # we try to have __ac_local_roles_group_id_dict__ set only if
          # it is actually defining something else than default
        else:
          try:
            del obj.__ac_local_roles_group_id_dict__
          except AttributeError:
            pass
        obj.reindexObject()

  def uninstall(self, context, object_path=None, **kw):
    p = context.getPortalObject()
    if object_path is not None:
      keys = [object_path]
    else:
      keys = self._objects.keys()
    for roles_path in keys:
      path = roles_path.split('/')[1:]
      # if document does not exists anymore longer,
      # there is no needs to fail
      obj = p.unrestrictedTraverse(path, None)
      if obj is not None:
        setattr(obj, '__ac_local_roles__', {})
        if getattr(aq_base(obj), '__ac_local_roles_group_id_dict__',
                    None) is not None:
          delattr(obj, '__ac_local_roles_group_id_dict__')
        obj.reindexObject()

class bt(dict):
  """Fake 'bt' item to read bt/* files through BusinessTemplateArchive"""

  def _importFile(self, file_name, file):
    self[file_name] = file.read()


class BusinessTemplate(XMLObject):
    """
    A business template allows to construct ERP5 modules
    in part or completely. Each object is separated from its
    subobjects and exported in xml format.
    It may include:

    - catalog definition
      - SQL method objects
      - SQL methods including:
        - purpose (catalog, uncatalog, etc.)
        - filter definition

    - portal_types definition
      - object without optimal actions
      - list of relation between portal type and workflow

    - module definition
      - id
      - title
      - portal type
      - roles/security

    - site property definition
      - id
      - type
      - value

    - document/propertysheet/extension/test definition
      - copy of the local file

    - message transalation definition
      - .po file

    The Business Template properties are exported to the bt folder with
    one property per file

    Technology:

    - download a gzip file or folder tree (from the web, from a CVS repository,
      from local file system) (import/donwload)

    - install files to the right location (install)

    Use case:

    - install core ERP5 (the minimum)

    - go to "BT" menu. Import BT. Select imported BT. Click install.

    - go to "BT" menu. Create new BT.
      Define BT elements (workflow, methods, attributes, etc.).
      Build BT and export or save it
      Done.
    """

    meta_type = 'ERP5 Business Template'
    portal_type = 'Business Template'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Version
                      , PropertySheet.BusinessTemplate
                      , PropertySheet.Comment
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Business Template is a set of definitions, such as skins, portal types and categories. This is used to set up a new ERP5 site very efficiently."""
         , 'icon'           : 'file_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addBusinessTemplate'
         , 'type_class'     : 'BusinessTemplate'
         , 'immediate_view' : 'BusinessTemplate_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': (
                                      )
         , 'filter_content_types' : 1
      }

    def __init__(self, *args, **kw):
      XMLObject.__init__(self, *args, **kw)
      self._clean()

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
      """
        This is called when a new business template is added or imported.
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      if portal_workflow is not None:
        # Make sure that the installation state is "not installed".
        if portal_workflow.getStatusOf(
                'business_template_installation_workflow', self) is not None:
          # XXX Not good to access the attribute directly,
          # but there is no API for clearing the history.
          self.workflow_history[
                            'business_template_installation_workflow'] = None

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getShortRevision')
    def getShortRevision(self):
      """Returned a shortened revision"""
      r = self.getRevision()
      return r and r[:5]

    security.declareProtected(Permissions.ManagePortal, 'storeTemplateItemData')
    def storeTemplateItemData(self):
      """
        Instanciate and Store Template items into properties.
      """
      # Store all Data
      self._portal_type_item = \
          PortalTypeTemplateItem(self.getTemplatePortalTypeIdList())
      self._portal_type_workflow_chain_item = \
          PortalTypeWorkflowChainTemplateItem(self.getTemplatePortalTypeWorkflowChainList())
      self._workflow_item = \
          WorkflowTemplateItem(self.getTemplateWorkflowIdList())
      self._skin_item = \
          SkinTemplateItem(self.getTemplateSkinIdList())
      self._registered_skin_selection_item = \
          RegisteredSkinSelectionTemplateItem(
              self.getTemplateRegisteredSkinSelectionList())
      self._registered_version_priority_selection_item = \
          RegisteredVersionPrioritySelectionTemplateItem(
              self.getTemplateRegisteredVersionPrioritySelectionList())
      self._category_item = \
          CategoryTemplateItem(self.getTemplateBaseCategoryList())
      self._catalog_method_item = \
          CatalogMethodTemplateItem(self.getTemplateCatalogMethodIdList())
      self._action_item = \
          ActionTemplateItem(self.getTemplateActionPathList())
      self._portal_type_roles_item = \
          PortalTypeRolesTemplateItem(self.getTemplatePortalTypeRoleList())
      self._site_property_item = \
          SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._module_item = \
          ModuleTemplateItem(self.getTemplateModuleIdList())
      self._document_item = \
          DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._property_sheet_item = \
          PropertySheetTemplateItem(self.getTemplatePropertySheetIdList(),
                                    context=self)
      self._constraint_item = \
          ConstraintTemplateItem(self.getTemplateConstraintIdList())
      self._extension_item = \
          ExtensionTemplateItem(self.getTemplateExtensionIdList())
      self._test_item = \
          TestTemplateItem(self.getTemplateTestIdList())
      self._product_item = \
          ProductTemplateItem(self.getTemplateProductIdList())
      self._role_item = \
          RoleTemplateItem(self.getTemplateRoleList())
      self._catalog_result_key_item = \
          CatalogResultKeyTemplateItem(
               self.getTemplateCatalogResultKeyList())
      self._catalog_related_key_item = \
          CatalogRelatedKeyTemplateItem(
               self.getTemplateCatalogRelatedKeyList())
      self._catalog_result_table_item = \
          CatalogResultTableTemplateItem(
               self.getTemplateCatalogResultTableList())
      self._message_translation_item = \
          MessageTranslationTemplateItem(
               self.getTemplateMessageTranslationList())
      self._portal_type_allowed_content_type_item = \
           PortalTypeAllowedContentTypeTemplateItem(
               self.getTemplatePortalTypeAllowedContentTypeList())
      self._portal_type_hidden_content_type_item = \
           PortalTypeHiddenContentTypeTemplateItem(
               self.getTemplatePortalTypeHiddenContentTypeList())
      self._portal_type_property_sheet_item = \
           PortalTypePropertySheetTemplateItem(
               self.getTemplatePortalTypePropertySheetList())
      self._portal_type_base_category_item = \
           PortalTypeBaseCategoryTemplateItem(
               self.getTemplatePortalTypeBaseCategoryList())
      self._path_item = \
               PathTemplateItem(self.getTemplatePathList())
      self._preference_item = \
               PreferenceTemplateItem(self.getTemplatePreferenceList())
      self._catalog_search_key_item = \
          CatalogSearchKeyTemplateItem(
               self.getTemplateCatalogSearchKeyList())
      self._catalog_keyword_key_item = \
          CatalogKeywordKeyTemplateItem(
               self.getTemplateCatalogKeywordKeyList())
      self._catalog_datetime_key_item = \
          CatalogDateTimeKeyTemplateItem(
               self.getTemplateCatalogDatetimeKeyList())
      self._catalog_full_text_key_item = \
          CatalogFullTextKeyTemplateItem(
               self.getTemplateCatalogFullTextKeyList())
      self._catalog_request_key_item = \
          CatalogRequestKeyTemplateItem(
               self.getTemplateCatalogRequestKeyList())
      self._catalog_multivalue_key_item = \
          CatalogMultivalueKeyTemplateItem(
               self.getTemplateCatalogMultivalueKeyList())
      self._catalog_topic_key_item = \
          CatalogTopicKeyTemplateItem(
               self.getTemplateCatalogTopicKeyList())
      self._local_roles_item = \
          LocalRolesTemplateItem(
               self.getTemplateLocalRoleList())
      self._tool_item = \
          ToolTemplateItem(
               self.getTemplateToolIdList())
      self._catalog_scriptable_key_item = \
          CatalogScriptableKeyTemplateItem(
               self.getTemplateCatalogScriptableKeyList())
      self._catalog_role_key_item = \
          CatalogRoleKeyTemplateItem(
               self.getTemplateCatalogRoleKeyList())
      self._catalog_local_role_key_item = \
          CatalogLocalRoleKeyTemplateItem(
               self.getTemplateCatalogLocalRoleKeyList())
      # The following properties have been introduced later on. See
      # PropertySheetTool to handle smoothly instances not upgraded yet.
      self._catalog_security_uid_column_item = \
          CatalogSecurityUidColumnTemplateItem(
               self.getTemplateCatalogSecurityUidColumnList())
      self._module_component_item = \
          ModuleComponentTemplateItem(self.getTemplateModuleComponentIdList())
      self._interface_item = \
          InterfaceTemplateItem(self.getTemplateInterfaceIdList())
      self._mixin_item = \
          MixinTemplateItem(self.getTemplateMixinIdList())
      self._tool_component_item = \
          ToolComponentTemplateItem(self.getTemplateToolComponentIdList())

    security.declareProtected(Permissions.ManagePortal, 'build')
    def build(self, no_action=0, update_revision=True):
      """
        Copy existing portal objects to self
      """
      if no_action: return
        # this is use at import of Business Template to get the status built
      # Make sure that everything is sane.
      self.clean()

      self._setTemplateFormatVersion(1)
      self.storeTemplateItemData()

      # Build each part
      for item_name in item_name_list:
        item = getattr(self, item_name)
        if item is None:
          continue
        if self.getBtForDiff():
          item.is_bt_for_diff = 1
        item.build(self)
      # update _p_jar property of objects cleaned by removeProperties
      transaction.savepoint(optimistic=True)
      if update_revision:
        self._export()

    def publish(self, url, username=None, password=None):
      """
        Publish in a format or another
      """
      return self.portal_templates.publish(self, url, username=username,
                                           password=password)

    security.declareProtected(Permissions.ManagePortal, 'update')
    def update(self):
      """
        Update template: download new template definition
      """
      return self.portal_templates.update(self)

    security.declareProtected(Permissions.ManagePortal, 'isCatalogUpdatable')
    def isCatalogUpdatable(self):
      """
      Return if catalog will be updated or not by business template installation
      """
      catalog_method = getattr(self, '_catalog_method_item', None)
      default_catalog = self.getPortalObject().portal_catalog.getSQLCatalog()
      my_catalog = _getCatalogValue(self)
      if default_catalog is not None and my_catalog is not None \
             and catalog_method is not None:
        if default_catalog.getId() == my_catalog.getId():
          # It is needed to update the catalog only if the default SQLCatalog is modified.
          for method_id in catalog_method._objects.keys():
            if 'related' not in method_id:
              # must update catalog
              return True
      return False

    security.declareProtected(Permissions.ManagePortal, 'preinstall')
    def preinstall(self, check_dependencies=1, **kw):
      """
        Return the list of modified/new/removed object between a Business Template
        and the one installed if exists
      """
      if check_dependencies:
        # required because in multi installation, dependencies has already
        # been checked before and it will failed here as dependencies can be
        # installed at the same time
        self.checkDependencies()

      modified_object_list = {}
      bt_title = self.getTitle()

      #  can be call to diff two Business Template in template tool
      bt2 = kw.get('compare_to', None)
      if  bt2 is not None:
        installed_bt = bt2
      else:
        installed_bt = self.portal_templates.getInstalledBusinessTemplate(title=bt_title)

      # if reinstall business template, must compare to object in ZODB
      # and not to those in the installed Business Template because it is itself.
      # same if we make a diff and select only one business template
      reinstall = 0
      if installed_bt == self:
        reinstall = 1
        if self.portal_templates._getOb(INSTALLED_BT_FOR_DIFF, None) is None:
          bt2 = self.portal_templates.manage_clone(ob=installed_bt,
                                                   id=INSTALLED_BT_FOR_DIFF)
          # update portal types properties to get last modifications
          bt2.getPortalTypesProperties()
          bt2.edit(description='tmp bt generated for diff', bt_for_diff=1)
          bt2.build()
          installed_bt = bt2
        else:
          installed_bt = self.portal_templates._getOb(INSTALLED_BT_FOR_DIFF)

      for item_name in item_name_list:
        new_item = getattr(self, item_name, None)
        installed_item = getattr(installed_bt, item_name, None)
        if new_item is not None:
          if installed_item is not None and hasattr(installed_item, '_objects'):
            modified_object = new_item.preinstall(context=self,
                                                  installed_item=installed_item,
                                                  installed_bt=installed_bt)
            if len(modified_object) > 0:
              modified_object_list.update(modified_object)
          else:
            modified_object_list.update(dict.fromkeys(new_item._objects,
              ('New', new_item.__class__.__name__[:-12])))

      if reinstall:
        self.portal_templates.manage_delObjects(ids=[INSTALLED_BT_FOR_DIFF])

      return modified_object_list

    def _install(self, force=1, object_to_update=None, update_translation=0,
                 update_catalog=False, check_dependencies=True, **kw):
      """
        Install a new Business Template, if force, all will be upgraded or installed
        otherwise depends of dict object_to_update
      """
      if object_to_update is not None:
        force=0
      else:
        object_to_update = {}

      site = self.getPortalObject()
      installed_bt = site.portal_templates.getInstalledBusinessTemplate(
                                                           self.getTitle())
      # When reinstalling, installation state should not change to replaced
      if installed_bt not in [None, self]:
        if site.portal_workflow.isTransitionPossible(
            installed_bt, 'replace'):
          installed_bt.replace(self)

      trash_tool = getToolByName(site, 'portal_trash', None)
      if trash_tool is None:
        raise AttributeError, 'Trash Tool is not installed'

      if not force and check_dependencies:
        self.checkDependencies()

      # always created a trash bin because we may to save object already present
      # but not in a previous business templates apart at creation of a new site
      if trash_tool is not None and (len(object_to_update) > 0 or len(self.portal_templates) > 2):
        trashbin = trash_tool.newTrashBin(self.getTitle(), self)
      else:
        trashbin = None

      # Install everything
      if len(object_to_update) or force:
        for item_name in item_name_list:
          item = getattr(self, item_name, None)
          if item is not None:
            item.install(self, force=force, object_to_update=object_to_update,
                               trashbin=trashbin, installed_bt=installed_bt)

      if update_catalog:
        catalog = _getCatalogValue(self)
        if (catalog is None) or (not site.isIndexable):
          LOG('Business Template', 0, 'no SQL Catalog available')
          update_catalog = 0
        else:
          LOG('Business Template', 0, 'Updating SQL Catalog')
          catalog.manage_catalogClear()

      # get objects to remove
      # do remove after because we may need backup object from installation
      remove_object_dict = {}
      for path, action in object_to_update.iteritems():
        if action in ('remove', 'save_and_remove'):
          remove_object_dict[path] = action

      # remove object from old business template
      if len(remove_object_dict):
        # XXX: this code assumes that there is an installed_bt
        for item_name in reversed(item_name_list):
          item = getattr(installed_bt, item_name, None)
          if item is not None:
            item.remove(self, remove_object_dict=remove_object_dict, trashbin=trashbin)


      # update tools if necessary
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateTool():
        from Products.ERP5.ERP5Site import ERP5Generator
        gen = getattr(site, '_generator_class', ERP5Generator)()
        LOG('Business Template', 0, 'Updating Tools')
        gen.setup(site, 0, update=1)

      # remove trashbin if empty
      if trashbin is not None:
        if len(trashbin) == 0:
          trash_tool.manage_delObjects([trashbin.getId(),])

      if update_catalog:
        site.ERP5Site_reindexAll()

      # Update translation table, in case we added new portal types or
      # workflow states.
      if update_translation:
        site.ERP5Site_updateTranslationTable()

      # Clear cache to avoid reusing cached values with replaced objects.
      site.portal_caches.clearAllCache()

    security.declareProtected(Permissions.ManagePortal, 'install')
    install = _install

    security.declareProtected(Permissions.ManagePortal, 'reinstall')
    reinstall = _install

    security.declareProtected(Permissions.ManagePortal, 'trash')
    def trash(self, new_bt, **kw):
      """
        Trash unnecessary items before upgrading to a new business
        template.
        This is similar to uninstall, but different in that this does
        not remove all items.
      """
      # Trash everything
      for item_name in reversed(item_name_list):
        item = getattr(self, item_name, None)
        if item is not None:
          item.trash(
                self,
                getattr(new_bt, item_name))

    def _uninstall(self, **kw):
      """
        For uninstall based on paramaters provided in **kw
      """
      # Uninstall everything
      # Trash everything
      for item_name in reversed(item_name_list):
        item = getattr(self, item_name, None)
        if item is not None:
          item.uninstall(self, **kw)
      # It is better to clear cache because the uninstallation of a
      # template deletes many things from the portal.
      self.getPortalObject().portal_caches.clearAllCache()

    security.declareProtected(Permissions.ManagePortal, 'uninstall')
    uninstall = _uninstall

    def _clean(self):
      """
        Clean built information.
      """
      # First, remove obsolete attributes if present.
      for attr in ( '_action_archive',
                    '_document_archive',
                    '_extension_archive',
                    '_test_archive',
                    '_module_archive',
                    '_object_archive',
                    '_portal_type_archive',
                    '_property_archive',
                    '_property_sheet_archive'):
        if hasattr(self, attr):
          delattr(self, attr)
      # Secondly, make attributes empty.
      for item_name in item_name_list:
        setattr(self, item_name, None)

    security.declareProtected(Permissions.ManagePortal, 'clean')
    clean = _clean

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBuildingState')
    def getBuildingState(self, default=None, id_only=1):
      """
        Returns the current state in building
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById(
                          'business_template_building_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstallationState')
    def getInstallationState(self, default=None, id_only=1):
      """
        Returns the current state in installation
      """
      portal_workflow = getToolByName(self.getPortalObject(), 'portal_workflow')
      wf = portal_workflow.getWorkflowById(
                           'business_template_installation_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    security.declareProtected(Permissions.AccessContentsInformation, 'toxml')
    def toxml(self):
      """
        Return this Business Template in XML
      """
      portal_templates = getToolByName(self, 'portal_templates')
      export_string = portal_templates.manage_exportObject(
                                               id=self.getId(),
                                               toxml=1,
                                               download=1)
      return export_string

    def _getOrderedList(self, id):
      """
        We have to set this method because we want an
        ordered list
      """
      method_id = '_baseGet%sList' % convertToUpperCase(id)
      result = getattr(self, method_id)(())
      if result is None: result = ()
      if result != ():
        result = list(result)
        result.sort()
        # XXX Why do we need to return a tuple ?
        result = tuple(result)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateCatalogMethodIdList')
    def getTemplateCatalogMethodIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_catalog_method_id')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateBaseCategoryList')
    def getTemplateBaseCategoryList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_base_category')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateWorkflowIdList')
    def getTemplateWorkflowIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_workflow_id')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeIdList')
    def getTemplatePortalTypeIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_id')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeWorkflowChainList')
    def getTemplatePortalTypeWorkflowChainList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_workflow_chain')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePathList')
    def getTemplatePathList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_path')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePreferenceList')
    def getTemplatePreferenceList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_preference')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeAllowedContentTypeList')
    def getTemplatePortalTypeAllowedContentTypeList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_allowed_content_type')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeHiddenContentTypeList')
    def getTemplatePortalTypeHiddenContentTypeList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_hidden_content_type')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypePropertySheetList')
    def getTemplatePortalTypePropertySheetList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_property_sheet')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeBaseCategoryList')
    def getTemplatePortalTypeBaseCategoryList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_base_category')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateActionPathList')
    def getTemplateActionPathList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_action_path')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePortalTypeRoleList')
    def getTemplatePortalTypeRoleList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_role')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateLocalRoleList')
    def getTemplateLocalRoleList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_local_role')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateSkinIdList')
    def getTemplateSkinIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_skin_id')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateRegisteredSkinSelectionList')
    def getTemplateRegisteredSkinSelectionList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_registered_skin_selection')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateRegisteredVersionPrioritySelectionList')
    def getTemplateRegisteredVersionPrioritySelectionList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      try:
        return self._getOrderedList('template_registered_version_priority_selection')
      # This property may not be defined if erp5_property_sheets has not been
      # upgraded yet
      except AttributeError:
        return ()

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateModuleIdList')
    def getTemplateModuleIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_module_id')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateMessageTranslationList')
    def getTemplateMessageTranslationList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_message_translation')

    security.declareProtected(Permissions.AccessContentsInformation, 'getTemplateToolIdList')
    def getTemplateToolIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_tool_id')

    def _isInKeepList(self, keep_list, path):
      for keep_path in keep_list:
        if keep_path.endswith('**') and path.startswith(keep_path[:-2]):
          return True
        elif keep_path.endswith('*') and path.startswith(keep_path[:-1])\
            and len(keep_path.split('/')) == len(path.split('/')):
          return True
        elif path == keep_path:
          return True
      return False

    security.declarePrivate('isKeepObject')
    def isKeepObject(self, path):
      """
      Return True if path is included in keep object list.
      """
      return self._isInKeepList(self.getTemplateKeepPathList(), path)

    security.declarePrivate('isKeepWorkflowObject')
    def isKeepWorkflowObject(self, path):
      """
      Return True if path is included in keep workflow object list.
      """
      return self._isInKeepList(self.getTemplateKeepWorkflowPathList(), path)

    security.declarePrivate('isKeepWorkflowObjectLastHistoryOnly')
    def isKeepWorkflowObjectLastHistoryOnly(self, path):
      """
      Return True if path is included in keep workflow last state only list
      """
      return self._isInKeepList(self.getTemplateKeepLastWorkflowHistoryOnlyPathList(),
                                path)

    security.declarePrivate('getExportPath')
    def getExportPath(self):
      preferences = self.getPortalObject().portal_preferences
      bt_name = self.getTitle()
      from App.config import getConfiguration
      instance_home = getConfiguration().instancehome
      for path in (preferences.getPreferredWorkingCopyList() or ['bt5']):
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
          path = os.path.join(instance_home, path)
        bt_path = os.path.join(path, bt_name)
        if os.path.isdir(bt_path):
          return bt_path
        for bt_path in glob.glob(os.path.join(path, '*', bt_name)):
          if os.path.isdir(bt_path):
            return bt_path

    @transactional_cached(lambda self, vcs=None, path=None, restricted=False:
                          (self, vcs, path, restricted))
    def _getVcsTool(self, vcs=None, path=None, restricted=False):
      from Products.ERP5VCS.WorkingCopy import getVcsTool
      if not (path or vcs):
        path = self.getExportPath()
      return getVcsTool(vcs, path, restricted).__of__(self)

    def getVcsTool(self, vcs=None, path=None):
      return self._getVcsTool(vcs, path, True)

    def isVcsType(self, *vcs):
      # could be moved to Products.ERP5.Base.Base
      from Products.ERP5VCS.WorkingCopy import NotAWorkingCopyError
      try:
        return self.getVcsTool().reference in vcs
      except NotAWorkingCopyError:
        return None in vcs

    security.declareProtected(Permissions.ManagePortal, 'export')
    def export(self, path=None, local=0, bta=None, **kw):
      """
        Export this Business Template
      """
      if self.getBuildingState() != 'built':
        raise TemplateConditionError, \
              'Business Template must be built before export'
      return self._export(path, local, bta)

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

    security.declareProtected(Permissions.ManagePortal, 'importFile')
    def importFile(self, path):
      """
        Import all xml files in Business Template
      """
      bta = (BusinessTemplateFolder if os.path.isdir(path) else
             BusinessTemplateTarball)(path, importing=1)
      bt_item = bt()
      bta.importFiles(bt_item)
      prop_dict = {}
      for prop in self.propertyMap():
        pid = prop['id']
        if pid != 'id':
          prop_type = prop['type']
          value = bt_item.get(pid)
          if prop_type in ('text', 'string'):
            prop_dict[pid] = value or ''
          elif prop_type in ('int', 'boolean'):
            prop_dict[pid] = value or 0
          elif prop_type in ('lines', 'tokens'):
            prop_dict[pid[:-5]] = (value or '').splitlines()
      self._edit(**prop_dict)

      from Products.ERP5VCS.WorkingCopy import NotAWorkingCopyError
      try:
        vcs_tool = self._getVcsTool(path=path)
      except NotAWorkingCopyError:
        pass
      else:
        comment = translateString(
          'Downloaded from ${type} repository at revision ${revision}',
          mapping={'type': vcs_tool.title,
                   'revision': vcs_tool.getRevision(True)})
        workflow_tool = self.getPortalObject().portal_workflow
        workflow_tool.business_template_building_workflow.notifyWorkflowMethod(
          self, 'edit', kw={'comment': comment})

      self.storeTemplateItemData()

      # Create temporary modules/classes for classes defined by this BT.
      # This is required if the BT contains instances of one of these classes.
      # XXX This is not required with portal types as classes.
      #     It is still there for compatibility with non-migrated objects.
      module_id_list = []
      for template_id in self.getTemplateDocumentIdList():
        module_id = 'Products.ERP5Type.Document.' + template_id
        if module_id not in sys.modules:
          module_id_list.append(module_id)
          sys.modules[module_id] = module = imp.new_module(module_id)
          setattr(module, template_id, type(template_id,
            (SimpleItem.SimpleItem,), {'__module__': module_id}))

      for item_name in item_name_list:
        item_object = getattr(self, item_name, None)
        # this check is due to backwards compatability when there can be a
        # difference between install erp5_property_sheets (esp. BusinessTemplate
        # property sheet)
        if item_object is not None:
          item_object.importFile(bta)

      # Remove temporary modules created above to allow import of real modules
      # (during the installation).
      for module_id in module_id_list:
        del sys.modules[module_id]

      self._setRevision(bta.getRevision())

    security.declareProtected(Permissions.AccessContentsInformation, 'getItemsList')
    def getItemsList(self):
      """Return list of items in business template
      """
      items_list = []
      for item_name in item_name_list:
        item = getattr(self, item_name, None)
        if item is not None:
          items_list.extend(item.getKeys())
      return items_list

    security.declareProtected(Permissions.ManagePortal, 'checkDependencies')
    def checkDependencies(self):
      """
       Check if all the dependencies of the business template
       are installed. Raise an exception with the list of
       missing dependencies if some are missing
      """
      missing_dep_list = self.getMissingDependencyList()
      if len(missing_dep_list) != 0:
        raise BusinessTemplateMissingDependency, \
          'Impossible to install %s, please install the following dependencies before: %s' \
          %(self.getTitle(), repr(missing_dep_list))

    security.declareProtected(Permissions.ManagePortal, 'getMissingDependencyList')
    def getMissingDependencyList(self):
      """
      Retuns a list of missing dependencies.
      """
      missing_dep_list = []
      dependency_list = self.getDependencyList()
      if len(dependency_list) > 0:
        for dependency_couple in dependency_list:
          dependency_couple_list = dependency_couple.strip().split(' ', 1)
          dependency = dependency_couple_list[0]
          if dependency in (None, ''):
            continue
          version_restriction = None
          if len(dependency_couple_list) > 1:
            version_restriction = dependency_couple_list[1]
            if version_restriction.startswith('('):
              # Something like "(>= 1.0rc6)".
              version_restriction = version_restriction[1:-1]
          installed_bt = self.portal_templates.getInstalledBusinessTemplate(dependency)
          if (not self.portal_templates.IsOneProviderInstalled(dependency)) \
             and ((installed_bt is None) \
                  or (version_restriction not in (None, '') and
                     (not self.portal_templates.compareVersionStrings(installed_bt.getVersion(), version_restriction)))):
            missing_dep_list.append((dependency, version_restriction or ''))
      return [' '.join([y for y in x if y]) for x in missing_dep_list]

    security.declareProtected(Permissions.ManagePortal, 'diffObjectAsHTML')
    def diffObjectAsHTML(self, REQUEST, **kw):
      """
        Convert diff into a HTML format before reply
        This is compatible with ERP5VCS look and feel but
        it is preferred in future we use more difflib python library.
      """
      return DiffFile(self.diffObject(REQUEST, **kw)).toHTML()

    security.declareProtected(Permissions.ManagePortal, 'diffObject')
    def diffObject(self, REQUEST, **kw):
      """
        Make a diff between an object in the Business Template
        and the same in the Business Template installed in the site
      """

      class_name_dict = {
        'Product' : '_product_item',
        'PropertySheet' : '_property_sheet_item',
        'Constraint' : '_constraint_item',
        'ModuleComponent' : '_module_component_item',
        'Document' : '_document_item',
        'Interface': '_interface_item',
        'Mixin': '_mixin_item',
        'ToolComponent' : '_tool_component_item',
        'Extension' : '_extension_item',
        'Test' : '_test_item',
        'Role' : '_role_item',
        'MessageTranslation' : '_message_translation_item',
        'Workflow' : '_workflow_item',
        'CatalogMethod' : '_catalog_method_item',
        'SiteProperty' : '_site_property_item',
        'PortalType' : '_portal_type_item',
        'PortalTypeWorkflowChain' : '_portal_type_workflow_chain_item',
        'PortalTypeAllowedContentType' : '_portal_type_allowed_content_type_item',
        'PortalHiddenAllowedContentType' : '_portal_type_hidden_content_type_item',
        'PortalTypePropertySheet' : '_portal_type_property_sheet_item',
        'PortalTypeBaseCategory' : '_portal_type_base_category_item',
        'Category' : '_category_item',
        'Module' : '_module_item',
        'Skin' : '_skin_item',
        'RegisteredSkinSelection' : '_registered_skin_selection_item',
        'Path' : '_path_item',
        'Preference' : '_preference_item',
        'Action' : '_action_item',
        'PortalTypeRoles' : '_portal_type_roles_item',
        'LocalRoles' : '_local_roles_item',
        'CatalogResultKey' : '_catalog_result_key_item',
        'CatalogRelatedKey' : '_catalog_related_key_item',
        'CatalogResultTable' : '_catalog_result_table_item',
        'CatalogSearchKey' : '_catalog_search_key_item',
        'CatalogKeywordKey' : '_catalog_keyword_key_item',
        'CatalogDateTimeKey' : '_catalog_datetime_key_item',
        'CatalogFullTextKey' : '_catalog_full_text_key_item',
        'CatalogRequestKey' : '_catalog_request_key_item',
        'CatalogMultivalueKey' : '_catalog_multivalue_key_item',
        'CatalogTopicKey' : '_catalog_topic_key_item',
        'Tool': '_tool_item',
        'CatalogScriptableKey' : '_catalog_scriptable_key_item',
        'CatalogRoleKey' : '_catalog_role_key_item',
        'CatalogLocalRoleKey' : '_catalog_local_role_key_item',
        'CatalogSecurityUidColumn' : '_catalog_security_uid_column_item',
        }

      object_id = REQUEST.object_id
      object_class = REQUEST.object_class

      # Get objects
      item_name = class_name_dict[object_class]

      new_bt = self
      # Compare with a given business template
      compare_to_zodb = 0
      bt2_id = kw.get('compare_with', None)
      if bt2_id is not None:
        if bt2_id == self.getId():
          compare_to_zodb = 1
          installed_bt = self.getInstalledBusinessTemplate(title=self.getTitle())
        else:
          installed_bt = self.portal_templates._getOb(bt2_id)
      else:
        installed_bt = self.getInstalledBusinessTemplate(title=self.getTitle())
        if installed_bt == new_bt:
          compare_to_zodb = 1
      if compare_to_zodb:
        bt2 = self.portal_templates.manage_clone(ob=installed_bt,
                                                 id=INSTALLED_BT_FOR_DIFF)
        # Update portal types properties to get last modifications
        bt2.getPortalTypesProperties()
        bt2.edit(description='tmp bt generated for diff')
        installed_bt = bt2

      new_item = getattr(new_bt, item_name)
      installed_item = getattr(installed_bt, item_name)
      if compare_to_zodb:
        # XXX maybe only build for the given object to gain time
        installed_item.build(self)
      new_object = new_item._objects[object_id]
      installed_object = installed_item._objects[object_id]
      diff_msg = ''

      # Real Zope Objects (can be exported into XML directly by Zope)
      # XXX Bad naming
      item_list_1 = ['_product_item', '_workflow_item', '_portal_type_item',
                     '_category_item', '_path_item', '_preference_tem',
                     '_skin_item', '_action_item', '_tool_item', ]

      # Not considered as objects by Zope (will be exported into XML manually)
      # XXX Bad naming
      item_list_2 = ['_site_property_item',
                     '_module_item',
                     '_catalog_result_key_item',
                     '_catalog_related_key_item',
                     '_catalog_result_table_item',
                     '_catalog_search_key_item',
                     '_catalog_keyword_key_item',
                     '_catalog_datetime_key_item',
                     '_catalog_full_text_key_item',
                     '_catalog_request_key_item',
                     '_catalog_multivalue_key_item',
                     '_catalog_topic_key_item',
                     '_catalog_scriptable_key_item',
                     '_catalog_role_key_item',
                     '_catalog_local_role_key_item',
                     '_catalog_security_uid_column_item',
                     '_portal_type_allowed_content_type_item',
                     '_portal_type_hidden_content_type_item',
                     '_portal_type_property_sheet_item',
                     '_portal_type_roles_item',
                     '_portal_type_base_category_item',
                     '_local_roles_item',
                     '_portal_type_workflow_chain_item',]

      # Text objects (no need to export them into XML)
      # XXX Bad naming
      item_list_3 = ['_module_component_item',
                     '_document_item', '_interface_item', '_mixin_item',
                     '_tool_component_item',
                     '_property_sheet_item',
                     '_constraint_item', '_extension_item',
                     '_test_item', '_message_translation_item',]

      if item_name in item_list_1:
        f1 = StringIO() # for XML export of New Object
        f2 = StringIO() # For XML export of Installed Object
        # Remove unneeded properties
        new_object = new_item.removeProperties(new_object, 1)
        installed_object = installed_item.removeProperties(installed_object, 1)
        # XML Export in memory
        OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, f1)
        OFS.XMLExportImport.exportXML(installed_object._p_jar,
                                      installed_object._p_oid, f2)
        new_obj_xml = f1.getvalue()
        f1.close()
        installed_obj_xml = f2.getvalue()
        f2.close()
        new_ob_xml_lines = new_obj_xml.splitlines()
        installed_ob_xml_lines = installed_obj_xml.splitlines()
        # End of XML export

        # Diff between XML objects
        diff_list = list(unified_diff(installed_ob_xml_lines, new_ob_xml_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' % (object_id,)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'

      elif item_name in item_list_2:
        # Generate XML code manually
        new_obj_xml = new_item.generateXml(path= object_id)
        installed_obj_xml = installed_item.generateXml(path= object_id)
        new_obj_xml_lines = new_obj_xml.splitlines()
        installed_obj_xml_lines = installed_obj_xml.splitlines()
        # End of XML Code Generation

        # Diff between XML objects
        diff_list = list(unified_diff(installed_obj_xml_lines, new_obj_xml_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' % (object_id,)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'

      elif item_name in item_list_3:
        # Diff between text objects
        if hasattr(new_object, 'getTextContent'): # ZODB component
          new_object = new_object.getTextContent()
        new_obj_lines = new_object.splitlines()
        if hasattr(installed_object, 'getTextContent'):
          installed_object = installed_object.getTextContent()
        installed_obj_lines = installed_object.splitlines()
        diff_list = list(unified_diff(installed_obj_lines, new_obj_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' % (object_id,)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'

      else:
        diff_msg += 'Unsupported file !'

      if compare_to_zodb:
        self.portal_templates.manage_delObjects(ids=[INSTALLED_BT_FOR_DIFF])

      return diff_msg


    security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTypesProperties')
    def getPortalTypesProperties(self, **kw):
      """
      Fill field about properties for each portal type
      """
      wtool = self.getPortalObject().portal_workflow
      ttool = self.getPortalObject().portal_types
      bt_allowed_content_type_list = list(
        self.getTemplatePortalTypeAllowedContentTypeList())
      bt_hidden_content_type_list = list(
        self.getTemplatePortalTypeHiddenContentTypeList())
      bt_property_sheet_list = list(
        self.getTemplatePortalTypePropertySheetList())
      bt_base_category_list = list(
        self.getTemplatePortalTypeBaseCategoryList())
      bt_action_list = list(self.getTemplateActionPathList())
      bt_portal_types_id_list = list(self.getTemplatePortalTypeIdList())
      bt_portal_type_roles_list = list(self.getTemplatePortalTypeRoleList())
      bt_wf_chain_list = list(self.getTemplatePortalTypeWorkflowChainList())

      for id in bt_portal_types_id_list:
        portal_type = ttool.getTypeInfo(id)
        if portal_type is None:
          continue
        if portal_type.getRoleInformationList():
          if id not in bt_portal_type_roles_list:
            bt_portal_type_roles_list.append(id)

        allowed_content_type_list = []
        hidden_content_type_list = []
        property_sheet_list = []
        base_category_list = []
        action_list = []
        if hasattr(portal_type, 'allowed_content_types'):
          allowed_content_type_list = portal_type.allowed_content_types
        if hasattr(portal_type, 'hidden_content_type_list'):
          hidden_content_type_list = portal_type.hidden_content_type_list
        if hasattr(portal_type, 'property_sheet_list'):
          property_sheet_list = portal_type.property_sheet_list
        if hasattr(portal_type, 'base_category_list'):
          base_category_list = portal_type.base_category_list
        for action in portal_type.getActionInformationList():
          action_list.append(action.getReference())

        for a_id in allowed_content_type_list:
          allowed_id = id+' | '+a_id
          if allowed_id not in bt_allowed_content_type_list:
            bt_allowed_content_type_list.append(allowed_id)

        for h_id in hidden_content_type_list:
          hidden_id = id+' | '+h_id
          if hidden_id not in bt_hidden_content_type_list:
            bt_hidden_content_type_list.append(hidden_id)

        for ps_id in property_sheet_list:
          p_sheet_id = id+' | '+ps_id
          if p_sheet_id not in bt_property_sheet_list:
            bt_property_sheet_list.append(p_sheet_id)

        for bc_id in base_category_list:
          base_cat_id = id+' | '+bc_id
          if base_cat_id not in bt_base_category_list:
            bt_base_category_list.append(base_cat_id)

        for act_id in action_list:
          action_id = id+' | '+act_id
          if action_id not in bt_action_list:
            bt_action_list.append(action_id)

        for workflow_id in [chain for chain in wtool.getChainFor(id)
                                    if chain != '(Default)']:
          wf_id = id+' | '+workflow_id
          if wf_id not in bt_wf_chain_list:
            bt_wf_chain_list.append(wf_id)

      bt_allowed_content_type_list.sort()
      bt_hidden_content_type_list.sort()
      bt_property_sheet_list.sort()
      bt_base_category_list.sort()
      bt_action_list.sort()
      bt_wf_chain_list.sort()

      self.setTemplatePortalTypeWorkflowChainList(bt_wf_chain_list)
      self.setTemplatePortalTypeRoleList(bt_portal_type_roles_list)
      self.setTemplatePortalTypeAllowedContentTypeList(bt_allowed_content_type_list)
      self.setTemplatePortalTypeHiddenContentTypeList(bt_hidden_content_type_list)
      self.setTemplatePortalTypePropertySheetList(bt_property_sheet_list)
      self.setTemplatePortalTypeBaseCategoryList(bt_base_category_list)
      self.setTemplateActionPathList(bt_action_list)


    security.declareProtected(Permissions.AccessContentsInformation,
                              'guessPortalTypes')
    def guessPortalTypes(self, **kw):
      """
      This method guesses portal types based on modules define in the Business Template
      """
      bt_module_id_list = list(self.getTemplateModuleIdList())
      if len(bt_module_id_list) == 0:
        raise TemplateConditionError, 'No module defined in business template'

      bt_portal_types_id_list = list(self.getTemplatePortalTypeIdList())

      def getChildPortalType(type_id):
        type_list = {}
        p = self.getPortalObject()
        try:
          portal_type = p.unrestrictedTraverse('portal_types/'+type_id)
        except KeyError:
          return type_list

        allowed_content_type_list = []
        hidden_content_type_list = []
        if hasattr(portal_type, 'allowed_content_types'):
          allowed_content_type_list = portal_type.allowed_content_types
        if hasattr(portal_type, 'hidden_content_type_list'):
          hidden_content_type_list = portal_type.hidden_content_type_list
        type_list[type_id] = ()
        # get same info for allowed portal types and hidden portal types
        for allowed_ptype_id in allowed_content_type_list:
          if allowed_ptype_id not in type_list.keys():
            type_list.update(getChildPortalType(allowed_ptype_id))
        for hidden_ptype_id in hidden_content_type_list:
          if hidden_ptype_id not in type_list.keys():
            type_list.update(getChildPortalType(hidden_ptype_id))
        return type_list

      p = self.getPortalObject()
      portal_dict = {}
      for module_id in bt_module_id_list:
        module = p.unrestrictedTraverse(module_id)
        portal_type_id = module.getPortalType()
        try:
          portal_type = p.unrestrictedTraverse('portal_types/'+portal_type_id)
        except KeyError:
          continue
        allowed_content_type_list = []
        hidden_content_type_list = []
        if hasattr(portal_type, 'allowed_content_types'):
          allowed_content_type_list = portal_type.allowed_content_types
        if hasattr(portal_type, 'hidden_content_type_list'):
          hidden_content_type_list = portal_type.hidden_content_type_list

        portal_dict[portal_type_id] = ()

        for allowed_type_id in allowed_content_type_list:
          if allowed_type_id not in portal_dict.keys():
            portal_dict.update(getChildPortalType(allowed_type_id))

        for hidden_type_id in hidden_content_type_list:
          if hidden_type_id not in portal_dict.keys():
            portal_dict.update(getChildPortalType(hidden_type_id))

      # construct portal type list, keep already present portal types
      for id in portal_dict.keys():
        if id not in bt_portal_types_id_list:
          bt_portal_types_id_list.append(id)

      bt_portal_types_id_list.sort()

      setattr(self, 'template_portal_type_id', bt_portal_types_id_list)
      return

    security.declarePrivate('clearPortalTypes')
    def clearPortalTypes(self, **kw):
      """
      clear id list register for portal types
      """
      setattr(self, 'template_portal_type_id', ())
      setattr(self, 'template_portal_type_allowed_content_type', ())
      setattr(self, 'template_portal_type_hidden_content_type', ())
      setattr(self, 'template_portal_type_property_sheet', ())
      setattr(self, 'template_portal_type_base_category', ())
      return

    def _getWorkingCopyPathList(self):
      working_copy_list = self.getPortalObject().portal_preferences.getPreferredWorkingCopyList([])
      if not working_copy_list:
        raise RuntimeError("No 'Working Copies' set in Preferences")

      return [ os.path.realpath(p) for p in working_copy_list ]

    def _checkFilesystemModulePath(self,
                                   module_obj,
                                   working_copy_path_list):
      """
      Return the path of the given module iff its path is in Working Copies
      """
      try:
        module_path = inspect.getsourcefile(module_obj)
      except TypeError:
        # No file, builtin or 'erp5' dynamic module
        return None
      else:
        # Canonicalize all paths before comparing (at the same time this will
        # take care of trailing '/')
        module_realpath = os.path.realpath(module_path)
        for working_copy_path in working_copy_path_list:
          working_copy_path = os.path.realpath(working_copy_path)
          if working_copy_path.endswith('bt5'):
            working_copy_path = working_copy_path[:-3]

          if module_realpath.startswith(working_copy_path):
            # Product
            if module_path.endswith('/__init__.py'):
              return module_path.rsplit('/', 1)[0]
            else:
              return module_path

        return None

    def _getAllFilesystemModuleFromPortalTypeIdList(self, portal_type_id_list):
      import erp5.portal_type
      import Products.ERP5Type
      import zope.interface

      working_copy_path_list = self._getWorkingCopyPathList()
      seen_cls_set = set()
      for portal_type in portal_type_id_list:
        # According to ObjectTemplateItem.__init__, this could happen (see
        # stepAddPortalTypeToBusinessTemplate)
        if portal_type == '':
          continue

        portal_type_cls = getattr(erp5.portal_type, portal_type)
        # Calling mro() would not load the class...
        try:
          portal_type_cls.loadClass()
        except Exception:
          LOG("BusinessTemplate", WARNING,
              "Could not load Portal Type Class %s, ignored for migration..." %
              portal_type,
              error=True)
          continue

        for cls in (tuple(zope.interface.implementedBy(portal_type_cls)) +
                    portal_type_cls.mro()):
          if cls in seen_cls_set:
            continue
          seen_cls_set.add(cls)

          cls_module_filepath = self._checkFilesystemModulePath(
            inspect.getmodule(cls),
            working_copy_path_list)
          if cls_module_filepath is not None:
            cls_module_name = cls.__module__
            yield cls.__name__, cls.__module__, cls_module_filepath

    security.declareProtected(Permissions.ManagePortal,
                              'getMigratableSourceCodeFromFilesystemList')
    def getMigratableSourceCodeFromFilesystemList(self,
                                                  *args,
                                                  **kwargs):
      """
      Return the list of Business Template {Extension, Document, Test} Documents
      and Products Documents which can be migrated to ZODB Components.
      """
      import inspect

      bt_migratable_uid_list = []
      migratable_component_list = []
      portal = self.getPortalObject()
      component_tool = portal.portal_components

      from base64 import b64encode
      import cPickle
      def __newTempComponent(portal_type, reference, source_reference, migrate=False):
        uid = b64encode("%s|%s|%s" % (portal_type, reference, source_reference))
        if migrate:
          bt_migratable_uid_list.append(uid)

        obj = component_tool.newContent(temp_object=1,
                                        id="temp_" + uid,
                                        uid=uid,
                                        portal_type=portal_type,
                                        reference=reference,
                                        source_reference=source_reference,
                                        migrate=migrate)

        migratable_component_list.append(obj)

        return obj

      for portal_type, id_list in (
          ('Document Component', self.getTemplateDocumentIdList()),
          ('Extension Component', self.getTemplateExtensionIdList()),
          ('Test Component', self.getTemplateTestIdList())):
        for id_ in id_list:
          existing_component = getattr(component_tool, id_, None)
          if existing_component is None:
            obj = __newTempComponent(portal_type=portal_type,
                                     reference=id_,
                                     source_reference="%s:%s" % (self.getTitle(), id_),
                                     migrate=True)

      # Inspect Portal Types classes mro() of this Business Template to find
      # Products Documents to migrate by default
      portal_type_module_filepath_set = set([
        filepath for _, _, filepath in 
        self._getAllFilesystemModuleFromPortalTypeIdList(
          self.getTemplatePortalTypeIdList())])

      working_copy_path_list = self._getWorkingCopyPathList()
      import Products
      for product_name, product_obj in inspect.getmembers(Products,
                                                          inspect.ismodule):
        if (product_name[0] == '_' or
            # Returned by inspect.getmembers()
            product_name == 'this_module' or
            product_name in (
              # Never going to be migrated (bootstrap)
              'ERP5Type',
              # Probably going to be migrated but at the end and should not be
              # done for now (especially ActiveObject and HBTreeFolder2
              # classes found in the MRO of most classes)
              'CMFActivity', 'HBTreeFolder2')):
          continue

        product_base_path = self._checkFilesystemModulePath(
          product_obj,
          working_copy_path_list)
        if product_base_path is None:
          continue

        seen_module_set = set()
        # 'Module Component': Only handle Product top-level modules
        for name, obj in inspect.getmembers(product_obj):
          if (name[0] == '_' or
              name in ('this_module', 'Permissions') or
              obj is product_obj):
            continue

          if inspect.ismodule(obj):
            source_reference = obj.__name__
            submodule_name = name
          else:
            try:
              source_reference = obj.__module__
            except AttributeError:
              continue
            try:
              submodule_name = source_reference.rsplit('.', 1)[1]
            except IndexError:
              continue

          if (source_reference == product_obj.__name__ or
              not source_reference.startswith(product_obj.__name__) or
              source_reference in seen_module_set):
            continue
          seen_module_set.add(source_reference)

          try:
            submodule_filepath = inspect.getsourcefile(obj)
          except TypeError:
            # No file, builtin?
            continue

          if submodule_filepath and submodule_filepath.rsplit('/', 1)[0] == product_base_path:
            migrate = submodule_filepath in portal_type_module_filepath_set
            obj = __newTempComponent(portal_type='Module Component',
                                     reference=submodule_name,
                                     source_reference=source_reference,
                                     migrate=migrate)

        # {Document,interfaces,mixin,Tool,tests} directories
        for directory_name, component_portal_type in (
            ('Document', 'Document Component'),
            ('interfaces', 'Interface Component'),
            ('mixin', 'Mixin Component'),
            ('Tool', 'Tool Component'),
            ('tests', 'Test Component')):
          submodule_name = '%s.%s' % (product_obj.__name__, directory_name)
          for filepath in glob.iglob("%s/%s/*.py" % (product_base_path,
                                                     directory_name)):
            subsubmodule_name = os.path.splitext(os.path.basename(filepath))[0]
            if subsubmodule_name == '__init__':
              continue

            subsubmodule_portal_type = component_portal_type
            source_reference = "%s.%s" % (submodule_name, subsubmodule_name)
            migrate = filepath in portal_type_module_filepath_set
            if component_portal_type == 'Test Component':
              # For non test classes (Mixin, utils...)
              if not subsubmodule_name.startswith('test'):
                subsubmodule_portal_type = 'Module Component'
            # FS: Products/ERP5ShortMessage/interfaces/sms_sending_gateway.py: ISmsSendingGateway
            # => ZODB Component Reference: ISmsSendingGateway
            elif component_portal_type == 'Interface Component':
              # Generally: foo_bar.py => IFooBar, but to avoid quirks (such as
              # 'sql_foo.py' => 'ISQLFoo'), get the Interface class __name__
              try:
                interface_module = __import__(source_reference, {}, {}, source_reference)
              except ImportError, e:
                LOG("BusinessTemplate", WARNING,
                    "Skipping %s: Cannot be imported (%s)" % (filepath, e))
                continue

              from zope.interface.interface import InterfaceClass
              interface_class_name = None
              for _, m in inspect.getmembers(interface_module):
                if (isinstance(m, InterfaceClass) and
                    # Local definition only
                    m.__module__ == interface_module.__name__):
                  if interface_class_name is not None:
                    # Do not try to be clever, just let the developer fix the problem
                    LOG("BusinessTemplate", WARNING,
                        "Skipping %s: More than one InterfaceClass defined" % filepath)
                    interface_class_name = None
                    break
                  else:
                    interface_class_name = m.__name__

              if interface_class_name is None:
                continue

              subsubmodule_name = interface_class_name

            obj = __newTempComponent(portal_type=subsubmodule_portal_type,
                                     reference=subsubmodule_name,
                                     source_reference=source_reference,
                                     migrate=migrate)


      # Automatically select ZODB Components to be migrated in Migration Dialog
      selection_name = kwargs.get('selection_name')
      if (selection_name is not None and
          # XXX: Do not set uids on {check,uncheck}All, better way?
          self.REQUEST.get('listbox_uncheckAll') is None and
          self.REQUEST.get('listbox_checkAll') is None):
        portal.portal_selections.setSelectionCheckedUidsFor(selection_name,
                                                            bt_migratable_uid_list)

      return sorted(migratable_component_list,
                    key=lambda o: (not o.getProperty('migrate', False),
                                   o.getPortalType(),
                                   o.getReference()))

    security.declareProtected(Permissions.ManagePortal,
                              'migrateSourceCodeFromFilesystem')
    def migrateSourceCodeFromFilesystem(self,
                                        version,
                                        **kw):
      """
      Migrate the given components from filesystem to ZODB by calling the
      appropriate importFromFilesystem according to the destination Portal
      Type and then update the Business Template property with migrated IDs
      """
      portal = self.getPortalObject()
      component_tool = portal.portal_components
      failed_import_dict = {}
      list_selection_name = kw.get('list_selection_name')
      migrated_product_module_set = set()

      template_module_component_id_set = set(self.getTemplateModuleComponentIdList())
      template_mixin_id_set = set(self.getTemplateMixinIdList())
      template_interface_id_set = set(self.getTemplateInterfaceIdList())
      template_document_id_set = set(self.getTemplateDocumentIdList())
      template_tool_component_id_set = set(self.getTemplateToolComponentIdList())
      template_extension_id_set = set(self.getTemplateExtensionIdList())
      template_test_id_set = set(self.getTemplateTestIdList())

      if list_selection_name is None:
        # Programmatically called, not through the UI
        temp_obj_list = [ temp_obj for temp_obj in self.getMigratableSourceCodeFromFilesystemList()
                          if temp_obj.migrate ]
      else:
        from base64 import b64decode
        import cPickle
        temp_obj_list = []
        for uid in portal.portal_selections.getSelectionCheckedUidsFor(
            list_selection_name):
          portal_type, reference, source_reference = b64decode(uid).split('|')
          obj = component_tool.newContent(temp_object=1,
                                          id="temp_" + uid,
                                          uid=uid,
                                          portal_type=portal_type,
                                          reference=reference,
                                          source_reference=source_reference)

          temp_obj_list.append(obj)

      if not temp_obj_list:
        if list_selection_name is not None:
          return self.Base_redirect(
            'view',
            keep_items={'portal_status_message': 'Nothing Selected.'})

        return

      filesystem_zodb_module_mapping_set = set()
      for temp_obj in temp_obj_list:
        source_reference = temp_obj.getSourceReference()
        if source_reference is not None:
          filesystem_zodb_module_mapping_set.add(
            (source_reference, "%s.%s" % (temp_obj._getDynamicModuleNamespace(),
                                          temp_obj.getReference())))

      for temp_obj in temp_obj_list:
        source_reference = temp_obj.getSourceReference()
        try:
          obj = temp_obj.importFromFilesystem(component_tool,
                                              temp_obj.getReference(),
                                              version,
                                              source_reference,
                                              filesystem_zodb_module_mapping_set)
        except Exception, e:
          LOG("BusinessTemplate", WARNING,
              "Could not import component '%s' ('%s') from the filesystem" %
              (temp_obj.getReference(),
               temp_obj.getSourceReference()),
              error=True)

          failed_import_dict[temp_obj.getReference()] = str(e)
        else:
          portal_type = obj.getPortalType()
          if portal_type == 'Extension Component':
            id_set = template_extension_id_set
          elif portal_type == 'Test Component':
            id_set = template_test_id_set
          elif portal_type == 'Mixin Component':
            id_set = template_mixin_id_set
          elif portal_type == 'Module Component':
            id_set = template_module_component_id_set
          elif portal_type == 'Interface Component':
            id_set = template_interface_id_set
          elif portal_type == 'Tool Component':
            id_set = template_tool_component_id_set
          # 'Document Component'
          else:
            id_set = template_document_id_set

          if source_reference.startswith('Products'):
            migrated_product_module_set.add(source_reference)
          else:
            id_set.discard(temp_obj.getReference())

          id_set.add(obj.getId())

      if failed_import_dict:
        message = (
          "The following component could not be imported: " +
          ', '.join([ "%s (%s)" % (name, error)
                      for name, error in failed_import_dict.iteritems() ]))

        if list_selection_name is not None:
          return self.Base_redirect('view',
                                    keep_items={'portal_status_message': message},
                                    abort_transaction=True)

        transaction.abort()
        raise RuntimeError(message)

      self.setTemplateModuleComponentIdList(sorted(template_module_component_id_set))
      self.setTemplateMixinIdList(sorted(template_mixin_id_set))
      self.setTemplateInterfaceIdList(sorted(template_interface_id_set))
      self.setTemplateDocumentIdList(sorted(template_document_id_set))
      self.setTemplateToolComponentIdList(sorted(template_tool_component_id_set))
      self.setTemplateExtensionIdList(sorted(template_extension_id_set))
      self.setTemplateTestIdList(sorted(template_test_id_set))

      # This will trigger a reset so that Portal Types mro() can be checked
      # after migration for filesystem Products modules still being used
      #
      # TODO-arnau: checkPythonSource code done twice (importFromFilesystem()
      # and newContent() through Interaction Workflow)
      transaction.commit()

      still_used_list_dict = {}
      for _, cls_module, _ in self._getAllFilesystemModuleFromPortalTypeIdList(
          portal.portal_types.objectIds()):
        if cls_module in migrated_product_module_set:
          package, module = cls_module.rsplit('.', 1)
          still_used_list_dict.setdefault(package, []).append(module)

      if still_used_list_dict:
        module_still_used_message = ', '.join(
            [ "%s.{%s}" % (package, ','.join(sorted(module_list)))
              for package, module_list in still_used_list_dict.iteritems() ])

        LOG('BusinessTemplate',
            WARNING,
            "The following Documents are still being imported so code need to "
            "be updated: " + module_still_used_message)

      if list_selection_name is not None:
        message = (
          "All components were successfully imported from filesystem to ZODB. "
          "Please note that imported {Document,Interfaces,Mixin,Tool Components} "
          "have not been validated automatically as imports must probably be "
          "adjusted before deleting them from the filesystem.")

        if still_used_list_dict:
          message = (
            message +
            " WARNING: Some migrated Documents have their filesystem Document "
            "still being imported so code need to be updated (see log file).")

        return self.Base_redirect('view',
                                  keep_items={'portal_status_message': message})

# Block acquisition on all _item_name_list properties by setting
# a default class value to None
for key in item_name_list:
  setattr(BusinessTemplate, key, None)
# Check naming convention of items.
assert item_set.issubset(globals()), item_set.difference(globals())
