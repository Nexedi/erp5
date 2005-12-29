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

from Globals import Persistent, PersistentMapping
from Acquisition import Implicit, aq_base
from AccessControl.Permission import Permission
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import readLocalPropertySheet, \
                                    writeLocalPropertySheet, \
                                    importLocalPropertySheet, \
                                    removeLocalPropertySheet
from Products.ERP5Type.Utils import readLocalExtension, writeLocalExtension, \
                                    removeLocalExtension
from Products.ERP5Type.Utils import readLocalTest, writeLocalTest, \
                                    removeLocalTest
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, \
                                    importLocalDocument, removeLocalDocument
from Products.ERP5Type.XMLObject import XMLObject
import fnmatch
import re, os, sys, string, tarfile
from Products.ERP5Type.Cache import clearCache
from DateTime import DateTime
from OFS.Traversable import NotFound
from OFS import XMLExportImport
from cStringIO import StringIO
from copy import deepcopy
from App.config import getConfiguration
import OFS.XMLExportImport
customImporters={
    XMLExportImport.magic: XMLExportImport.importXML,
    }

from zLOG import LOG
from OFS.ObjectManager import customImporters
from gzip import GzipFile
from xml.dom.minidom import parse
from Products.CMFCore.Expression import Expression
import tarfile
from urllib import pathname2url, url2pathname
from difflib import unified_diff


catalog_method_list = ('_is_catalog_list_method_archive',
                       '_is_uncatalog_method_archive',
                       '_is_clear_method_archive', '_is_filtered_archive')

catalog_method_filter_list = ('_filter_expression_archive', '_filter_expression_instance_archive',
                              '_filter_type_archive')


def removeAll(entry):
  '''
    Remove all files and directories under 'entry'.
    XXX: This is defined here, because os.removedirs() is buggy.
  '''
  try:
    if os.path.isdir(entry) and not os.path.islink(entry):
      pwd = os.getcwd()
      os.chmod(entry, 0755)
      os.chdir(entry)
      for e in os.listdir(os.curdir):
        removeAll(e)
      os.chdir(pwd)
      os.rmdir(entry)
    else:
      if not os.path.islink(entry):
        os.chmod(entry, 0644)
      os.remove(entry)
  except OSError:
    pass

class BusinessTemplateArchive:
  """
    This is the base class for all Business Template archives
  """

  def __init__(self, creation=0, importing=0, file=None, path=None, **kw):
    if creation:
      self._initCreation(path=path, **kw)
    elif importing:
      self._initImport(file=file, path=path, **kw)

  def addFolder(self, **kw):
    pass

  def addObject(self, *kw):
    pass

  def finishCreation(self, **kw):
    pass

class BusinessTemplateFolder(BusinessTemplateArchive):
  """
    Class archiving businnes template into a folder tree
  """
  def _initCreation(self, path):
    self.path = path
    try:
      os.makedirs(self.path)
    except OSError:
      # folder already exists, remove it
      removeAll(self.path)
      os.makedirs(self.path)

  def addFolder(self, name=''):
     if name !='':
      path = os.path.join(self.path, name)
      if not os.path.exists(path):
        os.makedirs(path)
      return path

  def addObject(self, obj, name, path=None, ext='.xml'):
    name = pathname2url(name)
    if path is None:
      object_path = os.path.join(self.path, name)
    else:
      if '%' not in path:
        path = pathname2url(path)
      object_path = os.path.join(path, name)
    f = open(object_path+ext, 'wt')
    f.write(str(obj))
    f.close()

  def _initImport(self, file=None, path=None, **kw):
    self.file_list = file
    # to make id consistent, must remove a part of path while importing
    self.root_path_len = len(string.split(path, os.sep)) + 1

  def importFiles(self, klass, **kw):
    """
      Import file from a local folder
    """
    class_name = klass.__class__.__name__
    for file_path in self.file_list:
      if class_name in file_path.split(os.sep):
        if os.path.isfile(file_path):
          file = open(file_path, 'r')
          # get object id
          folders = file_path.split(os.sep)
          file_name = string.join(folders[self.root_path_len:], os.sep)
          if '%' in file_name:
            file_name = url2pathname(file_name)
          klass._importFile(file_name, file)
          # close file
          file.close()

class BusinessTemplateTarball(BusinessTemplateArchive):
  """
    Class archiving businnes template into a tarball file
  """

  def _initCreation(self, path):
    # make tmp dir, must use stringIO instead
    self.path = path
    try:
      os.makedirs(self.path)
    except OSError:
      # folder already exists, remove it
      removeAll(self.path)
      os.makedirs(self.path)
    # init tarfile obj
    self.fobj = StringIO()
    self.tar = tarfile.open('', 'w:gz', self.fobj)

  def addFolder(self, name=''):
    if not os.path.exists(name):
      os.makedirs(name)

  def addObject(self, obj, name, path=None, ext='.xml'):
    name = pathname2url(name)
    if path is None:
      object_path = os.path.join(self.path, name)
    else:
      if '%' not in path:
        path = pathname2url(path)
      object_path = os.path.join(path, name)
    f = open(object_path+ext, 'wt')
    f.write(str(obj))
    f.close()

  def finishCreation(self):
    self.tar.add(self.path)
    self.tar.close()
    removeAll(self.path)
    return self.fobj

  def _initImport(self, file=None, **kw):
    self.f = file

  def importFiles(self, klass, **kw):
    """
      Import all file from the archive to the site
    """
    class_name = klass.__class__.__name__
    self.f.seek(0)
    data = GzipFile(fileobj=self.f).read()
    io = StringIO(data)
    tar = tarfile.TarFile(fileobj=io)
    for info in tar.getmembers():
      if 'CVS' in info.name.split('/'):
        continue
      if class_name in info.name:
        if info.isreg():
          file = tar.extractfile(info)
          folders = string.split(info.name, os.sep)
          file_name = (os.sep).join(folders[2:])
          if '%' in file_name:
            file_name = url2pathname(file_name)
          klass._importFile(file_name, file)
          file.close()
    tar.close()
    io.close()

class TemplateConditionError(Exception): pass

class TemplateConflictError(Exception): pass

