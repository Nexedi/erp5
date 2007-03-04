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
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.CatalogTool import IndexableObjectWrapper as CMFCoreIndexableObjectWrapper
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser, getToolByName
from Products.CMFCore.utils import _mergedLocalRoles
from Globals import InitializeClass, DTMLFile, package_home
from Acquisition import aq_base, aq_inner, aq_parent
from DateTime.DateTime import DateTime
from Products.CMFActivity.ActiveObject import ActiveObject

from AccessControl.PermissionRole import rolesForPermissionOn

from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine
from MethodObject import Method

from Products.ERP5Security.ERP5UserManager import SUPER_USER

import os, time, urllib, warnings
from zLOG import LOG

SECURITY_USING_NUX_USER_GROUPS, SECURITY_USING_PAS = range(2)
try:
  from Products.PluggableAuthService import PluggableAuthService
  PAS_meta_type = PluggableAuthService.PluggableAuthService.meta_type
except ImportError:
  PAS_meta_type = ''
try:
  from Products.ERP5Security import mergedLocalRoles as PAS_mergedLocalRoles
except ImportError:
  pass

try:
  from Products.NuxUserGroups import UserFolderWithGroups
  NUG_meta_type = UserFolderWithGroups.meta_type
except ImportError:
  NUG_meta_type = ''
try:
  from Products.NuxUserGroups.CatalogToolWithGroups import mergedLocalRoles
  from Products.NuxUserGroups.CatalogToolWithGroups import _getAllowedRolesAndUsers
except ImportError:
  pass

DEFAULT_RESULT_LIMIT = 1000

def getSecurityProduct(acl_users):
  """returns the security used by the user folder passed.
  (NuxUserGroup, ERP5Security, or None if anything else).
  """
  if acl_users.meta_type == PAS_meta_type:
    return SECURITY_USING_PAS
  elif acl_users.meta_type == NUG_meta_type:
    return SECURITY_USING_NUX_USER_GROUPS

class IndexableObjectWrapper(CMFCoreIndexableObjectWrapper):

    def __setattr__(self, name, value):
      # We need to update the uid during the cataloging process
      if name == 'uid':
        setattr(self.__ob, name, value)
      else:
        self.__dict__[name] = value

    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with
        View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self.__ob
        security_product = getSecurityProduct(ob.acl_users)
        withnuxgroups = security_product == SECURITY_USING_NUX_USER_GROUPS
        withpas = security_product == SECURITY_USING_PAS

        allowed = {}
        for r in rolesForPermissionOn('View', ob):
          allowed[r] = 1
        if withnuxgroups:
          localroles = mergedLocalRoles(ob, withgroups=1)
        elif withpas:
          localroles = PAS_mergedLocalRoles(ob)
        else:
          # CMF
          localroles = _mergedLocalRoles(ob)
        # For each group or user, we have a list of roles, this list
        # give in this order : [roles on object, roles acquired on the parent,
        # roles acquired on the parent of the parent....]
        # So if we have ['-Author','Author'] we should remove the role 'Author'
        # but if we have ['Author','-Author'] we have to keep the role 'Author'
        new_dict = {}
        for key in localroles.keys():
          new_list = []
          remove_list = []
          for role in localroles[key]:
            if role.startswith('-'):
              if not role[1:] in new_list and not role[1:] in remove_list:
                remove_list.append(role[1:])
            elif not role in remove_list:
              new_list.append(role)
          if len(new_list)>0:
            new_dict[key] = new_list
        localroles = new_dict
        for user, roles in localroles.items():
          for role in roles:
            if allowed.has_key(role):
              if withnuxgroups:
                allowed[user] = 1
              else:
                allowed['user:' + user] = 1
            # Added for ERP5 project by JP Smets
            # The reason why we do not want to keep Owner is because we are
            # trying to reduce the number of security definitions
            # However, this is a bad idea if we start to use Owner role
            # as a kind of bamed Assignee and if we need it for worklists. Therefore
            # we may sometimes catalog the owner user ID whenever the Owner
            # has view permission (see getAllowedRolesAndUsers bellow
            # as well as getViewPermissionOwner method in Base)
            if role != 'Owner': 
              if withnuxgroups:
                allowed[user + ':' + role] = 1
              else:
                allowed['user:' + user + ':' + role] = 1
        if allowed.has_key('Owner'):
          del allowed['Owner']
        return list(allowed.keys())

