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

from Globals import PersistentMapping
from Acquisition import Implicit
from AccessControl.Permission import Permission
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Utils import readLocalPropertySheet, writeLocalPropertySheet, importLocalPropertySheet
from Products.ERP5Type.Utils import readLocalExtension, writeLocalExtension
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, importLocalDocument
from Products.ERP5Type.XMLObject import XMLObject
import cStringIO

from zLOG import LOG

class TemplateItem(Implicit):
  pass # Compatibility

class ObjectTemplateItem(Implicit):
  """
    Attributes:

    tool_id             --  Id of the tool
    relative_url_or_id  --  URL relative to the tool
    relative_url        --  Complete relative_url
  """
  export_string = None

  def __init__(self, ob, **kw):
    self.__dict__.update(kw)
    self.export_string = cStringIO.StringIO()
    ob._p_jar.exportFile(ob._p_oid, self.export_string)
    self.export_string.seek(0)
    self.export_string = self.export_string.read()

  def install(self, local_configuration):
    portal = local_configuration.getPortalObject()
    container_path = self.relative_url.split('/')[0:-1]
    object_id = self.relative_url.split('/')[-1]
    container = portal.unrestrictedTraverse(container_path)
    #LOG('Installing' , 0, '%s in %s with %s' % (self.id, container.getPhysicalPath(), self.export_string))
    container_ids = container.objectIds()
    if object_id in container_ids:  # Object already exists
      #  pass # Do nothing for now
      n = 0
      new_object_id = object_id
      while new_object_id in container_ids:
        n = n + 1
        new_object_id = '%s_btsave_%s' % (object_id, n)
      container.manage_renameObject(object_id, new_object_id)
    container._importObjectFromFile(cStringIO.StringIO(self.export_string))
    #else:
    #  container._importObjectFromFile(cStringIO.StringIO(self.export_string))
    ob = container[object_id]
    if ob.meta_type in ('Z SQL Method',):
      # It is necessary to make sure that the sql connection in this method is valid.
      sql_connection_list = portal.objectIds(spec=('Z MySQL Database Connection',))
      if ob.connection_id not in sql_connection_list:
        ob.connection_id = sql_connection_list[0]

class PortalTypeTemplateItem(Implicit):
  """
    Attributes:

    tool_id             --  Id of the tool
    relative_url_or_id  --  URL relative to the tool
    relative_url        --  Complete relative_url
  """
  export_string = None

  def __init__(self, ob, **kw):
    self.__dict__.update(kw)
    self.export_string = cStringIO.StringIO()
    ob._p_jar.exportFile(ob._p_oid, self.export_string)
    self.export_string.seek(0)
    self.export_string = self.export_string.read()

  def install(self, local_configuration):
    portal = local_configuration.getPortalObject()
    container_path = self.relative_url.split('/')[0:-1]
    object_id = self.relative_url.split('/')[-1]
    container = portal.unrestrictedTraverse(container_path)
    #LOG('Installing' , 0, '%s in %s with %s' % (self.id, container.getPhysicalPath(), self.export_string))
    container_ids = container.objectIds()
    if object_id in container_ids:  # Object already exists
      pass # Do nothing for now
    else:
      container._importObjectFromFile(cStringIO.StringIO(self.export_string))