class BaseTemplateItem(Implicit, Persistent):
  """
    This class is the base class for all template items.
  """

  def __init__(self, id_list, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    for id in id_list:
      if not id: continue
      self._archive[id] = None

  def build(self, context, **kw):
    pass

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      new_keys = self._objects.keys()
      for path in new_keys:        
        if installed_bt._objects.has_key(path):
          # compare object to see it there is changes
          new_obj_xml = self.generateXml(path=path)
          old_obj_xml = installed_bt.generateXml(path=path)
          if new_obj_xml != old_obj_xml:
            modified_object_list.update({path : ['Modified', self.__class__.__name__[:-12]]})
        else: # new object
          modified_object_list.update({path : ['New', self.__class__.__name__[:-12]]})
      # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    pass

  def uninstall(self, context, **kw):
    pass

  def remove(self, context, **kw):
    remove_dict = kw.get('remove_object_dict', {})
    keys = self._objects.keys()
    keys.sort()
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
        

  def trash(self, context, new_item, **kw):
    # trash is quite similar to uninstall.
    return self.uninstall(context, new_item=new_item, trash=1, **kw)

  def export(self, context, bta, **kw):
    pass

  def importFile(self, bta, **kw):
    bta.importFiles(klass=self)

  def removeProperties(self, obj):
    """
    Remove unneeded properties for export
    """  
    if hasattr(obj, '__ac_local_roles__'):
      # remove local roles
      obj.__ac_local_roles__ = None
    if hasattr(obj, '_owner'):
      obj._owner = None
    if hasattr(aq_base(obj), 'uid'):
      obj.uid = None
    return obj      
    
class ObjectTemplateItem(BaseTemplateItem):
  """
    This class is used for generic objects and as a subclass.
  """

  def __init__(self, id_list, tool_id=None, **kw):
    BaseTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    if tool_id is not None:
      id_list = self._archive.keys()
      self._archive.clear()
      for id in id_list:
        self._archive["%s/%s" % (tool_id, id)] = None

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    for key in self._objects.keys():
      obj = self._objects[key]
      # create folder and subfolders
      folders, id = os.path.split(key)
      encode_folders = []
      for folder in folders.split('/'):
        if '%' not in folder:
          encode_folders.append(pathname2url(folder))
        else:
          encode_folders.append(folder)
      path = os.path.join(root_path, (os.sep).join(encode_folders))
      bta.addFolder(name=path)
      # export object in xml
      f=StringIO()
      XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
      bta.addObject(obj=f.getvalue(), name=id, path=path)

  def build_sub_objects(self, context, id_list, url, **kw):
    p = context.getPortalObject()
    sub_list = {}
    for id in id_list:
      relative_url = '/'.join([url,id])
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      obj = self.removeProperties(obj)
      id_list = obj.objectIds()
      if hasattr(aq_base(obj), 'groups'):
        # we must keep groups because it's ereased when we delete subobjects
        groups = deepcopy(obj.groups)
      if len(id_list) > 0:
        self.build_sub_objects(context, id_list, relative_url)
        obj.manage_delObjects(list(id_list))
      if hasattr(aq_base(obj), 'groups'):
        obj.groups = groups
      self._objects[relative_url] = obj
      obj.wl_clearLocks()
    return sub_list

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      obj = self.removeProperties(obj)
      id_list = obj.objectIds()
      if hasattr(aq_base(obj), 'groups'):
        # we must keep groups because it's ereased when we delete subobjects
        groups = deepcopy(obj.groups)
      if len(id_list) > 0:
        self.build_sub_objects(context, id_list, relative_url)
        obj.manage_delObjects(list(id_list))
      if hasattr(aq_base(obj), 'groups'):
        obj.groups = groups
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def _importFile(self, file_name, file):
    # import xml file
    obj = self
    connection = None
    while connection is None:
      obj=obj.aq_parent
      connection=obj._p_jar
    obj = connection.importFile(file, customImporters=customImporters)
    self._objects[file_name[:-4]] = obj

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      portal = context.getPortalObject()
      new_keys = self._objects.keys()
      for path in new_keys:
        if installed_bt._objects.has_key(path):
          # compare object to see it there is changes
          new_object = self._objects[path]
          old_object = installed_bt._objects[path]
          new_io = StringIO()
          old_io = StringIO()
          OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, new_io)
          OFS.XMLExportImport.exportXML(old_object._p_jar, old_object._p_oid, old_io)
          new_obj_xml = new_io.getvalue()
          old_obj_xml = old_io.getvalue()
          new_io.close()
          old_io.close()
          if new_obj_xml != old_obj_xml:
            modified_object_list.update({path : ['Modified', self.__class__.__name__[:-12]]})
        else: # new object
          modified_object_list.update({path : ['New', self.__class__.__name__[:-12]]})
      # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def _backupObject(self, action, trashbin, container_path, object_id):
    """
      Backup the object in portal trash if necessery and return its subobjects
    """
    subobjects_dict = {}
    if trashbin is None: #m ust return subobjects
      object_path = container_path + [object_id]
      obj = self.unrestrictedTraverse(object_path)
      for subobject_id in list(obj.objectIds()):
        subobject_path = object_path + [subobject_id]
        subobject = self.unrestrictedTraverse(subobject_path)
        subobject_copy = subobject._p_jar.exportFile(subobject._p_oid)
        subobjects_dict[subobject_id] = subobject_copy      
      return subobjects_dict
    # XXX btsave is for backward compatibility
    if action == 'backup' or action == 'btsave':
      subobjects_dict = self.portal_trash.backupObject(trashbin, container_path, object_id, save=1)
    elif action == 'install':
      subobjects_dict = self.portal_trash.backupObject(trashbin, container_path, object_id, save=0)
    return subobjects_dict
    
  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      groups = {}
      portal = context.getPortalObject()
      # sort to add objects before their subobjects
      keys = self._objects.keys()
      keys.sort()
      for path in keys:
        if update_dict.has_key(path) or force:
          # get action for the oject
          if not force:
            action = update_dict[path]
            if action == 'nothing':
              continue
          else:
            action = 'backup'
          # get subobjects in path
          container_path = path.split('/')[:-1]
          object_id = path.split('/')[-1]
          try:
            container = portal.unrestrictedTraverse(container_path)
          except KeyError:
            # parent object can be set to nothing, in this case just go on
            container_url = '/'.join(container_path)            
            if update_dict.has_key(container_url):
              if update_dict[container_url] == 'nothing':
                continue
            raise
          container_ids = container.objectIds()
          subobjects_dict = {}
          # Object already exists
          if object_id in container_ids:
            subobjects_dict = self._backupObject(action, trashbin, container_path, object_id)
            container.manage_delObjects([object_id])
          # install object
          obj = self._objects[path]
          if hasattr(aq_base(obj), 'groups'):
            # we must keep original order groups because they change when we add subobjects
            groups[path] = deepcopy(obj.groups)
          # copy the object
          obj = obj._getCopy(container)
          container._setObject(object_id, obj)
          obj = container._getOb(object_id)
          obj.manage_afterClone(obj)
          obj.wl_clearLocks()
          # import sub objects if there is
          if len(subobjects_dict) > 0:
            # get a jar
            connection = obj._p_jar
            o = obj
            while connection is None:
              o = o.aq_parent
              connection = o._p_jar
            # import subobjects
            for subobject_id in subobjects_dict.keys():
              subobject_data = subobjects_dict[subobject_id]
              subobject_data.seek(0)
              subobject = connection.importFile(subobject_data)
              if subobject_id not in obj.objectIds():
                obj._setObject(subobject_id, subobject)
              
          if obj.meta_type in ('Z SQL Method',):
            # It is necessary to make sure that the sql connection
            # in this method is valid.
            sql_connection_list = portal.objectIds(spec=('Z MySQL Database Connection',))
            if obj.connection_id not in sql_connection_list:
              obj.connection_id = sql_connection_list[0]
      # now put original order group
      for path in groups.keys():
        obj = portal.unrestrictedTraverse(path)
        obj.groups = groups[path]
    else:
      # for old business template format
      BaseTemplateItem.install(self, context, trashbin, **kw)
      portal = context.getPortalObject()
      for relative_url in self._archive.keys():
        obj = self._archive[relative_url]
        container_path = relative_url.split('/')[0:-1]
        object_id = relative_url.split('/')[-1]
        container = portal.unrestrictedTraverse(container_path)
        container_ids = container.objectIds()
        if object_id in container_ids:    # Object already exists          
          self._backupObject('backup', trashbin, container_path, object_id)
          container.manage_delObjects([object_id])
        # Set a hard link
        obj = obj._getCopy(container)
        container._setObject(object_id, obj)
        obj = container._getOb(object_id)
        obj.manage_afterClone(obj)
        obj.wl_clearLocks()
        if obj.meta_type in ('Z SQL Method',):
          # It is necessary to make sure that the sql connection
          # in this method is valid.
          sql_connection_list = portal.objectIds(
                                   spec=('Z MySQL Database Connection',))
          if obj.connection_id not in sql_connection_list:
            obj.connection_id = sql_connection_list[0]

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
        container = portal.unrestrictedTraverse(container_path)
        if trash and trashbin is not None:
          self.portal_trash.backupObject(trashbin, container_path, object_id, save=1, keep_subobjects=1)
        container.manage_delObjects([object_id])
      except (NotFound, KeyError):
        # object is already backup and/or removed
        pass
    BaseTemplateItem.uninstall(self, context, **kw)

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
    object_keys.sort()
    object_keys.reverse()
    for path in object_keys:
      for relative_url in self._resolvePath(p, [], path.split('/')):
        try:        
          container_path = relative_url.split('/')[0:-1]
          object_id = relative_url.split('/')[-1]
          container = portal.unrestrictedTraverse(container_path)
          if trash and trashbin is not None:
            self.portal_trash.backupObject(trashbin, container_path, object_id, save=1, keep_subobjects=1)
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
      obj = folder._getOb(id)
      return self._resolvePath(obj, relative_url_list + [id], id_list[1:])
    path_list = []
    for object_id in fnmatch.filter(folder.objectIds(), id):
      path_list.extend(self._resolvePath(folder._getOb(object_id), relative_url_list + [object_id], id_list[1:]))
    return path_list

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    keys = self._path_archive.keys()
    keys.sort()    
    for path in keys:
      include_subobjects = 0
      if '**' in path:
        include_subobjects = 1
      for relative_url in self._resolvePath(p, [], path.split('/')):
        obj = p.unrestrictedTraverse(relative_url)
        obj = obj._getCopy(context)
        id_list = obj.objectIds()
        obj = self.removeProperties(obj)
        if hasattr(aq_base(obj), 'groups'):
          # we must keep groups because it's ereased when we delete subobjects
          groups = deepcopy(obj.groups)
        if len(id_list) > 0:
          if include_subobjects:
            self.build_sub_objects(context, id_list, relative_url)
          obj.manage_delObjects(list(id_list))
        if hasattr(aq_base(obj), 'groups'):
          obj.groups = groups
        self._objects[relative_url] = obj
        obj.wl_clearLocks()
      
class CategoryTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_categories', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def build_sub_objects(self, context, id_list, url, **kw):
    p = context.getPortalObject()
    for id in id_list:
      relative_url = '/'.join([url,id])
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      obj = self.removeProperties(obj)
      id_list = obj.objectIds()
      if len(id_list) > 0:
        self.build_sub_objects(context, id_list, relative_url)
        obj.manage_delObjects(list(id_list))
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      obj = self.removeProperties(obj)
      include_sub_categories = obj.__of__(context).getProperty('business_template_include_sub_categories', 0)
      id_list = obj.objectIds()
      if len(id_list) > 0 and include_sub_categories:
        self.build_sub_objects(context, id_list, relative_url)
        obj.manage_delObjects(list(id_list))
      else:
        obj.manage_delObjects(list(id_list))
      self._objects[relative_url] = obj
      obj.wl_clearLocks()
      
  def install(self, context, trashbin, light_install = 0, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      if light_install == 0:
        ObjectTemplateItem.install(self, context, trashbin, **kw)
      else:
        portal = context.getPortalObject()
        category_tool = portal.portal_categories
        tool_id = self.tool_id
        keys = self._objects.keys()
        keys.sort()
        for path in keys:
          if update_dict.has_key(path) or force:
            if not force:
              action = update_dict[path]
              if action == 'nothing':
                continue
            else:
              action = 'backup'
            # Wrap the object by an aquisition wrapper for _aq_dynamic.
            obj = self._objects[path]
            obj = obj.__of__(category_tool)
            container_path = path.split('/')[:-1]
            category_id = path.split('/')[-1]
            try:
              container = category_tool.unrestrictedTraverse(container_path)
            except KeyError:
              # parent object can be set to nothing, in this case just go on
              container_url = '/'.join(container_path)            
              if update_dict.has_key(container_url):
                if update_dict[container_url] == 'nothing':
                  continue
              raise
            container_ids = container.objectIds() 
            # Object already exists
            if category_id in container_ids:
              subobjects_dict = self._backupObject(action, trashbin, container_path, category_id)
              container.manage_delObjects([category_id])
            category = container.newContent(portal_type=obj.getPortalType(), id=category_id)
            for property in obj.propertyIds():
              if property not in ('id', 'uid'):
                category.setProperty(property, obj.getProperty(property, evaluate=0))
            # import sub objects if there is
            if len(subobjects_dict) > 0:
              # get a jar
              connection = obj._p_jar
              o = category
              while connection is None:
                o = o.aq_parent
                connection = o._p_jar
              # import subobjects
              for subobject_id in subobjects_dict.keys():
                subobject_data = subobjects_dict[subobject_id]
                subobject_data.seek(0)
                subobject = connection.importFile(subobject_data)
                if subobject_id not in category.objectIds():
                  category._setObject(subobject_id, subobject)
    else:
      BaseTemplateItem.install(self, context, trashbin, **kw)
      portal = context.getPortalObject()
      category_tool = portal.portal_categories
      tool_id = self.tool_id
      if light_install==0:
        ObjectTemplateItem.install(self, context, trashbin, **kw)
      else:
        for relative_url in self._archive.keys():
          obj = self._archive[relative_url]
          # Wrap the object by an aquisition wrapper for _aq_dynamic.
          obj = obj.__of__(category_tool)
          container_path = relative_url.split('/')[0:-1]
          category_id = relative_url.split('/')[-1]
          container = category_tool.unrestrictedTraverse(container_path)
          container_ids = container.objectIds()
          if category_id in container_ids:    # Object already exists
            # XXX call backup here
            subobjects_dict = self._backupObject('backup', trashbin, container_path, category_id)
            container.manage_delObjects([category_id])
          category = container.newContent(portal_type=obj.getPortalType(), id=category_id)
          for property in obj.propertyIds():
            if property not in ('id', 'uid'):
              category.setProperty(property, obj.getProperty(property, evaluate=0))
          # import sub objects if there is
          if len(subobjects_dict) > 0:
            # get a jar
            connection = obj._p_jar
            o = category
            while connection is None:
              o = o.aq_parent
              connection = o._p_jar
            # import subobjects
            for subobject_id in subobjects_dict.keys():
              subobject_data = subobjects_dict[subobject_id]
              subobject_data.seek(0)
              subobject = connection.importFile(subobject_data)
              if subobject_id not in category.objectIds():
                category._setObject(subobject_id, subobject)


class SkinTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_skins', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    # It is necessary to make sure that the sql connections in Z SQL Methods are valid.
    sql_connection_list = p.objectIds(spec=('Z MySQL Database Connection',))
    for relative_url in self._archive.keys():
      folder = p.unrestrictedTraverse(relative_url)
      for obj in folder.objectValues(spec=('Z SQL Method',)):
        if obj.connection_id not in sql_connection_list:
          obj.connection_id = sql_connection_list[0]
    # Add new folders into skin paths.
    ps = p.portal_skins
    for skin_name, selection in ps.getSkinPaths():
      new_selection = []
      selection = selection.split(',')
      for relative_url in self._archive.keys():
        if context.getTemplateFormatVersion() == 1:
          if update_dict.has_key(relative_url) or force:
            if not force:
              if update_dict[relative_url] == 'nothing':
                continue
          obj = self._objects[relative_url]
        else:
          obj = self._archive[relative_url]
        skin_id = relative_url.split('/')[-1]
        selection_list = obj.getProperty('business_template_registered_skin_selections', None)
        if selection_list is None or skin_name in selection_list:
          if skin_id not in selection:
            new_selection.append(skin_id)
      new_selection.extend(selection)
      # sort the layer according to skin priorities
      new_selection.sort(lambda a, b : cmp(
        b in ps.objectIds() and ps[b].getProperty(
            'business_template_skin_layer_priority', 0) or 0,
        a in ps.objectIds() and ps[a].getProperty(
            'business_template_skin_layer_priority', 0) or 0))
      ps.manage_skinLayers(skinpath = tuple(new_selection), skinname = skin_name, add_skin = 1)
    # Make sure that skin data is up-to-date (see CMFCore/Skinnable.py).
    p.changeSkin(None)

  def uninstall(self, context, **kw):
    # Remove folders from skin paths.
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()    
    ps = context.portal_skins
    skin_id_list = [relative_url.split('/')[-1] for relative_url in object_keys]
    for skin_name, selection in ps.getSkinPaths():
      new_selection = []
      selection = selection.split(',')
      for skin_id in selection:
        if skin_id not in skin_id_list:
          new_selection.append(skin_id)
      ps.manage_skinLayers(skinpath = tuple(new_selection), skinname = skin_name, add_skin = 1)
    # Make sure that skin data is up-to-date (see CMFCore/Skinnable.py).
    context.getPortalObject().changeSkin(None)
    ObjectTemplateItem.uninstall(self, context, **kw)


class WorkflowTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_workflow', **kw):
    return ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      portal = context.getPortalObject()
      new_keys = self._objects.keys()
      for path in new_keys:
        if len(path.split('/')) == 2:
          if installed_bt._objects.has_key(path):          
            # compare object to see it there is changes
            new_object = self._objects[path]
            old_object = installed_bt._objects[path]
            new_io = StringIO()
            old_io = StringIO()
            OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, new_io)
            OFS.XMLExportImport.exportXML(old_object._p_jar, old_object._p_oid, old_io)
            new_obj_xml = new_io.getvalue()
            old_obj_xml = old_io.getvalue()
            new_io.close()
            old_io.close()
            if new_obj_xml != old_obj_xml:
              modified_object_list.update({path : ['Modified', 'Workflow']})
          else: # new object
            modified_object_list.update({path : ['New', 'Workflow']})
      # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    if context.getTemplateFormatVersion() == 1:
      portal = context.getPortalObject()
      # sort to add objects before their subobjects
      keys = self._objects.keys()
      keys.sort()
      update_dict = kw.get('object_to_update')
      force = kw.get('force')
      for path in keys:
        wf_path = '/'.join(path.split('/')[:2])
        if wf_path in update_dict or force:
          if not force:
            action = update_dict[wf_path]
            if action == 'nothing':
              continue
          else:
            action = 'backup'
          container_path = path.split('/')[:-1]
          object_id = path.split('/')[-1]
          try:
            container = portal.unrestrictedTraverse(container_path)
          except KeyError:
            # parent object can be set to nothing, in this case just go on
            container_url = '/'.join(container_path)            
            if update_dict.has_key(container_url):
              if update_dict[container_url] == 'nothing':
                continue
            raise
          container_ids = container.objectIds()
          if object_id in container_ids:    # Object already exists
            self._backupObject(action, trashbin, container_path, object_id)
            container.manage_delObjects([object_id])
          obj = self._objects[path]
          obj = obj._getCopy(container)
          container._setObject(object_id, obj)
          obj = container._getOb(object_id)
          obj.manage_afterClone(obj)
          obj.wl_clearLocks()
    else:
      ObjectTemplateItem.install(self, context, trashbin, **kw)

  

