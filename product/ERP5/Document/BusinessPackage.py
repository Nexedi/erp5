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

import fnmatch
import re
import gc
import os
import hashlib
import posixpath
import transaction
import imghdr
from copy import deepcopy
from collections import defaultdict
from cStringIO import StringIO
from lxml.etree import parse
from urllib import quote, unquote
from OFS import SimpleItem, XMLExportImport
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Products.ERP5Type.Globals import Persistent, PersistentMapping
from Products.ERP5Type.dynamic.portal_type_class import synchronizeDynamicModules
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.patches.ppml import importXML
customImporters={
    XMLExportImport.magic: importXML,
    }

import threading
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

    def _install(self, **kw):
      self._path_item.install(self)
      #self._object_property_item.install(self)

    security.declareProtected(Permissions.ManagePortal, 'install')
    install = _install

    security.declareProtected(Permissions.ManagePortal, 'preinstall')
    def preinstall(self, check_dependencies=1, **kw):
      return {}

    security.declareProtected(Permissions.ManagePortal, 'build')
    def build(self, no_action=False):
      """
      Should also export the objects from PathTemplateItem to their xml format
      """
      if not no_action:
        self.storePathData()
        self._path_item.build(self)
      pass
      #self._object_property_item.build(self)
      #self.setBuildingState('built')

    security.declareProtected(Permissions.ManagePortal, 'storePathData')
    def storePathData(self):
      self._path_item = PathTemplatePackageItem(self._getTemplatePathList())
      #self._object_property_item = \
      #    ObjectPropertyTemplatePackageItem(self._getTemplateObjectPropertyList())

    security.declareProtected(Permissions.ManagePortal, 'getTemplatePathList')
    def _getTemplateObjectPropertyList(self):
      result = self.getTemplateObjectPropertyList()
      if result is None:
        result = ()
      return tuple(result)

    security.declareProtected(Permissions.ManagePortal, 'getTemplatePathList')
    def _getTemplatePathList(self):
      result = tuple(self.getTemplatePathList())
      if result is None:
        result = ()
      return result

    security.declareProtected(Permissions.ManagePortal, 'export')
    def export(self, path=None, local=0, bpa=None):
      """
      Export the object
      XXX: Are we planning to use something like archive for saving the exported
      objects inside a Business Package
      """
      if not self.getBuildingState() == 'built':
        raise BusinessPackageException, 'Package not built properly'
      self._export(path, local, bpa)

    def _export(self, path=None, local=0, bpa=None):
      if bpa is None:
          if path is None:
            path = self.getTitle()
          bpa = BusinessPackageFolder(path, creation=1)

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
          bpa.addObject(str(value), name=id, path='bt', ext='')
        elif prop_type in ('lines', 'tokens'):
          bpa.addObject('\n'.join(value), name=id, path='bt', ext='')

      item_name_list = ['_path_item',]
      # Export each part
      for item_name in item_name_list:
        item = getattr(self, item_name, None)
        if item is not None:
          item.export(context=self, bpa=bpa)

      return bpa.finishCreation()

    security.declareProtected(Permissions.ManagePortal, 'importFile')
    def importFile(self, path):
      """
        Import all xml files in Business Template
      """
      bpa = BusinessPackageFolder(path, importing=1)
      bp_item = bp()
      bpa.importFiles(bp_item)
      prop_dict = {}
      for prop in self.propertyMap():
        pid = prop['id']
        if pid != 'id':
          prop_type = prop['type']
          value = bp_item.get(pid)
          if prop_type in ('text', 'string'):
            prop_dict[pid] = value or ''
          elif prop_type in ('int', 'boolean'):
            prop_dict[pid] = value or 0
          elif prop_type in ('lines', 'tokens'):
            prop_dict[pid[:-5]] = (value or '').splitlines()
      self._edit(**prop_dict)
      self.storePathData()

      item_name_list = ['_path_item',]
      for item_name in item_name_list:
        item_object = getattr(self, item_name, None)
        # this check is due to backwards compatability when there can be a
        # difference between install erp5_property_sheets (esp. BusinessTemplate
        # property sheet)
        if item_object is not None:
          item_object.importFile(bpa)

