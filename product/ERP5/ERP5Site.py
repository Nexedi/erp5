##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Portal class

$Id$
"""

import Globals
from Globals import package_home
from time import time
#from Products.ERP5 import content_classes
from AccessControl import ClassSecurityInfo
from Products.CMFDefault.Portal import CMFSite, PortalGenerator
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Document.Folder import FolderMixIn
from Products.ERP5Type.Document import addFolder
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
import ERP5Globals

import threading

from zLOG import LOG

import os

#factory_type_information = []
#for c in content_classes:
#  factory_type_information.append(getattr(c, 'factory_type_information', []))

# Optimized Module Menu
GLOBAL_MODULE_CACHE_DURATION = 300
cached_modules = {}
cached_modules_time = {}

# Site Creation DTML
manage_addERP5SiteForm = Globals.HTMLFile('dtml/addERP5Site', globals())
manage_addERP5SiteForm.__name__ = 'addERP5Site'

# ERP5Site Constructor
def manage_addERP5Site(self, id, title='ERP5', description='',
                         create_userfolder=1,
                         email_from_address='postmaster@localhost',
                         email_from_name='Portal Administrator',
                         validate_email=0,
                         sql_connection_type='Z MySQL Database Connection',
                         sql_connection_string='test test',
                         RESPONSE=None):
    '''
    Adds a portal instance.
    '''
    gen = ERP5Generator()
    from string import strip
    id = strip(id)
    p = gen.create(self, id, create_userfolder,sql_connection_type,sql_connection_string)
    gen.setupDefaultProperties(p, title, description,
                               email_from_address, email_from_name,
                               validate_email)
    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url() + '/finish_portal_construction')

class ERP5Site ( CMFSite, FolderMixIn ):
    """
        The *only* function this class should have is to help in the setup
        of a new ERP5.  It should not assist in the functionality at all.
    """
    meta_type = 'ERP5 Site'
    constructors = (manage_addERP5SiteForm, manage_addERP5Site, )
    uid = 0
    last_id = 0
    icon = 'portal.gif'

    _properties = (
        {'id':'title', 'type':'string'},
        {'id':'description', 'type':'text'},
        )
    title = ''
    description = ''

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    security.declareProtected(Permissions.View, 'getUid')
    def view(self):
        """
          Returns the default view.
          Implemented for consistency
        """
        return self.index_html()

    security.declareProtected(Permissions.AccessContentsInformation, 'getUid')
    def getUid(self):
      """
        Returns the UID of the object. Eventually reindexes
        the object in order to make sure there is a UID
        (useful for import / export).

        WARNING : must be updates for circular references issues
      """
      #if not hasattr(self, 'uid'):
      #  self.reindexObject()
      return getattr(self, 'uid', 0)

    security.declareProtected(Permissions.AccessContentsInformation, 'getParentUid')
    def getParentUid(self):
      """
        A portal has no parent
      """
      return self.getUid()

    # Required to allow content creation outside folders
    security.declareProtected(Permissions.View, 'getIdGroup')
    def getIdGroup(self):
      return None

    # Required to allow content creation outside folders
    security.declareProtected(Permissions.View, 'getIdGroup')
    def setLastId(self, id):
      self.last_id = id

    security.declareProtected(Permissions.AccessContentsInformation, 'searchFolder')
    def searchFolder(self, **kw):
      """
        Search the content of a folder by calling
        the portal_catalog.
      """
      if not kw.has_key('parent_uid'):
        kw['parent_uid'] = self.uid
      kw2 = {}
      # Remove useless matter before calling the
      # catalog. In particular, consider empty
      # strings as None values
      for cname in kw.keys():
        if kw[cname] != '' and kw[cname]!=None:
          kw2[cname] = kw[cname]
      # The method to call to search the folder
      # content has to be called z_search_folder
      method = self.portal_catalog.z_search_folder
      return method(**kw2)

    # Proxy methods for security reasons
    def getOwnerInfo(self):
      return self.owner_info()

    # Make sure fixConsistency is recursive - ERROR - this creates recursion errors
    # checkConsistency = Folder.checkConsistency
    # fixConsistency = Folder.fixConsistency

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementTypeList')
    def getMovementTypeList(self):
      """
        Returns possible movements types
      """
      return ERP5Globals.movement_type_list

    security.declarePublic('getOrderedGlobalActionList')
    def getModuleList(self):
      """
         Return a list of modules - result dependent on user - result is translated and cached
      """
      # Return Cache
      user = str(_getAuthenticatedUser(self))
      if cached_modules.has_key(user):
        if time() - cached_modules_time[user] < GLOBAL_MODULE_CACHE_DURATION:
          return cached_modules[user]
      result = []
      for module in self.objectValues('ERP5 Folder'):
        # XXX Restrict access to modules to valid users
        result.append({'url': module.absolute_url(), 'id': module.getId(), 'title': self.gettext(module.getTitle())})
      result.sort(lambda x,y: cmp(x['title'], y['title']))
      cached_modules[user] = result
      cached_modules_time[user] = time()
      return cached_modules[user]

    security.declarePublic('getOrderedGlobalActionList')
    def getOrderedGlobalActionList(self, action_list):
      """
      Returns a dictionnary of actions, sorted by type of object

      This should absolutely be rewritten by using clean concepts to separate worklists XXX
      """
      #LOG("getOrderedGlobalActionList", 0, str(action_list))
      sorted_workflow_actions = {}
      sorted_global_actions = []
      other_global_actions = []
      for action in action_list:
        action['disabled'] = 0
        if action.has_key('workflow_title'):
          if not sorted_workflow_actions.has_key(action['workflow_title']):
            sorted_workflow_actions[action['workflow_title']] = []
          sorted_workflow_actions[action['workflow_title']].append(action)
        else:
          other_global_actions.append(action)
      workflow_title_list = sorted_workflow_actions.keys()
      workflow_title_list.sort()
      for key in workflow_title_list:
        sorted_global_actions.append({'title': key, 'disabled': 1})
        sorted_global_actions.extend(sorted_workflow_actions[key])
      sorted_global_actions.append({'title': 'Other', 'disabled': 1})
      sorted_global_actions.extend(other_global_actions)
      return sorted_global_actions

    def setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email
                               ):
        CMFSite.setupDefaultProperties(self, p, title, description,
                               email_from_address, email_from_name,
                               validate_email)

Globals.InitializeClass(ERP5Site)

class ERP5Generator(PortalGenerator):

    klass = ERP5Site

    def create(self, parent, id, create_userfolder, sql_connection_type, sql_connection_string):
        id = str(id)
        portal = self.klass(id=id)
        parent._setObject(id, portal)
        # Return the fully wrapped object.
        p = parent.this()._getOb(id)
        p._setProperty('sql_connection_type', sql_connection_type, 'string')
        p._setProperty('sql_connection_string', sql_connection_string, 'string')
        self.setup(p, create_userfolder)
        return p

    def setupTools(self, p):
        """Set up initial tools"""

        PortalGenerator.setupTools(self, p)

        # Add ERP5 Tools
        addTool = p.manage_addProduct['ERP5'].manage_addTool
        #print "addTool = %s" % str(addTool)
        addTool('ERP5 Categories', None)
        addTool('ERP5 Rule Tool', None)
        addTool('ERP5 Id Tool', None)
        addTool('ERP5 Simulation Tool', None)
        addTool('ERP5 Template Tool', None)

        # Add Activity Tool
        addTool = p.manage_addProduct['CMFActivity'].manage_addTool
        #addTool('CMF Activity Tool', None) # Allow user to select active/passive

        # Add ERP5 SQL Catalog Tool
        addTool = p.manage_addProduct['ERP5Catalog'].manage_addTool
        p._delObject('portal_catalog')
        addTool('ERP5 Catalog', None)
        # Add Default SQL connection
        if p.sql_connection_type == 'Z MySQL Database Connection':
          addSQLConnectioon = p.manage_addProduct['ZSQLMethods'].manage_addZMySQLConnection
          addSQLConnectioon('erp5_sql_connection', 'ERP5 SQL Server Connection', p.sql_connection_string)
        elif p.sql_connection_type == 'Z Gadfly':
          pass
        # Create default methods in Catalog XXX
        portal_catalog = getToolByName(p, 'portal_catalog')
        addSQLMethod = portal_catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
        product_path = package_home(globals())
        zsql_dir = os.path.join(product_path, 'sql')
        #print ("zsql_dir = %s" % str(zsql_dir))
        # Iterate over the sql directory. Add all sql methods in that directory.
        for entry in os.listdir(zsql_dir):
          if len(entry) > 5 and entry[-5:] == '.zsql':
            id = entry[:-5]
            # Create an empty SQL method first.
            addSQLMethod(id = id, title = '', connection_id = '', arguments = '', template = '')
            sql_method = getattr(portal_catalog, id)
            # Set parameters of the SQL method from the contents of a .zsql file.
            sql_method.fromFile(os.path.join(zsql_dir, entry))
        # Setup ZSQLCaralog properties
        portal_catalog.sql_catalog_object = ('z0_catalog_object', 'z_catalog_category', 'z_catalog_movement',
                                             'z_catalog_roles_and_users', 'z_catalog_stock', 'z_catalog_subject',)
        portal_catalog.sql_uncatalog_object = ('z0_uncatalog_category', 'z0_uncatalog_movement', 'z0_uncatalog_roles_and_users',
                                               'z0_uncatalog_stock', 'z0_uncatalog_subject', 'z_uncatalog_object', )
        portal_catalog.sql_update_object = ('z0_uncatalog_category', 'z0_uncatalog_movement', 'z0_uncatalog_roles_and_users',
                                            'z0_uncatalog_stock', 'z0_uncatalog_subject', 'z_catalog_category',
                                            'z_catalog_movement', 'z_catalog_roles_and_users', 'z_catalog_stock', 'z_catalog_subject',
                                            'z_update_object', )
        portal_catalog.sql_clear_catalog = ('z0_drop_catalog', 'z0_drop_category', 'z0_drop_movement', 'z0_drop_roles_and_users',
                                            'z0_drop_stock', 'z0_drop_subject', 'z_create_catalog',
                                            'z_create_category', 'z_create_movement', 'z_create_roles_and_users',
                                            'z_create_stock', 'z_create_subject', )
        portal_catalog.sql_search_results = 'z_search_results'
        portal_catalog.sql_count_results = 'z_count_results'
        portal_catalog.sql_getitem_by_path = 'z_getitem_by_path'
        portal_catalog.sql_getitem_by_uid = 'z_getitem_by_uid'
        portal_catalog.sql_catalog_schema = 'z_show_columns'
        portal_catalog.sql_unique_values = 'z_unique_values'
        portal_catalog.sql_catalog_paths = 'z_catalog_paths'
        portal_catalog.sql_catalog_keyword_search_keys = ('Description', 'SearchableText', 'Title', )
        portal_catalog.sql_catalog_full_text_search_keys = ('Description', 'SearchableText', 'Title', )
        portal_catalog.sql_catalog_request_keys = ()
        portal_catalog.sql_search_result_keys = ('catalog.*',)
        portal_catalog.sql_search_tables = ('catalog', 'category', 'roles_and_users', 'movement', 'subject', )
        portal_catalog.sql_catalog_tables = 'z_show_tables'

        # Clear Catalog
        portal_catalog.manage_catalogClear()

        # Add Selection Tool
        addTool = p.manage_addProduct['ERP5Form'].manage_addTool
        addTool('ERP5 Selections', None)

        # Add ERP5SyncML Tools
        addTool = p.manage_addProduct['ERP5SyncML'].manage_addTool
        addTool('ERP5 Synchronizations', None)

        # Add Message Catalog
        addMessageCatalog = p.manage_addProduct['Localizer'].manage_addMessageCatalog
        addMessageCatalog('gettext', 'ERP5 Localized Messages', ('en'))
        addMessageCatalog('translated_ui', 'ERP5 Localized Interface', ('en'))
        addMessageCatalog('translated_content', 'ERP5 Localized Content', ('en'))

        # Add Translation Service
        p.manage_addProduct['TranslationService'].addPlacefulTranslationService('translation_service')
        p.translation_service.manage_setDomainInfo(domain_0=None, path_0='gettext')
        p.translation_service.manage_addDomainInfo(domain='ui', path='translated_ui')
        p.translation_service.manage_addDomainInfo(domain='content', path='translated_content')


    def setupMembersFolder(self, p):
        """
          ERP5 is not a CMS
        """
        pass
        #from Products.CMFDefault.MembershipTool import MembershipTool
        #addFolder(p, id=MembershipTool.membersfolder_id, title='ERP5 Members')
        #member_folder = p[MembershipTool.membersfolder_id]
        #member_folder.manage_addProduct['OFSP'].manage_addDTMLMethod(
        #    'index_html', 'Member list', '<dtml-return roster>')

    def setupFrontPage(self, p):
        text = """<span  metal:define-macro="body">
