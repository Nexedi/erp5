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

from Products.CMFCore.CatalogTool import CatalogTool as CMFCoreCatalogTool
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.CatalogTool import IndexableObjectWrapper as CMFCoreIndexableObjectWrapper
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser, getToolByName
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Acquisition import aq_base, aq_inner, aq_parent
from DateTime.DateTime import DateTime

from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFCore.utils import _mergedLocalRoles

from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine

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
        ob = self.__ob
        allowed = {}
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1
        localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
                # Added for ERP5 project by JP Smets
                if role != 'Owner': allowed['user:' + user + ':' + role] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
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
    _listAllowedRolesAndUsers = CMFCoreCatalogTool._listAllowedRolesAndUsers
    __url = CMFCoreCatalogTool.__url
    manage_catalogFind = CMFCoreCatalogTool.manage_catalogFind

    security.declareProtected( CMFCorePermissions.ManagePortal
                , 'manage_filter' )
    manage_filter = DTMLFile( 'dtml/manageFilter', globals() )

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

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        user = _getAuthenticatedUser(self)
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )

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
            #kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
            #kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        return apply(ZCatalog.searchResults, (self, REQUEST), kw)

    __call__ = searchResults

    def countResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.countResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        user = _getAuthenticatedUser(self)
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )

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

        # Forget about permissions in statistics
        # (we should not count lines more than once
        if kw.has_key('stat_query'): del kw[ 'allowedRolesAndUsers' ]



        if not _checkPermission(
            CMFCorePermissions.AccessInactivePortalContent, self ):
            base = aq_base( self )
            now = DateTime()
            #kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
            #kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        return apply(ZCatalog.countResults, (self, REQUEST), kw)

    def catalog_object(self, object, uid, idxs=[]):
        wf = getToolByName(self, 'portal_workflow')
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}
        w = IndexableObjectWrapper(vars, object)
        #try:
        ZCatalog.catalog_object(self, w, uid, idxs)
        #except:
          # When we import data into Zope
          # the ZSQLCatalog does not work currently
          # since most of the time the SQL tables are not
          # created (yet)
          # It is better not to return an error for now
        #  pass

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[]):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
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



InitializeClass(CatalogTool)
