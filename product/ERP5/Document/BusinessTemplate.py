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
from Products.ERP5Type.Utils import readLocalPropertySheet, writeLocalPropertySheet, importLocalPropertySheet, removeLocalPropertySheet
from Products.ERP5Type.Utils import readLocalExtension, writeLocalExtension, removeLocalExtension
from Products.ERP5Type.Utils import readLocalTest, writeLocalTest, removeLocalTest
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, importLocalDocument, removeLocalDocument
from Products.ERP5Type.XMLObject import XMLObject
import cStringIO
import fnmatch
import re
from Products.ERP5Type.Cache import clearCache

from zLOG import LOG

class TemplateConflictError(Exception): pass

class BaseTemplateItem(Implicit, Persistent):
  """
    This class is the base class for all template items.
  """

  def __init__(self, id_list, **kw):
    self.__dict__.update(kw)
    self._archive = PersistentMapping()
    for id in id_list:
      if not id: continue
      self._archive[id] = None

  def build(self, context, **kw):
    pass

  def install(self, context, **kw):
    pass

  def uninstall(self, context, **kw):
    pass

  def trash(self, context, new_item, **kw):
    # trash is quite similar to uninstall.
    return self.uninstall(context, new_item=new_item, trash=1, **kw)

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

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      object = p.unrestrictedTraverse(relative_url)
      #if not object.cb_isCopyable():
      #  raise CopyError, eNotSupported % escape(relative_url)
      object = object._getCopy(context)
      self._archive[relative_url] = object
      object.wl_clearLocks()

  def _backupObject(self, container, object_id, **kw):
    container_ids = container.objectIds()
    n = 0
    new_object_id = object_id
    while new_object_id in container_ids:
      n = n + 1
      new_object_id = '%s_btsave_%s' % (object_id, n)
    container.manage_renameObject(object_id, new_object_id)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    portal = context.getPortalObject()
    for relative_url,object in self._archive.items():
      container_path = relative_url.split('/')[0:-1]
      object_id = relative_url.split('/')[-1]
      container = portal.unrestrictedTraverse(container_path)
      #LOG('Installing' , 0, '%s in %s with %s' % (self.id, container.getPhysicalPath(), self.export_string))
      container_ids = container.objectIds()
      if object_id in container_ids:    # Object already exists
        self._backupObject(container, object_id)
      # Set a hard link
      #if not object.cb_isCopyable():
      #    raise CopyError, eNotSupported % escape(relative_url)
      object = object._getCopy(container)
      container._setObject(object_id, object)
      object = container._getOb(object_id)
      object.manage_afterClone(object)
      object.wl_clearLocks()
      if object.meta_type in ('Z SQL Method',):
        # It is necessary to make sure that the sql connection in this method is valid.
        sql_connection_list = portal.objectIds(spec=('Z MySQL Database Connection',))
        if object.connection_id not in sql_connection_list:
          object.connection_id = sql_connection_list[0]

  def uninstall(self, context, **kw):
    portal = context.getPortalObject()
    trash = kw.get('trash', 0)
    for relative_url in self._archive.keys():
      container_path = relative_url.split('/')[0:-1]
      object_id = relative_url.split('/')[-1]
      try:
        container = portal.unrestrictedTraverse(container_path)
        if trash:
          self._backupObject(container, object_id)
        else:
          if object_id in container.objectIds():
            container.manage_delObjects([object_id])
      except:
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
      object = folder._getOb(id)
      return self._resolvePath(object, relative_url_list + [id], id_list[1:])
      
    path_list = []
    for object_id in fnmatch.filter(folder.objectIds(), id):
      path_list.extend(self._resolvePath(folder._getOb(object_id), relative_url_list + [object_id], id_list[1:]))
    return path_list
      
  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for path in self._path_archive.keys():
      for relative_url in self._resolvePath(p, [], path.split('/')):
        object = p.unrestrictedTraverse(relative_url)
        #if not object.cb_isCopyable():
        #  raise CopyError, eNotSupported % escape(relative_url)
        object = object._getCopy(context)
        self._archive[relative_url] = object
        object.wl_clearLocks()


class CategoryTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, **kw):
    ObjectTemplateItem.__init__(self, id_list, **kw)
    self._light_archive = PersistentMapping()
    for id in id_list:
      self._light_archive[id] = None
    tool_id = 'portal_categories'
    id_list = self._archive.keys()
    self._archive.clear()
    for id in id_list:
      self._archive["%s/%s" % (tool_id, id)] = None

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    category_tool = p.portal_categories
    for relative_url in self._archive.keys():
      category = p.unrestrictedTraverse(relative_url)
      category_id = relative_url.split('/')[-1]
      #if not object.cb_isCopyable():
      #  raise CopyError, eNotSupported % escape(relative_url)
      category_copy = category._getCopy(context)
      include_sub_categories = category.getProperty('business_template_include_sub_categories', 1)
      if not include_sub_categories:
        id_list = category_copy.objectIds()
        if len(id_list) > 0:
          category_copy.manage_delObjects(list(id_list))
      self._archive[relative_url] = category_copy
      category_copy.wl_clearLocks()
      # No store attributes for light install
      mapping = PersistentMapping()
      mapping['id'] = category.getId()
      property_list = PersistentMapping()
      for property in [x for x in category.propertyIds() if x not in ('id','uid')]:
        property_list[property] = category.getProperty(property,evaluate=0)
      mapping['property_list'] = property_list
      #mapping['title'] = category.getTitle()
      self._light_archive[category_id] = mapping

  def install(self, context, light_install = 0, **kw):
    BaseTemplateItem.install(self, context, **kw)
    portal = context.getPortalObject()
    category_tool = portal.portal_categories
    tool_id = self.tool_id
    if light_install==0:
      ObjectTemplateItem.install(self, context, **kw)
    else:
      for category_id in self._light_archive.keys():
        if category_id in category_tool.objectIds():
          raise TemplateConflictError, 'the category %s already exists' % category_id
        category = category_tool.newContent(portal_type='Base Category',id=category_id)
        property_list = self._light_archive[category_id]['property_list']
        for property,value in property_list.items():
          category.setProperty(property,value)


class SkinTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id='portal_skins', **kw)

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for relative_url in self._archive.keys():
      object = p.unrestrictedTraverse(relative_url)
      #if not object.cb_isCopyable():
      #  raise CopyError, eNotSupported % escape(relative_url)
      object = object._getCopy(context)
      if hasattr(aq_base(object), 'objectValues'):
        for script in object.objectValues(spec=('Script (Python)',)):
          if getattr(aq_base(script), '_code', None) is not None:
            LOG('Business Template', 0, 'clear _code in %r' % (script,))
            # Disable this at the moment, until the unstability is solved.
            #script._code = None
      self._archive[relative_url] = object
      object.wl_clearLocks()

  def install(self, context, **kw):
    ObjectTemplateItem.install(self, context, **kw)
    p = context.getPortalObject()
    # It is necessary to make sure that the sql connections in Z SQL Methods are valid.
    sql_connection_list = p.objectIds(spec=('Z MySQL Database Connection',))
    for relative_url in self._archive.keys():
      folder = p.unrestrictedTraverse(relative_url)
      for object in folder.objectValues(spec=('Z SQL Method',)):
        if object.connection_id not in sql_connection_list:
          object.connection_id = sql_connection_list[0]
    # Add new folders into skin paths.
    ps = p.portal_skins
    for skin_name, selection in ps.getSkinPaths():
      new_selection = []
      selection = selection.split(',')
      for relative_url, object in self._archive.items():
        skin_id = relative_url.split('/')[-1]
        selection_list = object.getProperty('business_template_registered_skin_selections', None)
        if selection_list is None or skin_name in selection_list:
          if skin_id not in selection:
            new_selection.append(skin_id)
      new_selection.extend(selection)
      ps.manage_skinLayers(skinpath = tuple(new_selection), skinname = skin_name, add_skin = 1)

  def uninstall(self, context, **kw):
    # Remove folders from skin paths.
    ps = context.portal_skins
    skin_id_list = [relative_url.split('/')[-1] for relative_url in self._archive.keys()]
    for skin_name, selection in ps.getSkinPaths():
      new_selection = []
      selection = selection.split(',')
      for skin_id in selection:
        if skin_id not in skin_id_list:
          new_selection.append(skin_id)
      ps.manage_skinLayers(skinpath = tuple(new_selection), skinname = skin_name, add_skin = 1)

    ObjectTemplateItem.uninstall(self, context, **kw)


class WorkflowTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id='portal_workflow', **kw)


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

  def __init__(self, id_list, **kw):
    kw['tool_id'] = 'portal_types'
    ObjectTemplateItem.__init__(self, id_list, **kw)
    self._workflow_chain_archive = PersistentMapping()

  def build(self, context, **kw):
    ObjectTemplateItem.build(self, context, **kw)
    (default_chain, chain_dict) = self._getChainByType(context)
    for object in self._archive.values():
      portal_type = object.id
      self._workflow_chain_archive[portal_type] = chain_dict['chain_%s' % portal_type]

  def install(self, context, **kw):
    ObjectTemplateItem.install(self, context, **kw)
    # We now need to setup the list of workflows corresponding to
    # each portal type
    (default_chain, chain_dict) = self._getChainByType(context)
    # Set the default chain to the empty string is probably the
    # best solution, by default it is 'default_workflow', wich is
    # not very usefull
    default_chain = ''
    for object in self._archive.values():
      portal_type = object.id
      chain_dict['chain_%s' % portal_type] = self._workflow_chain_archive[portal_type]
    context.portal_workflow.manage_changeWorkflows(default_chain,props=chain_dict)