class BusinessPackageException(Exception):
  pass

class BusinessPackageArchive(object):
  """
    This is the base class for all Business Template archives
  """
  def __init__(self, path, **kw):
    self.path = path

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
      self._writeString(obj, path)
    else:
      if isinstance(obj, str):
        obj = StringIO(obj)
      else:
        obj.seek(0)
      write(obj, path)

  def finishCreation(self):
    pass

class BusinessPackageFolder(BusinessPackageArchive):
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
            #self.revision.hash(item_name + '/' + file_name, f.read())
            f.seek(0)
            item._importFile(file_name, f)
    finally:
      if hasattr(cache_database, 'db'):
        cache_database.db.close()
        del cache_database.db

class bp(dict):
  """Fake 'bp' item to read bp/* files through BusinessPackageArchive"""

  def _importFile(self, file_name, file):
    self[file_name] = file.read()

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

  def export(self, context, bpa, catalog_method_template_item = 0, **kw):
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
        bpa.addObject(obj, name=key, ext='.py')
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
            bpa.addObject(StringIO(data), key, path=path,
              ext='._xml' if extension == 'xml' else '.' + extension)
            break
          # since we get the obj from context we should
          # again remove useless properties
          #obj = self.removeProperties(obj, 1, keep_workflow_history = True)
          transaction.savepoint(optimistic=True)

        f = StringIO()
        XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
        bpa.addObject(f, key, path=path)

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

  def importFile(self, bta, **kw):
    bta.importFiles(self)

  def _importFile(self, file_name, file_obj, catalog_method_template_item = 0):
    obj_key, file_ext = os.path.splitext(file_name)
    # id() for installing several bt5 in the same transaction
    transactional_variable_obj_key = "%s-%s" % (id(self), obj_key)
    if file_ext != '.xml':
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

  def _restoreSeparatelyExportedProperty(self, obj, data):
    unicode_data, property_name = SEPARATELY_EXPORTED_PROPERTY_DICT[
      obj.__class__.__name__][1:]
    if unicode_data:
      data = data.decode(obj.output_encoding)
    try:
      setattr(obj, property_name, data)
    except BrokenModified:
      obj.__Broken_state__[property_name] = data
      obj._p_changed = 1

  def getConnection(self, obj):
    while True:
      connection = obj._p_jar
      if connection is not None:
        return connection
      obj = obj.aq_parent

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

