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

from Products.CMFCore.CatalogTool import CatalogTool as CMFCoreCatalogTool
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.CatalogTool import IndexableObjectWrapper as CMFCoreIndexableObjectWrapper
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser, getToolByName
from Products.CMFCore.utils import _mergedLocalRoles
from Globals import InitializeClass, DTMLFile, PersistentMapping, package_home
from Acquisition import aq_base, aq_inner, aq_parent
from DateTime.DateTime import DateTime
from BTrees.OIBTree import OIBTree

from AccessControl.PermissionRole import rolesForPermissionOn

from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine

import os, time, urllib

from zLOG import LOG

class IndexableObjectWrapper(CMFCoreIndexableObjectWrapper):

    def __setattr__(self, name, value):
      # We need to update the uid during the cataloging process
      if name == 'uid':
        setattr(self.__ob, name, value)
      else:
        self.__dict__[name] = value

    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        # Try to import CPS (import here to make sure no circular)
        try:
          from Products.NuxUserGroups.CatalogToolWithGroups import mergedLocalRoles
          withgroups = 1
        except ImportError:
          withgroups = 0

        ob = self.__ob
        allowed = {}
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1
        if withgroups:
          localroles = mergedLocalRoles(ob, withgroups=1)
          #LOG("allowedRolesAndUsers",0,str(allowed.keys()))
        else:
          # CMF
          localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    if withgroups:
                      allowed[user] = 1
                    else:
                      allowed['user:' + user] = 1
                # Added for ERP5 project by JP Smets
                if role != 'Owner':
                  if withgroups:
                    allowed[user + ':' + role] = 1
                  else:
                    allowed['user:' + user + ':' + role] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        #LOG("allowedRolesAndUsers",0,str(allowed.keys()))
        return list(allowed.keys())