class RelatedBaseCategory(Method):
    """A Dynamic Method to act as a related key.
    """
    def __init__(self, id,strict_membership=0):
      self._id = id
      self.strict_membership=strict_membership

    def __call__(self, instance, table_0, table_1, query_table='catalog', **kw):
      """Create the sql code for this related key."""
      base_category_uid = instance.portal_categories._getOb(self._id).getUid()
      expression_list = []
      append = expression_list.append
      append('%s.uid = %s.category_uid' % (table_1,table_0))
      if self.strict_membership:
        append('AND %s.category_strict_membership = 1' % table_0)
      append('AND %s.base_category_uid = %s' % (table_0,base_category_uid))
      append('AND %s.uid = %s.uid' % (table_0,query_table))
      return ' '.join(expression_list)

class CatalogTool (UniqueObject, ZCatalog, CMFCoreCatalogTool, ActiveObject):
    """
    This is a ZSQLCatalog that filters catalog queries.
    It is based on ZSQLCatalog
    """
    id = 'portal_catalog'
    meta_type = 'ERP5 Catalog'
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' },
                     ) + ZCatalog.manage_options


    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    # Explicit Inheritance
    __url = CMFCoreCatalogTool.__url
    manage_catalogFind = CMFCoreCatalogTool.manage_catalogFind

    security.declareProtected( CMFCorePermissions.ManagePortal
                , 'manage_schema' )
    manage_schema = DTMLFile( 'dtml/manageSchema', globals() )

    security.declareProtected( 'Import/Export objects', 'addDefaultSQLMethods' )
    def addDefaultSQLMethods(self, config_id='erp5'):
      """
        Add default SQL methods for a given configuration.
      """
      # For compatibility.
      if config_id.lower() == 'erp5':
        config_id = 'erp5_mysql'
      elif config_id.lower() == 'cps3':
        config_id = 'cps3_mysql'

      addSQLCatalog = self.manage_addProduct['ZSQLCatalog'].manage_addSQLCatalog
      if config_id not in self.objectIds():
        addSQLCatalog(config_id, '')

      catalog = self.getSQLCatalog(config_id)
      addSQLMethod = catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
      product_path = package_home(globals())
      zsql_dirs = []

      # Common methods - for backward compatibility
      # SQL code distribution is supposed to be business template based nowadays
      if config_id.lower() == 'erp5_mysql':
        zsql_dirs.append(os.path.join(product_path, 'sql', 'common_mysql'))
        zsql_dirs.append(os.path.join(product_path, 'sql', 'erp5_mysql'))
      elif config_id.lower() == 'cps3_mysql':
        zsql_dirs.append(os.path.join(product_path, 'sql', 'common_mysql'))
        zsql_dirs.append(os.path.join(product_path, 'sql', 'cps3_mysql'))

      # Iterate over the sql directory. Add all sql methods in that directory.
      for directory in zsql_dirs:
        for entry in os.listdir(directory):
          if entry.endswith('.zsql'):
            id = entry[:-5]
            # Create an empty SQL method first.
            addSQLMethod(id = id, title = '', connection_id = '', arguments = '', template = '')
            #LOG('addDefaultSQLMethods', 0, 'catalog = %r' % (catalog.objectIds(),))
            sql_method = getattr(catalog, id)
            # Set parameters of the SQL method from the contents of a .zsql file.
            sql_method.fromFile(os.path.join(directory, entry))
          elif entry == 'properties.xml':
            # This sets up the attributes. The file should be generated by manage_exportProperties.
            catalog.manage_importProperties(os.path.join(directory, entry))

      # Make this the default.
      self.default_sql_catalog_id = config_id
     
    security.declareProtected( 'Import/Export objects', 'exportSQLMethods' )
    def exportSQLMethods(self, sql_catalog_id=None, config_id='erp5'):
      """
        Export SQL methods for a given configuration.
      """
      # For compatibility.
      if config_id.lower() == 'erp5':
        config_id = 'erp5_mysql'
      elif config_id.lower() == 'cps3':
        config_id = 'cps3_mysql'

      catalog = self.getSQLCatalog(sql_catalog_id)
      product_path = package_home(globals())
      common_sql_dir = os.path.join(product_path, 'sql', 'common_mysql')
      config_sql_dir = os.path.join(product_path, 'sql', config_id)
      common_sql_list = ('z0_drop_record', 'z_read_recorded_object_list', 'z_catalog_paths',
                         'z_record_catalog_object', 'z_clear_reserved', 'z_record_uncatalog_object',
                         'z_create_record', 'z_related_security', 'z_delete_recorded_object_list',
                         'z_reserve_uid', 'z_getitem_by_path', 'z_show_columns', 'z_getitem_by_path',
                         'z_show_tables', 'z_getitem_by_uid', 'z_unique_values', 'z_produce_reserved_uid_list',)
    
      msg = ''
      for id in catalog.objectIds(spec=('Z SQL Method',)):
        if id in common_sql_list:
          d = common_sql_dir
        else:
          d = config_sql_dir
        sql = catalog._getOb(id)
        # First convert the skin to text
        text = sql.manage_FTPget()
        name = os.path.join(d, '%s.zsql' % (id,))
        msg += 'Writing %s\n' % (name,)
        f = open(name, 'w')
        try:
          f.write(text)
        finally:
          f.close()
          
      properties = self.manage_catalogExportProperties(sql_catalog_id=sql_catalog_id)
      name = os.path.join(config_sql_dir, 'properties.xml')
      msg += 'Writing %s\n' % (name,)
      f = open(name, 'w')
      try:
        f.write(properties)
      finally:
        f.close()
        
      return msg
        
    def _listAllowedRolesAndUsers(self, user):
      security_product = getSecurityProduct(self.acl_users)
      if security_product == SECURITY_USING_PAS:
        # We use ERP5Security PAS based authentication
        try:
          # check for proxy role in stack
          eo = getSecurityManager()._context.stack[-1]
          proxy_roles = getattr(eo,'_proxy_roles',None)
        except IndexError:
          proxy_roles = None
        if proxy_roles:
          # apply proxy roles
          user = eo.getOwner()
          result = list( proxy_roles )
        else:
          result = list( user.getRoles() )
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        # deal with groups
        getGroups = getattr(user, 'getGroups', None)
        if getGroups is not None:
            groups = list(user.getGroups())
            groups.append('role:Anonymous')
            if 'Authenticated' in result:
                groups.append('role:Authenticated')
            for group in groups:
                result.append('user:%s' % group)
        # end groups
        return result
      elif security_product == SECURITY_USING_NUX_USER_GROUPS:
        return _getAllowedRolesAndUsers(user)
      else:
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


    security.declarePublic( 'getAllowedRolesAndUsers' )
    def getAllowedRolesAndUsers(self, **kw):
      """
        Return allowed roles and users.

        This is supposed to be used with Z SQL Methods to check permissions
        when you list up documents. It is also able to take into account
        a parameter named local_roles so that listed documents only include
        those documents for which the user (or the group) was
        associated one of the given local roles.

        XXX allowedRolesAndUsers naming is wrong
      """
      user = _getAuthenticatedUser(self)
      allowedRolesAndUsers = self._listAllowedRolesAndUsers(user)
      role_column_dict = {}

      # Patch for ERP5 by JP Smets in order
      # to implement worklists and search of local roles
      if kw.has_key('local_roles'):
        # XXX user is not enough - we should also include groups of the user
        # Only consider local_roles if it is not empty
        if kw['local_roles'] != '' and  kw['local_roles'] != [] and  kw['local_roles'] is not None:
          local_roles = kw['local_roles']
          new_allowedRolesAndUsers = []
          # Turn it into a list if necessary according to ';' separator
          if type(local_roles) == type('a'):
            local_roles = local_roles.split(';')
          # Local roles now has precedence (since it comes from a WorkList)
          for user_or_group in allowedRolesAndUsers:
            for role in local_roles:
              # Performance optimisation
              lower_role = role.lower()
              if self.getSQLCatalog().getColumnMap().has_key(lower_role):
                # If a given role exists as a column in the catalog,
                # then it is considered as single valued and indexed
                # through the catalog.
                if user != SUPER_USER:
                  role_column_dict[lower_role] = str(user) # XXX This should be a list
                                                           # which also includes all user groups
              else:
                # Else, we use the standard approach
                new_allowedRolesAndUsers.append('%s:%s' % (user_or_group, role))
          allowedRolesAndUsers = new_allowedRolesAndUsers
      else:
        # We only consider here the Owner role (since it was not indexed)
        # since some objects may only be visible by their owner
        # which was not indexed
        if self.getSQLCatalog().getColumnMap().has_key('owner'):
          if user != SUPER_USER:
            role_column_dict['owner'] = str(user)

      return allowedRolesAndUsers, role_column_dict

    security.declarePrivate('getSecurityQuery')
    def getSecurityQuery(self, query=None, **kw):
      """
        Build a query based on allowed roles (DEPRECATED)
        or on a list of security_uid values. The query takes into
        account the fact that some roles are catalogued with columns.
      """
      allowedRolesAndUsers, role_column_dict = self.getAllowedRolesAndUsers(**kw)
      catalog = self.getSQLCatalog()
      method = getattr(catalog, catalog.sql_search_security, '')
      original_query = query
      if method in ('', None):
        # XXX old way, should not be used anylonger
        warnings.warn("The usage of allowedRolesAndUsers is deprecated.\n"
                      "Please update your business template erp5_mysql_innodb.",
                      DeprecationWarning)
        if role_column_dict:
          query_list = []
          for key, value in role_column_dict.items():
            new_query = Query(**{key : value})
            query_list.append(new_query)
          operator_kw = {'operator': 'AND'} 
          query = ComplexQuery(*query_list, **operator_kw)
          if allowedRolesAndUsers:
            query = ComplexQuery(Query(allowedRolesAndUsers=allowedRolesAndUsers),
                                 query, operator='OR')
        else:
          query = Query(allowedRolesAndUsers=allowedRolesAndUsers)
      else:
        if allowedRolesAndUsers:
          allowedRolesAndUsers = ["'%s'" % (role, ) for role in allowedRolesAndUsers]
          security_uid_list = [x.uid for x in method(security_roles_list = allowedRolesAndUsers)]
        if role_column_dict:
          query_list = []
          for key, value in role_column_dict.items():
            new_query = Query(**{key : value})
            query_list.append(new_query)
          operator_kw = {'operator': 'AND'}
          query = ComplexQuery(*query_list, **operator_kw)
          if allowedRolesAndUsers and security_uid_list:
            query = ComplexQuery(Query(security_uid=security_uid_list),
                                 query, operator='OR')
        else:
          query = Query(security_uid=security_uid_list)
      if original_query is not None:
        query = ComplexQuery(query, original_query, operator='AND')
      return query

    # searchResults has inherited security assertions.
    def searchResults(self, query=None, **kw):
        """
        Calls ZCatalog.searchResults with extra arguments that
        limit the results to what the user is allowed to see.
        """
        if not _checkPermission(
            CMFCorePermissions.AccessInactivePortalContent, self ):
            now = DateTime()
            kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
            kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        query = self.getSecurityQuery(query=query, **kw)
        kw.setdefault('limit', DEFAULT_RESULT_LIMIT)
        return ZCatalog.searchResults(self, query=query, **kw)

    __call__ = searchResults

    security.declarePrivate('unrestrictedSearchResults')
    def unrestrictedSearchResults(self, REQUEST=None, **kw):
        """Calls ZSQLCatalog.searchResults directly without restrictions.
        """
        kw.setdefault('limit', DEFAULT_RESULT_LIMIT)
        return ZCatalog.searchResults(self, REQUEST, **kw)

    # We use a string for permissions here due to circular reference in import
    # from ERP5Type.Permissions
    security.declareProtected('Search ZCatalog', 'getResultValue')
    def getResultValue(self, query=None, **kw):
        """
        A method to factor common code used to search a single
        object in the database.
        """
        result = self.searchResults(query=query, **kw)
        try:
          return result[0].getObject()
        except IndexError:
          return None
    
    def countResults(self, query=None, **kw):
        """
            Calls ZCatalog.countResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        # XXX This needs to be set again
        #if not _checkPermission(
        #    CMFCorePermissions.AccessInactivePortalContent, self ):
        #    base = aq_base( self )
        #    now = DateTime()
        #    #kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
        #    #kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        query = self.getSecurityQuery(query=query, **kw)
        kw.setdefault('limit', DEFAULT_RESULT_LIMIT)
        return ZCatalog.countResults(self, query=query, **kw)
    
    security.declarePrivate('unrestrictedCountResults')
    def unrestrictedCountResults(self, REQUEST=None, **kw):
        """Calls ZSQLCatalog.countResults directly without restrictions.
        """
        return ZCatalog.countResults(self, REQUEST, **kw)

    def wrapObject(self, object, sql_catalog_id=None, **kw):
        """
          Return a wrapped object for reindexing.
        """
        catalog = self.getSQLCatalog(sql_catalog_id)
        if catalog is None:
          # Nothing to do.
          LOG('wrapObject', 0, 'Warning: catalog is not available')
          return (None, None)

        wf = getToolByName(self, 'portal_workflow')
        if wf is not None:
          vars = wf.getCatalogVariablesFor(object)
        else:
          vars = {}
        #LOG('catalog_object vars', 0, str(vars))

        w = IndexableObjectWrapper(vars, object)

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
        else:
          document_w = w

        (security_uid, optimised_roles_and_users) = catalog.getSecurityUid(document_w)
        #LOG('catalog_object optimised_roles_and_users', 0, str(optimised_roles_and_users))
        # XXX we should build vars begore building the wrapper
        if optimised_roles_and_users is not None:
          vars['optimised_roles_and_users'] = optimised_roles_and_users
        else:
          vars['optimised_roles_and_users'] = None
        predicate_property_dict = catalog.getPredicatePropertyDict(object)
        if predicate_property_dict is not None:
          vars['predicate_property_dict'] = predicate_property_dict
        vars['security_uid'] = security_uid

        return w

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=None, sql_catalog_id=None,**kw):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs, sql_catalog_id=sql_catalog_id,**kw)


    security.declarePrivate('unindexObject')
    def unindexObject(self, object, path=None, uid=None,sql_catalog_id=None):
        """
          Remove from catalog.
        """
        if path is None and uid is None:
          path = self.__url(object)
        self.uncatalog_object(path=path,uid=uid, sql_catalog_id=sql_catalog_id)

    security.declarePrivate('beforeUnindexObject')
    def beforeUnindexObject(self, object, path=None, uid=None,sql_catalog_id=None):
        """
          Remove from catalog.
        """
        if path is None and uid is None:
          path = self.__url(object)
        self.beforeUncatalogObject(path=path,uid=uid, sql_catalog_id=sql_catalog_id)

    security.declarePrivate('getUrl')
    def getUrl(self, object):
      return self.__url(object)

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

    security.declarePublic('getPredicatePropertyDict')
    def getPredicatePropertyDict(self, object):
      """
      Construct a dictionnary with a list of properties
      to catalog into the table predicate
      """
      if not getattr(object,'isPredicate',None):
        return None
      object = object.asPredicate()
      if object is None:
        return None
      property_dict = {}
      identity_criterion = getattr(object,'_identity_criterion',None)
      range_criterion = getattr(object,'_range_criterion',None)
      if identity_criterion is not None:
        for property, value in identity_criterion.items():
          if value is not None:
            property_dict[property] = value
      if range_criterion is not None:
        for property, (min, max) in range_criterion.items():
          if min is not None:
            property_dict['%s_range_min' % property] = min
          if max is not None:
            property_dict['%s_range_max' % property] = max
      property_dict['membership_criterion_category_list'] = object.getMembershipCriterionCategoryList()
      return property_dict

    security.declarePrivate('getDynamicRelatedKeyList')
    def getDynamicRelatedKeyList(self, key_list, sql_catalog_id=None):
      """
      Return the list of dynamic related keys.
      This method will try to automatically generate new related key
      by looking at the category tree.

      For exemple it will generate:
      destination_title | category,catalog/title/z_related_destination
      default_destination_title | category,catalog/title/z_related_destination
      """
      related_key_list = []
      base_cat_id_list = self.portal_categories.getBaseCategoryDict()
      default_string = 'default_'
      strict_string = 'strict_'
      for key in key_list:
        prefix = ''
        strict = 0
        if key.startswith(default_string):
          key = key[len(default_string):]
          prefix = default_string
        if key.startswith(strict_string):
          strict = 1
          key = key[len(strict_string):]
          prefix = prefix + strict_string
        splitted_key = key.split('_')
        # look from the end of the key from the beginning if we
        # can find 'title', or 'portal_type'...
        for i in range(1,len(splitted_key))[::-1]:
          expected_base_cat_id = '_'.join(splitted_key[0:i])
          if expected_base_cat_id != 'parent' and \
             expected_base_cat_id in base_cat_id_list:
            # We have found a base_category
            end_key = '_'.join(splitted_key[i:])
            # accept only some catalog columns
            if end_key in ('title', 'uid', 'description',
                           'relative_url', 'id', 'portal_type'):
              if strict:
                related_key_list.append(
                      '%s%s | category,catalog/%s/z_related_strict_%s' %
                      (prefix, key, end_key, expected_base_cat_id))
              else:
                related_key_list.append(
                      '%s%s | category,catalog/%s/z_related_%s' %
                      (prefix, key, end_key, expected_base_cat_id))

      return related_key_list

    def _aq_dynamic(self, name):
      """
      Automatic related key generation.
      Will generate z_related_[base_category_id] if possible
      """
      aq_base_name = getattr(aq_base(self), name, None)
      if aq_base_name == None:
        DYNAMIC_METHOD_NAME = 'z_related_'
        STRICT_DYNAMIC_METHOD_NAME = 'z_related_strict_'
        method_name_length = len(DYNAMIC_METHOD_NAME)
        zope_security = '__roles__'
        if (name.startswith(DYNAMIC_METHOD_NAME) and \
          (not name.endswith(zope_security))):
          if name.startswith(STRICT_DYNAMIC_METHOD_NAME):
            base_category_id = name[len(STRICT_DYNAMIC_METHOD_NAME):]
            method = RelatedBaseCategory(base_category_id,strict_membership=1)
          else:
            base_category_id = name[len(DYNAMIC_METHOD_NAME):]
            method = RelatedBaseCategory(base_category_id)
          setattr(self.__class__, name, 
                  method)
          klass = aq_base(self).__class__
          if hasattr(klass, 'security'):
            from Products.ERP5Type import Permissions as ERP5Permissions
            klass.security.declareProtected(ERP5Permissions.View, name)
          else:
            # XXX security declaration always failed....
            LOG('WARNING ERP5Form SelectionTool, security not defined on',
                0, klass.__name__)
          return getattr(self, name)
        else:
          return aq_base_name
      return aq_base_name



InitializeClass(CatalogTool)