class CatalogMethodTemplateItem(ObjectTemplateItem):

  def __init__(self, id_list, **kw):
    ObjectTemplateItem.__init__(self, id_list, tool_id='portal_catalog', **kw)
    self._is_catalog_method_archive = PersistentMapping()
    self._is_catalog_list_method_archive = PersistentMapping()
    self._is_uncatalog_method_archive = PersistentMapping()
    self._is_update_method_archive = PersistentMapping()
    self._is_clear_method_archive = PersistentMapping()
    self._is_filtered_archive = PersistentMapping()
    self._filter_expression_archive = PersistentMapping()
    self._filter_expression_instance_archive = PersistentMapping()
    self._filter_type_archive = PersistentMapping()

  def build(self, context, **kw):
    ObjectTemplateItem.build(self, context, **kw)

    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      return

    if catalog is None:
      return

    for object in self._archive.values():
      method_id = object.id
      self._is_catalog_method_archive[method_id] = method_id in catalog.sql_catalog_object
      self._is_catalog_list_method_archive[method_id] = method_id in catalog.sql_catalog_object_list
      self._is_uncatalog_method_archive[method_id] = method_id in catalog.sql_uncatalog_object
      self._is_update_method_archive[method_id] = method_id in catalog.sql_update_object
      self._is_clear_method_archive[method_id] = method_id in catalog.sql_clear_catalog
      self._is_filtered_archive[method_id] = 0
      if catalog.filter_dict.has_key(method_id):
        self._is_filtered_archive[method_id] = catalog.filter_dict[method_id]['filtered']
        self._filter_expression_archive[method_id] = catalog.filter_dict[method_id]['expression']
        self._filter_expression_instance_archive[method_id] = catalog.filter_dict[method_id]['expression_instance']
        self._filter_type_archive[method_id] = catalog.filter_dict[method_id]['type']

  def install(self, context, **kw):
    ObjectTemplateItem.install(self, context, **kw)

    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    # Make copies of attributes of the default catalog of portal_catalog.
    sql_catalog_object = list(catalog.sql_catalog_object)
    sql_catalog_object_list = list(catalog.sql_catalog_object_list)
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_update_object = list(catalog.sql_update_object)
    sql_clear_catalog = list(catalog.sql_clear_catalog)

    for object in self._archive.values():
      method_id = object.id
      is_catalog_method = self._is_catalog_method_archive[method_id]
      is_catalog_list_method = self._is_catalog_list_method_archive[method_id]
      is_uncatalog_method = self._is_uncatalog_method_archive[method_id]
      is_update_method = self._is_update_method_archive[method_id]
      is_clear_method = self._is_clear_method_archive[method_id]
      is_filtered = self._is_filtered_archive[method_id]

      if is_catalog_method and method_id not in sql_catalog_object:
        sql_catalog_object.append(method_id)
      elif not is_catalog_method and method_id in sql_catalog_object:
        sql_catalog_object.remove(method_id)

      if is_catalog_list_method and method_id not in sql_catalog_object_list:
        sql_catalog_object_list.append(method_id)
      elif not is_catalog_list_method and method_id in sql_catalog_object_list:
        sql_catalog_object_list.remove(method_id)

      if is_update_method and method_id not in sql_uncatalog_object:
        sql_uncatalog_object.append(method_id)
      elif not is_update_method and method_id in sql_uncatalog_object:
        sql_uncatalog_object.remove(method_id)

      if is_uncatalog_method and method_id not in sql_update_object:
        sql_update_object.append(method_id)
      elif not is_uncatalog_method and method_id in sql_update_object:
        sql_update_object.remove(method_id)

      if is_clear_method and method_id not in sql_clear_catalog:
        sql_clear_catalog.append(method_id)
      elif not is_clear_method and method_id in sql_clear_catalog:
        sql_clear_catalog.remove(method_id)

      if is_filtered:
        expression = self._filter_expression_archive[method_id]
        expression_instance = self._filter_expression_instance_archive[method_id]
        type = self._filter_type_archive[method_id]

        catalog.filter_dict[method_id] = PersistentMapping()
        catalog.filter_dict[method_id]['filtered'] = 1
        catalog.filter_dict[method_id]['expression'] = expression
        catalog.filter_dict[method_id]['expression_instance'] = expression_instance
        catalog.filter_dict[method_id]['type'] = type
      elif method_id in catalog.filter_dict.keys():
        catalog.filter_dict[method_id]['filtered'] = 0

    sql_catalog_object.sort()
    catalog.sql_catalog_object = tuple(sql_catalog_object)
    sql_catalog_object_list.sort()
    catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
    sql_uncatalog_object.sort()
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    sql_update_object.sort()
    catalog.sql_update_object = tuple(sql_update_object)
    sql_clear_catalog.sort()
    catalog.sql_clear_catalog = tuple(sql_clear_catalog)

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    # Make copies of attributes of the default catalog of portal_catalog.
    sql_catalog_object = list(catalog.sql_catalog_object)
    sql_catalog_object_list = list(catalog.sql_catalog_object_list)
    sql_uncatalog_object = list(catalog.sql_uncatalog_object)
    sql_update_object = list(catalog.sql_update_object)
    sql_clear_catalog = list(catalog.sql_clear_catalog)

    for object in self._archive.values():
      method_id = object.id

      if method_id in sql_catalog_object:
        sql_catalog_object.remove(method_id)

      if method_id in sql_catalog_object_list:
        sql_catalog_object_list.remove(method_id)

      if method_id in sql_uncatalog_object:
        sql_uncatalog_object.remove(method_id)

      if method_id in sql_update_object:
        sql_update_object.remove(method_id)

      if method_id in sql_clear_catalog:
        sql_clear_catalog.remove(method_id)

      if catalog.filter_dict.has_key(method_id):
        del catalog.filter_dict[method_id]

    catalog.sql_catalog_object = tuple(sql_catalog_object)
    catalog.sql_catalog_object_list = tuple(sql_catalog_object_list)
    catalog.sql_uncatalog_object = tuple(sql_uncatalog_object)
    catalog.sql_update_object = tuple(sql_update_object)
    catalog.sql_clear_catalog = tuple(sql_clear_catalog)

    ObjectTemplateItem.uninstall(self, context, **kw)


