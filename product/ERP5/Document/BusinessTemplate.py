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

from Shared.DC.ZRDB.Connection import Connection as RDBConnection
from Globals import Persistent, PersistentMapping
from Acquisition import Implicit, aq_base
from AccessControl.Permission import Permission
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
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
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.RoleInformation import RoleInformation
import fnmatch
import re, os, sys, string, tarfile
from Products.ERP5Type.Cache import clearAllCache
from DateTime import DateTime
from OFS.Traversable import NotFound
from OFS import XMLExportImport
from cStringIO import StringIO
from copy import deepcopy
from App.config import getConfiguration
from zExceptions import BadRequest
import OFS.XMLExportImport
customImporters={
    XMLExportImport.magic: XMLExportImport.importXML,
    }

from zLOG import LOG, WARNING, ERROR
from OFS.ObjectManager import customImporters
from gzip import GzipFile
from xml.dom.minidom import parse
from Products.CMFCore.Expression import Expression
import tarfile
from urllib import pathname2url, url2pathname
from difflib import unified_diff


# those attributes from CatalogMethodTemplateItem are kept for
# backward compatibility
catalog_method_list = ('_is_catalog_list_method_archive',
                       '_is_uncatalog_method_archive',
                       '_is_clear_method_archive',
                       '_is_filtered_archive',)

catalog_method_filter_list = ('_filter_expression_archive',
                              '_filter_expression_instance_archive',
                              '_filter_type_archive',)

def _getCatalog(acquisition_context):
  """
    Return the id of the SQLCatalog which correspond to the current BT.
  """
  catalog_method_id_list = acquisition_context.getTemplateCatalogMethodIdList()
  if len(catalog_method_id_list) == 0:
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
  if hasattr(aq_base(obj), 'uid'):
    obj.uid = None
  for subobj in obj.objectValues():
    _recursiveRemoveUid(subobj)

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


def getChainByType(context):
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
    Class archiving business template into a folder tree
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
    # Normalize the paths to eliminate the effect of double-slashes.
    self.file_list = [os.path.normpath(f) for f in file]
    path = os.path.normpath(path)
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
      if '.svn' in info.name.split('/'):
        continue
      if class_name in info.name.split('/'):
        if info.isreg():
          file = tar.extractfile(info)
          tar_file_name = info.name.startswith('./') and info.name[2:] or \
              info.name
          folders = string.split(tar_file_name, os.sep)
          file_name = (os.sep).join(folders[2:])
          if '%' in file_name:
            file_name = url2pathname(file_name)
          klass._importFile(file_name, file)
          file.close()
    tar.close()
    io.close()

class TemplateConditionError(Exception): pass
class TemplateConflictError(Exception): pass
class BusinessTemplateMissingDependency(Exception): pass