class PortalTypeTemplateItem(ObjectTemplateItem):

  workflow_chain = None

  def _getChainByType(self, context):
    """
    This is used in order to construct the full list
    of mapping between type and list of workflow associated
    This is only useful in order to use
    portal_workflow.manage_changeWorkflows
    """
    pw = context.portal_workflow
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

  def __init__(self, id_list, tool_id='portal_types', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    self._workflow_chain_archive = PersistentMapping()

  def build(self, context, **kw):
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      id_list = obj.objectIds()
      # remove optional actions and properties
      optional_action_list = []
      for index,ai in enumerate(obj.listActions()):
        if ai.getOption():
          optional_action_list.append(index)
      if len(optional_action_list) > 0:
        obj.deleteActions(selections=optional_action_list)
      obj = self.removeProperties(obj)
      # remove some properties
      if hasattr(obj, 'allowed_content_types'):
        setattr(obj, 'allowed_content_types', ())
      if hasattr(obj, 'hidden_content_type_list'):
        setattr(obj, 'hidden_content_type_list', ())
      if hasattr(obj, 'property_sheet_list'):
        setattr(obj, 'property_sheet_list', ())
      if hasattr(obj, 'base_category_list'):
        setattr(obj, 'base_category_list', ())
      self._objects[relative_url] = obj
      obj.wl_clearLocks()
    # also export workflow chain
    (default_chain, chain_dict) = self._getChainByType(context)
    for obj in self._objects.values():
      portal_type = obj.id
      self._workflow_chain_archive[portal_type] = chain_dict['chain_%s' % portal_type]

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    # export portal type object
    ObjectTemplateItem.export(self, context, bta, **kw)
    # export workflow chain
    xml_data = '<workflow_chain>'
    keys = self._workflow_chain_archive.keys()
    keys.sort()
    for key in keys:
      xml_data += os.linesep+' <chain>'
      xml_data += os.linesep+'  <type>%s</type>' %(key,)
      xml_data += os.linesep+'  <workflow>%s</workflow>' %(self._workflow_chain_archive[key],)
      xml_data += os.linesep+' </chain>'
    xml_data += os.linesep+'</workflow_chain>'
    bta.addObject(obj=xml_data, name='workflow_chain_type',  path=root_path)

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # We now need to setup the list of workflows corresponding to
    # each portal type
    (default_chain, chain_dict) = self._getChainByType(context)
    # Set the default chain to the empty string is probably the
    # best solution, by default it is 'default_workflow', wich is
    # not very usefull
    default_chain = ''
    if context.getTemplateFormatVersion() == 1:
      object_list = self._objects
    else:
      object_list = self._archive
    for path in object_list.keys():
      if update_dict.has_key(path) or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue          
        obj = object_list[path]
        portal_type = obj.id
        chain_dict['chain_%s' % portal_type] = \
                              self._workflow_chain_archive[portal_type]
        context.portal_workflow.manage_changeWorkflows(default_chain,
                                                       props=chain_dict)

  def _importFile(self, file_name, file):
    if 'workflow_chain_type.xml' in file_name:
      # import workflow chain for portal_type
      dict = {}
      xml = parse(file)
      chain_list = xml.getElementsByTagName('chain')
      for chain in chain_list:
        ptype = chain.getElementsByTagName('type')[0].childNodes[0].data
        workflow_list = chain.getElementsByTagName('workflow')[0].childNodes
        if len(workflow_list) == 0:
          workflow = ''
        else:
          workflow = workflow_list[0].data
        dict[str(ptype)] = str(workflow)
      self._workflow_chain_archive = dict
    else:
      ObjectTemplateItem._importFile(self, file_name, file)


class PortalTypeAllowedContentTypeTemplateItem(BaseTemplateItem):

  xml_tag = 'allowed_content_type_list'
  class_property = 'allowed_content_types'

  def build(self, context, **kw):
    for key in self._archive.keys():
      portal_type, allowed_type = key.split(' | ')
      if self._objects.has_key(portal_type):
        allowed_list = self._objects[portal_type]
        allowed_list.append(allowed_type)
        self._objects[portal_type] = allowed_list
      else:
        self._objects[portal_type] = [allowed_type]

  def generateXml(self, path=None):
    if path is None:
      dict = self._objects
    xml_data = '<%s>' %(self.xml_tag,)
    keys = dict.keys()
    keys.sort()
    for key in keys:
      allowed_list = dict[key]
      xml_data += os.linesep+' <portal_type id="%s">' %(key,)
      for allowed_item in allowed_list:
        xml_data += os.linesep+'  <item>%s</item>' %(allowed_item,)
      xml_data += os.linesep+' </portal_type>'
    xml_data += os.linesep+'</%s>' %(self.xml_tag,)
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    path = self.__class__.__name__+os.sep+self.class_property
    xml_data = self.generateXml(path=None)
    bta.addObject(obj=xml_data, name=path, path=None)

  def _importFile(self, file_name, file):
    path, name = os.path.split(file_name)
    id = string.split(name, '.')[0]
    xml = parse(file)
    portal_type_list = xml.getElementsByTagName('portal_type')
    for portal_type in portal_type_list:
      id = portal_type.getAttribute('id')
      item_type_list = []
      item_list = portal_type.getElementsByTagName('item')
      for item in item_list:
        item_type_list.append(str(item.childNodes[0].data))
      self._objects[self.class_property+'/'+id] = item_type_list

  def install(self, context, trashbin, **kw):
    p = context.getPortalObject()
    pt = p.unrestrictedTraverse('portal_types')
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    for key in self._objects.keys():
      if update_dict.has_key(key) or force:
        if not force:
          action = update_dict[key]
          if action == 'nothing':
            continue
        try:
          portal_id = key.split('/')[-1]
          portal_type = pt._getOb(portal_id)
        except KeyError:
          LOG("portal types not found : ", 100, portal_id)
          continue
        property_list = self._objects[key]
        object_property_list = getattr(portal_type, self.class_property, ())
        if len(object_property_list) > 0:
          # merge differences between portal types properties
          # only add new, do not remove
          for id in object_property_list:
            if id not in property_list:              
              property_list.append(id)        
        setattr(portal_type, self.class_property, list(property_list))

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path', None)
    pt = p.unrestrictedTraverse('portal_types')
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._objects.keys()
    for key in object_keys:
      try:
        portal_id = key.split('/')[-1]
        portal_type = pt._getOb(portal_id)
      except KeyError:
        LOG("portal types not found : ", 100, portal_id)
        continue
      property_list = self._objects[key]
      original_property_list = getattr(portal_type, self.class_property, ())
      for id in propert_list:
        if id in original_propert_list:
          original_propert_list.remove(id)        
      setattr(portal_type, self.class_property, list(original_property_list))
    
class PortalTypeHiddenContentTypeTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  xml_tag = 'hidden_content_type_list'
  class_property = 'hidden_content_type_list'

class PortalTypePropertySheetTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  xml_tag = 'property_sheet_list'
  class_property = 'property_sheet_list'

class PortalTypeBaseCategoryTemplateItem(PortalTypeAllowedContentTypeTemplateItem):

  xml_tag = 'base_category_list'
  class_property = 'base_category_list'

class CatalogMethodTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, tool_id='portal_catalog', **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id=tool_id, **kw)
    self._is_catalog_list_method_archive = PersistentMapping()
    self._is_uncatalog_method_archive = PersistentMapping()
    self._is_clear_method_archive = PersistentMapping()
    self._is_filtered_archive = PersistentMapping()
    self._filter_expression_archive = PersistentMapping()
    self._filter_expression_instance_archive = PersistentMapping()
    self._filter_type_archive = PersistentMapping()

  def build(self, context, **kw):
    ObjectTemplateItem.build(self, context, **kw)
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate build', 0, 'catalog not found')
      return
    for obj in self._objects.values():
      method_id = obj.id
      self._is_catalog_list_method_archive[method_id] = method_id in catalog.sql_catalog_object_list
      self._is_uncatalog_method_archive[method_id] = method_id in catalog.sql_uncatalog_object
      self._is_clear_method_archive[method_id] = method_id in catalog.sql_clear_catalog
      self._is_filtered_archive[method_id] = 0
      if catalog.filter_dict.has_key(method_id):
        self._is_filtered_archive[method_id] = catalog.filter_dict[method_id]['filtered']
        self._filter_expression_archive[method_id] = catalog.filter_dict[method_id]['expression']
        self._filter_expression_instance_archive[method_id] = catalog.filter_dict[method_id]['expression_instance']
        self._filter_type_archive[method_id] = catalog.filter_dict[method_id]['type']

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    for key in self._objects.keys():
      obj = self._objects[key]
      # create folder and subfolders
      folders, id = os.path.split(key)
      path = os.path.join(root_path, folders)
      bta.addFolder(name=path)
      # export object in xml
      f=StringIO()
      XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
      bta.addObject(obj=f.getvalue(), name=id, path=path)
      # add all datas specific to catalog inside one file
      catalog = context.portal_catalog.getSQLCatalog()
      method_id = obj.id
      object_path = os.path.join(path, method_id+'.catalog_keys.xml')

      f = open(object_path, 'wt')
      xml_data = '<catalog_method>'
      for method in catalog_method_list:
        value = getattr(self, method, 0)[method_id]
        xml_data += os.linesep+' <item key="%s" type="int">' %(method,)
        xml_data += os.linesep+'  <value>%s</value>' %(str(int(value)))
        xml_data += os.linesep+' </item>'
      if catalog.filter_dict.has_key(method_id):
        for method in catalog_method_filter_list:
          value = getattr(self, method, '')[method_id]
          if method == '_filter_expression_instance_archive':
            pass
          else:
            if type(value) in (type(''), type(u'')):
              xml_data += os.linesep+' <item key="%s" type="str">' %(method,)
              xml_data += os.linesep+'  <value>%s</value>' %(str(value))
              xml_data += os.linesep+' </item>'
            elif type(value) in (type(()), type([])):
              xml_data += os.linesep+' <item key="%s" type="tuple">'%(method)
              for item in value:
                xml_data += os.linesep+'  <value>%s</value>' %(str(item))
              xml_data += os.linesep+' </item>'
      xml_data += os.linesep+'</catalog_method>'
      f.write(str(xml_data))
      f.close()

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
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
    new_bt_format = context.getTemplateFormatVersion()

    if force: # get all objects
      if new_bt_format:
        values = self._objects.values()
      else:
        values = self._archive.values()
    else: # get only selected object
      if new_bt_format == 1:
        keys = self._objects.keys()
      else:
        keys = self._archive.keys()
      for key in keys:
        if update_dict.has_key(key) or force:
          if not force:
            action = update_dict[key]
            if action == 'nothing':
              continue          
          if new_bt_format:
            values.append(self._objects[key])
          else:
            values.append(self._archive[key])
          
    for obj in values:
      method_id = obj.id

      is_catalog_list_method = int(self._is_catalog_list_method_archive[method_id])
      is_uncatalog_method = int(self._is_uncatalog_method_archive[method_id])
      is_clear_method = int(self._is_clear_method_archive[method_id])
      is_filtered = int(self._is_filtered_archive[method_id])

      if is_catalog_list_method and method_id not in sql_catalog_object_list:
        sql_catalog_object_list.append(method_id)
      elif not is_catalog_list_method and method_id in sql_catalog_object_list:
        sql_catalog_object_list.remove(method_id)

      if is_uncatalog_method and method_id not in sql_uncatalog_object:
        sql_uncatalog_object.append(method_id)
      elif not is_uncatalog_method and method_id in sql_uncatalog_object:
        sql_uncatalog_object.remove(method_id)

      if is_clear_method and method_id not in sql_clear_catalog:
        sql_clear_catalog.append(method_id)
      elif not is_clear_method and method_id in sql_clear_catalog:
        sql_clear_catalog.remove(method_id)

      if is_filtered:
        expression = self._filter_expression_archive[method_id]
        if context.getTemplateFormatVersion() == 1:
          expr_instance = Expression(expression)
        else:
          expr_instance = self._filter_expression_instance_archive[method_id]
        filter_type = self._filter_type_archive[method_id]
        catalog.filter_dict[method_id] = PersistentMapping()
        catalog.filter_dict[method_id]['filtered'] = 1
        catalog.filter_dict[method_id]['expression'] = expression
        catalog.filter_dict[method_id]['expression_instance'] = expr_instance
        catalog.filter_dict[method_id]['type'] = filter_type
      elif method_id in catalog.filter_dict.keys():
        catalog.filter_dict[method_id]['filtered'] = 0

    sql_catalog_object_list.sort()
    catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    sql_clear_catalog.sort()
    catalog.sql_clear_catalog = tuple(sql_clear_catalog)

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    
    values = []
    object_path = kw.get('object_path', None)
    # get required values
    if object_path is None:
      if context.getTemplateFormatVersion() == 1:
        values = self._objects.values()
      else:
        values = self._archive.values()
    else:      
      values.append(self._archive[object_path])
    # Make copies of attributes of the default catalog of portal_catalog.
    sql_catalog_object_list = list(catalog.sql_catalog_object_list)
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_clear_catalog = list(catalog.sql_clear_catalog)

    for obj in values:
      method_id = obj.id
      if method_id in sql_catalog_object_list:
        sql_catalog_object_list.remove(method_id)
      if method_id in sql_uncatalog_object:
        sql_uncatalog_object.remove(method_id)
      if method_id in sql_clear_catalog:
        sql_clear_catalog.remove(method_id)
      if catalog.filter_dict.has_key(method_id):
        del catalog.filter_dict[method_id]
        
    catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    catalog.sql_clear_catalog = tuple(sql_clear_catalog)
    # uninstall objects
    ObjectTemplateItem.uninstall(self, context, **kw)

  def _importFile(self, file_name, file):
    if not '.catalog_keys' in file_name:
      # just import xml object
      obj = self
      connection = None
      while connection is None:
        obj=obj.aq_parent
        connection=obj._p_jar
      obj = connection.importFile(file, customImporters=customImporters)
      self._objects[file_name[:-4]] = obj
    elif '.catalog_keys' in file_name:
      # recreate data mapping specific to catalog method
      path, name = os.path.split(file_name)
      id = string.split(name, '.')[0]
      xml = parse(file)
      method_list = xml.getElementsByTagName('item')
      for method in method_list:
        key = method.getAttribute('key')
        key_type = str(method.getAttribute('type'))
        if key_type == "str":
          value = str(method.getElementsByTagName('value')[0].childNodes[0].data)
          key = str(key)
        elif key_type == "int":
          value = int(method.getElementsByTagName('value')[0].childNodes[0].data)
          key = str(key)
        elif key_type == "tuple":
          value = []
          value_list = method.getElementsByTagName('value')
          for item in value_list:
            value.append(item.childNodes[0].data)
        else:
          LOG('BusinessTemplate import CatalogMethod, type unknown', 0, key_type)
          continue
        if key in catalog_method_list or key in catalog_method_filter_list:
          dict = getattr(self, key)
          dict[id] = value