class ActionTemplateItem(BaseTemplateItem):

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
      object = p.unrestrictedTraverse(relative_url)
      for ai in object.listActions():
        if getattr(ai, key) == value:
          #LOG('BusinessTemplate', 0, 'ai = %r, ai.action = %r, key = %r, value = %r' % (ai, ai.action, key, value))
          self._archive[id] = ai._getCopy(context)
          self._archive[id].wl_clearLocks()
          break
      else:
        raise NotFound, 'no action has %s as %s' % (value, key)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    p = context.getPortalObject()
    for id,action in self._archive.items():
      relative_url, key, value = self._splitPath(id)
      object = p.unrestrictedTraverse(relative_url)
      for ai in object.listActions():
        if getattr(ai, key) == value:
          raise TemplateConflictError, 'the portal type %s already has the action %s' % (object.id, value)
      object.addAction(
                    id = action.id
                  , name = action.title
                  , action = action.action.text
                  , condition = action.condition
                  , permission = action.permissions
                  , category = action.category
                  , visible=action.visible
                  )

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    for id,action in self._archive.items():
      relative_url, key, value = self._splitPath(id)
      object = p.unrestrictedTraverse(relative_url)
      action_list = object.listActions()
      for index in range(len(action_list)):
        if getattr(ai, key) == value:
          object.deleteActions(selections=(index,))
          break
    BaseTemplateItem.uninstall(self, context, **kw)


class SitePropertyTemplateItem(BaseTemplateItem):

  def __init__(self, id_list, **kw):
    BaseTemplateItem.__init__(self, id_list, **kw)

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      for property in p.propertyMap():
        if property['id'] == id:
          property['value'] = p.getProperty(id)
          break
      else:
        property = None
      if property is None:
        raise NotFound, 'the property %s is not found' % id
      #LOG('SitePropertyTemplateItem build', 0, 'property = %r' % (property,))
      self._archive[id] = property

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    p = context.getPortalObject()
    for id,property in self._archive.items():
      if p.hasProperty(id):
        # Too much???
        raise TemplateConflictError, 'the property %s already exists' % id
      p._setProperty(id, property['value'], type=property['type'])

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    for id in self._archive.keys():
      if p.hasProperty(id):
        p._delProperty(id)
    BaseTemplateItem.uninstall(self, context, **kw)


class ModuleTemplateItem(BaseTemplateItem):

  def __init__(self, id_list, **kw):
    BaseTemplateItem.__init__(self, id_list, **kw)

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    p = context.getPortalObject()
    for id in self._archive.keys():
      module = p.unrestrictedTraverse(id)
      mapping = PersistentMapping()
      mapping['id'] = module.getId()
      mapping['title'] = module.getTitle()
      mapping['portal_type'] = module.getPortalType()
      permission_list = []
      for permission in module.ac_inherited_permissions(1):
        name, value = permission[:2]
        role_list = Permission(name, value, module).getRoles()
        permission_list.append((name, role_list))
      mapping['permission_list'] = permission_list
      self._archive[id] = mapping

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    portal = context.getPortalObject()
    for id,mapping in self._archive.items():
      if id in portal.objectIds():
        module = portal._getOb(id)
        module.portal_type = mapping['portal_type'] # XXX
      else:
        module = portal.newContent(id=id, portal_type=mapping['portal_type'])
      module.setTitle(mapping['title'])
      for name,role_list in mapping['permission_list']:
        acquire = (type(role_list) == type([]))
        try:
          module.manage_permission(name, roles=role_list, acquire=acquire)
        except:
          # Normally, an exception is raised when you don't install any Product which
          # has been in use when this business template is created.
          pass

  def uninstall(self, context, **kw):
    p = context.getPortalObject()
    id_list = p.objectIds()
    for id in self._archive.keys():
      if id in id_list:
        try:
          p.manage_delObjects([id])
        except:
          pass
    BaseTemplateItem.uninstall(self, context, **kw)

  def trash(self, context, new_item, **kw):
    # Do not remove any module for safety.
    pass

class DocumentTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for id in self._archive.keys():
      self._archive[id] = readLocalDocument(id)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    for id,text in self._archive.items():
      writeLocalDocument(id, text, create=1) # This raises an exception if the file exists.
      importLocalDocument(id)

  def uninstall(self, context, **kw):
    for id in self._archive.keys():
      try:
        removeLocalDocument(id)
      except OSError:
        pass
    BaseTemplateItem.uninstall(self, context, **kw)


class PropertySheetTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for id in self._archive.keys():
      self._archive[id] = readLocalPropertySheet(id)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    for id,text in self._archive.items():
      writeLocalPropertySheet(id, text, create=1) # This raises an exception if the file exists.
      importLocalPropertySheet(id)

  def uninstall(self, context, **kw):
    for id in self._archive.keys():
      try:
        removeLocalPropertySheet(id)
      except OSError:
        pass
    BaseTemplateItem.uninstall(self, context, **kw)


class ExtensionTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for id in self._archive.keys():
      self._archive[id] = readLocalExtension(id)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    for id,text in self._archive.items():
      writeLocalExtension(id, text, create=1) # This raises an exception if the file exists.
      importLocalPropertySheet(id)

  def uninstall(self, context, **kw):
    for id in self._archive.keys():
      try:
        removeLocalExtension(id)
      except OSError:
        pass
    BaseTemplateItem.uninstall(self, context, **kw)

class TestTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    for id in self._archive.keys():
      self._archive[id] = readLocalTest(id)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    for id,text in self._archive.items():
      writeLocalTest(id, text, create=1) # This raises an exception if the file exists.

  def uninstall(self, context, **kw):
    for id in self._archive.keys():
      try:
        removeLocalTest(id)
      except OSError:
        pass
    BaseTemplateItem.uninstall(self, context, **kw)


class ProductTemplateItem(BaseTemplateItem): pass # Not implemented yet


class RoleTemplateItem(BaseTemplateItem):

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)
    p = context.getPortalObject()
    roles = {}
    for role in p.__ac_roles__:
      roles[role] = 1
    for role in self._archive.keys():
      roles[role] = 1
    p.__ac_roles__ = tuple(roles.keys())

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


class CatalogResultKeyTemplateItem(BaseTemplateItem):

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)

    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_result_keys = list(catalog.sql_search_result_keys)
    for key in self._archive.keys():
      if key not in sql_search_result_keys:
        sql_search_result_keys.append(key)
    catalog.sql_search_result_keys = sql_search_result_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_result_keys = list(catalog.sql_search_result_keys)
    for key in self._archive.keys():
      if key in sql_search_result_keys:
        sql_search_result_keys.remove(key)
    catalog.sql_search_result_keys = sql_search_result_keys
    BaseTemplateItem.uninstall(self, context, **kw)


class CatalogRelatedKeyTemplateItem(BaseTemplateItem):

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)

    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_related_keys = list(catalog.sql_catalog_related_keys)
    for key in self._archive.keys():
      if key not in sql_catalog_related_keys:
        sql_catalog_related_keys.append(key)
    catalog.sql_catalog_related_keys = sql_catalog_related_keys

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_catalog_related_keys = list(catalog.sql_catalog_related_keys)
    for key in self._archive.keys():
      if key in sql_catalog_related_keys:
        sql_catalog_related_keys.remove(key)
    catalog.sql_catalog_related_keys = sql_catalog_related_keys
    BaseTemplateItem.uninstall(self, context, **kw)


class CatalogResultTableTemplateItem(BaseTemplateItem):

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)

    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_tables = list(catalog.sql_search_tables)
    for key in self._archive.keys():
      if key not in sql_search_tables:
        sql_search_tables.append(key)
    catalog.sql_search_tables = sql_search_tables

  def uninstall(self, context, **kw):
    try:
      catalog = context.portal_catalog.getSQLCatalog()
    except:
      catalog = None

    if catalog is None:
      LOG('BusinessTemplate', 0, 'no SQL catalog was available')
      return

    sql_search_tables = list(catalog.sql_search_tables)
    for key in self._archive.keys():
      if key in sql_search_tables:
        sql_search_tables.remove(key)
    catalog.sql_search_tables = sql_search_tables
    BaseTemplateItem.uninstall(self, context, **kw)


class MessageTranslationTemplateItem(BaseTemplateItem):

  def build(self, context, **kw):
    BaseTemplateItem.build(self, context, **kw)
    localizer = context.getPortalObject().Localizer
    for lang in self._archive.keys():
      self._archive[lang] = PersistentMapping()
      # Export only erp5_ui at the moment. This is safer against information leak.
      for catalog in ('erp5_ui', ):
        LOG('MessageTranslationTemplateItem build', 0, 'catalog = %r' % (catalog,))
        mc = localizer._getOb(catalog)
        LOG('MessageTranslationTemplateItem build', 0, 'mc = %r' % (mc,))
        self._archive[lang][catalog] = mc.manage_export(lang)

  def install(self, context, **kw):
    BaseTemplateItem.install(self, context, **kw)

    localizer = context.getPortalObject().Localizer
    for lang, catalogs in self._archive.items():
      if lang not in localizer.get_languages():
        localizer.manage_addLanguage(lang)
      for catalog, po in catalogs.items():
        mc = localizer._getOb(catalog)
        if lang not in mc.get_languages():
          mc.manage_addLanguage(lang)
        mc.manage_import(lang, po)