class CatalogTool (UniqueObject, ZCatalog, CMFCoreCatalogTool):
    """
    This is a ZSQLCatalog that filters catalog queries.
    It is based on ZSQLCatalog
    """
    id = 'portal_catalog'
    meta_type = 'ERP5 Catalog'
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' },
                       { 'label' : 'Filter', 'action' : 'manage_filter' },
                     ) + ZCatalog.manage_options


    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    # Explicite Inheritance
    __url = CMFCoreCatalogTool.__url
    manage_catalogFind = CMFCoreCatalogTool.manage_catalogFind

    security.declareProtected( CMFCorePermissions.ManagePortal
                , 'manage_filter' )
    manage_filter = DTMLFile( 'dtml/manageFilter', globals() )

    security.declareProtected( CMFCorePermissions.ManagePortal
                , 'manage_schema' )
    manage_schema = DTMLFile( 'dtml/manageSchema', globals() )

    # Setup properties for various configs : CMF, ERP5, CPS, etc.
    def setupPropertiesForConfig(self, config_id='erp5'):
        if config_id.lower() == 'erp5':
            self.sql_catalog_produce_reserved = 'z_produce_reserved_uid_list'
            self.sql_catalog_clear_reserved = 'z_clear_reserved'
            self.sql_catalog_object = ('z_update_object', 'z_catalog_category', 'z_catalog_movement',
                                                 'z_catalog_roles_and_users', 'z_catalog_stock', 'z_catalog_subject',)
            self.sql_uncatalog_object = ('z0_uncatalog_category', 'z0_uncatalog_movement',
                                                   'z0_uncatalog_roles_and_users',
                                                   'z0_uncatalog_stock', 'z0_uncatalog_subject', 'z_uncatalog_object', )
            self.sql_update_object = ('z0_uncatalog_category', 'z0_uncatalog_movement',
                                                'z0_uncatalog_roles_and_users',
                                                'z0_uncatalog_stock', 'z0_uncatalog_subject', 'z_catalog_category',
                                                'z_catalog_movement', 'z_catalog_roles_and_users', 'z_catalog_stock',
                                                'z_catalog_subject', 'z_update_object', )
            self.sql_clear_catalog = ('z0_drop_catalog', 'z0_drop_category', 'z0_drop_movement',
                                                'z0_drop_roles_and_users',
                                                'z0_drop_stock', 'z0_drop_subject', 'z_create_catalog',
                                                'z_create_category', 'z_create_movement', 'z_create_roles_and_users',
                                                'z_create_stock', 'z_create_subject',
                                                'z_clear_reserved', )
            self.sql_search_results = 'z_search_results'
            self.sql_count_results = 'z_count_results'
            self.sql_getitem_by_path = 'z_getitem_by_path'
            self.sql_getitem_by_uid = 'z_getitem_by_uid'
            self.sql_catalog_schema = 'z_show_columns'
            self.sql_unique_values = 'z_unique_values'
            self.sql_catalog_paths = 'z_catalog_paths'
            self.sql_catalog_keyword_search_keys = ('Description', 'SearchableText', 'Title', )
            self.sql_catalog_full_text_search_keys = ('Description', 'SearchableText', 'Title', )
            self.sql_catalog_request_keys = ()
            self.sql_search_result_keys = ('catalog.uid', 'catalog.path')
            self.sql_search_tables = ('catalog', 'category', 'roles_and_users', 'movement', 'subject', )
            self.sql_catalog_tables = 'z_show_tables'

        elif config_id.lower() == 'cps3':
            self.sql_catalog_produce_reserved = 'z_produce_reserved_uid_list'
            self.sql_catalog_clear_reserved = 'z_clear_reserved'
            self.sql_catalog_object = ('z_update_object', 'z_catalog_roles_and_users', 'z_catalog_subject',
                                                 'z_catalog_local_users_with_roles', 'z_catalog_cps', )
            self.sql_uncatalog_object = ('z0_uncatalog_roles_and_users', 'z0_uncatalog_cps',
                                                   'z0_uncatalog_local_users_with_roles', 'z0_uncatalog_subject',
                                                   'z_uncatalog_object', )
            self.sql_update_object = ('z0_uncatalog_roles_and_users', 'z0_uncatalog_subject',
                                                'z_catalog_roles_and_users', 'z_catalog_subject',
                                                'z_update_object', 'z_update_cps')
            self.sql_clear_catalog = ('z0_drop_catalog', 'z0_drop_roles_and_users', 'z0_drop_cps',
                                                'z0_drop_local_users_with_roles', 'z0_drop_subject', 'z_create_catalog',
                                                'z_create_roles_and_users', 'z_create_local_users_with_roles',
                                                'z_create_subject', 'z_create_cps',
                                                'z_clear_reserved', )
            self.sql_search_results = 'z_search_results'
            self.sql_count_results = 'z_count_results'
            self.sql_getitem_by_path = 'z_getitem_by_path'
            self.sql_getitem_by_uid = 'z_getitem_by_uid'
            self.sql_catalog_schema = 'z_show_columns'
            self.sql_unique_values = 'z_unique_values'
            self.sql_catalog_paths = 'z_catalog_paths'
            self.sql_catalog_keyword_search_keys = ('Description', 'SearchableText', 'Title', )
            # XXX Not sure about local_users_with_roles.allowedRolesAndUser
            # self.sql_catalog_keyword_search_keys = ('Description', 'SearchableText', 'Title', 
            #                                                   'local_users_with_roles.allowedRolesAndUser' )
            self.sql_catalog_full_text_search_keys = ('Description', 'SearchableText', 'Title', )
            self.sql_catalog_request_keys = ()
            # XXX Check if cps.* is useful or not for result_keys
            self.sql_search_result_keys = ('catalog.uid', 'catalog.security_uid', 'catalog.path',
                                           'catalog.relative_url', 'catalog.parent_uid', 'catalog.CreationDate',
                                           'catalog.Creator', 'catalog.Date', 'catalog.Description',
                                           'catalog.PrincipiaSearchSource', 'catalog.SearchableText', 
                                           'catalog.EffectiveDate',
                                           'catalog.ExpiresDate', 'catalog.ModificationDate', 'catalog.Title',
                                           'catalog.Type', 'catalog.bobobase_modification_time', 'catalog.created',
                                           'catalog.effective', 'catalog.expires', 'catalog.getIcon',
                                           'catalog.id', 'catalog.in_reply_to', 'catalog.meta_type',
                                           'catalog.portal_type', 'catalog.modified', 'catalog.review_state',
                                           'catalog.opportunity_state', 'catalog.default_source_reference', 
                                           'catalog.default_destination_reference',
                                           'catalog.default_source_title', 'catalog.default_destination_title', 
                                           'catalog.default_source_section_title',
                                           'catalog.default_destination_section_title', 'catalog.default_causality_id', 
                                           'catalog.location',
                                           'catalog.ean13_code', 'catalog.validation_state',
                                           'catalog.simulation_state',
                                           'catalog.causality_state', 'catalog.discussion_state', 'catalog.invoice_state',
                                           'catalog.payment_state', 'catalog.event_state', 'catalog.order_id',
                                           'catalog.reference', 'catalog.source_reference',
                                           'catalog.destination_reference', 'catalog.summary',)
            self.sql_search_tables = ('catalog', 'cps', 'local_users_with_roles', 'roles_and_users', 'subject', )
            self.sql_catalog_tables = 'z_show_tables'

            # CPS specific
            self.sql_catalog_topic_search_keys = ('cps_filter_sets',)

        elif config_id.lower() == 'cmf':
            pass
            # XXX TODO

    def addDefaultSQLMethods(self, config_id='erp5'):
        addSQLMethod = self.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
        product_path = package_home(globals())
        zsql_dirs = []

        # Common methods
        zsql_dirs.append(os.path.join(product_path, 'sql', 'common_mysql'))
        # Specific methods
        if config_id.lower() == 'erp5':
            zsql_dirs.append(os.path.join(product_path, 'sql', 'erp5_mysql'))
        elif config_id.lower() == 'cps3':
            zsql_dirs.append(os.path.join(product_path, 'sql', 'cps3_mysql'))
        # XXX TODO : add other cases

        #print ("zsql_dir = %s" % str(zsql_dir))
        # Iterate over the sql directory. Add all sql methods in that directory.
        for directory in zsql_dirs:
            for entry in os.listdir(directory):
                if len(entry) > 5 and entry[-5:] == '.zsql':
                    id = entry[:-5]
                    # Create an empty SQL method first.
                    addSQLMethod(id = id, title = '', connection_id = '', arguments = '', template = '')
                    sql_method = getattr(self, id)
                    # Set parameters of the SQL method from the contents of a .zsql file.
                    sql_method.fromFile(os.path.join(directory, entry))

    def _listAllowedRolesAndUsers(self, user):
      try:
        from Products.NuxUserGroups.CatalogToolWithGroups import _getAllowedRolesAndUsers
        return _getAllowedRolesAndUsers(user)
      except ImportError:
        return CMFCoreCatalogTool._listAllowedRolesAndUsers(self, user)

    # Schema Management
    def editColumn(self, column_id, sql_definition, method_id, default_value, REQUEST=None, RESPONSE=None):
      """
        Modifies a schema column of the catalog
      """
      new_schema = []
      for c in self.getIndexList():
        if c.id == index_id:
          new_c = {'id': index_id, 'sql_definition': sql_definition, 'method_id': method_id, 'default_value': default_value}
        else:
          new_c = c
        new_schema.append(new_c)
      self.setColumnList(new_schema)

    def setColumnList(self, column_list):
      """
      """
      self._sql_schema = column_list

    def getColumnList(self):
      """
      """
      if not hasattr(self, '_sql_schema'): self._sql_schema = []
      return self._sql_schema

    def getColumn(self, column_id):
      """
      """
      for c in self.getColumnList():
        if c.id == column_id:
          return c
      return None

    def editIndex(self, index_id, sql_definition, REQUEST=None, RESPONSE=None):
      """
        Modifies the schema of the catalog
      """
      new_index = []
      for c in self.getIndexList():
        if c.id == index_id:
          new_c = {'id': index_id, 'sql_definition': sql_definition}
        else:
          new_c = c
        new_index.append(new_c)
      self.setIndexList(new_index)

    def setIndexList(self, index_list):
      """
      """
      self._sql_index = index_list

    def getIndexList(self):
      """
      """
      if not hasattr(self, '_sql_index'): self._sql_index = []
      return self._sql_index

    def getIndex(self, index_id):
      """
      """
      for c in self.getIndexList():
        if c.id == index_id:
          return c
      return None


    # Filtering
    def editFilter(self, REQUEST=None, RESPONSE=None):
      """
      This methods allows to set a filter on each zsql method called,
      so we can test if we should or not call a zsql method, so we can
      increase a lot the speed.
      """
      for zsql_method in self.objectValues():
        # We will first look if the filter is activated
        id = zsql_method.id
        if not self.filter_dict.has_key(id):
          self.filter_dict[id] = PersistentMapping()
          self.filter_dict[id]['filtered']=0
          self.filter_dict[id]['type']=[]
          self.filter_dict[id]['expression']=""
        if REQUEST.has_key('%s_box' % id):
          self.filter_dict[id]['filtered'] = 1
        else:
          self.filter_dict[id]['filtered'] = 0

        if REQUEST.has_key('%s_expression' % id):
          expression = REQUEST['%s_expression' % id]
          if expression == "":
            self.filter_dict[id]['expression'] = ""
            self.filter_dict[id]['expression_instance'] = None
          else:
            expr_instance = Expression(expression)
            self.filter_dict[id]['expression'] = expression
            self.filter_dict[id]['expression_instance'] = expr_instance
        else:
          self.filter_dict[id]['expression'] = ""
          self.filter_dict[id]['expression_instance'] = None

        if REQUEST.has_key('%s_type' % id):
          list_type = REQUEST['%s_type' % id]
          if type(list_type) is type('a'):
            list_type = [list_type]
          self.filter_dict[id]['type'] = list_type
        else:
          self.filter_dict[id]['type'] = []

      if RESPONSE is not None:
        RESPONSE.redirect('manage_filter')

    def isMethodFiltered(self, method_name):
      """
      Returns 1 if the method is already filtered,
      else it returns 0
      """
      # Reset Filtet dict
      # self.filter_dict= PersistentMapping()
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return 0
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['filtered']
      return 0

    def getExpression(self, method_name):
      """
      Returns 1 if the method is already filtered,
      else it returns 0
      """
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return ""
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['expression']
      return ""

    def getExpressionInstance(self, method_name):
      """
      Returns 1 if the method is already filtered,
      else it returns 0
      """
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return None
      if self.filter_dict.has_key(method_name):
        return self.filter_dict[method_name]['expression_instance']
      return None

    def isPortalTypeSelected(self, method_name,portal_type):
      """
      Returns 1 if the method is already filtered,
      else it returns 0
      """
      if not hasattr(self,'filter_dict'):
        self.filter_dict = PersistentMapping()
        return 0
      if self.filter_dict.has_key(method_name):
        result = portal_type in (self.filter_dict[method_name]['type'])
        return result
      return 0


    def getFilterableMethodList(self):
      """
      Returns only zsql methods wich catalog or uncatalog objets
      """
      method_dict = {}
      for method_id in self.sql_catalog_object + self.sql_uncatalog_object + self.sql_update_object:
        method_dict[method_id] = 1
      method_list = map(lambda method_id: getattr(self, method_id, None), method_dict.keys())
      return filter(lambda method: method is not None, method_list)

    def getExpressionContext(self, ob):
        '''
        An expression context provides names for TALES expressions.
        '''
        data = {
            'here':         ob,
            'container':    aq_parent(aq_inner(ob)),
            'nothing':      None,
            'root':         ob.getPhysicalRoot(),
            'request':      getattr( ob, 'REQUEST', None ),
            'modules':      SecureModuleImporter,
            'user':         getSecurityManager().getUser(),
            }
        return getEngine().getContext(data)

    security.declarePublic( 'getAllowedRolesAndUsers' )
    def getAllowedRolesAndUsers(self, **kw):
      """
        Return allowed roles and users.
        This is supposed to be used with Z SQL Methods to check permissions
        when you list up documents.
      """
      user = _getAuthenticatedUser(self)
      allowedRolesAndUsers = self._listAllowedRolesAndUsers( user )

      # Patch for ERP5 by JP Smets in order
      # to implement worklists and search of local roles
      if kw.has_key('local_roles'):
        # Only consider local_roles if it is not empty
        if kw['local_roles'] != '' and  kw['local_roles'] != [] and  kw['local_roles'] is not None:
          local_roles = kw['local_roles']
          # Turn it into a list if necessary according to ';' separator
          if type(local_roles) == type('a'):
            local_roles = local_roles.split(';')
          # Local roles now has precedence (since it comes from a WorkList)
          allowedRolesAndUsers = []
          for role in local_roles:
            allowedRolesAndUsers.append('user:%s:%s' % (user, role))

      return allowedRolesAndUsers

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        kw[ 'allowedRolesAndUsers' ] = self.getAllowedRolesAndUsers(**kw) # XXX allowedRolesAndUsers naming is wrong

        # Patch for ERP5 by JP Smets in order
        # to implement worklists and search of local roles
        if kw.has_key('local_roles'):
          # Only consider local_roles if it is not empty
          if kw['local_roles'] != '' and  kw['local_roles'] != [] and  kw['local_roles'] is not None:
            local_roles = kw['local_roles']
            # Turn it into a list if necessary according to ';' separator
            if type(local_roles) == type('a'):
              local_roles = local_roles.split(';')
            # Local roles now has precedence (since it comes from a WorkList)
            kw[ 'allowedRolesAndUsers' ] = []
            for role in local_roles:
                 kw[ 'allowedRolesAndUsers' ].append('user:%s:%s' % (user, role))

        if not _checkPermission(
            CMFCorePermissions.AccessInactivePortalContent, self ):
            base = aq_base( self )
            now = DateTime()
            kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
            kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        #LOG("search allowedRolesAndUsers",0,str(kw[ 'allowedRolesAndUsers' ]))
        return apply(ZCatalog.searchResults, (self, REQUEST), kw)

    __call__ = searchResults

    def countResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.countResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        kw[ 'allowedRolesAndUsers' ] = self.getAllowedRolesAndUsers(**kw) # XXX allowedRolesAndUsers naming is wrong

        # Forget about permissions in statistics
        # (we should not count lines more than once
        if kw.has_key('select_expression'): del kw[ 'allowedRolesAndUsers' ]

        #if not _checkPermission(
        #    CMFCorePermissions.AccessInactivePortalContent, self ):
        #    base = aq_base( self )
        #    now = DateTime()
        #    #kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
        #    #kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        return apply(ZCatalog.countResults, (self, REQUEST), kw)

    def catalog_object(self, object, uid, idxs=None, is_object_moved=0):
        if idxs is None: idxs = []
        wf = getToolByName(self, 'portal_workflow')
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}
        #LOG('catalog_object vars', 0, str(vars))            
        w = IndexableObjectWrapper(vars, object)
        (security_uid, optimised_roles_and_users) = self.getSecurityUid(object, w)
        #LOG('catalog_object optimised_roles_and_users', 0, str(optimised_roles_and_users))
        # XXX we should build vars begore building the wrapper
        if optimised_roles_and_users is not None:
          vars['optimised_roles_and_users'] = optimised_roles_and_users
        else:
          vars['optimised_roles_and_users'] = None
        vars['security_uid'] = security_uid
        #LOG("IndexableObjectWrapper", 0,str(w.allowedRolesAndUsers()))
        #try:
        #LOG('catalog_object wrapper', 0, str(w.__dict__))  
        ZCatalog.catalog_object(self, w, uid, idxs=idxs, is_object_moved=is_object_moved)
        #except:
          # When we import data into Zope
          # the ZSQLCatalog does not work currently
          # since most of the time the SQL tables are not
          # created (yet)
          # It is better not to return an error for now
        #  pass

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=None):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object, path=None):
        """
          Remove from catalog.
        """
        if path is None:
          url = self.__url(object)
        else:
          url = path
        self.uncatalog_object(url)

    security.declarePrivate('moveObject')
    def moveObject(self, object, idxs=None):
        """
          Reindex in catalog, taking into account
          peculiarities of ERP5Catalog / ZSQLCatalog

          Useless ??? XXX
        """
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs, is_object_moved=1)

    security.declarePrivate('getSecurityUid')
    def getSecurityUid(self, object, w):
        """
          Cache a uid for each security permission

          We try to create a unique security (to reduce number of lines)
          and to assign security only to root document
        """
        # Find parent document (XXX this extra step should be deactivated on complex ERP5 installations)
        object_path = object.getPhysicalPath()
        portal_path = object.portal_url.getPortalObject().getPhysicalPath()
        if len(object_path) > len(portal_path) + 2 and getattr(object, 'isRADContent', 0):
          # This only applied to ERP5 Contents (not CPS)
          # We are now in the case of a subobject of a root document          
          # We want to return single security information          
          document_object = aq_inner(object)
          for i in range(0, len(object_path) - len(portal_path) - 2):
            document_object = document_object.aq_parent
          document_w = IndexableObjectWrapper({}, document_object)
          return self.getSecurityUid(document_object, document_w)
        # Get security information
        allowed_roles_and_users = w.allowedRolesAndUsers()
        # Sort it
        allowed_roles_and_users = list(allowed_roles_and_users)
        allowed_roles_and_users.sort()
        allowed_roles_and_users = tuple(allowed_roles_and_users)
        # Make sure no diplicates
        if not hasattr(aq_base(self), 'security_uid_dict'):
          self._clearSecurityCache()
        if self.security_uid_dict.has_key(allowed_roles_and_users):
          return (self.security_uid_dict[allowed_roles_and_users], None)
        self.security_uid_index = self.security_uid_index + 1
        self.security_uid_dict[allowed_roles_and_users] = self.security_uid_index
        return (self.security_uid_index, allowed_roles_and_users)

    # Overriden methods
    def _clearSecurityCache(self):
        self.security_uid_dict = OIBTree()
        self.security_uid_index = 0

    def refreshCatalog(self, clear=0):
        """ clear security cache and re-index everything we can find """
        self._clearSecurityCache()
        return ZCatalog.refreshCatalog(self, clear=clear)

    def manage_catalogClear(self, REQUEST=None, RESPONSE=None, URL1=None):
        """ clear security cache and the rest """
        self._clearSecurityCache()
        return ZCatalog.manage_catalogClear(self, REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL1)

    def manage_catalogIndexAll(self, REQUEST, RESPONSE, URL1):
      """ adds all objects to the catalog starting from the parent """
      elapse = time.time()
      c_elapse = time.clock()
  
      def reindex(oself, r_dict):
        path = oself.getPhysicalPath()
        if r_dict.has_key(path): return
        r_dict[path] = 1
        try:
          oself.reindexObject()
          get_transaction().commit() # Allows to reindex up to 10,000 objects without problems
        except:
          # XXX better exception handling required
          pass
        for o in oself.objectValues():
          reindex(o, r_dict)
      
      new_dict = {}        
      reindex(self.aq_parent, new_dict)
  
      elapse = time.time() - elapse
      c_elapse = time.clock() - c_elapse
  
      RESPONSE.redirect(URL1 +
                '/manage_catalogAdvanced?manage_tabs_message=' +
                urllib.quote('Catalog Indexed<br>'
                      'Total time: %s<br>'
                      'Total CPU time: %s' % (`elapse`, `c_elapse`)))                                    
    
InitializeClass(CatalogTool)
