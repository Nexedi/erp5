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
manage_addERP5SiteForm = Globals.HTMLFile('dtml/addPortal', globals())
manage_addERP5SiteForm.__name__ = 'addPortal'

# ERP5Site Constructor
def manage_addERP5Site(self, id, title='ERP5', description='',
                         create_userfolder=1,
                         email_from_address='postmaster@localhost',
                         email_from_name='Portal Administrator',
                         validate_email=0, RESPONSE=None):
    '''
    Adds a portal instance.
    '''
    gen = ERP5Generator()
    from string import strip
    id = strip(id)
    p = gen.create(self, id, create_userfolder)
    gen.setupDefaultProperties(p, title, description,
                               email_from_address, email_from_name,
                               validate_email)
    if RESPONSE is not None:
        RESPONSE.redirect(p.absolute_url() + '/finish_portal_construction')

class ERP5Site ( CMFSite ):
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

    security.declareProtected(Permissions.ManagePortal, 'generateNewId')
    def generateNewId(self):
        """
          Generate a new Id which has not been taken yet in this folder.
          Eventually increment the id number until an available id
          can be found
        """
        my_id = self.last_id
        l = threading.Lock()
        l.acquire()
        try:
          while hasattr(self,str(my_id)):
            self.last_id = self.last_id + 1
            my_id = self.last_id
        finally:
          l.release()
        return str(my_id)

    # Proxy methods for security reasons
    def getOwnerInfo(self):
      return self.owner_info()

    def getPhysicalPath(self):
      """
      We can have some crasy things with the default
      getPhysicalPath, when for example we tried
      http://localhost:9673/toto/toto/toto/getPhysicalPath we had
      ('', 'toto', 'toto', 'toto') instead of ('', 'toto')
      So we have to rewrite this method
      """
      path = (self.__name__,)

      p = aq_parent(aq_inner(self))

      # JPS: We use uid instead of getUid so that it is compatible with CMFSite
      while p is not None and hasattr(p,'uid') and \
            getattr(p, 'uid', None) == getattr(self, 'uid', None):
        p = aq_parent(aq_inner(p))
      if p is not None:
        path = p.getPhysicalPath() + path

      return path

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

Globals.InitializeClass(ERP5Site)

class ERP5Generator(PortalGenerator):

    klass = ERP5Site

    def setupTools(self, p):
        """Set up initial tools"""

        PortalGenerator.setupTools(self, p)

        #print "Coucou"
        #print "Portal Membership exists %s" % str(getattr(p, 'portal_membership'))

        # Add ERP5 Tools
        addTool = p.manage_addProduct['ERP5'].manage_addTool
        #print "addTool = %s" % str(addTool)
        addTool('ERP5 Categories', None)
        addTool('ERP5 Rule Tool', None)
        addTool('ERP5 Id Tool', None)
        addTool('ERP5 Simulation Tool', None)

        # Add ERP5 SQL Catalog Tool
        addTool = p.manage_addProduct['ERP5Catalog'].manage_addTool
        p._delObject('portal_catalog')
        addTool('ERP5 Catalog', None)
        # Add Default SQL connection
        addSQLConnectioon = p.manage_addProduct['ZSQLMethods'].manage_addZMySQLConnection
        addSQLConnectioon('erp5_sql_connection', 'ERP5 SQL Server Connection', 'test')
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
        portal_catalog.sql_catalog_schema = ('z_show_category_columns', 'z_show_columns', 'z_show_movement',
                                             'z_show_roles_columns', 'z_show_stock_columns', 'z_show_subject_columns', )
        portal_catalog.sql_unique_values = 'z_unique_values'
        portal_catalog.sql_catalog_paths = 'z_catalog_paths'
        portal_catalog.sql_catalog_keyword_search_keys = ('Description', 'SearchableText', 'Title', )
        portal_catalog.sql_catalog_full_text_search_keys = ('Description', 'SearchableText', 'Title', )
        portal_catalog.sql_catalog_request_keys = ()

        # Add Selection Tool
        addTool = p.manage_addProduct['ERP5Form'].manage_addTool
        addTool('ERP5 Selections', None)

        # Add ERP5SyncML Tools
        addTool = p.manage_addProduct['ERP5SyncML'].manage_addTool
        addTool('ERP5 Synchronizations', None)

        # Add Translation Service
        p.manage_addProduct['TranslationService'].addPlacefulTranslationService('translation_service')

    #def setupMembersFolder(self, p):
    #    PortalFolder.manage_addPortalFolder(p, 'Members')
    #    p.Members.manage_addProduct['OFSP'].manage_addDTMLMethod(
    #        'index_html', 'Member list', '<dtml-return roster>')


    #def setupDefaultSkins(self, p):
    #    PortalGenerator.setupDefaultSkins(self, p)
    #    ps = getToolByName(p, 'portal_skins')
        #ps.addSkinSelection('Nouvelle',
        #    'nouvelle, custom, topic, content, generic, control, Images')

    #def setupTypes(self, p, initial_types=factory_type_information):
    #    method = PortalGenerator.setupTypes
    #    #method(self, p, factory_type_information)
    #    LOG("Type", 0, str(factory_type_information))
    #    PortalGenerator.setupTypes(self, p, {'initial_types':factory_type_information})

# Patch the standard method
CMFSite.getPhysicalPath = ERP5Site.getPhysicalPath