class BusinessTemplate(XMLObject):
    """
    A business template allows to construct ERP5 modules
    in part or completely. It may include:

    - dependency

    - conflicts

    - catalog definition ( -> formal definition + sql files )
      - SQL methods including:
        - purpose (catalog, uncatalog, etc.)
        - filter definition
      - Mapping definition
        - id (ex. getTitle)
        - column_id (ex. title)
        - indexed
        - preferred table (ex. catalog)

    - portal_types definition ( -> zexp/xml file)
      - id
      - actions

    - module definition ( -> zexp/xml file)
      - id
      - relative_url
      - menus
      - roles/security

    - workflow definitions ( -> zexp/xml file)
      - workflow_id
      - XML/XMI definition
      - relevant portal_types

    - tool definition ( -> formal definition)

    - categories definition

    Each definition should be usable in both import and update mode.

    Technology:

    - download a zip file (from the web, from a CVS repository)

    - install files to the right location (publish / update) (in the ZODB)

    - PUBLISH: publish method allows to publish an application (and share code)
      publication in a CVS repository allows to develop

      THIS IS THE MOST IMPORTANT CONCEPT

    Use case:

    - install core ERP5 (the minimum)

    - go to "BT" menu. Refresh list. Select BT. Click register.

    - go to "BT" menu. Select register BT. Define params. Click install / update.

    - go to "BT" menu. Create new BT. Define BT elements (workflow, methods, attributes, etc.). Click publish. Provide URL.
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
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'BusinessTemplate_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'history'
          , 'name'          : 'History'
          , 'category'      : 'object_view'
          , 'action'        : 'Base_viewHistory'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'Base_viewMetadata'
          , 'permissions'   : (
              Permissions.ManageProperties, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_exchange'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        , { 'id'            : 'update'
          , 'name'          : 'Update Business Template'
          , 'category'      : 'object_action'
          , 'action'        : 'BusinessTemplate_update'
          , 'permissions'   : (
              Permissions.ModifyPortalContent, )
          }
        , { 'id'            : 'save'
          , 'name'          : 'Save Business Template'
          , 'category'      : 'object_action'
          , 'action'        : 'BusinessTemplate_save'
          , 'permissions'   : (
              Permissions.ManagePortal, )
          }
        , { 'id'            : 'export'
          , 'name'          : 'Export Business Template'
          , 'category'      : 'object_action'
          , 'action'        : 'BusinessTemplate_export'
          , 'permissions'   : (
              Permissions.ManagePortal, )
          }
        )
      }

    _workflow_item = None
    _skin_item = None
    _category_item = None
    _catalog_method_item = None
    _path_item = None
    _portal_type_item = None
    _action_item = None
    _site_property_item = None
    _module_item = None
    _document_item = None
    _property_sheet_item = None
    _extension_item = None
    _test_item = None
    _product_item = None
    _role_item = None
    _catalog_result_key_item = None
    _catalog_related_key_item = None
    _catalog_result_table_item = None
    _message_translation_item = None

    def manage_afterAdd(self, item, container):
      """
        This is called when a new business template is added or imported.
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      if portal_workflow is not None:
        # Make sure that the installation state is "not installed".
        if portal_workflow.getStatusOf('business_template_installation_workflow', self) is not None:
          # XXX Not good to access the attribute directly, but there is no API for clearing the history.
          self.workflow_history['business_template_installation_workflow'] = None

    def build(self):
      """
        Copy existing portal objects to self
      """
      # Make sure that everything is sane.
      self.clean()

      # XXX Trim down the history to prevent it from bloating the bt5 file.
      # XXX Is there any better way to shrink the size???
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf_id_list = portal_workflow.getChainFor(self)
      original_history_dict = {}
      for wf_id in wf_id_list:
        history = portal_workflow.getHistoryOf(wf_id, self)
        if history is not None and len(history) > 30:
          original_history_dict[wf_id] = history
          LOG('Business Template', 0, 'trim down the history of %s' % (wf_id,))
          self.workflow_history[wf_id] = history[-30:]
      
      # Copy portal_types
      self._portal_type_item = PortalTypeTemplateItem(self.getTemplatePortalTypeIdList())
      self._portal_type_item.build(self)

      # Copy workflows
      self._workflow_item = WorkflowTemplateItem(self.getTemplateWorkflowIdList())
      self._workflow_item.build(self)

      # Copy skins
      self._skin_item = SkinTemplateItem(self.getTemplateSkinIdList())
      self._skin_item.build(self)

      # Copy categories
      self._category_item = CategoryTemplateItem(self.getTemplateBaseCategoryList())
      self._category_item.build(self)

      # Copy catalog methods
      self._catalog_method_item = CatalogMethodTemplateItem(self.getTemplateCatalogMethodIdList())
      self._catalog_method_item.build(self)

      # Copy actions
      self._action_item = ActionTemplateItem(self.getTemplateActionPathList())
      self._action_item.build(self)

      # Copy properties
      self._site_property_item = SitePropertyTemplateItem(self.getTemplateSitePropertyIdList())
      self._site_property_item.build(self)

      # Copy modules
      self._module_item = ModuleTemplateItem(self.getTemplateModuleIdList())
      self._module_item.build(self)

      # Copy Document Classes
      self._document_item = DocumentTemplateItem(self.getTemplateDocumentIdList())
      self._document_item.build(self)

      # Copy Propertysheet Classes
      self._property_sheet_item = PropertySheetTemplateItem(self.getTemplatePropertySheetIdList())
      self._property_sheet_item.build(self)

      # Copy Extensions Classes (useful for catalog)
      self._extension_item = ExtensionTemplateItem(self.getTemplateExtensionIdList())
      self._extension_item.build(self)

      # Copy Test Classes
      self._test_item = TestTemplateItem(self.getTemplateTestIdList())
      self._test_item.build(self)

      # Copy Products
      self._product_item = ProductTemplateItem(self.getTemplateProductIdList())
      self._product_item.build(self)

      # Copy roles
      self._role_item = RoleTemplateItem(self.getTemplateRoleList())
      self._role_item.build(self)

      # Copy catalog result keys
      self._catalog_result_key_item = CatalogResultKeyTemplateItem(self.getTemplateCatalogResultKeyList())
      self._catalog_result_key_item.build(self)

      # Copy catalog related keys
      self._catalog_related_key_item = CatalogRelatedKeyTemplateItem(self.getTemplateCatalogRelatedKeyList())
      self._catalog_related_key_item.build(self)

      # Copy catalog result tables
      self._catalog_result_table_item = CatalogResultTableTemplateItem(self.getTemplateCatalogResultTableList())
      self._catalog_result_table_item.build(self)

      # Copy message translations
      self._message_translation_item = MessageTranslationTemplateItem(self.getTemplateMessageTranslationList())
      self._message_translation_item.build(self)

      # Other objects
      self._path_item = PathTemplateItem(self.getTemplatePathList())
      self._path_item.build(self)

    build = WorkflowMethod(build)

    def publish(self, url, username=None, password=None):
      """
        Publish in a format or another
      """
      return self.portal_templates.publish(self, url, username=username, password=password)

    def update(self):
      """
        Update template: download new template defition
      """
      return self.portal_templates.update(self)

    def install(self, **kw):
      """
        For install based on paramaters provided in **kw
      """
      installed_bt = self.portal_templates.getInstalledBusinessTemplate(self.getTitle())
      if installed_bt is not None:
        installed_bt.trash(self)
        installed_bt.replace(self)

      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)

      # Classes and security information
      if self._product_item is not None: self._product_item.install(local_configuration)
      if self._property_sheet_item is not None: self._property_sheet_item.install(local_configuration)
      if self._document_item is not None: self._document_item.install(local_configuration)
      if self._extension_item is not None: self._extension_item.install(local_configuration)
      if self._test_item is not None: self._test_item.install(local_configuration)
      if self._role_item is not None: self._role_item.install(local_configuration)

      # Message translations
      if self._message_translation_item is not None: self._message_translation_item.install(local_configuration)

      # Objects and properties
      if self._workflow_item is not None: self._workflow_item.install(local_configuration)
      if self._catalog_method_item is not None: self._catalog_method_item.install(local_configuration)
      if self._site_property_item is not None: self._site_property_item.install(local_configuration)

      # Portal Types
      if self._portal_type_item is not None: self._portal_type_item.install(local_configuration)

      # Categories
      if self._category_item is not None: self._category_item.install(local_configuration,**kw)

      # Modules.
      if self._module_item is not None: self._module_item.install(local_configuration)

      # Install Paths after Modules, as we may want to keep static objects in some modules defined in the BT.
      if self._path_item is not None: self._path_item.install(local_configuration)

      # Skins
      if self._skin_item is not None: self._skin_item.install(local_configuration)

      # Actions, catalog
      if self._action_item is not None: self._action_item.install(local_configuration)
      if self._catalog_result_key_item is not None: self._catalog_result_key_item.install(local_configuration)
      if self._catalog_related_key_item is not None: self._catalog_related_key_item.install(local_configuration)
      if self._catalog_result_table_item is not None: self._catalog_result_table_item.install(local_configuration)

      # It is better to clear cache because the installation of a template
      # adds many new things into the portal.
      clearCache()

    install = WorkflowMethod(install)

    def trash(self, new_bt, **kw):
      """
        Trash unnecessary items before upograding to a new business template.
        This is similar to uninstall, but different in that this does not remove
        all items.
      """
      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)

      # Actions, catalog
      if self._action_item is not None: self._action_item.trash(local_configuration, new_bt._action_item)
      if self._catalog_result_key_item is not None: self._catalog_result_key_item.trash(local_configuration, new_bt._catalog_result_key_item)
      if self._catalog_related_key_item is not None: self._catalog_related_key_item.trash(local_configuration, new_bt._catalog_related_key_item)
      if self._catalog_result_table_item is not None: self._catalog_result_table_item.trash(local_configuration, new_bt._catalog_result_table_item)

      # Skins
      if self._skin_item is not None: self._skin_item.trash(local_configuration, new_bt._skin_item)

      # Portal Types
      if self._portal_type_item is not None: self._portal_type_item.trash(local_configuration, new_bt._portal_type_item)

      # Modules.
      if self._module_item is not None: self._module_item.trash(local_configuration, new_bt._module_item)

      # Objects and properties
      if self._path_item is not None: self._path_item.trash(local_configuration, new_bt._path_item)
      if self._workflow_item is not None: self._workflow_item.trash(local_configuration, new_bt._workflow_item)
      if self._category_item is not None: self._category_item.trash(local_configuration, new_bt._category_item)
      if self._catalog_method_item is not None: self._catalog_method_item.trash(local_configuration, new_bt._catalog_method_item)
      if self._site_property_item is not None: self._site_property_item.trash(local_configuration, new_bt._site_property_item)

      # Message translations
      if self._message_translation_item is not None: self._message_translation_item.trash(local_configuration, new_bt._message_translation_item)

      # Classes and security information
      if self._product_item is not None: self._product_item.trash(local_configuration, new_bt._product_item)
      if self._property_sheet_item is not None: self._property_sheet_item.trash(local_configuration, new_bt._property_sheet_item)
      if self._document_item is not None: self._document_item.trash(local_configuration, new_bt._document_item)
      if self._extension_item is not None: self._extension_item.trash(local_configuration, new_bt._extension_item)
      if self._test_item is not None: self._test_item.trash(local_configuration, new_bt._test_item)
      if self._role_item is not None: self._role_item.trash(local_configuration, new_bt._role_item)

    def uninstall(self, **kw):
      """
        For uninstall based on paramaters provided in **kw
      """
      # Update local dictionary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)

      # Actions, catalog
      if self._action_item is not None: self._action_item.uninstall(local_configuration)
      if self._catalog_result_key_item is not None: self._catalog_result_key_item.uninstall(local_configuration)
      if self._catalog_related_key_item is not None: self._catalog_related_key_item.uninstall(local_configuration)
      if self._catalog_result_table_item is not None: self._catalog_result_table_item.uninstall(local_configuration)

      # Skins
      if self._skin_item is not None: self._skin_item.uninstall(local_configuration)

      # Portal Types
      if self._portal_type_item is not None: self._portal_type_item.uninstall(local_configuration)

      # Modules.
      if self._module_item is not None: self._module_item.uninstall(local_configuration)

      # Objects and properties
      if self._path_item is not None: self._path_item.uninstall(local_configuration)
      if self._workflow_item is not None: self._workflow_item.uninstall(local_configuration)
      if self._category_item is not None: self._category_item.uninstall(local_configuration)
      if self._catalog_method_item is not None: self._catalog_method_item.uninstall(local_configuration)
      if self._site_property_item is not None: self._site_property_item.uninstall(local_configuration)

      # Message translations
      if self._message_translation_item is not None: self._message_translation_item.uninstall(local_configuration)

      # Classes and security information
      if self._product_item is not None: self._product_item.uninstall(local_configuration)
      if self._property_sheet_item is not None: self._property_sheet_item.uninstall(local_configuration)
      if self._document_item is not None: self._document_item.uninstall(local_configuration)
      if self._extension_item is not None: self._extension_item.uninstall(local_configuration)
      if self._test_item is not None: self._test_item.uninstall(local_configuration)
      if self._role_item is not None: self._role_item.uninstall(local_configuration)

      # It is better to clear cache because the uninstallation of a template
      # deletes many things from the portal.
      clearCache()

    uninstall = WorkflowMethod(uninstall)

    def clean(self):
      """
        Clean built information.
      """
      # First, remove obsolete attributes if present.
      for attr in ('_action_archive', '_document_archive', '_extension_archive', '_test_archive', '_module_archive',
                   '_object_archive', '_portal_type_archive', '_property_archive', '_property_sheet_archive'):
        if hasattr(self, attr):
          delattr(self, attr)
      # Secondly, make attributes empty.
      self._workflow_item = None
      self._skin_item = None
      self._category_item = None
      self._catalog_method_item = None
      self._path_item = None
      self._portal_type_item = None
      self._action_item = None
      self._site_property_item = None
      self._module_item = None
      self._document_item = None
      self._property_sheet_item = None
      self._extension_item = None
      self._test_item = None
      self._product_item = None
      self._role_item = None
      self._catalog_result_key_item = None
      self._catalog_related_key_item = None
      self._catalog_result_table_item = None
      self._message_translation_item = None

    clean = WorkflowMethod(clean)

    security.declareProtected(Permissions.AccessContentsInformation, 'getBuildingState')
    def getBuildingState(self, id_only=1):
      """
        Returns the current state in building
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('business_template_building_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    security.declareProtected(Permissions.AccessContentsInformation, 'getInstallationState')
    def getInstallationState(self, id_only=1):
      """
        Returns the current state in installation
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('business_template_installation_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    security.declareProtected(Permissions.AccessContentsInformation, 'toxml')
    def toxml(self):
      """
        Return this Business Template in XML
      """
      portal_templates = getToolByName(self, 'portal_templates')
      export_string = portal_templates.manage_exportObject(id=self.getId(), toxml=1, download=1)
      return export_string
      
    def _getOrderedList(self, id):
      """
        We have to set this method because we want an
        ordered list
      """
      #LOG('BuisinessTemplate _getOrderedList', 0, 'id = %s' % repr(id))
      result = getattr(self,id,())
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
