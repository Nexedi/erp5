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
from Globals import InitializeClass, DTMLFile, package_home
from Acquisition import aq_base, aq_inner, aq_parent
from DateTime.DateTime import DateTime
from Products.CMFActivity.ActiveObject import ActiveObject

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

    # Explicite Inheritance
    __url = CMFCoreCatalogTool.__url
    manage_catalogFind = CMFCoreCatalogTool.manage_catalogFind

    security.declareProtected( CMFCorePermissions.ManagePortal
                , 'manage_schema' )
    manage_schema = DTMLFile( 'dtml/manageSchema', globals() )

    def addDefaultSQLMethods(self, config_id='erp5'):
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

      # Common methods
      if config_id.lower() == 'erp5_mysql':
        zsql_dirs.append(os.path.join(product_path, 'sql', 'common_mysql'))
        zsql_dirs.append(os.path.join(product_path, 'sql', 'erp5_mysql'))
      elif config_id.lower() == 'cps3_mysql':
        zsql_dirs.append(os.path.join(product_path, 'sql', 'common_mysql'))
        zsql_dirs.append(os.path.join(product_path, 'sql', 'cps3_mysql'))
      # XXX TODO : add other cases

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
          (security_uid, optimised_roles_and_users) = catalog.getSecurityUid(document_w)
        else:
          document_w = w

        (security_uid, optimised_roles_and_users) = catalog.getSecurityUid(document_w)
        #LOG('catalog_object optimised_roles_and_users', 0, str(optimised_roles_and_users))
        # XXX we should build vars begore building the wrapper
        if optimised_roles_and_users is not None:
          vars['optimised_roles_and_users'] = optimised_roles_and_users
        else:
          vars['optimised_roles_and_users'] = None
        vars['security_uid'] = security_uid

        return w

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=None, sql_catalog_id=None):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs, sql_catalog_id=sql_catalog_id)

    security.declarePrivate('unindexObject')
    def unindexObject(self, object, path=None, sql_catalog_id=None):
        """
          Remove from catalog.
        """
        if path is None:
          url = self.__url(object)
        else:
          url = path
        self.uncatalog_object(url, sql_catalog_id=sql_catalog_id)

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

InitializeClass(CatalogTool)