class CatalogMethodTemplateItem(ObjectTemplateItem):

  def __init__(self, ob, **kw):
    ObjectTemplateItem.__init__(self, ob, **kw)
    method_id = ob.getId()
    portal_catalog = ob.portal_catalog
    self._is_catalog_method = method_id in portal_catalog.sql_catalog_object
    self._is_uncatalog_method = method_id in portal_catalog.sql_uncatalog_object
    self._is_update_method = method_id in portal_catalog.sql_update_object
    self._is_clear_method = method_id in portal_catalog.sql_clear_catalog
    self._is_filtered = portal_catalog.filter_dict[method_id]['filtered']
    self._filter_expression = portal_catalog.filter_dict[method_id]['expression']
    self._filter_expression_instance = portal_catalog.filter_dict[method_id]['expression_instance']
    self._filter_type = portal_catalog.filter_dict[method_id]['type']

  def install(self, local_configuration):
    ObjectTemplateItem.install(self, local_configuration)
    portal = local_configuration.getPortalObject()
    portal_catalog = portal.portal_catalog
    method_id = self.id
    if self._is_catalog_method and method_id not in portal_catalog.sql_catalog_object:
      new_list = list(portal_catalog.sql_catalog_object + (method_id,))
      new_list.sort()
      portal_catalog.sql_catalog_object = tuple(new_list)
    if not(self._is_catalog_method) and method_id in portal_catalog.sql_catalog_object:
      portal_catalog.sql_catalog_object = tuple(filter(lambda id: id != method_id, portal_catalog.sql_catalog_object))
    if self._is_uncatalog_method and method_id not in portal_catalog.sql_uncatalog_object:
      new_list = list(portal_catalog.sql_uncatalog_object + (method_id,))
      new_list.sort()
      portal_catalog.sql_uncatalog_object = tuple(new_list)
    if not(self._is_uncatalog_method) and method_id in portal_catalog.sql_uncatalog_object:
      portal_catalog.sql_uncatalog_object = tuple(filter(lambda id: id != method_id, portal_catalog.sql_uncatalog_object))
    if self._is_update_method and method_id not in portal_catalog.sql_update_object:
      new_list = list(portal_catalog.sql_update_object + (method_id,))
      new_list.sort()
      portal_catalog.sql_update_object = tuple(new_list)
    if not(self._is_update_method) and method_id in portal_catalog.sql_update_object:
      portal_catalog.sql_update_object = tuple(filter(lambda id: id != method_id, portal_catalog.sql_update_object))
    if self._is_clear_method and method_id not in portal_catalog.sql_clear_catalog:
      new_list = list(portal_catalog.sql_clear_catalog + (method_id,))
      new_list.sort()
      portal_catalog.sql_clear_catalog = tuple(new_list)
    if not(self._is_clear_method) and method_id in portal_catalog.sql_clear_catalog:
      portal_catalog.sql_clear_catalog = tuple(filter(lambda id: id != method_id, portal_catalog.sql_clear_catalog))
    if self._is_filtered:
      portal_catalog.filter_dict[method_id] = PersistentMapping()
      portal_catalog.filter_dict[method_id]['filtered'] = 1
      portal_catalog.filter_dict[method_id]['expression'] = self._filter_expression
      portal_catalog.filter_dict[method_id]['expression_instance'] = self._filter_expression_instance
      portal_catalog.filter_dict[method_id]['type'] = self._filter_type

class ActionTemplateItem(Implicit):
  export_string = None

  def __init__(self, ai, **kw):
    self.__dict__.update(kw)
    self.__dict__.update(ai.__dict__)

  def install(self, portal, local_configuration):
    portal = local_configuration.getPortalObject()
    portal_type = portal.unrestrictedTraverse(self.relative_url)
    found_action = 0
    for ai in object.listActions():
      if getattr(ai, 'id') == self.action_id:
        found_action = 1
    if not found_action:
      portal_type.addAction(
                   self.id
                 , self.title
                 , self.action
                 , self.permission
                 , self.category
                 , visible=self.visible
                 )

class PropertyTemplateItem(Implicit):
  export_string = None

  def __init__(self, pi, **kw):
    self.__dict__.update(kw)
    self.property_definition = pi.copy()

  def install(self, local_configuration):
    portal = local_configuration.getPortalObject()
    object = portal.unrestrictedTraverse(self.relative_url)
    if not object.hasProperty(self.pi['id']):
      object._setProperty(pi['id'], type=pi['type'])

