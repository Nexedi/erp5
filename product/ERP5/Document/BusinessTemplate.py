##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
import cStringIO

from zLOG import LOG

class ObjectTemplateItem(Implicit):
  export_string = None

  def __init__(self, ob, **kw):
    self.__dict__.update(kw)
    self.export_string = cStringIO.StringIO()
    ob._p_jar.exportFile(ob._p_oid, self.export_string)
    self.export_string = self.export_string.read()

  def install(self, portal):
    folder._importObjectFromFile(cStringIO.StringIO(self.export_string))

class ActionTemplateItem(Implicit):
  export_string = None

  def __init__(self, ai, **kw):
    self.__dict__.update(kw)
    self.id = id
    self.title = ai.title
    self.description = ai.description
    self.category = ai.category
    self.condition = ai.condition
    self.permissions = ai.permissions
    self.priority = ai.priority
    self.visible = ai.visible
    self.expression = ai.getActionExpression()

  def install(self, portal):
    folder._importObjectFromFile(cStringIO.StringIO(self.export_string))

class PropertyTemplateItem(Implicit):
  export_string = None

  def __init__(self, pi, **kw):
    self.__dict__.update(kw)
    self.property_definition = pi.copy()

  def install(self, portal):
    folder._importObjectFromFile(cStringIO.StringIO(self.export_string))

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
    add_permission = Permissions.AddERP5Content
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
         , 'product'        : 'ERP5'
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
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
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
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }


    def initInstance(self):
      if not hasattr(self, 'object_archive'):
        self.object_archive = PersistentMapping()
      if not hasattr(self, 'action_archive'):
        self.action_archive = PersistentMapping()
      if not hasattr(self, 'property_archive'):
        self.property_archive = PersistentMapping()

    def addObjectTemplateItem(self, relative_url_or_id, tool_id=None):
      p = self.getPortalObject()
      if tool_id is not None:
        relative_url = "%s/%s" % (tool_id, relative_url_or_id)
      object = p.unrestrictedTraverse(relative_url)
      if object is not None:
        self.object_archive[(relative_url_or_id, tool_id)] = ObjectTemplateItem(object,
                                           id = object.id,
                                           tool_id=tool_id,
                                           relative_url=relative_url,
                                           relative_url_or_id=relative_url_or_id)

    def splitPath(self, path):
      # Add error checking here
      relative_url = path[0:path.find('[')]
      id_block = path[path.find('[')+1:path.find(']')]
      key = path.split('=')[0]
      value = path.split('=')[2]
      return relative_url, key, value

    def addActionTemplateItem(self, path):
      relative_url, key, value = self.splitPath(path)
      p = self.getPortalObject()
      object = p.unrestrictedTraverse(relative_url)
      for ai in object.listActions(): # Replace this with some kind of regexp
        if getattr(ai, key) == value:
          self.action_archive[path] = ActionTemplateItem(ai,
                                           id = key,
                                           relative_url = relative_url,
                                           path = path)

    def addSitePropertyTemplateItem(self, path):
      relative_url, key, value = self.splitPath(path)
      p = self.getPortalObject()
      object = p.unrestrictedTraverse(relative_url)
      for pi in object.propertyMap():
        if getattr(pi, key) == value: # Replace this with some kind of regexp
          self.property_archive[path] = PropertyTemplateItem(pi,
                                           id = key,
                                           value = object.getProperty(key),
                                           relative_url = relative_url,
                                           path = path)

    def build(self):
      """
        Copy existing portal objects to self
      """
      self.initInstance()
      # Copy portal_types
      for id in self.getTemplatePortalTypeIdList():
        self.addObjectTemplateItem(id, 'portal_types')
      # Copy workflows
      for id in self.getTemplateWorkflowIdList():
        self.addObjectTemplateItem(id, 'portal_workflow')
      # Copy skins
      for id in self.getTemplateSkinIdList():
        self.addObjectTemplateItem(id, 'portal_skins')
      # Copy categories
      for id in self.getTemplateBaseCategoryIdList():
        self.addObjectTemplateItem(id, 'portal_categories')
      # Copy catalog methods
      for id in self.getTemplateCatalogMethodIdList():
        self.addObjectTemplateItem(id, 'portal_catalog')

      # Copy actions
      for id in self.getTemplateActionPathList():
        self.addActionTemplateItem(path)

      # Copy properties
      for id in self.getTemplateSitePropertyIdList():
        self.addSitePropertyTemplateItem(id)


    def publish(self, format='web'):
      """
        Publish in a format or another
      """

    def upgrade(self):
      """
        Upgrade template
      """

    def update(self):
      """
        Update the current portal with this template definition
      """
      # call local update


    def install(self, **kw):
      """
        For install based on paramaters provided in **kw
      """
      # call local install

    def installRoles(self, update=1):
      """
        C
      """
      p.__ac_roles__ = ('Member', 'Reviewer',)

    def installPermissions(self, update=1):
      """
        C
      """
      mp = p.manage_permission

      mp('Set own password',        ['Member','Manager',],    1)


    def installSkins(self, update=1):
          from Products.CMFCore.DirectoryView import addDirectoryViews
          ps = getToolByName(p, 'portal_skins')
          addDirectoryViews(ps, 'skins', globals())
          addDirectoryViews(ps, 'skins', topic_globals)
          ps.manage_addProduct['OFSP'].manage_addFolder(id='custom')
          ps.addSkinSelection('Basic',
              'custom, zpt_topic, zpt_content, zpt_generic,'
              + 'zpt_control, topic, content, generic, control, Images',
              make_default=1)
          ps.addSkinSelection('Nouvelle',
              'nouvelle, custom, topic, content, generic, control, Images')
          ps.addSkinSelection('No CSS',
              'no_css, custom, topic, content, generic, control, Images')
          p.setupCurrentSkin()

    def installPortalTypes(self, update=1):
      """
        C
      """

    def installWorklow(self, update=1):
      """
        C
      """

    def installProperties(self, update=1):
      """
        C
      """