class BaseTemplateItem(Implicit, Persistent):
  """
    This class is the base class for all template items.
  """

  def __init__(self, id_list, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    self._objects = PersistentMapping()
    for id in id_list:
      if id is not None and id != '':
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


  def trash(self, context, new_item, **kw):
    # trash is quite similar to uninstall.
    return self.uninstall(context, new_item=new_item, trash=1, **kw)

  def export(self, context, bta, **kw):
    pass

  def getKeys(self):
    return self._objects.keys()

  def importFile(self, bta, **kw):
    bta.importFiles(klass=self)

  def removeProperties(self, obj):
    """
    Remove unneeded properties for export
    """
    if hasattr(aq_base(obj), '_dav_writelocks'):
      del aq_base(obj)._dav_writelocks
    if hasattr(obj, '__ac_local_roles__'):
      # remove local roles
      obj.__ac_local_roles__ = None
    if hasattr(obj, '_owner'):
      obj._owner = None
    if hasattr(aq_base(obj), 'uid'):
      obj.uid = None
    if hasattr(aq_base(obj), '_filepath'):
      obj._filepath = None
    if hasattr(aq_base(obj), 'workflow_history'):
      if hasattr(obj.__class__, 'workflow_history'):
        obj.workflow_history = None
      else:
        del obj.workflow_history
    if getattr(obj, 'meta_type', None) == 'Script (Python)':
      if hasattr(aq_base(obj), '_code'):
        obj._code = None
      if hasattr(aq_base(obj), 'Python_magic'):
        obj.Python_magic = None
    elif getattr(obj, 'meta_type', None) == 'ERP5 PDF Form' :
      if not obj.getProperty('business_template_include_content', 1) :
        obj.deletePdfContent()
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
      for id in id_list :
        if id != '':
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
      if id_list:
        self.build_sub_objects(context, id_list, relative_url)
        for id_ in list(id_list):
          obj._delObject(id_)
      if hasattr(aq_base(obj), 'groups'):
        obj.groups = groups
      self._objects[relative_url] = obj
      obj.wl_clearLocks()
    return sub_list

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
      obj = self.removeProperties(obj)
      id_list = obj.objectIds()
      if hasattr(aq_base(obj), 'groups'):
        # we must keep groups because it's erased when we delete subobjects
        groups = deepcopy(obj.groups)
      if len(id_list) > 0:
        self.build_sub_objects(context, id_list, relative_url)
        for id_ in list(id_list):
          obj._delObject(id_)
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
    __traceback_info__ = 'Importing %s' % file_name
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
          new_object = self.removeProperties(new_object)
          old_object = self.removeProperties(old_object)
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

  def _backupObject(self, action, trashbin, container_path, object_id, **kw):
    """
      Backup the object in portal trash if necessery and return its subobjects
    """
    subobjects_dict = {}
    if trashbin is None: # must return subobjects
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
      subobjects_dict = self.portal_trash.backupObject(trashbin, container_path, object_id, save=1, **kw)
    elif action == 'install':
      subobjects_dict = self.portal_trash.backupObject(trashbin, container_path, object_id, save=0, **kw)
    return subobjects_dict

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
      groups = {}
      old_groups = {}
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
          action = 'backup'
          # get subobjects in path
          path_list = path.split('/')
          container_path = path_list[:-1]
          object_id = path_list[-1]
          try:
            container = portal.unrestrictedTraverse(container_path)
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
              if container_container.meta_type == 'ERP5 Catalog':
                container_container.manage_addProduct['ZSQLCatalog'].manage_addSQLCatalog(id=container_path[-1], title='')
                if len(container_container.objectIds()) == 1:
                  container_container.default_sql_catalog_id = container_path[-1]
                container = portal.unrestrictedTraverse(container_path)
            else:
              raise
          container_ids = container.objectIds()
          subobjects_dict = {}
          # Object already exists
          if object_id in container_ids:
            old_obj = container._getOb(object_id)
            if hasattr(aq_base(old_obj), 'groups'):
              # we must keep original order groups
              # from old form in case we keep some
              # old widget, thus we can readd them in
              # the right order group
              old_groups[path] = deepcopy(old_obj.groups)
            subobjects_dict = self._backupObject(action, trashbin,
                                                 container_path, object_id)
            container.manage_delObjects([object_id])
          # install object
          obj = self._objects[path]
          if getattr(obj, 'meta_type', None) == 'Script (Python)':
            if getattr(obj, '_code') is None:
              obj._compile()
          if hasattr(aq_base(obj), 'groups'):
            # we must keep original order groups
            # because they change when we add subobjects
            groups[path] = deepcopy(obj.groups)
          # copy the object
          obj = obj._getCopy(container)
          container._setObject(object_id, obj)
          obj = container._getOb(object_id)
          # mark a business template installation so in 'PortalType_afterClone' scripts
          # we can implement logical for reseting or not attributes (i.e reference).
          self.REQUEST.set('is_business_template_installation', 1)
          obj.manage_afterClone(obj)
          obj.wl_clearLocks()
          # if portal types upgrade, set backup properties
          if getattr(obj, 'meta_type', None) == 'ERP5 Type Information' and \
              len(subobjects_dict) > 0:
            setattr(obj, 'allowed_content_types',
                    subobjects_dict['allowed_content_type_list'] or [])
            setattr(obj, 'hidden_content_type_list',
                    subobjects_dict['hidden_content_type_list'] or [])
            setattr(obj, 'property_sheet_list',
                    subobjects_dict['property_sheet_list'] or [])
            setattr(obj, 'base_category_list',
                    subobjects_dict['base_category_list'] or [])
            setattr(obj, '_roles', subobjects_dict['roles_list'] or [])
            # set actions
            action_list = subobjects_dict['action_list']
            for action in action_list:
              obj.addAction(id = action.id
                            , name = action.title
                            , action = action.action.text
                            , condition = action.getCondition()
                            , permission = action.permissions
                            , category = action.category
                            , visible = action.visible
                            , icon = getattr(action, 'icon', None) and action.icon.text or ''
                            , priority = action.priority
                            )
            # set workflow chain
            wf_chain = subobjects_dict['workflow_chain']
            chain_dict = getChainByType(context)[1]
            default_chain = ''
            chain_dict['chain_%s' % (object_id)] = wf_chain
            context.portal_workflow.manage_changeWorkflows(default_chain, props=chain_dict)
          # import sub objects if there is
          elif len(subobjects_dict) > 0:
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
            fixZSQLMethod(portal, obj)
      # now put original order group
      # we remove object not added in forms
      # we put old objects we have kept
      for path in groups.keys():
        new_groups_dict = groups[path]
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
            for group_id in new_groups_dict.keys():
              group_values = new_groups_dict[group_id]
              if widget_id in group_values:
                widget_in_form = 1
                break
            # if not, add it in the same groups
            # defined on the former form
            previous_group_id = None
            if not widget_in_form:
              for old_group_id in old_groups_dict.keys():
                old_group_values = old_groups_dict[old_group_id]
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
          for group_id in new_groups_dict.keys():
            for widget_id in new_groups_dict[group_id]:
              if widget_id not in widget_id_list:
                # if we don't find the widget id in the form
                # remove it fro the group
                new_groups_dict[group_id].remove(widget_id)
          # now set new group object
          obj.groups = new_groups_dict
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
          fixZSQLMethod(portal, obj)

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
        if container.aq_parent.meta_type == 'ERP5 Catalog' and len(container.objectIds()) == 0:
          # We are removing a ZSQLMethod, remove the SQLCatalog if empty
          container.getParentValue().manage_delObjects([container.id])
      except (NotFound, KeyError, BadRequest):
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
          container = portal.unrestrictedTraverse(container_path)
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
      if '**' in path:
        include_subobjects = 1
      for relative_url in self._resolvePath(p, [], path.split('/')):
        obj = p.unrestrictedTraverse(relative_url)
        obj = obj._getCopy(context)
        obj = obj.__of__(context)
        _recursiveRemoveUid(obj)
        id_list = obj.objectIds()
        obj = self.removeProperties(obj)
        if hasattr(aq_base(obj), 'groups'):
          # we must keep groups because it's ereased when we delete subobjects
          groups = deepcopy(obj.groups)
        if len(id_list) > 0:
          if include_subobjects:
            self.build_sub_objects(context, id_list, relative_url)
          for id_ in list(id_list):
            obj._delObject(id_)
        if hasattr(aq_base(obj), 'groups'):
          obj.groups = groups
        self._objects[relative_url] = obj
        obj.wl_clearLocks()

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
        portal.portal_workflow.doActionFor(
                      pref,
                      'enable_action',
                      wf_id='preference_workflow',
                      comment="Initialized during Business Template " \
                              "installation.")

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
      if id_list:
        self.build_sub_objects(context, id_list, relative_url)
        for id_ in list(id_list):
          obj._delObject(id_)
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      obj = p.unrestrictedTraverse(relative_url)
      obj = obj._getCopy(context)
      _recursiveRemoveUid(obj)
      obj = self.removeProperties(obj)
      include_sub_categories = obj.__of__(context).getProperty('business_template_include_sub_categories', 0)
      id_list = obj.objectIds()
      if len(id_list) > 0 and include_sub_categories:
        self.build_sub_objects(context, id_list, relative_url)
        for id_ in list(id_list):
          obj._delObject(id_)
      else:
        for id_ in list(id_list):
          obj._delObject(id_)
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    if context.getTemplateFormatVersion() == 1:
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
          object_uid = None
          subobjects_dict = {}
          if category_id in container_ids:
            object_uid = container[category_id].getUid()
            subobjects_dict = self._backupObject(action, trashbin, container_path, category_id)
            container.manage_delObjects([category_id])
          category = container.newContent(portal_type=obj.getPortalType(), id=category_id)
          if object_uid is not None:
            category.setUid(object_uid)
          for prop in obj.propertyIds():
            if prop not in ('id', 'uid'):
              try:
                prop_value = obj.getProperty(prop, evaluate=0)
              except TypeError: # the getter doesn't support evaluate=
                prop_value = obj.getProperty(prop)
              category.setProperty(prop, prop_value)
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
        for prop in obj.propertyIds():
          if prop not in ('id', 'uid'):
            try:
              prop_value = obj.getProperty(prop, evaluate=0)
            except TypeError: # the getter doesn't support evaluate=
              prop_value = obj.getProperty(prop)
            category.setProperty(prop, prop_value)
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

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = ObjectTemplateItem.preinstall(self, context, installed_bt, **kw)
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
              modified_object_list.update({bt_obj_path: ['Modified', self.__class__.__name__[:-12]]})
    return modified_object_list

  def install(self, context, trashbin, **kw):
    ObjectTemplateItem.install(self, context, trashbin, **kw)
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      folder = p.unrestrictedTraverse(relative_url)
      for obj in folder.objectValues(spec=('Z SQL Method',)):
        fixZSQLMethod(p, obj)

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
            wf_id = path.split('/')[:2]
            modified_object_list.update({'/'.join(wf_id) : ['Modified', 'Workflow']})
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
            self._backupObject(action, trashbin, container_path, object_id, keep_subobjects=1)
            container.manage_delObjects([object_id])
          obj = self._objects[path]
          if getattr(obj, 'meta_type', None) == 'Script (Python)':
            if getattr(obj, '_code') is None:
              obj._compile()
          obj = obj._getCopy(container)
          container._setObject(object_id, obj)
          obj = container._getOb(object_id)
          obj.manage_afterClone(obj)
          obj.wl_clearLocks()
    else:
      ObjectTemplateItem.install(self, context, trashbin, **kw)


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
      obj = obj._getCopy(context)
      # remove actions and properties
      action_len = len(obj.listActions())
      obj.deleteActions(selections=range(action_len))
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
      if hasattr(obj, '_roles'):
        setattr(obj, '_roles', [])
      self._objects[relative_url] = obj
      obj.wl_clearLocks()

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

class PortalTypeWorkflowChainTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    # we can either specify nothing, +, - or = before the chain
    # this is used to know how to manage the chain
    # if nothing or +, chain is added to the existing one
    # if - chain is removed from the exisiting one
    # if = chain replaced the existing one
    p = context.getPortalObject()
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
      if chain_dict.has_key('chain_%s' % portal_type):
        if workflow[0] in ['+', '-', '=']:
          workflow_name = workflow[1:]
        else:
          workflow_name = workflow
        if workflow[0] != '-' and \
            workflow_name not in chain_dict['chain_%s' % portal_type]:
          raise NotFound, 'workflow %s not found in chain for portal_type %s'\
                % (workflow, portal_type)
        if self._objects.has_key(portal_type):
          # other workflow id already defined for this portal type
          self._objects[portal_type].append(workflow)
        else:
          self._objects[portal_type] = [workflow,]
      else:
        raise NotFound, 'portal type %s not found in workflow chain'\
                                                    % portal_type

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    xml_data = '<workflow_chain>'
    keys = self._objects.keys()
    keys.sort()
    for key in keys:
      workflow_list = self._objects[key]
      # XXX Not always a list
      if isinstance(workflow_list, str):
        workflow_list = [workflow_list]
      xml_data += os.linesep+' <chain>'
      xml_data += os.linesep+'  <type>%s</type>' %(key,)
      xml_data += os.linesep+'  <workflow>%s</workflow>' %(', '.join(workflow_list))
      xml_data += os.linesep+' </chain>'
    xml_data += os.linesep+'</workflow_chain>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=root_path)
    # export workflow chain
    xml_data = self.generateXml()
    bta.addObject(obj=xml_data, name='workflow_chain_type',  path=root_path)

  def install(self, context, trashbin, **kw):
    update_dict = kw.get('object_to_update')
    force = kw.get('force')
    # We now need to setup the list of workflows corresponding to
    # each portal type
    (default_chain, chain_dict) = getChainByType(context)
    # Set the default chain to the empty string is probably the
    # best solution, by default it is 'default_workflow', which is
    # not very usefull
    default_chain = ''
    for path in self._objects.keys():
      if update_dict.has_key(path) or force:
        if not force:
          action = update_dict[path]
          if action == 'nothing':
            continue
        path_splitted = path.split('/', 1)
        # XXX: to avoid crashing when no portal_type
        if len(path_splitted) < 2:
          continue
        portal_type = path_splitted[1]
        if chain_dict.has_key('chain_%s' % portal_type):
          old_chain_dict = chain_dict['chain_%s' % portal_type]
          # XXX we don't use the chain (Default) in erp5 so don't keep it
          if old_chain_dict != '(Default)' and old_chain_dict != '':
            old_chain_workflow_id_set = {}
            # get existent workflow id list
            for wf_id in old_chain_dict.split(', '):
              old_chain_workflow_id_set[wf_id] = 1
            # get new workflow id list
            for wf_id in self._objects[path].split(', '):
              if wf_id[0] == '-':
                # remove wf id if already present
                if old_chain_workflow_id_set.has_key(wf_id[1:]):
                  old_chain_workflow_id_set.pop(wf_id[1:])
              elif wf_id[0] == '=':
                # replace existing chain by this one
                old_chain_workflow_id_set = {}
                old_chain_workflow_id_set[wf_id[1:]] = 1
              # then either '+' or nothing, add wf id to the list
              elif wf_id[0] == '+':
                old_chain_workflow_id_set[wf_id[1:]] = 1
              else:
                old_chain_workflow_id_set[wf_id] = 1
            # create the new chain
            chain_dict['chain_%s' % portal_type] = ', '.join(
                                              old_chain_workflow_id_set.keys())
          else:
            chain_dict['chain_%s' % portal_type] = self._objects[path]
        else:
          chain_dict['chain_%s' % portal_type] = self._objects[path]
    context.portal_workflow.manage_changeWorkflows(default_chain,
                                                   props=chain_dict)

  def uninstall(self, context, **kw):
    (default_chain, chain_dict) = getChainByType(context)
    object_path = kw.get('object_path', None)
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._objects.keys()
    for path in object_keys:
      path_splitted = path.split('/', 1)
      if len(path_splitted) < 2:
        continue
      portal_type = path_splitted[1]
      id = 'chain_%s' % portal_type
      if id in chain_dict.keys():
        del chain_dict[id]
    context.portal_workflow.manage_changeWorkflows('', props=chain_dict)

  def _importFile(self, file_name, file):
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
      if 'portal_type_workflow_chain/' not in str(ptype):
        ptype = 'portal_type_workflow_chain/' + str(ptype)
      dict[str(ptype)] = str(workflow)
    self._objects = dict

# just for backward compatibility
PortalTypeTemplateWorkflowChainItem = PortalTypeWorkflowChainTemplateItem

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

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    dictio = self._objects
    xml_data = '<%s>' %(self.xml_tag,)
    keys = dictio.keys()
    keys.sort()
    for key in keys:
      allowed_list = dictio[key]
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

  def preinstall(self, context, installed_bt, **kw):
    modified_object_list = {}
    if context.getTemplateFormatVersion() == 1:
      portal = context.getPortalObject()
      new_keys = self._objects.keys()
      if installed_bt.id == 'installed_bt_for_diff':
        #must rename keys in dict if reinstall
        new_dict = PersistentMapping()
        for key in installed_bt._objects.keys():
          new_key = self.class_property+'/'+key
          new_dict[new_key] = installed_bt._objects[key]
        installed_bt._objects = new_dict
      for path in new_keys:
        if installed_bt._objects.has_key(path):
          # compare object to see it there is changes
          new_object = self._objects[path]
          old_object = installed_bt._objects[path]
          if new_object != old_object:
            modified_object_list.update({path : ['Modified', self.__class__.__name__[:-12]]})
        else: # new object
          modified_object_list.update({path : ['New', self.__class__.__name__[:-12]]})
      # get removed object
      old_keys = installed_bt._objects.keys()
      for path in old_keys:
        if path not in new_keys:
          modified_object_list.update({path : ['Removed', self.__class__.__name__[:-12]]})
    return modified_object_list

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
        except AttributeError:
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
    p = context.getPortalObject()
    pt = p.unrestrictedTraverse('portal_types')
    if object_path is not None:
      object_keys = [object_path]
    else:
      object_keys = self._objects.keys()
    for key in object_keys:
      try:
        portal_id = key.split('/')[-1]
        portal_type = pt._getOb(portal_id)
      except AttributeError:
        LOG("portal types not found : ", 100, portal_id)
        continue
      property_list = self._objects[key]
      original_property_list = list(getattr(portal_type,
                                    self.class_property, ()))
      for id in property_list:
        if id in original_property_list:
          original_property_list.remove(id)
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
    self._filter_expression_archive = PersistentMapping()
    self._filter_expression_instance_archive = PersistentMapping()
    self._filter_type_archive = PersistentMapping()

  def _extractMethodProperties(self, catalog, method_id):
    """Extracts properties for a given method in the catalog.
    Returns a mapping of property name -> boolean """
    method_properties = PersistentMapping()
    for prop in catalog._properties:
      if prop.get('select_variable') == 'getCatalogMethodIds':
        if prop['type'] == 'selection' and \
            getattr(catalog, prop['id']) == method_id:
          method_properties[prop['id']] = 1
        elif prop['type'] == 'multiple selection' and \
            method_id in getattr(catalog, prop['id']):
          method_properties[prop['id']] = 1
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
      self._method_properties[method_id] = self._extractMethodProperties(
                                                          catalog, method_id)
      self._is_filtered_archive[method_id] = 0
      if catalog.filter_dict.has_key(method_id):
        if catalog.filter_dict[method_id]['filtered']:
          self._is_filtered_archive[method_id] = \
                      catalog.filter_dict[method_id]['filtered']
          self._filter_expression_archive[method_id] = \
                      catalog.filter_dict[method_id]['expression']
          self._filter_expression_instance_archive[method_id] = \
                      catalog.filter_dict[method_id]['expression_instance']
          self._filter_type_archive[method_id] = \
                      catalog.filter_dict[method_id]['type']

  def export(self, context, bta, **kw):
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate, export', 0, 'no SQL catalog was available')
      return

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
      method_id = obj.id
      object_path = os.path.join(path, method_id+'.catalog_keys.xml')

      f = open(object_path, 'wt')
      xml_data = '<catalog_method>'

      for method_property, value in self._method_properties[method_id].items():
        xml_data += os.linesep+' <item key="%s" type="int">' %(method_property,)
        xml_data += os.linesep+'  <value>%s</value>' %(value,)
        xml_data += os.linesep+' </item>'

      if catalog.filter_dict.has_key(method_id):
        if catalog.filter_dict[method_id]['filtered']:
          xml_data += os.linesep+' <item key="_is_filtered_archive" type="int">'
          xml_data += os.linesep+'  <value>1</value>'
          xml_data += os.linesep+' </item>'
          for method in catalog_method_filter_list:
            value = getattr(self, method, '')[method_id]
            if method != '_filter_expression_instance_archive':
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
      f.write(xml_data)
      f.close()

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    obj = self._objects[path]
    xml_data = '<key_list>'
    obj.sort()
    for key in obj:
      xml_data += os.linesep+' <key>%s</key>' %(key)
    xml_data += os.linesep+'</key_list>'
    return xml_data

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

      # Restore catalog properties for methods
      if hasattr(self, '_method_properties'):
        for key in self._method_properties.get(method_id, {}).keys():
          old_value = getattr(catalog, key, None)
          if isinstance(old_value, str):
            setattr(catalog, key, method_id)
          elif isinstance(old_value, list) or isinstance(old_value, tuple):
            if method_id not in old_value:
              new_value = list(old_value) + [method_id]
              new_value.sort()
              setattr(catalog, key, tuple(new_value))

      # Restore filter
      if self._is_filtered_archive.get(method_id, 0):
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
      if context.getTemplateFormatVersion() == 1:
        values = self._objects.values()
      else:
        values = self._archive.values()
    else:
      try:
        value = self._archive[object_path]
      except KeyError:
        value = None
      if value is not None:
        values.append(value)
    for obj in values:
      method_id = obj.id
      # remove method references in portal_catalog
      for catalog_prop in catalog._properties:
        if catalog_prop.get('select_variable') == 'getCatalogMethodIds'\
            and catalog_prop['type'] == 'multiple selection':
          old_value = getattr(catalog, catalog_prop['id'], ())
          if method_id in old_value:
            new_value = list(old_value)
            new_value.remove(method_id)
            setattr(catalog, catalog_prop['id'], new_value)

      if catalog.filter_dict.has_key(method_id):
        del catalog.filter_dict[method_id]

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
    else:
      # recreate data mapping specific to catalog method
      path, name = os.path.split(file_name)
      id = string.split(name, '.')[0]
      xml = parse(file)
      method_list = xml.getElementsByTagName('item')
      for method in method_list:
        key = method.getAttribute('key')
        key_type = str(method.getAttribute('type'))
        if key_type == "str":
          if len(method.getElementsByTagName('value')[0].childNodes):
            value = str(method.getElementsByTagName('value')[0].childNodes[0].data)
          else:
            value = ''
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
          dict = getattr(self, key, {})
          dict[id] = value
        else:
          # new style key
          self._method_properties.setdefault(id, PersistentMapping())[key] = 1

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

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      relative_url, value = id.split(' | ')
      obj = p.unrestrictedTraverse(relative_url)
      for ai in obj.listActions():
        if getattr(ai, 'id') == value:
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
                    , icon = getattr(action, 'icon', None) \
                                      and action.icon.text or ''
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
      if  '|' in id:
        relative_url, value = id.split(' | ')
        key = 'id'
      else:
        relative_url, key, value = self._splitPath(id)
      obj = p.unrestrictedTraverse(relative_url, None)
      if obj is not None:
        action_list = obj.listActions()
        for index in range(len(action_list)):
          if getattr(action_list[index], key) == value:
            obj.deleteActions(selections=(index,))
            break
      else :
        LOG('BusinessTemplate', 100,
            'unable to uninstall action at %s, ignoring' % relative_url )
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
      type_roles_obj = getattr(obj, '_roles', ())
      type_role_list = []
      for role in type_roles_obj:
        type_role_dict = {}
        # uniq
        for property in ('id', 'title', 'description',
            'priority', 'base_category_script'):
          prop_value = getattr(role, property)
          if prop_value:
            type_role_dict[property] = prop_value
        # condition
        prop_value = getattr(role, 'condition')
        if prop_value:
          type_role_dict['condition'] = prop_value.text
        # multi
        for property in ('category', 'base_category'):
          prop_value_list = []
          for prop_value in getattr(role, property):
            prop_value_list.append(prop_value)
          type_role_dict[property] = prop_value_list
        type_role_list.append(type_role_dict)
      self._objects[relative_url] = type_role_list

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    type_role_list = self._objects[path]
    xml_data = '<type_roles>'
    for role in type_role_list:
      xml_data += os.linesep+"  <role id='%s'>" % role['id']
      # uniq
      for property in ('title', 'description', 'condition', 'priority',
          'base_category_script'):
        prop_value = role.get(property)
        if prop_value:
          xml_data += os.linesep+"   <property id='%s'>%s</property>" % \
              (property, prop_value)
      # multi
      for property in ('category', 'base_category'):
        for prop_value in role.get(property, []):
          xml_data += os.linesep+"   <multi_property "\
          "id='%s'>%s</multi_property>" % (property, prop_value)
      xml_data += os.linesep+"  </role>"
    xml_data += os.linesep+'</type_roles>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=root_path)
    for key in self._objects.keys():
      xml_data = self.generateXml(key)
      name = key.split('/', 1)[1]
      bta.addObject(obj=xml_data, name=name, path=root_path)

  def _importFile(self, file_name, file):
    type_roles_list = []
    xml = parse(file)
    xml_type_roles_list = xml.getElementsByTagName('role')
    for role in xml_type_roles_list:
      id = role.getAttribute('id')
      type_role_property_dict = {'id':id}
      # uniq
      property_list = role.getElementsByTagName('property')
      for property in property_list:
        property_id = property.getAttribute('id').encode()
        if property.hasChildNodes():
          property_value = property.childNodes[0].data.encode('utf_8', 'backslashreplace')
          if property_id == 'priority':
            property_value = float(property_value)
          type_role_property_dict[property_id] = property_value
      # multi
      multi_property_list = role.getElementsByTagName('multi_property')
      for property in multi_property_list:
        property_id = property.getAttribute('id').encode()
        if not type_role_property_dict.has_key(property_id):
          type_role_property_dict[property_id] = []
        if property.hasChildNodes():
          property_value = property.childNodes[0].data.encode('utf_8', 'backslashreplace')
          type_role_property_dict[property_id].append(property_value)
      type_roles_list.append(type_role_property_dict)
    self._objects['portal_type_roles/'+file_name[:-4]] = type_roles_list

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
        setattr(obj, '_roles', []) # reset roles before applying
        type_roles_list = self._objects[roles_path] or []
        for type_role_property_dict in type_roles_list:
          obj._roles.append(RoleInformation(**type_role_property_dict))

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
        setattr(obj, '_roles', [])
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

  # Function to generate XML Code Manually
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

  # Function to generate XML Code Manually
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
          # the type of the permission defined if we use acquired or not
          if type(perm[1]) == type([]):
            ptype = "list"
          else:
            ptype = "tuple"
          xml_data += os.linesep+"  <permission type='%s'>" %(ptype,)
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
          perm_type = perm.getAttribute('type').encode() or None
          name_elt = perm.getElementsByTagName('name')[0]
          name_node = name_elt.childNodes[0]
          name = name_node.data
          role_list = perm.getElementsByTagName('role')
          rlist = []
          for role in role_list:
            role_node = role.childNodes[0]
            role = role_node.data
            rlist.append(str(role))
          if perm_type == "list" or perm_type is None:
            perm_tuple = (str(name), list(rlist))
          else:
            perm_tuple = (str(name), tuple(rlist))
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
            globals()[self.local_file_writer_name](name, text, create=0)
          except IOError, error:
            LOG("BusinessTemplate.py", WARNING, "Cannot install class %s on file system" %(name,))
            if error.errno :
              raise
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

class ConstraintTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalConstraint'
  local_file_writer_name = 'writeLocalConstraint'
  local_file_importer_name = 'importLocalConstraint'
  local_file_remover_name = 'removeLocalConstraint'

class ExtensionTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalExtension'
  local_file_writer_name = 'writeLocalExtension'
  # Extension needs no import
  local_file_importer_name = None
  local_file_remover_name = 'removeLocalExtension'

class TestTemplateItem(DocumentTemplateItem):
  local_file_reader_name = 'readLocalTest'
  local_file_writer_name = 'writeLocalTest'
  # Test needs no import
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
      if installed_bt.id == 'installed_bt_for_diff':
        #must rename keys in dict if reinstall
        new_dict = PersistentMapping()
        old_keys = ()
        if len(installed_bt._objects.values()) > 0:
          old_keys = installed_bt._objects.values()[0]
        for key in old_keys:
          new_dict[key] = ''
        installed_bt._objects = new_dict
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_result_keys = list(catalog.sql_search_result_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_result_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Result key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_related_keys = list(catalog.sql_catalog_related_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_related_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Related key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_search_result_tables = list(catalog.sql_search_tables)
    key_list = []
    for key in self._archive.keys():
      if key in sql_search_result_tables:
        key_list.append(key)
      else:
        raise NotFound, 'Result table "%r" not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'result_table_list'] = key_list

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
    catalog = _getCatalogValue(self)
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
      catalog.sql_search_tables = tuple(sql_search_tables)

  def uninstall(self, context, **kw):
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_keyword_keys = list(catalog.sql_catalog_keyword_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_keyword_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Keyword key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_full_text_keys = list(catalog.sql_catalog_full_text_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_full_text_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Fulltext key "%r" not found in catalog' %(key,)
    if len(key_list) > 0:
      self._objects[self.__class__.__name__+os.sep+'full_text_key_list'] = key_list

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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_request_keys = list(catalog.sql_catalog_request_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_request_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Request key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_multivalue_keys = list(catalog.sql_catalog_multivalue_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_multivalue_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Multivalue key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    catalog = _getCatalogValue(self)
    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return
    sql_catalog_topic_search_keys = list(catalog.sql_catalog_topic_search_keys)
    key_list = []
    for key in self._archive.keys():
      if key in sql_catalog_topic_search_keys:
        key_list.append(key)
      else:
        raise NotFound, 'Topic key "%r" not found in catalog' %(key,)
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
    catalog = _getCatalogValue(self)
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
    catalog = _getCatalogValue(self)
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

  # Function to generate XML Code Manually
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
    for lang_key in self._archive.keys():
      if '|' in lang_key:
        lang, catalog = lang_key.split(' | ')
      else: # XXX backward compatibilty
        lang = lang_key
        catalog = 'erp5_ui'
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
      f = open(path+os.sep+'translation.po', 'wt')
      f.write(str(obj))
      f.close()

  def _importFile(self, file_name, file):
    if os.path.split(file_name)[1] == 'translation.po':
      text = file.read()
      self._objects[file_name[:-3]] = text

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
      group_local_roles_dict = getattr(obj, '__ac_local_group_roles__',
                                        {}) or {}
      self._objects[path] = (local_roles_dict, group_local_roles_dict)

  # Function to generate XML Code Manually
  def generateXml(self, path=None):
    local_roles_dict, group_local_roles_dict = self._objects[path]
    local_roles_keys = local_roles_dict.keys()
    group_local_roles_keys = group_local_roles_dict.keys()
    local_roles_keys.sort()
    group_local_roles_keys.sort()
    # local roles
    xml_data = '<local_roles_item>'
    xml_data += os.linesep+' <local_roles>'
    for key in local_roles_keys:
      xml_data += os.linesep+"  <role id='%s'>" %(key,)
      tuple = local_roles_dict[key]
      for item in tuple:
        xml_data += os.linesep+"   <item>%s</item>" %(item,)
      xml_data += os.linesep+"  </role>"
    xml_data += os.linesep+' </local_roles>'
    # group local roles
    xml_data += os.linesep+' <group_local_roles>'
    for key in group_local_roles_keys:
      xml_data += os.linesep+"  <role id='%s'>" %(key,)
      tuple = group_local_roles_dict[key]
      for item in tuple:
        xml_data += os.linesep+"   <item>%s</item>" %(item,)
      xml_data += os.linesep+"  </role>"
    xml_data += os.linesep+' </group_local_roles>'
    xml_data += os.linesep+'</local_roles_item>'
    return xml_data

  def export(self, context, bta, **kw):
    if len(self._objects.keys()) == 0:
      return
    root_path = os.path.join(bta.path, self.__class__.__name__)
    bta.addFolder(name=root_path)
    for key in self._objects.keys():
      xml_data = self.generateXml(key)

      folders, id = os.path.split(key)
      encode_folders = []
      for folder in folders.split('/')[1:]:
        if '%' not in folder:
          encode_folders.append(pathname2url(folder))
        else:
          encode_folders.append(folder)
      path = os.path.join(root_path, (os.sep).join(encode_folders))
      bta.addFolder(name=path)
      bta.addObject(obj=xml_data, name=id, path=path)

  def _importFile(self, file_name, file):
    xml = parse(file)
    # local roles
    local_roles = xml.getElementsByTagName('local_roles')[0]
    local_roles_list = local_roles.getElementsByTagName('role')
    local_roles_dict = {}
    for role in local_roles_list:
      id = role.getAttribute('id')
      item_type_list = []
      item_list = role.getElementsByTagName('item')
      for item in item_list:
        item_type_list.append(str(item.childNodes[0].data))
      local_roles_dict[id] = item_type_list
    # group local roles
    group_local_roles = xml.getElementsByTagName('group_local_roles')[0]
    local_roles_list = group_local_roles.getElementsByTagName('role')
    group_local_roles_dict = {}
    for role in local_roles_list:
      id = role.getAttribute('id')
      item_type_list = []
      item_list = role.getElementsByTagName('item')
      for item in item_list:
        item_type_list.append(str(item.childNodes[0].data))
      group_local_roles_dict[id] = item_type_list
    self._objects['local_roles/'+file_name[:-4]] = (local_roles_dict, group_local_roles_dict)

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
      local_roles_dict, group_local_roles_dict = self._objects[roles_path]
      setattr(obj, '__ac_local_roles__', local_roles_dict)
      setattr(obj, '__ac_local_group_roles__', group_local_roles_dict)

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    for roles_path in self._objects.keys():
      path = roles_path.split('/')[1:]
      obj = p.unrestrictedTraverse(path)
      setattr(obj, '__ac_local_roles__', {})
      setattr(obj, '__ac_local_group_roles__', {})

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
    isPortalContent = 1
    isRADContent = 1

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
    # We want to have:
    #  * path after module, because path can be module content
    #  * path after categories, because path can be categories content
    #  * skin after paths, because we can install a custom connection string as
    #       path and use it with SQLMethods in a skin.
    #    ( and more )
    _item_name_list = [
      '_product_item',
      '_property_sheet_item',
      '_constraint_item',
      '_document_item',
      '_extension_item',
      '_test_item',
      '_role_item',
      '_message_translation_item',
      '_workflow_item',
      '_site_property_item',
      '_portal_type_item',
      '_portal_type_workflow_chain_item',
      '_portal_type_allowed_content_type_item',
      '_portal_type_hidden_content_type_item',
      '_portal_type_property_sheet_item',
      '_portal_type_base_category_item',
      '_category_item',
      '_module_item',
      '_path_item',
      '_skin_item',
      '_preference_item',
      '_action_item',
      '_portal_type_roles_item',
      '_local_roles_item',
      '_catalog_method_item',
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

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRevision')
    def getRevision(self):
      """returns the revision property.
      This is a workaround for #461.
      """
      return self._baseGetRevision()

    def updateRevisionNumber(self):
        """Increment bt revision number.
        """
        revision_number = self.getRevision()
        if revision_number is None or revision_number.strip() == '':
          revision_number = 1
        else:
          revision_number = int(revision_number)+1
        self.setRevision(revision_number)

    security.declareProtected(Permissions.ManagePortal, 'build')
    def build(self, no_action=0):
      """
        Copy existing portal objects to self
      """
      if no_action: return
        # this is use at import of Business Template to get the status built
      # Make sure that everything is sane.
      self.clean()

      # Update revision number
      # <christophe@nexedi.com>
      self.updateRevisionNumber()

      self._setTemplateFormatVersion(1)

      # Store all data
      self._portal_type_item = \
          PortalTypeTemplateItem(self.getTemplatePortalTypeIdList())
      self._portal_type_workflow_chain_item = \
          PortalTypeWorkflowChainTemplateItem(self.getTemplatePortalTypeWorkflowChainList())
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
      self._portal_type_roles_item = \
          PortalTypeRolesTemplateItem(self.getTemplatePortalTypeRolesList())
      self._site_property_item = \
          SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._module_item = \
          ModuleTemplateItem(self.getTemplateModuleIdList())
      self._document_item = \
          DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._property_sheet_item = \
          PropertySheetTemplateItem(self.getTemplatePropertySheetIdList())
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
      self._local_roles_item = \
          LocalRolesTemplateItem(
               self.getTemplateLocalRolesList())

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

    def isCatalogUpdatable(self):
      """
      Return if catalog will be updated or not by business template installation
      """
      catalog_method = getattr(self, '_catalog_method_item', None)
      default_catalog = self.getPortalObject().portal_catalog.getSQLCatalog()
      my_catalog = _getCatalogValue(self)
      if default_catalog is not None and my_catalog is not None \
             and catalog_method is not None and self.getTemplateFormatVersion() == 1:
        if default_catalog.getId() == my_catalog.getId():
          # It is needed to update the catalog only if the default SQLCatalog is modified.
          for method_id in catalog_method._objects.keys():
            if 'related' not in method_id:
              # must update catalog
              return True
      return False

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
      if installed_bt is None:
        installed_bt_format = 0 # that will not check for modification
      else:
        installed_bt_format = installed_bt.getTemplateFormatVersion()

      # if reinstall business template, must compare to object in ZODB
      # and not to those in the installed Business Template because it is itself.
      # same if we make a diff and select only one business template
      reinstall = 0
      if installed_bt == self:
        reinstall = 1
        bt2 = self.portal_templates.manage_clone(ob=installed_bt, id='installed_bt_for_diff')
        # update portal types properties to get last modifications
        bt2.getPortalTypesProperties()
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
          if old_item is not None and hasattr(old_item, '_objects'):
            modified_object = new_item.preinstall(context=local_configuration, installed_bt=old_item)
            if len(modified_object) > 0:
              modified_object_list.update(modified_object)
          else:
            for path in new_item._objects.keys():
              modified_object_list.update({path : ['New', new_item.__class__.__name__[:-12]]})

      if reinstall:
        self.portal_templates.manage_delObjects(ids=['installed_bt_for_diff'])

      return modified_object_list

    def _install(self, force=1, object_to_update=None, **kw):
      """
        Install a new Business Template, if force, all will be upgraded or installed
        otherwise depends of dict object_to_update
      """
      if object_to_update is not None:
        force=0
      else:
        object_to_update = {}

      installed_bt = self.portal_templates.getInstalledBusinessTemplate(
                                                           self.getTitle())
      if installed_bt is not None:
        if installed_bt.getTemplateFormatVersion() == 0:
          force = 1
        installed_bt.replace(self)

      trash_tool = getToolByName(self, 'portal_trash', None)
      if trash_tool is None and self.getTemplateFormatVersion() == 1:
        raise AttributeError, 'Trash Tool is not installed'

      # Check the format of business template, if old, force install
      if self.getTemplateFormatVersion() == 0:
        force = 1

      if not force:
        self.checkDependencies()

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
            LOG('Business Template', 0, 'Updating Business Template Workflows')
            gen.setupWorkflow(site)
          return

      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)

      # always created a trash bin because we may to save object already present
      # but not in a previous business templates apart at creation of a new site
      if trash_tool is not None and (len(object_to_update) > 0 or len(self.portal_templates.objectIds()) > 1):
        trashbin = trash_tool.newTrashBin(self.getTitle(), self)
      else:
        trashbin = None

      # Install everything
      if len(object_to_update) > 0 or force:
        for item_name in self._item_name_list:
          item = getattr(self, item_name, None)
          if item is not None:
            item.install(local_configuration, force=force, object_to_update=object_to_update, trashbin=trashbin)

      # update catalog if necessary
      if force and self.isCatalogUpdatable():
        update_catalog = 1
      else:
        update_catalog = kw.get('update_catalog', 0)
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


      # update tools if necessary
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateTool():
        LOG('Business Template', 0, 'Updating Tools')
        gen.setup(site, 0, update=1)

      # check if we have to update business template workflow
      if self.getTitle() == 'erp5_core' and self.getTemplateUpdateBusinessTemplateWorkflow():
        LOG('Business Template', 0, 'Updating Business Template Workflows')
        gen.setupWorkflow(site)
        # XXX keep TM in case update of workflow doesn't work
        #         self._v_txn = WorkflowUpdateTM()
        #         self._v_txn.register(update=1, gen=gen, site=site)

      # remove trashbin if empty
      if trashbin is not None:
        if len(trashbin.objectIds()) == 0:
          trash_tool.manage_delObjects([trashbin.getId(),])

      if update_catalog:
        site.ERP5Site_reindexAll()

      # Update translation table, in case we added new portal types or
      # workflow states.
      update_translation = kw.get('update_translation', 0)
      if update_translation:
        site.ERP5Site_updateTranslationTable()

      # It is better to clear cache because the installation of a template
      # adds many new things into the portal.
      clearAllCache()

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
      clearAllCache()

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
        # XXX Why do we need to return a tuple ?
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

    def getTemplatePortalTypeWorkflowChainList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_workflow_chain')

    def getTemplatePathList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_path')

    def getTemplatePreferenceList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_preference')

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

    def getTemplatePortalTypeRolesList(self):
      """
      We have to set this method because we want an
      ordered list
      """
      return self._getOrderedList('template_portal_type_roles')

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
        raise TemplateConditionError, \
              'Business Template must be built before export'
      if self.getInstallationState() == 'installed':
        raise TemplateConditionError, \
              'Can not export installed Business Template'

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
        if id in ('id', 'uid', 'rid', 'sid', 'id_group', 'last_id',
                  'install_object_list_list', 'id_generator'):
          continue
        value = self.getProperty(id)
        if prop_type in ('text', 'string', 'int', 'boolean'):
          bta.addObject(obj=value, name=id, path=path+os.sep+'bt', ext='')
        elif prop_type in ('lines', 'tokens'):
          bta.addObject(obj=str(os.linesep).join(value), name=id,
                        path=path+os.sep+'bt', ext='')

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
      self._portal_type_workflow_chain_item = \
          PortalTypeWorkflowChainTemplateItem(self.getTemplatePortalTypeWorkflowChainList())
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
      self._portal_type_roles_item = \
          PortalTypeRolesTemplateItem(self.getTemplatePortalTypeRolesList())
      self._site_property_item = \
          SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._module_item = \
          ModuleTemplateItem(self.getTemplateModuleIdList())
      self._document_item = \
          DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._property_sheet_item = \
          PropertySheetTemplateItem(self.getTemplatePropertySheetIdList())
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
      self._path_item = \
               PathTemplateItem(self.getTemplatePathList())
      self._preference_item = \
               PreferenceTemplateItem(self.getTemplatePreferenceList())
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
      self._local_roles_item = \
          LocalRolesTemplateItem(
               self.getTemplateLocalRolesList())

      for item_name in self._item_name_list:
        getattr(self, item_name).importFile(bta)

    #By christophe Dumez <christophe@nexedi.com>
    def getItemsList(self):
      """Return list of items in business template
      """
      items_list = []
      for item_name in self._item_name_list:
        item = getattr(self, item_name, None)
        if item is not None:
          items_list.extend(item.getKeys())
      return items_list

    #By christophe Dumez <christophe@nexedi.com>
    def checkDependencies(self):
      """
       Check if all the dependencies of the business template
       are installed. Raise an exception with the list of
       missing dependencies if some are missing
      """
      missing_dep_list = []
      dependency_list = self.getDependencyList()
      if len(dependency_list)!=0:
        for dependency_couple in dependency_list:
          dependency_couple_list = dependency_couple.split(' ')
          dependency = dependency_couple_list[0]
          if dependency in (None, ''):
            continue
          version_restriction = None
          if len(dependency_couple_list) > 1:
            version_restriction = dependency_couple_list[1][1:-1]
          installed_bt = self.portal_templates.getInstalledBusinessTemplate(dependency)
          if (not self.portal_templates.IsOneProviderInstalled(dependency)) \
             and ((installed_bt is None) \
                  or (version_restriction not in (None, '') and
                     (not self.portal_templates.compareVersionStrings(installed_bt.getVersion(), version_restriction)))):
            missing_dep_list.append((dependency, version_restriction or ''))
      if len(missing_dep_list) != 0:
        raise BusinessTemplateMissingDependency, 'Impossible to install, please install the following dependencies before: %s'%repr(missing_dep_list)

    def diffObject(self, REQUEST, **kw):
      """
        Make a diff between an object in the Business Template
        and the same in the Business Template installed in the site
      """

      class_name_dict = {
        'Product' : '_product_item',
        'PropertySheet' : '_property_sheet_item',
        'Constraint' : '_constraint_item',
        'Document' : '_document_item',
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
        'Path' : '_path_item',
        'Preference' : '_preference_item',
        'Action' : '_action_item',
        'PortalTypeRoles' : '_portal_type_roles_item',
        'LocalRoles' : '_local_roles_item',
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

      # Get objects
      item_name = class_name_dict[object_class]

      new_bt =self
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
        bt2 = self.portal_templates.manage_clone(ob=installed_bt, id='installed_bt_for_diff')
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
                     '_skin_item', '_action_item',]

      # Not considered as objects by Zope (will be exported into XML manually)
      # XXX Bad naming
      item_list_2 = ['_site_property_item', '_module_item',
                     '_catalog_result_key_item', '_catalog_related_key_item',
                     '_catalog_result_table_item',
                     '_catalog_keyword_key_item',
                     '_catalog_full_text_key_item',
                     '_catalog_request_key_item',
                     '_catalog_multivalue_key_item',
                     '_catalog_topic_key_item',
                     '_portal_type_allowed_content_type_item',
                     '_portal_type_hidden_content_type_item',
                     '_portal_type_property_sheet_item',
                     '_portal_type_roles_item',
                     '_portal_type_base_category_item',
                     '_local_roles_item',
                     '_portal_type_workflow_chain_item',]

      # Text objects (no need to export them into XML)
      # XXX Bad naming
      item_list_3 = ['_document_item', '_property_sheet_item',
                     '_constraint_item', '_extension_item',
                     '_test_item', '_message_translation_item',]

      if item_name in item_list_1:
        f1 = StringIO() # for XML export of New Object
        f2 = StringIO() # For XML export of Installed Object
        # Remove unneeded properties
        new_object = new_item.removeProperties(new_object)
        installed_object = installed_item.removeProperties(installed_object)
        # XML Export in memory
        OFS.XMLExportImport.exportXML(new_object._p_jar, new_object._p_oid, f1)
        OFS.XMLExportImport.exportXML(installed_object._p_jar, installed_object._p_oid, f2)
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
        new_obj_lines = new_object.splitlines()
        installed_obj_lines = installed_object.splitlines()
        diff_list = list(unified_diff(installed_obj_lines, new_obj_lines, tofile=new_bt.getId(), fromfile=installed_bt.getId(), lineterm=''))
        if len(diff_list) != 0:
          diff_msg += '\n\nObject %s diff :\n' % (object_id,)
          diff_msg += '\n'.join(diff_list)
        else:
          diff_msg = 'No diff'

      else: # Added By <christophe@nexedi.com>
        diff_msg += 'Unsupported file !'

      if compare_to_zodb:
        self.portal_templates.manage_delObjects(ids=['installed_bt_for_diff'])

      return diff_msg


    def getPortalTypesProperties(self, **kw):
      """
      Fill field about properties for each portal type
      """
      wtool = self.getPortalObject().portal_workflow
      ttool = self.getPortalObject().portal_types
      bt_allowed_content_type_list = list(getattr(self, 'template_portal_type_allowed_content_type', []) or [])
      bt_hidden_content_type_list = list(getattr(self, 'template_portal_type_hidden_content_type', []) or [])
      bt_property_sheet_list = list(getattr(self, 'template_portal_type_property_sheet', []) or [])
      bt_base_category_list = list(getattr(self, 'template_portal_type_base_category', []) or [])
      bt_action_list = list(getattr(self, 'template_action_path', []) or [])
      bt_portal_types_id_list = list(self.getTemplatePortalTypeIdList())
      bt_portal_type_roles_list =  list(getattr(self, 'template_portal_type_roles', []) or [])
      bt_wf_chain_list = list(getattr(self, 'template_portal_type_workflow_chain', []) or [])

      p = self.getPortalObject()
      for id in bt_portal_types_id_list:
        portal_type = ttool.getTypeInfo(id)
        if portal_type is None:
          continue
        if len(getattr(portal_type, '_roles', ())) > 0:
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
        if hasattr(portal_type, 'listActions'):
          action_list = [x.getId() for x in portal_type.listActions()]

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

      self.setProperty('template_portal_type_workflow_chain', bt_wf_chain_list)
      self.setProperty('template_portal_type_roles', bt_portal_type_roles_list)
      self.setProperty('template_portal_type_allowed_content_type', bt_allowed_content_type_list)
      self.setProperty('template_portal_type_hidden_content_type', bt_hidden_content_type_list)
      self.setProperty('template_portal_type_property_sheet', bt_property_sheet_list)
      self.setProperty('template_portal_type_base_category', bt_base_category_list)
      self.setProperty('template_action_path', bt_action_list)
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

# Block acquisition on all _item_name_list properties by setting
# a default class value to None
for key in BusinessTemplate._item_name_list:
  setattr(BusinessTemplate, key, None)

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