class ObjectPropertyTemplatePackageItem(Implicit, Persistent):

  xml_tag = "object_property_list"

  def __init__(self, id_list, tool_id=None, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    self._hash = PersistentMapping()
    for id in id_list:
      if id is not None and id != '':
        self._archive[id] = None

  def build(self, context, **kw):
    p = context.getPortalObject()
    for key in self._archive:
      relative_url, property_name = key.split(' | ')
      property_value = p.unrestrictedTraverse(relative_url) \
                             .getProperty(property_name)
      self._objects.setdefault(relative_url, {})[property_name] = property_value
      self._hash[relative_url] = hashlib.sha1(self.generateXml(relative_url)).hexdigest()

  def generateXml(self, path):
    xml_data = '<%s>' % self.xml_tag
    relative_url = path
    xml_data += '\n  <object relative_url="%s">' % relative_url
    for property_name, property_value in self._objects[relative_url].iteritems():
      xml_data += '\n    <property name="%s">' % property_name.replace('_list', '')
      if property_name.endswith('_list'):
        for value in property_value:
          xml_data += '\n      <item>%s</item>' % value
      else:
        xml_data += '\n      <item>%s</item>' % property_value
      xml_data += '\n    </property>'
    xml_data += '\n  </object>'
    xml_data += '\n</%s>' % self.xml_tag
    return xml_data

  def export(self, context, bpa, **kw):
    path = self.__class__.__name__
    if self._objects.keys():
      xml_data = self.generateXml()
      bpa.addObject(xml_data, name=self.xml_tag, path=path)

  def _importFile(self, file_name, file):
    if not file_name.endswith('.xml'):
      LOG('Business Template', 0, 'Skipping file "%s"' % (file_name, ))
      return
    xml = parse(file)
    object_list = xml.findall('object')
    for obj in object_list:
      for obj_property in obj.findall('property'):
        item_list = []
        for item in obj_property.findall('item'):
          item_list.append(item.text)
        property_name = obj_property.get('name') + ('' if len(item_list) <= 1 else '_list')
        self._objects[obj.get('relative_url')] = {property_name: item_list}

  def preinstall(self, context, installed_item, **kw):
    modified_object_list = {}
    for relative_url in self._objects:
      new_object = self._objects[relative_url]
      try:
        old_object = installed_item._objects[relative_url]
      except KeyError:
        modified_object_list.update({relative_url : ['New', self.__class__.__name__[:-12]]})
      else:
        modified_object_list.update({relative_url : ['Modified', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, *args, **kw):
    portal = context.getPortalObject()
    for relative_url in self._objects:
      obj = portal.unrestrictedTraverse(relative_url)
      for property_name, property_value in self._objects[relative_url].iteritems():
        obj.setProperty(property_name, property_value)

  def uninstall(self, context, **kw):
    portal = context.getPortalObject()
    for relative_url in self._objects:
      obj = portal.unrestrictedTraverse(relative_url)
      for property_name in self._objects[relative_url]:
        obj.setProperty(property_name, None)

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
  import copy
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
      elif not final_data.has_key(path):
        final_data[path] = object_metadata

      # If the object is neither in conflicted_data already in final_data,
      # compare hash of the objects
      else:
        # Leave the metadata in final_data in case the hash matches,
        # else add it to conflicted_data and remove the older
        if final_data[path]['sha'] ==  object_metadata['sha']:
          continue
        else:
          conflicted_data[path] = [object_metadata]
          conflict_object_metadata = copy.copy(final_data[path])
          conflicted_data[path].append(conflict_object_metadata)
          del final_data[path]

  return final_data, conflicted_data

class InstallationTree(object):
  """
  Tree implemetation to manage install/update/remove between states.
  This is a very rough code to explain what can be achieved. In real case,
  this class should be a well defined ERP5 object and most possibly act as a
  portal tool, cause there should be one installation tree per site(agree ??)

  Data at every node:
  {'_path_item': PathTemplateItem, }

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
    self.children = []

  def addNewState(self, state):
    """
    In tree language, should act as set next node to the tree

    This should add package list after comparing the states of
    packages with the installed state. So even if we try to install multiple
    packages at a time, it should be counted as one state being implented on
    another installed state, i.e, the state of ERP5Site
    """
    self.children.append(state)

  def mapToERP5Site(self, context=None):
    """
    Create a new state by comparing all BP combined built and the ERP5Site,
    then calls setNewState to update the state
    While mapping we compare between installed_item of BT, if exisits as well
    as ZODB. The Installation Tree should be smart enough to take us nearest to
    the installed state. If any conflict whatsoever arise, it should raise it.
    """
    # Return if the context is None
    if context is None:
      return

    for path, metadata in self.data.items():
      obj = metadata['obj']
      path_list = path.split('/')
      container_path = path_list[:-1]
      object_id = path_list[-1]
      try:
        container = context.unrestrictedTraverse(container_path)
      except KeyError:
        # parent object can be set to nothing, in this case just go on
        container_url = '/'.join(container_path)
      old_obj = container._getOb(object_id, None)
      # install object
      obj = obj._getCopy(container)
      container._setObject(object_id, obj)