class ModuleTemplateItem(Implicit):
  export_string = None

  def __init__(self, module, **kw):
    self.__dict__.update(kw)
    self.module_id = module.getId()
    self.module_type = module.getPortalType()
    self.module_permission_list = []
    for p in module.ac_inherited_permissions(1):
      name, value = p[:2]
      role_list = Permission(name, value, module).getRoles()
      self.module_permission_list.append((name, role_list))

  def install(self, local_configuration):
    portal = local_configuration.getPortalObject()
    if self.module_id not in portal.objectIds():  # No renaming mapping for now
      module = portal.newContent(id=self.module_id, portal_type=self.module_type)
      for name,role_list in self.module_permission_list:
        acquire = (type(role_list) == type([]))
        try:
          module.manage_permission(name, roles=role_list, acquire=acquire)
        except:
          # Normally, an exception is raised when you don't install any Product which
          # has been in use when this business template is created.
          pass

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
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addBusinessTemplate'
         , 'immediate_view' : 'BusinessTemplate_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('BusinessTemplate',
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
          , 'action'        : 'history_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'BusinessTemplate_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_view'
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
        )
      }

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

    def initInstance(self):
      self._object_archive = PersistentMapping()
      self._portal_type_archive = PersistentMapping()
      self._action_archive = PersistentMapping()
      self._property_archive = PersistentMapping()
      self._module_archive = PersistentMapping()
      self._document_archive = PersistentMapping()
      self._property_sheet_archive = PersistentMapping()
      self._extension_archive = PersistentMapping()

    def checkInstance(self):
      if not hasattr(self, '_object_archive'):
        self._object_archive = PersistentMapping()
      if not hasattr(self, '_portal_type_archive'):
        self._portal_type_archive = PersistentMapping()
      if not hasattr(self, '_action_archive'):
        self._action_archive = PersistentMapping()
      if not hasattr(self, '_property_archive'):
        self._property_archive = PersistentMapping()
      if not hasattr(self, '_module_archive'):
        self._module_archive = PersistentMapping()
      if not hasattr(self, '_document_archive'):
        self._document_archive = PersistentMapping()
      if not hasattr(self, '_property_sheet_archive'):
        self._property_sheet_archive = PersistentMapping()
      if not hasattr(self, '_extension_archive'):
        self._extension_archive = PersistentMapping()

    def addObjectTemplateItem(self, relative_url_or_id, tool_id=None):
      if relative_url_or_id in ('', None): return # Make sure empty lines are eliminated
      p = self.getPortalObject()
      if tool_id is not None:
        relative_url = "%s/%s" % (tool_id, relative_url_or_id)
      else:
        relative_url = relative_url_or_id
      object = p.unrestrictedTraverse(relative_url)
      if object is not None:
        self._object_archive[(relative_url_or_id, tool_id)] = ObjectTemplateItem(object,
                                           id = object.id,
                                           tool_id=tool_id,
                                           relative_url=relative_url,
                                           relative_url_or_id=relative_url_or_id)

    def addPortalTypeTemplateItem(self, relative_url_or_id, tool_id=None):
      if relative_url_or_id in ('', None): return # Make sure empty lines are eliminated
      p = self.getPortalObject()
      if tool_id is not None:
        relative_url = "%s/%s" % (tool_id, relative_url_or_id)
      object = p.unrestrictedTraverse(relative_url)
      if object is not None:
        # Set the workflow_chain thanks to the portal_workflow
        portal_type = relative_url_or_id
        (default_chain, chain_dict) = self._getChainByType()
        workflow_chain = chain_dict['chain_%s' % portal_type]
        self._portal_type_archive[(relative_url_or_id, tool_id)] = \
                                           PortalTypeTemplateItem(object,
                                           id = object.id,
                                           tool_id=tool_id,
                                           relative_url=relative_url,
                                           relative_url_or_id=relative_url_or_id,
                                           portal_type = portal_type,
                                           workflow_chain = workflow_chain)

    def addCatalogMethodTemplateItem(self, relative_url_or_id, tool_id=None):
      if relative_url_or_id in ('', None): return # Make sure empty lines are eliminated
      p = self.getPortalObject()
      if tool_id is not None:
        relative_url = "%s/%s" % (tool_id, relative_url_or_id)
      object = p.unrestrictedTraverse(relative_url)
      if object is not None:
        self._object_archive[(relative_url_or_id, tool_id)] = CatalogMethodTemplateItem(object,
                                           id = object.id,
                                           tool_id=tool_id,
                                           relative_url=relative_url,
                                           relative_url_or_id=relative_url_or_id)

    def splitPath(self, path):
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

    def addActionTemplateItem(self, path):
      relative_url, key, value = self.splitPath(path)
      p = self.getPortalObject()
      object = p.unrestrictedTraverse(relative_url)
      for ai in object.listActions(): # Replace this with some kind of regexp
        if getattr(ai, key) == value:
          self._action_archive[path] = ActionTemplateItem(ai,
                                           id = (key, value),
                                           relative_url = relative_url,
                                           path = path)

    def addSitePropertyTemplateItem(self, path):
      relative_url, key, value = self.splitPath(path)
      p = self.getPortalObject()
      object = p.unrestrictedTraverse(relative_url)
      for pi in object.propertyMap():
        if pi.get(key) == value: # Replace this with some kind of regexp
          self._property_archive[path] = PropertyTemplateItem(pi,
                                           id = (key, value),
                                           value = object.getProperty(value),
                                           type = object.getPropertyType(value),
                                           relative_url = relative_url,
                                           path = path)

    def addModuleTemplateItem(self, id):
      module = self.getPortalObject().unrestrictedTraverse(id)
      self._module_archive[id] = ModuleTemplateItem(module, id=id)

    def addDocumentTemplateItem(self, id):
      self._document_archive[id] = readLocalDocument(id)

    def addPropertySheetTemplateItem(self, id):
      self._property_sheet_archive[id] = readLocalPropertySheet(id)

    def addExtensionTemplateItem(self, id):
      self._extension_archive[id] = readLocalExtension(id)

    def build(self):
      """
        Copy existing portal objects to self
      """
      self.initInstance()

      # Copy portal_types
      for id in self.getTemplatePortalTypeIdList():
        self.addPortalTypeTemplateItem(id, 'portal_types')
      # Copy workflows
      for id in self.getTemplateWorkflowIdList():
        self.addObjectTemplateItem(id, 'portal_workflow')
      # Copy skins
      for id in self.getTemplateSkinIdList():
        LOG('build', 0, 'id = %s' % repr(id))
        self.addObjectTemplateItem(id, 'portal_skins')
      # Copy categories
      for id in self.getTemplateBaseCategoryList():
        self.addObjectTemplateItem(id, 'portal_categories')
      # Copy catalog methods
      for id in self.getTemplateCatalogMethodIdList():
        self.addCatalogMethodTemplateItem(id, 'portal_catalog')
      # Copy actions
      for path in self.getTemplateActionPathList():
        self.addActionTemplateItem(path)
      # Copy properties
      for id in self.getTemplateSitePropertyIdList():
        self.addSitePropertyTemplateItem("[id=%s]" % id)
      # Copy modules
      for id in self.getTemplateModuleIdList():
        self.addModuleTemplateItem(id)

      # Copy Document Classes
      for id in self.getTemplateDocumentIdList():
        self.addDocumentTemplateItem(id)

      # Copy Propertysheet Classes
      for id in self.getTemplatePropertySheetIdList():
        self.addPropertySheetTemplateItem(id)

      # Copy Extensions Classes (useful for catalog)
      for id in self.getTemplateExtensionIdList():
        self.addExtensionTemplateItem(id)

      # Copy Products
      ### Make a tar archive and copy into local archive

      # Copy roles
      ### Nothing to do

      # Copy catalog columns
      ### Nothing to do

      # Copy catalog result tables
      ### Nothing to do

      # Copy Permissions
      ### Copy root values

      # Other objects and properties
      for path in self.getTemplatePathList():
        for id in self.getTemplatePortalTypeIdList():
          if path.find('=') >= 0:
            # This is a property
            self.addSitePropertyTemplateItem(path)
          else:
            # This is an object
            self.addObjectTemplateItem(path)

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

    def upgrade(self):
      """
        Upgrade the current portal with      self.installModules(linstallObjectsocal_configuration, update=update) this template definition
      """
      self.install(update=1)

    def install(self, update=0, **kw):
      """
        For install based on paramaters provided in **kw
      """
      # Update local dictionnary containing all setup parameters
      # This may include mappings
      self.portal_templates.updateLocalConfiguration(self, **kw)
      local_configuration = self.portal_templates.getLocalConfiguration(self)
      LOG('install Business Template: ',0,'local dictionnary updated')

      # Classes and security information
      self.installPropertySheets(local_configuration, update=update)
      self.installDocuments(local_configuration, update=update)
      self.installExtensions(local_configuration, update=update)
      self.installRoles(local_configuration, update=update)
      self.installPermissions(local_configuration, update=update)
      LOG('install Business Template: ',0,'security information updated')

      # Objects and properties
      self.installObjects(local_configuration, update=update)
      self.installProperties(local_configuration, update=update)
      LOG('install Business Template: ',0,'object and properties  updated')

      # Skins
      self.installSkins(local_configuration, update=update)
      LOG('install Business Template: ',0,'skins  updated')

      # Portal Types
      self.installPortalTypes(local_configuration, update=update)
      LOG('install Business Template: ',0,'portal types  updated')

      # Actions, modules, catalog
      self.installActions(local_configuration, update=update)
      self.installModules(local_configuration, update=update)
      self.installCatalog(local_configuration, update=update)
      LOG('install Business Template: ',0,'action, modules and catalog  updated')


    def installPropertySheets(self, local_configuration, update=0):
      """
        Install PropertySheet files into local instance
      """
      for id, text in self._property_sheet_archive.items():
        writeLocalPropertySheet(id, text)
        importLocalPropertySheet(id)

    def installDocuments(self, local_configuration, update=0):
      """
        Install Document files into local instance
      """
      for id, text in self._document_archive.items():
        writeLocalDocument(id, text)
        importLocalDocument(id)

    def installExtensions(self, local_configuration, update=0):
      """
        Install Extension files into local instance
      """
      for id, text in self._extension_archive.items():
        writeLocalExtension(id, text)

    def installRoles(self, local_configuration, update=0):
      """
        Add template roles to portal
      """
      p = local_configuration.getPortalObject()
      roles = {}
      for role in p.__ac_roles__:
        roles[role] = 1
      for role in self.getTemplateRoleList():
        roles[role] = 1
      p.__ac_roles__ = tuple(roles.keys())

    def installPermissions(self, local_configuration, update=0):
      """
        Nothing for now
      """
      #mp = p.manage_permission
      #mp('Set own password',        ['Member','Manager',],    1)

    def installSkins(self, local_configuration, update=0):
      """
        Make sure installed skins are defined in skin properties
      """
      portal_skins = self.portal_skins
      for skin_name, selection in portal_skins.getSkinPaths():
        new_selection = []
        for skin_id in self.getTemplateSkinIdList():
          if skin_id not in selection:
            new_selection.append(skin_id)
        new_selection.append(selection)
        portal_skins.manage_skinLayers(chosen = tuple(new_selection), skinname=skin_name)

    def installProperties(self, local_configuration, update=0):
      """
        Create properties if needed
      """
      for o in self._property_archive.values():
        o.install(local_configuration)

    def installActions(self, local_configuration, update=0):
      """
        Create actions if needed
      """
      for o in self._action_archive.values():
        o.install(local_configuration)

    def installModules(self, local_configuration, update=0):
      """
        Create modules if needed
      """
      for o in self._module_archive.values():
        o.install(local_configuration)

    def installCatalog(self, local_configuration, update=0):
      """
        Add tables and keys to catalog default search_result
      """
      portal_catalog = self.portal_catalog
      for c in self.getTemplateCatalogResultKeyList():
        if c not in portal_catalog.sql_search_result_keys:
          portal_catalog.sql_search_result_keys = tuple([c] + portal_catalog.sql_search_result_keys)
      for t in self.getTemplateCatalogResultTableList():
        if c not in portal_catalog.sql_search_tables:
          portal_catalog.sql_search_tables = tuple([c] + portal_catalog.sql_search_tables)

    def installObjects(self, local_configuration, update=0):
      """
      """
      for o in self._object_archive.values():
        o.install(local_configuration)

    def installPortalTypes(self, local_configuration, update=0):
      """
      """
      portal_workflow = self.portal_workflow
      for o in self._portal_type_archive.values():
        o.install(local_configuration)
        # We now need to setup the list of workflows corresponding to
        # each portal type
        (default_chain, chain_dict) = self._getChainByType()
        # Set the default chain to the empty string is probably the
        # best solution, by default it is 'default_workflow', wich is
        # not very usefull
        default_chain = ''
        LOG('installPortalTypes, portal_type: ',0,o.portal_type)
        LOG('installPortalTypes, workflow_chain: ',0,repr(o.workflow_chain))
        LOG('installPortalTypes, chain_dict: ',0,chain_dict)
        LOG('installPortalTypes, default_chain: ',0,default_chain)
        chain_dict['chain_%s' % o.portal_type] = o.workflow_chain
        portal_workflow.manage_changeWorkflows(default_chain,props=chain_dict)
      
    def _getChainByType(self):
      """
      This is used in order to construct the full list
      of mapping between type and list of workflow associated
      This is only usefull in order to use
      portal_workflow.manage_changeWorkflows
      """
      self = self.portal_workflow
      cbt = self._chains_by_type
      ti = self._listTypeInfo()
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
      default_chain=', '.join(self._default_chain)
      return (default_chain, new_dict)

 