class ActionTemplateItem(ObjectTemplateItem):

  def _splitPath(self, path):
    """
      Split path tries to split a complexe path such as:

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

  def __init__(self, id_list, **kw):
    # XXX It's look like ObjectTemplateItem __init__
    BaseTemplateItem.__init__(self, id_list, **kw)
    id_list = self._archive.keys()
    self._archive.clear()
    for id in id_list:
      self._archive["%s/%s" % ('portal_types', id)] = None

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      relative_url, key, value = self._splitPath(id)
      obj = p.unrestrictedTraverse(relative_url)
      for ai in obj.listActions():
        if getattr(ai, key) == value:
          url = os.path.split(relative_url)
          key = os.path.join(url[-2], url[-1], value)
          action = ai._getCopy(context)
          action = self.removeProperties(action)
          self._objects[key] = action
          self._objects[key].wl_clearLocks()
          break
      else:
        raise NotFound, 'Action %r not found' %(id,)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      p = context.getPortalObject()
      for id in self._objects.keys():
        if update_dict.has_key(id) or force:
          if not force:
            action = update_dict[id]
            if action == 'nothing':
              continue
          path = id.split(os.sep)
          obj = p.unrestrictedTraverse(path[:-1])
          action_list = obj.listActions()
          for index in range(len(action_list)):
            if getattr(action_list[index], 'id') == path[-1]:          
              # remove previous action
              obj.deleteActions(selections=(index,))
          action = self._objects[id]
          obj.addAction(
                        id = action.id
                      , name = action.title
                      , action = action.action.text
                      , condition = action.getCondition()
                      , permission = action.permissions
                      , category = action.category
                      , visible = action.visible
                      , icon = getattr(action, 'icon', None) and action.icon.text or ''
                      , optional = getattr(action, 'optional', 0)
                      , priority = action.priority
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
    else:
      BaseTemplateItem.install(self, context, trashbin, **kw)
      p = context.getPortalObject()
      for id in self._archive.keys():
        action = self._archive[id]
        relative_url, key, value = self._splitPath(id)
        obj = p.unrestrictedTraverse(relative_url)
        for ai in obj.listActions():
          if getattr(ai, key) == value:
            raise TemplateConflictError, 'the portal type %s already has the action %s' % (obj.id, value)
        obj.addAction(
                      id = action.id
                    , name = action.title
                    , action = action.action.text
                    , condition = action.getCondition()
                    , permission = action.permissions
                    , category = action.category
                    , visible = action.visible
                    , icon = getattr(action, 'icon', None) and action.icon.text or ''
                    , optional = getattr(action, 'optional', 0)
                    )
        new_priority = action.priority
        action_list = obj.listActions()
        move_down_list = []
        for index in range(len(action_list)):
          action = action_list[index]
          if action.priority > new_priority:
            move_down_list.append(str(index))
          obj.moveDownActions(selections=tuple(move_down_list))


  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    object_path = kw.get("object_path", None)
    if object_path is not None:
      keys = [object_path]
    else:
      keys = self._archive.keys()
    
    for id in keys:
      action = self._archive[id]
      relative_url, key, value = self._splitPath(id)
      obj = p.unrestrictedTraverse(relative_url)
      action_list = obj.listActions()
      for index in range(len(action_list)):
        if getattr(action_list[index], key) == value:
          obj.deleteActions(selections=(index,))
          break
    BaseTemplateItem.uninstall(self, context, **kw)

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
      if obj is None:
        raise NotFound, 'the property %s is not found' % id
      self._objects[id] = (prop_type, obj)

  def _importFile(self, file_name, file):
    # recreate list of site property from xml file
    xml = parse(file)
    property_list = xml.getElementsByTagName('property')
    for prop in property_list:
      id = prop.getElementsByTagName('id')[0].childNodes[0].data
      prop_type = prop.getElementsByTagName('type')[0].childNodes[0].data
      if prop_type in ('lines', 'tokens'):
        value = []
        values = prop.getElementsByTagName('value')[0]
        items = values.getElementsByTagName('item')
        for item in items:
          i = item.childNodes[0].data
          value.append(str(i))
      else:
        value = str(prop.getElementsByTagName('value')[0].childNodes[0].data)
      self._objects[str(id)] = (str(prop_type), value)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      p = context.getPortalObject()
      for path in self._objects.keys():
        if update_dict.has_key(path) or force:
          if not force:
            action = update_dict[path]
            if action == 'nothing':
              continue          
          dir, id = os.path.split(path)
          if p.hasProperty(id):
            continue
          prop_type, property = self._objects[path]
          p._setProperty(id, property, type=prop_type)
    else:
      BaseTemplateItem.install(self, context, trashbin, **kw)
      p = context.getPortalObject()
      for id,property in self._archive.keys():
        property = self._archive[id]
        if p.hasProperty(id):
          continue
          # Too much???
          #raise TemplateConflictError, 'the property %s already exists' % id
        p._setProperty(id, property['value'], type=property['type'])

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

  def generateXml(self, path=None):
    xml_data = ''
    prop_type, obj = self._objects[path]
    xml_data += os.linesep+' <property>'
    xml_data += os.linesep+'  <id>%s</id>' %(path,)
    xml_data += os.linesep+'  <type>%s</type>' %(prop_type,)
    if prop_type in ('lines', 'tokens'):
      xml_data += os.linesep+'  <value>'
      for item in obj:
        if item != '':
          xml_data += os.linesep+'   <item>%s</item>' %(item,)
      xml_data += os.linesep+'  </value>'
    else:
      xml_data += os.linesep+'  <value>%r</value>' %((os.linesep).join(obj),)
    xml_data += os.linesep+' </property>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=root_path)
    xml_data = '<site_property>'
    keys = self._objects.keys()
    keys.sort()
    for path in keys:
      xml_data += self.generateXml(path)
    xml_data += os.linesep+'</site_property>'
    bta.addObject(obj=xml_data, name='properties', path=root_path)

class ModuleTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      module = p.unrestrictedTraverse(id)
      dict = {}
      dict['id'] = module.getId()
      dict['title'] = module.getTitle()
      dict['portal_type'] = module.getPortalType()
      permission_list = []
      # use show permission
      dict['permission_list'] = module.showPermissions()
      self._objects[id] = dict

  def generateXml(self, path=None):
    dict = self._objects[path]
    xml_data = '<module>'
    # sort key
    keys = dict.keys()
    keys.sort()
    for key in keys:
      if key =='permission_list':
        # separe permission dict into xml
        xml_data += os.linesep+' <%s>' %(key,)
        permission_list = dict[key]
        for perm in permission_list:
          xml_data += os.linesep+'  <permission>'
          xml_data += os.linesep+'   <name>%s</name>' %(perm[0])
          role_list = list(perm[1])
          role_list.sort()
          for role in role_list:
            xml_data += os.linesep+'   <role>%s</role>' %(role)
          xml_data += os.linesep+'  </permission>'
        xml_data += os.linesep+' </%s>' %(key,)
      else:
        xml_data += os.linesep+' <%s>%s</%s>' %(key, dict[key], key)
    xml_data += os.linesep+'</module>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(path)
    keys = self._objects.keys()
    keys.sort()
    for id in keys:
      # expor module one by one
      xml_data = self.generateXml(path=id)
      bta.addObject(obj=xml_data, name=id, path=path)

  def install(self, context, trashbin, **kw):
    portal = context.getPortalObject()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      items = self._objects
    else:
      items = self._archive

    for id in items.keys():
      if update_dict.has_key(id) or force:
        if not force:
          action = update_dict[id]
          if action == 'nothing':
            continue
        mapping = items[id]
        path, id = os.path.split(id)
        if id in portal.objectIds():
          module = portal._getOb(id)
          module.portal_type = str(mapping['portal_type']) 
        else:
          module = portal.newContent(id=id, portal_type=str(mapping['portal_type']))
        module.setTitle(str(mapping['title']))
        for name,role_list in list(mapping['permission_list']):
          acquire = (type(role_list) == type([]))
          try:
            module.manage_permission(name, roles=role_list, acquire=acquire)
          except ValueError:
            # Ignore a permission not present in this system.
            pass

  def _importFile(self, file_name, file):
    dict = {}
    xml = parse(file)
    for id in ('portal_type', 'id', 'title', 'permission_list'):
      elt = xml.getElementsByTagName(id)[0]
      if id == 'permission_list':
        plist = []
        perm_list = elt.getElementsByTagName('permission')
        for perm in perm_list:
          name_elt = perm.getElementsByTagName('name')[0]
          name_node = name_elt.childNodes[0]
          name = name_node.data
          role_list = perm.getElementsByTagName('role')
          rlist = []
          for role in role_list:
            role_node = role.childNodes[0]
            role = role_node.data
            rlist.append(str(role))
          perm_tuple = (str(name), rlist)
          plist.append(perm_tuple)
        dict[id] = plist
      else:
        node_list = elt.childNodes
        if len(node_list) == 0:
          value=''
        else:
          value = node_list[0].data
        dict[id] = str(value)
    self._objects[file_name[:-4]] = dict

  def uninstall(self, context, **kw):
    trash = kw.get('trash', 0)      
    object_path = kw.get('object_path', None)
    trashbin = kw.get('trashbin', None)
    if object_path is None:
      keys = self._archive.keys()
    else:
      keys = [object_path]
    p = context.getPortalObject()
    id_list = p.objectIds()
    for id in keys:
      if id in id_list:
        try:
          if trash and trashbin is not None:
            container_path = id.split('/')
            self.portal_trash.backupObject(trashbin, container_path, id, save=1, keep_subobjects=1)
          p.manage_delObjects([id])
        except NotFound:
          pass
    BaseTemplateItem.uninstall(self, context, **kw)

  def trash(self, context, new_item, **kw):
    # Do not remove any module for safety.
    pass

class DocumentTemplateItem(BaseTemplateItem):
  local_file_reader_name = 'readLocalDocument'
  local_file_writer_name = 'writeLocalDocument'
  local_file_importer_name = 'importLocalDocument'
  local_file_remover_name = 'removeLocalDocument'

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for id in self._archive.keys():
      self._objects[self.__class__.__name__+os.sep+id] = globals()[self.local_file_reader_name](id)

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      new_keys = self._objects.keys()
      for path in new_keys:
        if installed_bt._objects.has_key(path):
          # compare object to see if there is changes
          new_obj_code = self._objects[path]
          old_obj_code = installed_bt._objects[path]
          if new_obj_code != old_obj_code:
            modified_object_list.update({path : ['Modified', self.__class__.__name__[:-12]]})
        else: # new object
          modified_object_list.update({path : ['New', self.__class__.__name__[:-12]]})
          # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      for id in self._objects.keys():
        if update_dict.has_key(id) or force:
          if not force:
            action = update_dict[id]
            if action == 'nothing':
              continue
          text = self._objects[id]
          path, name = os.path.split(id)
          # This raises an exception if the file already exists.
          try:
            globals()[self.local_file_writer_name](name, text, create=1)
          except IOError:
            continue
          if self.local_file_importer_name is not None:
            globals()[self.local_file_importer_name](name)
    else:
      BaseTemplateItem.install(self, context, trashbin, **kw)
      for id in self._archive.keys():
        text = self._archive[id]
        # This raises an exception if the file exists.
        globals()[self.local_file_writer_name](id, text, create=1)
        if self.local_file_importer_name is not None:
          globals()[self.local_file_importer_name](id)

  def uninstall(self, context, **kw):
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for id in object_keys:
      globals()[self.local_file_remover_name](id)
    BaseTemplateItem.uninstall(self, context, **kw)

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      obj = self._objects[path]
      bta.addObject(obj=obj, name=path, path=None, ext='.py')

  def _importFile(self, file_name, file):
    text = file.read()
    self._objects[file_name[:-3]]=text

class PropertySheetTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalPropertySheet'
  local_file_writer_name = 'writeLocalPropertySheet'
  local_file_importer_name = 'importLocalPropertySheet'
  local_file_remover_name = 'removeLocalPropertySheet'


class ExtensionTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalExtension'
  local_file_writer_name = 'writeLocalExtension'
  # XXX is this method a error or ?
  local_file_importer_name = 'importLocalPropertySheet'
  local_file_remover_name = 'removeLocalExtension'

class TestTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalTest'
  local_file_writer_name = 'writeLocalTest'
  # XXX is this a error ?
  local_file_importer_name = None
  local_file_remover_name = 'removeLocalTest'


class ProductTemplateItem(BaseTemplateItem):
  # XXX Not implemented yet
  pass

class RoleTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    role_list = []
    for key in self._archive.keys():
      role_list.append(key)
    if len(role_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'role_list'] = role_list

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      new_roles = self._objects.keys()
      for role in new_roles:
        if installed_bt._objects.has_key(role):
          continue
        else: # only show new roles
          modified_object_list.update({role : ['New', 'Role']})
      # get removed roles
      old_roles = installed_bt._objects.keys()
      for role in old_roles:
        if role not in new_roles:
          modified_object_list.update({role : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    p = context.getPortalObject()
    # get roles
    if context.getTemplateFormatVersion() == 1:
      role_list = self._objects.keys()
    else:
      role_list = self._archive.keys()
    # set roles in PAS
    if p.acl_users.meta_type == 'Pluggable Auth Service':
      role_manager_list = p.acl_users.objectValues('ZODB Role Manager')
      for role_manager in role_manager_list:
        existing_role_list = role_manager.listRoleIds()
        for role in role_list:
          if role not in existing_role_list:
            role_manager.addRole(role)
    # set roles on portal
    roles = {}
    for role in p.__ac_roles__:
      roles[role] = 1
    for role in role_list:
      roles[role] = 1
    p.__ac_roles__ = tuple(roles.keys())

  def _importFile(self, file_name, file):
    xml = parse(file)
    role_list = xml.getElementsByTagName('role')
    for role in role_list:
      node = role.childNodes[0]
      value = node.data
      self._objects[str(value)] = 1

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

  def generateXml(self, path):
    obj = self._objects[path]
    xml_data = '<role_list>'
    obj.sort()
    for role in obj:
      xml_data += os.linesep+' <role>%s</role>' %(role)
    xml_data += os.linesep+'</role_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None,)

class CatalogResultKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_result_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'result_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_result_keys = list(catalog.sql_search_result_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX same as related key
    if update_dict.has_key('result_key_list') or force:
      if not force:
        action = update_dict['result_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_search_result_keys:
          sql_search_result_keys.append(key)
      catalog.sql_search_result_keys = sql_search_result_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_search_result_keys:
        sql_search_result_keys.remove(key)
    catalog.sql_search_result_keys = sql_search_result_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

class CatalogRelatedKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_related_keys = list(catalog.sql_catalog_related_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_related_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'related_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_related_keys = list(catalog.sql_catalog_related_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX must a find a better way to manage related key
    if update_dict.has_key('related_key_list') or update_dict.has_key('key_list') or force:
      if not force:
        if update_dict.has_key('related_key_list'):
          action = update_dict['related_key_list']
        else: # XXX for backward compatibility
          action = update_dict['key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_catalog_related_keys:
          sql_catalog_related_keys.append(key)
      catalog.sql_catalog_related_keys = tuple(sql_catalog_related_keys)

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_related_keys = list(catalog.sql_catalog_related_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_catalog_related_keys:
        sql_catalog_related_keys.remove(key)
    catalog.sql_catalog_related_keys = sql_catalog_related_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

class CatalogResultTableTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_result_tables = list(catalog.sql_search_tables)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_result_tables:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'resutl_table_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_tables = list(catalog.sql_search_tables)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX same as related keys
    if update_dict.has_key('result_table_list') or force:
      if not force:
        action = update_dict['result_table_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_search_tables:
          sql_search_tables.append(key)
      catalog.sql_search_tables = sql_search_tables

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_tables = list(catalog.sql_search_tables)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_search_tables:
        sql_search_tables.remove(key)
    catalog.sql_search_tables = sql_search_tables
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'    
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)
      
# keyword
class CatalogKeywordKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_keyword_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'keyword_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX same as related key
    if update_dict.has_key('keyword_key_list') or force:
      if not force:
        action = update_dict['keyword_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_keyword_keys:
          sql_keyword_keys.append(key)
      catalog.sql_catalog_keyword_search_keys = sql_keyword_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_keyword_keys:
        sql_keyword_keys.remove(key)
    catalog.sql_catalog_keyword_search_keys = sql_keyword_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

# full text
class CatalogFullTextKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_full_text_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'ful_text_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX same as related key
    if update_dict.has_key('full_text_key_list') or force:
      if not force:
        action = update_dict['full_text_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_full_text_keys:
          sql_full_text_keys.append(key)
      catalog.sql_catalog_full_text_search_keys = sql_full_text_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_full_text_keys:
        sql_full_text_keys.remove(key)
    catalog.sql_catalog_full_text_search_keys = sql_full_text_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)


# request
class CatalogRequestKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_request_keys = list(catalog.sql_catalog_request_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_request_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'request_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX must a find a better way to manage related key
    if update_dict.has_key('request_key_list') or force:
      if not force:
        action = update_dict['request_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_catalog_request_keys:
          sql_catalog_request_keys.append(key)
      catalog.sql_catalog_request_keys = tuple(sql_catalog_request_keys)

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_request_keys = list(catalog.sql_catalog_request_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_catalog_request_keys:
        sql_catalog_request_keys.remove(key)
    catalog.sql_catalog_request_keys = sql_catalog_request_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

# multivalue
class CatalogMultivalueKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_multivalue_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'multivalue_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if update_dict.has_key('multivalue_key_list') or force:
      if not force:
        action = update_dict['multivalue_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_catalog_multivalue_keys:
          sql_catalog_multivalue_keys.append(key)
      catalog.sql_catalog_multivalue_keys = tuple(sql_catalog_multivalue_keys)

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_catalog_multivalue_keys:
        sql_catalog_multivalue_keys.remove(key)
    catalog.sql_catalog_multivalue_keys = sql_catalog_multivalue_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

# topic
class CatalogTopicKeyTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_topic_search_keys = list(catalog.sql_catalog_topic_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_catalog_topic_search_keys:
        key_list.append(key)
      else:
        raise NotFound, 'key %r not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'topic_key_list'] = key_list

  def _importFile(self, file_name, file):
    list = []
    xml = parse(file)
    key_list = xml.getElementsByTagName('key')
    for key in key_list:
      node = key.childNodes[0]
      value = node.data
      list.append(str(value))
    self._objects[file_name[:-4]] = list

  def install(self, context, trashbin, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_topic_search_keys = list(catalog.sql_catalog_topic_search_keys)
    if context.getTemplateFormatVersion() == 1:
      if len(self._objects.keys()) == 0: # needed because of pop()
        return
      keys = []
      for k in self._objects.values().pop(): # because of list of list
        keys.append(k)
    else:
      keys = self._archive.keys()
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # XXX same as related key
    if update_dict.has_key('topic_key_list') or force:
      if not force:
        action = update_dict['topic_key_list']
        if action == 'nothing':
          return
      for key in keys:
        if key not in sql_catalog_topic_search_keys:
          sql_catalog_topic_search_keys.append(key)
      catalog.sql_catalog_topic_search_keys = sql_catalog_topic_search_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except KeyError:
      catalog = None
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_topic_search_keys = list(catalog.sql_catalog_topic_search_keys)
    object_path = kw.get('object_path', None)    
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._archive.keys()
    for key in object_keys:
      if key in sql_catalog_topic_search_keys:
        sql_catalog_topic_search_keys.remove(key)
    catalog.sql_catalog_topic_search_keys = sql_catalog_topic_search_keys
    BaseTemplateItem.uninstall(self, context, **kw)

  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=path)
    for path in self._objects.keys():
      xml_data = self.generateXml(path=path)
      bta.addObject(obj=xml_data, name=path, path=None)

class MessageTranslationTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    localizer = context.getPortalObject().Localizer
    for lang in self._archive.keys():
      # Export only erp5_ui at the moment.
      # This is safer against information leak.
      for catalog in ('erp5_ui', ):
        path = os.path.join(lang, catalog)
        mc = localizer._getOb(catalog)
        self._objects[path] = mc.manage_export(lang)

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      new_keys = self._objects.keys()
      for path in new_keys:
        if installed_bt._objects.has_key(path):
          # compare object to see if there is changes
          new_obj_code = self._objects[path]
          old_obj_code = installed_bt._objects[path]
          if new_obj_code != old_obj_code:
            modified_object_list.update({path : ['Modified', self.__class__.__name__[:-12]]})
        else: # new object
          modified_object_list.update({path : ['New', self.__class__.__name__[:-12]]})
      # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    localizer = context.getPortalObject().Localizer
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      for path, po in self._objects.items():
        if update_dict.has_key(path) or force:
          if not force:
            action = update_dict[path]
            if action == 'nothing':
              continue          
          path = string.split(path, '/')
          lang = path[-3]
          catalog = path[-2]
          if lang not in localizer.get_languages():
            localizer.manage_addLanguage(lang)
          mc = localizer._getOb(catalog)
          if lang not in mc.get_languages():
            mc.manage_addLanguage(lang)
          mc.manage_import(lang, po)
    else:
      BaseTemplateItem.install(self, context, trashbin, **kw)
      for lang, catalogs in self._archive.items():
        if lang not in localizer.get_languages():
          localizer.manage_addLanguage(lang)
        for catalog, po in catalogs.items():
          mc = localizer._getOb(catalog)
          if lang not in mc.get_languages():
            mc.manage_addLanguage(lang)
          mc.manage_import(lang, po)

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=root_path)
    for key in self._objects.keys():
      obj = self._objects[key]
      path = os.path.join(root_path, key)
      bta.addFolder(name=path)
      f = open(path+'/translation.po', 'wt')
      f.write(str(obj))
      f.close()

  def _importFile(self, file_name, file):
    text = file.read()
    self._objects[file_name[:-3]]=text

class BusinessTemplate(XMLObject):
    """
    A business template allows to construct ERP5 modules
    in part or completely. Each object are separated from its
    subobjects and exported in xml format.
    It may include:

    - catalog definition
      - SQL method objects
      - SQL methods including:
        - purpose (catalog, uncatalog, etc.)
        - filter definition

    - portal_types definition
      - object without optinal actions
      - list of relation between portal type and worklfow

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
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Version
                      , PropertySheet.BusinessTemplate
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Business Template is a set of definitions, such as skins, portal types and categories. This is used to set up a new ERP5 site very efficiently."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addBusinessTemplate'
         , 'immediate_view' : 'BusinessTemplate_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': (
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
      }

    # This is a global variable
    # Order is important for installation
    _item_name_list = [
      '_product_item',
      '_property_sheet_item',
      '_document_item',
      '_extension_item',
      '_test_item',
      '_role_item',
      '_message_translation_item',
      '_workflow_item',
      '_catalog_method_item',
      '_site_property_item',
      '_portal_type_item',
      '_portal_type_allowed_content_type_item',
      '_portal_type_hidden_content_type_item',
      '_portal_type_property_sheet_item',
      '_portal_type_base_category_item',
      '_category_item',
      '_module_item',
      '_skin_item',
      '_path_item',
      '_action_item',
      '_catalog_result_key_item',
      '_catalog_related_key_item',
      '_catalog_result_table_item',
      '_catalog_keyword_key_item',
      '_catalog_full_text_key_item',
      '_catalog_request_key_item',
      '_catalog_multivalue_key_item',
      '_catalog_topic_key_item',
    ]

    def __init__(self, *args, **kw):
      XMLObject.__init__(self, *args, **kw)
      self._clean()

    def getTemplateFormatVersion(self, **kw):
      """This is a workaround, because template_format_version was not set even for the new format.
      """
      if self.hasProperty('template_format_version'):
        self._baseGetTemplateFormatVersion()

      # the attribute _objects in BaseTemplateItem was added in the new format.
      if hasattr(self._path_item, '_objects'):
        return 1
      
      return 0
        
    security.declareProtected(Permissions.ManagePortal, 'manage_afterAdd')
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

    security.declareProtected(Permissions.ManagePortal, 'build')
    def build(self, no_action=0):
      """
        Copy existing portal objects to self
      """
      if no_action: return # this is use at import of Business Template to get the status built
      
      # Make sure that everything is sane.
      self.clean()

      # Set the format version.
      self._setTemplateFormatVersion(1)

      # Store all datas
      self._portal_type_item = \
          PortalTypeTemplateItem(self.getTemplatePortalTypeIdList())
      self._workflow_item = \
          WorkflowTemplateItem(self.getTemplateWorkflowIdList())
      self._skin_item = \
          SkinTemplateItem(self.getTemplateSkinIdList())
      self._category_item = \
          CategoryTemplateItem(self.getTemplateBaseCategoryList())
      self._catalog_method_item = \
          CatalogMethodTemplateItem(self.getTemplateCatalogMethodIdList())
      self._action_item = \
          ActionTemplateItem(self.getTemplateActionPathList())
      self._site_property_item = \
          SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._module_item = \
          ModuleTemplateItem(self.getTemplateModuleIdList())
      self._document_item = \
          DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._property_sheet_item = \
          PropertySheetTemplateItem(self.getTemplatePropertySheetIdList())
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
      self._catalog_keyword_key_item = \
          CatalogKeywordKeyTemplateItem(
               self.getTemplateCatalogKeywordKeyList())      
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
      
      # Build each part
      for item_name in self._item_name_list:
        getattr(self, item_name).build(self)

    build = WorkflowMethod(build)

    def publish(self, url, username=None, password=None):
      """
        Publish in a format or another
      """
      return self.portal_templates.publish(self, url, username=username,
                                           password=password)

    def update(self):
      """
        Update template: download new template definition
      """
      return self.portal_templates.update(self)

    def preinstall(self, **kw):
      """
        Return the list of modified/new/removed object between a Business Template
        and the one installed if exists
      """      
      modified_object_list = {}
      bt_title = self.getTitle()
      installed_bt = self.portal_templates.getInstalledBusinessTemplate(title=bt_title)
      if installed_bt is None:
        installed_bt_format = 0 # that will not check for modification
      else:
        installed_bt_format = installed_bt.getTemplateFormatVersion()

      # if reinstall business template, must compare to object in ZODB
      # and not to those in the installed Business Template because it is itself
      reinstall = 0
      if installed_bt == self:
        reinstall = 1
        bt2 = self.portal_templates.manage_clone(ob=installed_bt, id='installed_bt')
        bt2.edit(description='tmp bt generated for diff')
        bt2.build()
        installed_bt = bt2
      
      new_bt_format = self.getTemplateFormatVersion()
      if installed_bt_format == 0 and new_bt_format == 0:
        # still use old format, so install everything, no choice
        return modified_object_list
      elif installed_bt_format == 0 and new_bt_format == 1:
        # return list of all object in bt
        for item_name in self._item_name_list:
          item = getattr(self, item_name, None)
          if item is not None:
            for path in item._objects.keys():
              modified_object_list.update({path : ['New', item.__class__.__name__[:-12]]})
        return modified_object_list
        
      # get the list of modified and new object
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)
      for item_name in self._item_name_list:
        new_item = getattr(self, item_name, None)
        old_item = getattr(installed_bt, item_name, None)
        if new_item is not None:
          if old_item is not None:
            modified_object = new_item.preinstall(context=local_configuration, installed_bt=old_item)
            if len(modified_object) > 0:
              modified_object_list.update(modified_object)
          else:
            for path in new_item._objects.keys():
              modified_object_list.update({path : ['New', new_item.__class__.__name__[:-12]]})

      if reinstall:
        self.portal_templates.manage_delObjects(ids=['installed_bt'])
      
      return modified_object_list

    def _install(self, force=1, object_to_update={}, **kw):
      """
        Install a new Business Template, if force, all we be upgrade or installed
        otherwise depends of dict object_to_update
      """
      installed_bt = self.portal_templates.getInstalledBusinessTemplate(
                                                           self.getTitle())
      if installed_bt is not None:        
        if installed_bt.getTemplateFormatVersion() == 0:
          # maybe another to uninstall old format bt, maybe not needed
          installed_bt.trash(self)
          force = 1
        installed_bt.replace(self)
        
      site = self.getPortalObject()
      from Products.ERP5.ERP5Site import ERP5Generator
      gen = ERP5Generator()
      # update activity tool first if necessary
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateTool():
        LOG('Business Template', 0, 'Updating Activity Tool')
        gen.setupLastTools(site, update=1, create_activities=1)
             
      if not force:
        if len(object_to_update) == 0:
          # check if we have to update tools
          if self.getTitle() == 'erp5_core' and self.getTemplateUpdateTool():
            LOG('Business Template', 0, 'Updating Tools')
            gen.setup(site, 0, update=1)
          if self.getTitle() == 'erp5_core' and self.getTemplateUpdateBusinessTemplateWorkflow():
            LOG('set flag to update workfow', 0, '')
            gen.setupWorkflow(site)
          return

      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)    

      # update catalog if necessary
      update_catalog=0
      catalog_method = getattr(self, '_catalog_method_item', None)
      if catalog_method is not None:
        for id in catalog_method._objects.keys():
          if id in object_to_update.keys() or force:
            if not force:
              action = object_to_update[id]
              if action == 'nothing':
                continue
            if 'related' not in id:
              # must update catalog
              update_catalog = 1
              break            
      if update_catalog:
        catalog = local_configuration.portal_catalog.getSQLCatalog()
        if catalog is None:
          LOG('Business Template', 0, 'no SQL Catalog available')
          update_catalog = 0
        else:
          LOG('Business Template', 0, 'Updating SQL Catalog')
          catalog.manage_catalogClear()
              
      # always created a trash bin because we may to save object already present
      # but not in a previous business templates apart at creation of a new site
      trash_tool = getToolByName(self, 'portal_trash', None)
      if trash_tool is not None and (len(object_to_update) > 0 or len(self.portal_templates.objectIds()) > 1):
        trashbin = trash_tool.newTrashBin(self.getTitle(), self)
      else:
        trashbin = None
              
      # get objects to remove
      remove_object_dict = {}
      for path in object_to_update.keys():
        action = object_to_update[path]
        if action == 'remove' or action == 'save_and_remove':
          remove_object_dict[path] = action
          object_to_update.pop(path)
      # remove object from old business template
      if len(remove_object_dict) > 0:
        for item_name in installed_bt._item_name_list:
          item = getattr(installed_bt, item_name, None)
          if item is not None:
            item.remove(local_configuration, remove_object_dict=remove_object_dict, trashbin=trashbin)
      # Install everything
      if len(object_to_update) > 0 or force:
        for item_name in self._item_name_list:
          item = getattr(self, item_name, None)
          if item is not None:
            item.install(local_configuration, force=force, object_to_update=object_to_update, trashbin=trashbin)

      # update tools if necessary
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateTool():
        LOG('Business Template', 0, 'Updating Tools')
        gen.setup(site, 0, update=1)

      # check if we have to updater business template workflow
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateBusinessTemplateWorkflow():
        LOG('set flag to update workfow', 0, '')
        gen.setupWorkflow(site)
        # XXX keep TM in case update of workflow doesn't work
        #         self._v_txn = WorkflowUpdateTM()
        #         self._v_txn.register(update=1, gen=gen, site=site)

      if update_catalog:
        site.ERP5Site_reindexAll()
       
      # It is better to clear cache because the installation of a template
      # adds many new things into the portal.
      clearCache()

    security.declareProtected(Permissions.ManagePortal, 'install')
    def install(self, **kw):
      """
        For install based on paramaters provided in **kw
      """
      return self._install(**kw)

    install = WorkflowMethod(install)

    security.declareProtected(Permissions.ManagePortal, 'reinstall')
    def reinstall(self, **kw):
      """Reinstall Business Template.
      """
      return self._install(**kw)

    reinstall = WorkflowMethod(reinstall)

    security.declareProtected(Permissions.ManagePortal, 'trash')
    def trash(self, new_bt, **kw):
      """
        Trash unnecessary items before upgrading to a new business
        template.
        This is similar to uninstall, but different in that this does
        not remove all items.
      """
      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)
      # Trash everything
      for item_name in self._item_name_list[::-1]:
        item = getattr(self, item_name, None)
        if item is not None:
          item.trash(
                local_configuration,
                getattr(new_bt, item_name))

    security.declareProtected(Permissions.ManagePortal, 'uninstall')
    def uninstall(self, **kw):
      """
        For uninstall based on paramaters provided in **kw
      """
      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)
      # Uninstall everything
      # Trash everything
      for item_name in self._item_name_list[::-1]:
        item = getattr(self, item_name, None)
        if item is not None:
          item.uninstall(local_configuration)
      # It is better to clear cache because the uninstallation of a
      # template deletes many things from the portal.
      clearCache()

    uninstall = WorkflowMethod(uninstall)

    security.declareProtected(Permissions.ManagePortal, 'clean')
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
      for item_name in self._item_name_list:
        item = setattr(self, item_name, None)

    clean = WorkflowMethod(_clean)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBuildingState')
    def getBuildingState(self, id_only=1):
      """
        Returns the current state in building
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById(
                          'business_template_building_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstallationState')
    def getInstallationState(self, id_only=1):
      """
        Returns the current state in installation
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
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
      result = getattr(self, id, ())
      if result is None: result = ()
      if result != ():
        result = list(result)
        result.sort()
        result = tuple(result)
      return result

    def getTemplateCatalogMethodIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_catalog_method_id')

    def getTemplateBaseCategoryList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_base_category')

    def getTemplateWorkflowIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_workflow_id')

    def getTemplatePortalTypeIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_id')

    def getTemplatePortalTypeAllowedContentTypeList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_allowed_content_type')
    
    def getTemplatePortalTypeHiddenContentTypeList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_hidden_content_type')

    def getTemplatePortalTypePropertySheetList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_property_sheet')

    def getTemplatePortalTypeBaseCategoryList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_base_category')

    def getTemplateActionPathList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_action_path')

    def getTemplateSkinIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_skin_id')

    def getTemplateModuleIdList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_module_id')

    def getTemplateMessageTranslationList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_message_translation')

    security.declareProtected(Permissions.ManagePortal, 'export')
    def export(self, path=None, local=0, **kw):
      """
        Export this Business Template
      """
      if self.getBuildingState() != 'built':
        raise TemplateConditionError, 'Business Template must be build before export'
      
      if local:
        # we export into a folder tree
        bta = BusinessTemplateFolder(creation=1, path=path)
      else:
        # We export BT into a tarball file
        bta = BusinessTemplateTarball(creation=1, path=path)

      # export bt
      bta.addFolder(path+os.sep+'bt')
      for prop in self.propertyMap():
        prop_type = prop['type']
        id = prop['id']
        if id in ('id', 'uid', 'rid', 'sid', 'id_group', 'last_id', 'install_object_list_list'):
          continue