<span tal:condition="python: not here.portal_membership.isAnonymousUser()">
<br/>
<br/>
<br/>
<br/>
<h3 align=center>Welcome to your new information system</h3>
<table border=1 align=center>
<tr tal:define="module_list python:here.objectValues('ERP5 Folder');
                dummy python:module_list.sort(lambda x,y: cmp(x.getTitle(), y.getTitle()));
                module_len python:len(module_list);
                col_size python:16;
                col_len python:module_len / col_size">
  <td>
   <img src="erp5_logo.png" alt="ERP5 Logo" />
  </td>
  <td tal:repeat="col_no python:range(col_len)" valign="top" class="ModuleShortcut">
    <p tal:repeat="module python:module_list[col_size*col_no:min(col_size*(col_no+1),module_len)] "><a href="composant"
       tal:content="module/title"
       tal:attributes="href module/id">Composants</a></p>
  </td>
</tr>
</table>

</span>
<span tal:condition="python: here.portal_membership.isAnonymousUser()">
<p tal:define="dummy python:request.RESPONSE.redirect('%s/login_form' % here.absolute_url())"/>
</span>
</span>
"""
        p.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                  'local_pt', title='ERP5 Front Page', text=text)

    def setupDefaultSkins(self, p):
        from Products.CMFCore.DirectoryView import addDirectoryViews
        from Products.CMFDefault import cmfdefault_globals
        from Products.CMFActivity import cmfactivity_globals
        ps = getToolByName(p, 'portal_skins')
        addDirectoryViews(ps, 'skins', globals())
        addDirectoryViews(ps, 'skins', cmfdefault_globals)
        addDirectoryViews(ps, 'skins', cmfactivity_globals)
        ps.manage_addProduct['OFSP'].manage_addFolder(id='external_method')
        ps.manage_addProduct['OFSP'].manage_addFolder(id='local_pro')
        ps.manage_addProduct['OFSP'].manage_addFolder(id='local_erp5')
        ps.manage_addProduct['OFSP'].manage_addFolder(id='local_list_method')
        ps.addSkinSelection('ERP5', 'local_pro, local_erp5, local_list_method, '
                                  + 'external_method, pro, erp5, activity, '
                                  + 'zpt_topic, zpt_content, zpt_generic,'
                                  + 'zpt_control, topic, content, generic, control, Images',
                            make_default=1)
        p.setupCurrentSkin()

    def setupWorkflow(self, p):
        """
          ERP5 has no default worklow
        """
        pass

    def setupIndex(self, p):
        from Products.CMFDefault.MembershipTool import MembershipTool
        # Make sure all tools and folders have been indexed
        portal_catalog = p.portal_catalog
        portal_catalog.manage_catalogClear()
        portal_catalog.reindexObject(p)
        portal_catalog.reindexObject(p.portal_templates)
        portal_catalog.reindexObject(p.portal_categories)
        # portal_catalog.reindexObject(p.portal_activities)
        #p[MembershipTool.membersfolder_id].immediateReindexObject()

    def setup(self, p, create_userfolder):
        self.setupTools(p)
        self.setupMailHost(p)
        if int(create_userfolder) != 0:
            self.setupUserFolder(p)
        self.setupCookieAuth(p)
        self.setupRoles(p)
        self.setupPermissions(p)
        self.setupDefaultSkins(p)

        # Initialize Activities
        #p.portal_skins.activity.SQLDict_createMessageTable()

        # Finish setup
        self.setupMembersFolder(p)

        # ERP5 Design Choice is that all content should be user defined
        # Content is disseminated through business templates
        from Products.ERP5.Document.BusinessTemplate import BusinessTemplate
        from Products.ERP5Type.Document.Folder import Folder
        self.setupTypes(p, (BusinessTemplate.factory_type_information, Folder.factory_type_information))

        self.setupMimetypes(p)
        self.setupWorkflow(p)
        self.setupFrontPage(p)

        # Make sure tools are cleanly indexed with a uid before creating children
        # XXX for some strange reason, member was indexed 5 times
        self.setupIndex(p)

# Patch the standard method
CMFSite.getPhysicalPath = ERP5Site.getPhysicalPath