#         if id in ('template_update_business_template_workflow', 'template_update_tool') and self.getTitle() != 'erp5_core':
#           continue
        value = self.getProperty(id)
        if prop_type in ('text', 'string', 'int', 'boolean'):
          bta.addObject(obj=value, name=id, path=path+os.sep+'bt', ext='')
        elif prop_type in ('lines', 'tokens'):
          bta.addObject(obj=str(os.linesep).join(value), name=id, path=path+os.sep+'bt', ext='')

      # Export each part
      for item_name in self._item_name_list:
        getattr(self, item_name).export(context=self, bta=bta)
        
      return bta.finishCreation()

    security.declareProtected(Permissions.ManagePortal, 'importFile')
    def importFile(self, dir = 0, file=None, root_path=None):
      """
        Import all xml files in Business Template
      """
      if dir:
        bta = BusinessTemplateFolder(importing=1, file=file, path=root_path)
      else:
        bta = BusinessTemplateTarball(importing=1, file=file)

      self._portal_type_item = \
          PortalTypeTemplateItem(self.getTemplatePortalTypeIdList())
      self._workflow_item = \
          WorkflowTemplateItem(self.getTemplateWorkflowIdList())
      self._skin_item = \
          SkinTemplateItem(self.getTemplateSkinIdList())
      self._category_item = \
          CategoryTemplateItem(self.getTemplateBaseCategoryList())
      self._catalog_method_item = \
          CatalogMethodTemplateItem(self.getTemplateCatalogMethodIdList())
      self._action_item = \
          ActionTemplateItem(self.getTemplateActionPathList())
      self._site_property_item = \
          SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._module_item = \
          ModuleTemplateItem(self.getTemplateModuleIdList())
      self._document_item = \
          DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._property_sheet_item = \
          PropertySheetTemplateItem(self.getTemplatePropertySheetIdList())
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
      self._path_item = \
               PathTemplateItem(self.getTemplatePathList())
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
      self._catalog_keyword_key_item = \
          CatalogKeywordKeyTemplateItem(
               self.getTemplateCatalogKeywordKeyList())      
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
      
      for item_name in self._item_name_list:
        getattr(self, item_name).importFile(bta)


    def diffObject(self, REQUEST):
      """
        Make a diff between an object in the Business Template
        and the same in the Business Template installed in the site
      """

      class_name_dict = {
        'Product' : '_product_item',
        'PropertySheet' : '_property_sheet_item', 
        'Document' : '_document_item',
        'Extension' : '_extension_item',
        'Test' : '_test_item',
        'Role' : '_role_item',
        'MessageTranslation' : '_message_translation_item',
        'Workflow' : '_workflow_item',
        'CatalogMethod' : '_catalog_method_item',
        'SiteProperty' : '_site_property_item',
        'PortalType' : '_portal_type_item',
        'PortalTypeAllowedContentType' : '_portal_type_allowed_content_type_item',
        'PortalHiddenAllowedContentType' : '_portal_type_hidden_content_type_item',
        'PortalTypePropertySheet' : '_portal_type_property_sheet_item',
        'PortalTypeBaseCategory' : '_portal_type_base_category_item',
        'Category' : '_category_item',
        'Module' : '_module_item',
        'Skin' : '_skin_item',
        'Path' : '_path_item',
        'Action' : '_action_item',
        'CatalogResultKey' : '_catalog_result_key_item',
        'CatalogRelatedKey' : '_catalog_related_key_item',
        'CatalogResultTable' : '_catalog_result_table_item',
        'CatalogKeywordKey' : '_catalog_keyword_key_item',
        'CatalogFullTextKey' : '_catalog_full_text_key_item',
        'CatalogRequestKey' : '_catalog_request_key_item',
        'CatalogMultivalueKey' : '_catalog_multivalue_key_item',
        'CatalogTopicKey' : '_catalog_topic_key_item',
        }

      object_id = REQUEST.object_id
      object_class = REQUEST.object_class
      # get objects
      item_name = class_name_dict[object_class]
      new_bt =self
      installed_bt = self.getInstalledBusinessTemplate(title=self.getTitle())
      if installed_bt == new_bt:
        return 'No diff at reinstall'
      new_item = getattr(new_bt, item_name)
      installed_item = getattr(installed_bt, item_name)
      new_object = new_item._objects[object_id]
      installed_object = installed_item._objects[object_id]
      # make diff
      diff_msg = ''
      item_list_1 = ['_product_item', '_workflow_item', '_portal_type_item', '_category_item', '_path_item',
                     '_skin_item', '_action_item']
      item_list_2 = ['_site_property_item', '_module_item', '_catalog_result_key_item', '_catalog_related_key_item',
                     '_catalog_result_table_item',   '_catalog_keyword_key_item', '_catalog_full_text_key_item',
                     '_catalog_request_key_item', '_catalog_multivalue_key_item', '_catalog_topic_key_item',
                     '_portal_type_allowed_content_type_item', '_portal_type_hidden_content_type_item',
                     '_portal_type_property_sheet_item', '_portal_type_base_category_item',]
      item_list_3 = ['_document_item', '_property_sheet_item', '_extension_item', '_test_item', '_message_translation_item']
      if item_name in item_list_1:
        f1 = StringIO()
        f2 = StringIO()
        OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, f1)
        OFS.XMLExportImport.exportXML(installed_object._p_jar, installed_object._p_oid, f2)
        new_obj_xml = f1.getvalue()
        installed_obj_xml = f2.getvalue()
        f1.close()
        f2.close()
        new_ob_xml_lines = new_obj_xml.splitlines()
        installed_ob_xml_lines = installed_obj_xml.splitlines()
        diff_list = list(unified_diff(installed_ob_xml_lines, new_ob_xml_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' %( object_id)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'
      elif item_name in item_list_2:
        new_obj_xml = new_item.generateXml(path= object_id)
        installed_obj_xml = installed_item.generateXml(path= object_id)
        new_obj_xml_lines = new_obj_xml.splitlines()
        installed_obj_xml_lines = installed_obj_xml.splitlines()
        diff_list = list(unified_diff(installed_obj_xml_lines, new_obj_xml_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' %( object_id)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'
      elif item_name in item_list_3:
        new_obj_lines = new_object.splitlines()
        installed_obj_lines = installed_object.splitlines()
        diff_list = list(unified_diff(installed_obj_lines, new_obj_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' %( object_id)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'                
      
      return diff_msg

    
    def getPortalTypesProperties(self, **kw):
      """
      Fill field about properties for each portal type
      """
      bt_allowed_content_type_list = []
      bt_hidden_content_type_list = []
      bt_property_sheet_list = []
      bt_base_category_list = []
      
      bt_portal_types_id_list = list(self.getTemplatePortalTypeIdList())      
      p = self.getPortalObject()
      for id in bt_portal_types_id_list:        
        try:
          portal_type = p.unrestrictedTraverse('portal_types/'+id)
        except KeyError:
          continue
        allowed_content_type_list = []
        hidden_content_type_list = []
        property_sheet_list = []
        base_category_list = []
        if hasattr(portal_type, 'allowed_content_types'):
          allowed_content_type_list = portal_type.allowed_content_types
        if hasattr(portal_type, 'hidden_content_type_list'):
          hidden_content_type_list = portal_type.hidden_content_type_list
        if hasattr(portal_type, 'property_sheet_list'):
          property_sheet_list = portal_type.property_sheet_list
        if hasattr(portal_type, 'base_category_list'):
          base_category_list = portal_type.base_category_list       

        for a_id in allowed_content_type_list:            
          bt_allowed_content_type_list.append(id+' | '+a_id)
        for h_id in hidden_content_type_list:
          bt_hidden_content_type_list.append(id+' | '+h_id)
        for ps_id in property_sheet_list:           
          bt_property_sheet_list.append(id+' | '+ps_id)
        for bc_id in base_category_list:            
          bt_base_category_list.append(id+' | '+bc_id)

      bt_allowed_content_type_list.sort()
      bt_hidden_content_type_list.sort()
      bt_property_sheet_list.sort()
      bt_base_category_list.sort()

      setattr(self, 'template_portal_type_allowed_content_type', bt_allowed_content_type_list)
      setattr(self, 'template_portal_type_hidden_content_type', bt_hidden_content_type_list)
      setattr(self, 'template_portal_type_property_sheet', bt_property_sheet_list)
      setattr(self, 'template_portal_type_base_category', bt_base_category_list)        
      return


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

# Transaction Manager used for update of business template workflow
# XXX update seems to works without it

# from Shared.DC.ZRDB.TM import TM

# class WorkflowUpdateTM(TM):

#   _p_oid=_p_changed=_registered=None
#   _update = 0

#   def __init__(self, ):
#     LOG('init TM', 0, '')

#   def register(self, update=0, gen=None, site=None):
#     LOG('register TM', 0, update)
#     self._gen = gen
#     self._site = site
#     self._update = update
#     self._register()

#   def tpc_prepare(self, *d, **kw):
#     LOG("tpc_prepare", 0, self._update)
#     if self._update:
#       # do it one time
#       self._update = 0
#       LOG('call update of wf', 0, '')
#       self._gen.setupWorkflow(self._site)
      

#   def _finish(self, **kw):
#     LOG('finish TM', 0, '')
#     pass

#   def _abort(self, **kw):
#     LOG('abort TM', 0, '')
#     pass
  
