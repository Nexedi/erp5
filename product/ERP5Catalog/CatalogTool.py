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

import sys
from copy import deepcopy
from collections import defaultdict
from math import ceil
from Products.CMFCore.CatalogTool import CatalogTool as CMFCoreCatalogTool
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery, SimpleQuery
from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.User import system as system_user
from Products.CMFCore.utils import UniqueObject, _getAuthenticatedUser, getToolByName
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Acquisition import aq_base, aq_inner, aq_parent, ImplicitAcquisitionWrapper
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.CMFActivity.ActivityTool import GroupedMessage
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from AccessControl.PermissionRole import rolesForPermissionOn

from MethodObject import Method

from Products.ERP5Security import mergedLocalRoles
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from Products.ZSQLCatalog.Utils import sqlquote

import warnings
from zLOG import LOG, PROBLEM, WARNING, INFO

ACQUIRE_PERMISSION_VALUE = []
DYNAMIC_METHOD_NAME = 'z_related_'
DYNAMIC_METHOD_NAME_LEN = len(DYNAMIC_METHOD_NAME)
STRICT_DYNAMIC_METHOD_NAME = DYNAMIC_METHOD_NAME + 'strict_'
STRICT_DYNAMIC_METHOD_NAME_LEN = len(STRICT_DYNAMIC_METHOD_NAME)
RELATED_DYNAMIC_METHOD_NAME = '_related'
# Negative as it's used as a slice end offset
RELATED_DYNAMIC_METHOD_NAME_LEN = -len(RELATED_DYNAMIC_METHOD_NAME)
ZOPE_SECURITY_SUFFIX = '__roles__'

class IndexableObjectWrapper(object):

    def __init__(self, ob):
        self.__ob = ob

    def __getattr__(self, name):
        return getattr(self.__ob, name)

    # We need to update the uid during the cataloging process
    uid = property(lambda self: self.__ob.getUid(),
                   lambda self, value: setattr(self.__ob, 'uid', value))

    def _getSecurityParameterList(self):
      result = self.__dict__.get('_cache_result', None)
      if result is None:
        ob = self.__ob
        # For each group or user, we have a list of roles, this list
        # give in this order : [roles on object, roles acquired on the parent,
        # roles acquired on the parent of the parent....]
        # So if we have ['-Author','Author'] we should remove the role 'Author'
        # but if we have ['Author','-Author'] we have to keep the role 'Author'
        localroles = {}
        skip_role_set = set()
        skip_role = skip_role_set.add
        clear_skip_role = skip_role_set.clear
        for key, role_list in mergedLocalRoles(ob).iteritems():
          new_role_list = []
          new_role = new_role_list.append
          clear_skip_role()
          for role in role_list:
            if role[:1] == '-':
              skip_role(role[1:])
            elif role not in skip_role_set:
              new_role(role)
          if new_role_list:
            localroles[key] = [new_role_list, False]

        portal = ob.getPortalObject()
        role_dict = dict(portal.portal_catalog.getSQLCatalog().\
                                              getSQLCatalogRoleKeysList())
        for user_info in portal.acl_users.searchUsers(id=tuple(localroles), exact_match=True):
          key = user_info['id']
          try:
            localroles[key][1] = True
          except KeyError:
            # We found a bug, report it but do not make indexation fail.
            LOG(
              'CatalogTool.IndexableObjectWrapper',
              PROBLEM,
              'searchUser(id=%r, exact_match=True) returned an entry with '
              'id=%r. This is very likely a bugin a PAS plugin !' % (
                tuple(localroles),
                key,
              ),
            )

        allowed_dict = {}

        # For each local role of a user:
        #   If the local role grants View permission, add it.
        # Every addition implies 2 lines:
        #   user:<user_id>
        #   user:<user_id>:<role_id>
        # A line must not be present twice in final result.
        allowed_role_set = set(rolesForPermissionOn('View', ob))
        # XXX the permission name is included by default for verbose
        # logging of security errors, but the catalog does not need to
        # index it. Unfortunately, rolesForPermissionOn does not have
        # an option to disable this behavior at calling time, so
        # discard it explicitly.
        allowed_role_set.discard('_View_Permission')
        # XXX Owner is hardcoded, in order to prevent searching for user on the
        # site root.
        allowed_role_set.discard('Owner')

        # XXX make this a method of base ?
        local_roles_group_id_dict = deepcopy(getattr(ob,
          '__ac_local_roles_group_id_dict__', {}))

        # If we acquire a permission, then we also want to acquire the local
        # roles group ids
        local_roles_container = ob
        while getattr(local_roles_container, 'isRADContent', 0):
          if local_roles_container._getAcquireLocalRoles():
            local_roles_container = local_roles_container.aq_parent
            for role_definition_group, user_and_role_list in \
                getattr(local_roles_container,
                        '__ac_local_roles_group_id_dict__',
                        {}).items():
              local_roles_group_id_dict.setdefault(role_definition_group, set()
                ).update(user_and_role_list)
          else:
            break

        allowed_by_local_roles_group_id = {}
        allowed_by_local_roles_group_id[''] = allowed_role_set

        optimized_role_set = set()
        for role_definition_group, user_and_role_list in local_roles_group_id_dict.iteritems():
          group_allowed_set = allowed_by_local_roles_group_id.setdefault(
            role_definition_group, set())
          for user, role in user_and_role_list:
            if role in allowed_role_set:
              prefix = 'user:' + user
              group_allowed_set.update((prefix, '%s:%s' % (prefix, role)))
              optimized_role_set.add((user, role))
        user_role_dict = {}
        user_view_permission_role_dict = {}
        for user, (roles, user_exists) in localroles.iteritems():
          prefix = 'user:' + user
          for role in roles:
            is_not_in_optimised_role_set = (user, role) not in optimized_role_set
            if user_exists and role in role_dict:
              # User is a user (= not a group) and role is configured as
              # monovalued.
              if is_not_in_optimised_role_set:
                user_role_dict[role] = user
              if role in allowed_role_set:
                # ...and local role grants view permission.
                user_view_permission_role_dict[role] = user
            elif role in allowed_role_set:
              # User is a group and local role grants view permission.
              for group in local_roles_group_id_dict.get(user, ('', )):
                group_allowed_set = allowed_by_local_roles_group_id.setdefault(
                  group, set())
                if is_not_in_optimised_role_set:
                  group_allowed_set.add(prefix)
                  group_allowed_set.add('%s:%s' % (prefix, role))

        # sort `allowed` principals
        sorted_allowed_by_local_roles_group_id = {}
        for local_roles_group_id, allowed in \
                allowed_by_local_roles_group_id.iteritems():
          sorted_allowed_by_local_roles_group_id[local_roles_group_id] = tuple(
            sorted(allowed))

        self._cache_result = result = (sorted_allowed_by_local_roles_group_id,
                                       user_role_dict,
                                       user_view_permission_role_dict)
      return result

    def getLocalRolesGroupIdDict(self):
      """Returns a mapping of local roles group id to roles and users with View
      permission.
      """
      return self._getSecurityParameterList()[0]

    def getAssignee(self):
      """Returns the user ID of the user with 'Assignee' local role on this
      document.

      If there is more than one Assignee local role, the result is undefined.
      """
      return self._getSecurityParameterList()[1].get('Assignee', None)

    def getViewPermissionAssignee(self):
      """Returns the user ID of the user with 'Assignee' local role on this
      document, if the Assignee role has View permission.

      If there is more than one Assignee local role, the result is undefined.
      """
      return self._getSecurityParameterList()[2].get('Assignee', None)

    def getViewPermissionAssignor(self):
      """Returns the user ID of the user with 'Assignor' local role on this
      document, if the Assignor role has View permission.

      If there is more than one Assignor local role, the result is undefined.
      """
      return self._getSecurityParameterList()[2].get('Assignor', None)

    def getViewPermissionAssociate(self):
      """Returns the user ID of the user with 'Associate' local role on this
      document, if the Associate role has View permission.

      If there is more than one Associate local role, the result is undefined.
      """
      return self._getSecurityParameterList()[2].get('Associate', None)

    def __repr__(self):
      return '<Products.ERP5Catalog.CatalogTool.IndexableObjectWrapper'\
          ' for %s>' % ('/'.join(self.__ob.getPhysicalPath()), )


class RelatedBaseCategory(Method):
    """A Dynamic Method to act as a related key.
    """
    def __init__(self, id, strict_membership=0, related=0):
      self._id = id
      if strict_membership:
        strict = 'AND %(category_table)s.category_strict_membership = 1\n'
      else:
        strict = ''
      # From the point of view of query_table, we are looking up objects...
      if related:
        # ... which have a relation toward us
        # query_table's uid = category table's category_uid
        query_table_side = 'category_uid'
        # category table's uid = foreign_table's uid
        foreign_side = 'uid'
      else:
        # ... toward which we have a relation
        # query_table's uid = category table's uid
        query_table_side = 'uid'
        # category table's category_uid = foreign_table's uid
        foreign_side = 'category_uid'
      self._template = """\
%%(category_table)s.base_category_uid = %%(base_category_uid)s
%(strict)sAND %%(foreign_catalog)s.uid = %%(category_table)s.%(foreign_side)s
%%(RELATED_QUERY_SEPARATOR)s
%%(category_table)s.%(query_table_side)s = %%(query_table)s.uid""" % {
          'strict': strict,
          'foreign_side': foreign_side,
          'query_table_side': query_table_side,
      }
      self._monotable_template = """\
%%(category_table)s.base_category_uid = %%(base_category_uid)s
%(strict)sAND %%(category_table)s.%(query_table_side)s = %%(query_table)s.uid""" % {
          'strict': strict,
          'query_table_side': query_table_side,
      }

    def __call__(self, instance, table_0, table_1=None, query_table='catalog',
        RELATED_QUERY_SEPARATOR=' AND ', **kw):
      """Create the sql code for this related key."""
      # Note: in normal conditions, our category's uid will not change from
      # one invocation to the next.
      return (
        self._monotable_template if table_1 is None else self._template
      ) % {
        'base_category_uid': instance.getPortalObject().portal_categories.\
          _getOb(self._id).getUid(),
        'query_table': query_table,
        'category_table': table_0,
        'foreign_catalog': table_1,
        'RELATED_QUERY_SEPARATOR': RELATED_QUERY_SEPARATOR,
      }

class CatalogTool (UniqueObject, ZCatalog, CMFCoreCatalogTool, ActiveObject):
    """
    This is a ZSQLCatalog that filters catalog queries.
    It is based on ZSQLCatalog
    """
    id = 'portal_catalog'
    meta_type = 'ERP5 Catalog'
    security = ClassSecurityInfo()

    default_result_limit = None
    default_count_limit = 1

    manage_options = ({ 'label' : 'Overview', 'action' : 'manage_overview' },
                     ) + ZCatalog.manage_options

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    # Explicit Inheritance
    __url = CMFCoreCatalogTool.__url
    manage_catalogFind = CMFCoreCatalogTool.manage_catalogFind

    security.declareProtected(Permissions.ManagePortal
                , 'manage_schema')
    manage_schema = DTMLFile('dtml/manageSchema', globals())

    security.declarePublic('getPreferredSQLCatalogId')
    def getPreferredSQLCatalogId(self, id=None):
      """
      Get the SQL Catalog from preference.
      """
      if id is None:
        # Check if we want to use an archive
        #if getattr(aq_base(self.portal_preferences), 'uid', None) is not None:
        archive_path = self.portal_preferences.getPreferredArchive(sql_catalog_id=self.default_sql_catalog_id)
        if archive_path not in ('', None):
          try:
            archive = self.restrictedTraverse(archive_path)
          except KeyError:
            # Do not fail if archive object has been removed,
            # but preference is not up to date
            return None
          if archive is not None:
            catalog_id = archive.getCatalogId()
            if catalog_id not in ('', None):
              return catalog_id
        return None
      else:
        return id

    def _listAllowedRolesAndUsers(self, user):
        # We use ERP5Security PAS based authentication
        try:
          # check for proxy role in stack
          eo = getSecurityManager()._context.stack[-1]
          proxy_roles = getattr(eo, '_proxy_roles',None)
        except IndexError:
          proxy_roles = None
        if proxy_roles:
          # apply proxy roles
          user = eo.getOwner()
          result = list(proxy_roles)
        else:
          result = list(user.getRoles())
        result.append('Anonymous')
        result.append('user:%s' % user.getId())
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

    # Schema Management
    security.declareProtected(Permissions.ManagePortal, 'editColumn')
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

    security.declareProtected(Permissions.ManagePortal, 'setColumnList')
    def setColumnList(self, column_list):
      """
      """
      self._sql_schema = column_list

    security.declarePublic('getColumnList')
    def getColumnList(self):
      """
      """
      if not hasattr(self, '_sql_schema'): self._sql_schema = []
      return self._sql_schema

    security.declarePublic('getColumn')
    def getColumn(self, column_id):
      """
      """
      for c in self.getColumnList():
        if c.id == column_id:
          return c
      return None

    security.declareProtected(Permissions.ManagePortal, 'editIndex')
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

    security.declareProtected(Permissions.ManagePortal, 'setIndexList')
    def setIndexList(self, index_list):
      """
      """
      self._sql_index = index_list

    security.declarePublic('getIndexList')
    def getIndexList(self):
      """
      """
      if not hasattr(self, '_sql_index'): self._sql_index = []
      return self._sql_index

    security.declarePublic('getIndex')
    def getIndex(self, index_id):
      """
      """
      for c in self.getIndexList():
        if c.id == index_id:
          return c
      return None


    security.declarePublic('getAllowedRolesAndUsers')
    def getAllowedRolesAndUsers(self, sql_catalog_id=None, local_roles=None):
      """
        Return allowed roles and users.

        This is supposed to be used with Z SQL Methods to check permissions
        when you list up documents. It is also able to take into account
        a parameter named local_roles so that listed documents only include
        those documents for which the user (or the group) was
        associated one of the given local roles.

        The use of getAllowedRolesAndUsers is deprecated, you should use
        getSecurityQuery instead
      """
      user = _getAuthenticatedUser(self)
      user_str = user.getIdOrUserName()
      user_is_superuser = (user == system_user) or (user_str == SUPER_USER)
      allowedRolesAndUsers = self._listAllowedRolesAndUsers(user)
      role_column_dict = {}
      local_role_column_dict = {}
      catalog = self.getSQLCatalog(sql_catalog_id)
      column_map = catalog.getColumnMap()

      # We only consider here the Owner role (since it was not indexed)
      # since some objects may only be visible by their owner
      # which was not indexed
      for role, column_id in catalog.getSQLCatalogRoleKeysList():
        # XXX This should be a list
        if not user_is_superuser:
          try:
            # if called by an executable with proxy roles, we don't use
            # owner, but only roles from the proxy.
            eo = getSecurityManager()._context.stack[-1]
            proxy_roles = getattr(eo, '_proxy_roles', None)
            if not proxy_roles:
              role_column_dict[column_id] = user_str
          except IndexError:
            role_column_dict[column_id] = user_str

      # Patch for ERP5 by JP Smets in order
      # to implement worklists and search of local roles
      if local_roles:
        local_role_dict = dict(catalog.getSQLCatalogLocalRoleKeysList())
        role_dict = dict(catalog.getSQLCatalogRoleKeysList())
        # XXX user is not enough - we should also include groups of the user
        new_allowedRolesAndUsers = []
        new_role_column_dict = {}
        # Turn it into a list if necessary according to ';' separator
        if isinstance(local_roles, str):
          local_roles = local_roles.split(';')
        # Local roles now has precedence (since it comes from a WorkList)
        for user_or_group in allowedRolesAndUsers:
          for role in local_roles:
            # Performance optimisation
            if local_role_dict.has_key(role):
              # XXX This should be a list
              # If a given role exists as a column in the catalog,
              # then it is considered as single valued and indexed
              # through the catalog.
              if not user_is_superuser:
                # XXX This should be a list
                # which also includes all user groups
                column_id = local_role_dict[role]
                local_role_column_dict[column_id] = user_str
            if role_dict.has_key(role):
              # XXX This should be a list
              # If a given role exists as a column in the catalog,
              # then it is considered as single valued and indexed
              # through the catalog.
              if not user_is_superuser:
                # XXX This should be a list
                # which also includes all user groups
                column_id = role_dict[role]
                new_role_column_dict[column_id] = user_str
            new_allowedRolesAndUsers.append('%s:%s' % (user_or_group, role))
        if local_role_column_dict == {}:
          allowedRolesAndUsers = new_allowedRolesAndUsers
          role_column_dict = new_role_column_dict

      return allowedRolesAndUsers, role_column_dict, local_role_column_dict

    security.declarePublic('getSecurityUidDictAndRoleColumnDict')
    def getSecurityUidDictAndRoleColumnDict(self, sql_catalog_id=None, local_roles=None):
      """
        Return a dict of local_roles_group_id -> security Uids and a
        dictionnary containing available role columns.

        XXX: This method always uses default catalog. This should not break a
        site as long as security uids are considered consistent among all
        catalogs.
      """
      allowedRolesAndUsers, role_column_dict, local_role_column_dict = \
          self.getAllowedRolesAndUsers(
            sql_catalog_id=sql_catalog_id,
            local_roles=local_roles,
          )
      catalog = self.getSQLCatalog(sql_catalog_id)
      method = getattr(catalog, catalog.sql_search_security, None)
      if allowedRolesAndUsers:
        allowedRolesAndUsers.sort()
        cache_key = tuple(allowedRolesAndUsers)
        tv = getTransactionalVariable()
        try:
          security_uid_cache = tv['getSecurityUidDictAndRoleColumnDict']
        except KeyError:
          security_uid_cache = tv['getSecurityUidDictAndRoleColumnDict'] = {}
        try:
          security_uid_dict = security_uid_cache[cache_key]
        except KeyError:
          if method is None:
            warnings.warn("The usage of allowedRolesAndUsers is "\
                          "deprecated. Please update your catalog "\
                          "business template.", DeprecationWarning)
            security_uid_dict = {None: [x.security_uid for x in \
              self.unrestrictedSearchResults(
                allowedRolesAndUsers=allowedRolesAndUsers,
                select_expression="security_uid",
                group_by_expression="security_uid")] }
          else:
            # XXX: What with this string transformation ?! Souldn't it be done in
            # dtml instead ? ... yes, but how to be bw compatible ?
            allowedRolesAndUsers = [sqlquote(role) for role in allowedRolesAndUsers]

            security_uid_dict = defaultdict(list)
            for brain in method(security_roles_list=allowedRolesAndUsers):
              security_uid_dict[getattr(brain, 'local_roles_group_id', '')
                ].append(brain.uid)

          security_uid_cache[cache_key] = security_uid_dict
      else:
        security_uid_dict = []
      return security_uid_dict, role_column_dict, local_role_column_dict

    security.declarePublic('getSecurityQuery')
    def getSecurityQuery(self, query=None, sql_catalog_id=None, local_roles=None, **kw):
      """
        Build a query based on allowed roles or on a list of security_uid
        values. The query takes into account the fact that some roles are
        catalogued with columns.
      """
      user = _getAuthenticatedUser(self)
      user_str = user.getIdOrUserName()
      user_is_superuser = (user == system_user) or (user_str == SUPER_USER)
      if user_is_superuser:
        # We need no security check for super user.
        return query
      original_query = query
      security_uid_dict, role_column_dict, local_role_column_dict = \
          self.getSecurityUidDictAndRoleColumnDict(
            sql_catalog_id=sql_catalog_id,
            local_roles=local_roles,
          )

      role_query = None
      security_uid_query = None
      if role_column_dict:
        query_list = []
        for key, value in role_column_dict.items():
          new_query = Query(**{key : value})
          query_list.append(new_query)
        operator_kw = {'operator': 'OR'}
        role_query = ComplexQuery(*query_list, **operator_kw)
      if security_uid_dict:
        catalog_security_uid_groups_columns_dict = \
            self.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict()

        query_list = []
        for local_roles_group_id, security_uid_list in\
                 security_uid_dict.iteritems():
          assert security_uid_list
          query_list.append(Query(**{
            catalog_security_uid_groups_columns_dict[local_roles_group_id]:
                  security_uid_list,
            'operator': 'IN'}))

        security_uid_query = ComplexQuery(*query_list, operator='OR')

      if role_query:
        if security_uid_query:
          # merge
          query = ComplexQuery(security_uid_query, role_query, operator='OR')
        else:
          query = role_query
      elif security_uid_query:
        query = security_uid_query

      else:
        # XXX A false query has to be generated.
        # As it is not possible to use SQLKey for now, pass impossible value
        # on uid (which will be detected as False by MySQL, as it is not in the
        # column range)
        # Do not pass security_uid_list as empty in order to prevent useless
        # overhead
        query = Query(uid=-1)

      if local_role_column_dict:
        query_list = []
        for key, value in local_role_column_dict.items():
          new_query = Query(**{key : value})
          query_list.append(new_query)
        operator_kw = {'operator': 'AND'}
        local_role_query = ComplexQuery(*query_list, **operator_kw)
        query = ComplexQuery(query, local_role_query, operator='AND')

      if original_query is not None:
        query = ComplexQuery(query, original_query, operator='AND')
      return query

    # searchResults has inherited security assertions.
    def searchResults(self, query=None, sql_catalog_id=None, local_roles=None, **kw):
        """
        Calls ZCatalog.searchResults with extra arguments that
        limit the results to what the user is allowed to see.
        """
        #if not _checkPermission(
        #    Permissions.AccessInactivePortalContent, self):
        #    now = DateTime()
        #    kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
        #    kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }

        catalog_id = self.getPreferredSQLCatalogId(sql_catalog_id)
        query = self.getSecurityQuery(
          query=query,
          sql_catalog_id=catalog_id,
          local_roles=local_roles,
        )
        if query is not None:
          kw['query'] = query
        kw.setdefault('limit', self.default_result_limit)
        # get catalog from preference
        #LOG("searchResult", INFO, catalog_id)
        #         LOG("searchResult", INFO, ZCatalog.searchResults(self, query=query, sql_catalog_id=catalog_id, src__=1, **kw))
        return ZCatalog.searchResults(self, sql_catalog_id=catalog_id, **kw)

    __call__ = searchResults

    security.declarePrivate('unrestrictedSearchResults')
    def unrestrictedSearchResults(self, **kw):
        """Calls ZSQLCatalog.searchResults directly without restrictions.
        """
        kw.setdefault('limit', self.default_result_limit)
        return ZCatalog.searchResults(self, **kw)

    # We use a string for permissions here due to circular reference in import
    # from ERP5Type.Permissions
    security.declareProtected('Search ZCatalog', 'getResultValue')
    def getResultValue(self, **kw):
        """
        A method to factor common code used to search a single
        object in the database.
        """
        kw.setdefault('limit', 1)
        result = self.searchResults(**kw)
        try:
          return result[0].getObject()
        except IndexError:
          return None

    security.declarePrivate('unrestrictedGetResultValue')
    def unrestrictedGetResultValue(self, **kw):
        """
        A method to factor common code used to search a single
        object in the database. Same as getResultValue but without
        taking into account security.
        """
        kw.setdefault('limit', 1)
        result = self.unrestrictedSearchResults(**kw)
        try:
          return result[0].getObject()
        except IndexError:
          return None

    def countResults(self, query=None, sql_catalog_id=None, local_roles=None, **kw):
        """
            Calls ZCatalog.countResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        # XXX This needs to be set again
        #if not _checkPermission(
        #    Permissions.AccessInactivePortalContent, self):
        #    base = aq_base(self)
        #    now = DateTime()
        #    #kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
        #    #kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }
        catalog_id = self.getPreferredSQLCatalogId(sql_catalog_id)
        query = self.getSecurityQuery(
          query=query,
          sql_catalog_id=catalog_id,
          local_roles=local_roles,
        )
        if query is not None:
          kw['query'] = query
        kw.setdefault('limit', self.default_count_limit)
        # get catalog from preference
        return ZCatalog.countResults(self, sql_catalog_id=catalog_id, **kw)

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

        document_object = aq_inner(object)
        w = IndexableObjectWrapper(document_object)

        wf = getToolByName(self, 'portal_workflow')
        if wf is not None:
          w.__dict__.update(wf.getCatalogVariablesFor(object))

        # Find the parent definition for security
        is_acquired = 0
        while getattr(document_object, 'isRADContent', 0):
          # This condition tells which object should acquire
          # from their parent.
          # XXX Hardcode _View_Permission for a performance point of view
          if getattr(aq_base(document_object), '_View_Permission', ACQUIRE_PERMISSION_VALUE) == ACQUIRE_PERMISSION_VALUE\
             and document_object._getAcquireLocalRoles():
            document_object = document_object.aq_parent
            is_acquired = 1
          else:
            break
        if is_acquired:
          document_w = IndexableObjectWrapper(document_object)
        else:
          document_w = w

        (security_uid_dict, optimised_roles_and_users) = \
              catalog.getSecurityUidDict(document_w)


        w.optimised_roles_and_users = optimised_roles_and_users

        catalog_security_uid_groups_columns_dict = \
            catalog.getSQLCatalogSecurityUidGroupsColumnsDict()
        default_security_uid_column = catalog_security_uid_groups_columns_dict['']
        for local_roles_group_id, security_uid in security_uid_dict.items():
          catalog_column = catalog_security_uid_groups_columns_dict.get(
                local_roles_group_id, default_security_uid_column)
          setattr(w, catalog_column, security_uid)

        # XXX we should build vars begore building the wrapper

        predicate_property_dict = catalog.getPredicatePropertyDict(object)
        if predicate_property_dict is not None:
          w.predicate_property_dict = predicate_property_dict
        else:
          w.predicate_property_dict = {}

        (subject_set_uid, optimised_subject_list) = catalog.getSubjectSetUid(document_w)
        w.optimised_subject_list = optimised_subject_list
        w.subject_set_uid = subject_set_uid

        return ImplicitAcquisitionWrapper(w, aq_parent(document_object))

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=None, sql_catalog_id=None,**kw):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs, sql_catalog_id=sql_catalog_id,**kw)


    def catalogObjectList(self, object_list, *args, **kw):
        """Catalog a list of objects"""
        m = object_list[0]
        if isinstance(m, GroupedMessage):
          tmp_object_list = [x.object for x in object_list]
          super(CatalogTool, self).catalogObjectList(tmp_object_list, **m.kw)
          if tmp_object_list:
            exc_info = sys.exc_info()
          for x in object_list:
            if x.object in tmp_object_list:
              x.raised(exc_info)
            else:
              x.result = None
        else:
          super(CatalogTool, self).catalogObjectList(object_list, *args, **kw)

    security.declarePrivate('uncatalogObjectList')
    def uncatalogObjectList(self, message_list):
      """Uncatalog a list of objects"""
      # TODO: this is currently only a placeholder for further optimization
      try:
        for m in message_list:
          m.result = self.unindexObject(*m.args, **m.kw)
      except Exception:
        m.raised()

    security.declarePrivate('unindexObject')
    def unindexObject(self, object=None, path=None, uid=None,sql_catalog_id=None):
        """
          Remove from catalog.
        """
        if path is None and uid is None:
          if object is None:
            raise TypeError, 'One of uid, path and object parameters must not be None'
          path = self.__url(object)
        if uid is None:
          raise TypeError, "unindexObject supports only uid now"
        self.uncatalog_object(path=path, uid=uid, sql_catalog_id=sql_catalog_id)

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
      if not object.providesIPredicate():
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
      strict_destination_title | category,catalog/title/z_related_strict_destination

      strict_ related keys only returns documents which are strictly member of
      the category.
      """
      related_key_list = []
      base_cat_id_set = set(
        self.getPortalObject().portal_categories.getBaseCategoryList()
      )
      base_cat_id_set.discard('parent')
      default_string = 'default_'
      strict_string = 'strict_'
      related_string = 'related_'
      column_map = self.getSQLCatalog(sql_catalog_id).getColumnMap()
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
        split_key = key.split('_')
        for i in xrange(len(split_key) - 1, 0, -1):
          expected_base_cat_id = '_'.join(split_key[0:i])
          if expected_base_cat_id in base_cat_id_set:
            # We have found a base_category
            end_key = '_'.join(split_key[i:])
            related = end_key.startswith(related_string)
            if related:
              end_key = end_key[len(related_string):]
            # XXX: joining with non-catalog tables is not trivial and requires
            # ZSQLCatalog's ColumnMapper cooperation, so only allow catalog
            # columns.
            if 'catalog' in column_map.get(end_key, ()):
              is_uid = end_key == 'uid'
              if is_uid:
                end_key = 'uid' if related else 'category_uid'
              related_key_list.append(
                prefix + key + ' | category' +
                ('' if is_uid else ',catalog') +
                '/' +
                end_key +
                '/z_related_' +
                ('strict_' if strict else '') +
                expected_base_cat_id +
                ('_related' if related else '')
              )

      return related_key_list

    def _aq_dynamic(self, name):
      """
      Automatic related key generation.
      Will generate z_related_[base_category_id] if possible
      """
      result = None
      if name.startswith(DYNAMIC_METHOD_NAME) and \
          not name.endswith(ZOPE_SECURITY_SUFFIX):
        kw = {}
        if name.endswith(RELATED_DYNAMIC_METHOD_NAME):
          end_offset = RELATED_DYNAMIC_METHOD_NAME_LEN
          kw['related'] = 1
        else:
          end_offset = None
        if name.startswith(STRICT_DYNAMIC_METHOD_NAME):
          start_offset = STRICT_DYNAMIC_METHOD_NAME_LEN
          kw['strict_membership'] = 1
        else:
          start_offset = DYNAMIC_METHOD_NAME_LEN
        method = RelatedBaseCategory(name[start_offset:end_offset], **kw)
        setattr(self.__class__, name, method)
        # This getattr has 2 purposes:
        # - wrap in acquisition context
        #   This alone should be explicitly done rather than through getattr.
        # - wrap (if needed) class attribute on the instance
        #   (for the sake of not relying on current implementation details
        #   "too much")
        result = getattr(self, name)
      return result

    def _searchAndActivate(self, method_id, method_args=(), method_kw={},
                           activate_kw={}, min_uid=None, group_kw={}, **kw):
      """Search the catalog and run a script by activity on all found objects

      In order to not generate too many activities, this method limits the
      number of rows to fetch from the catalog, and if the catalog would return
      more results, it resumes by calling itself by activity.

      'activate_kw' is for common activate parameters between all generated
      activities and is usually used for priority and dependencies.

      Common usage is to call this method without 'select_method_id'.
      In this case, found objects are processed via a CMFActivity grouping,
      and this can be configured via 'group_kw', for additional parameters to
      pass to CMFActivity (in particular: 'activity' and 'group_method_*').
      A generic grouping method is used if none is given.
      group_method_cost default to 30 objects per packet.

      'select_method_id', if provided, will be called with partial catalog
      results and returned value will be provided to the callable identified by
      'method_id' (which will no longer be invoked in the context of a given
      document returned by catalog) as first positional argument.
      Use 'packet_size' parameter to limit the size of each group (default: 30).

      'activity_count' parameter is deprecated.
      Its value should be hardcoded because CMFActivity can now handle many
      activities efficiently and any tweak should benefit to everyone.
      However, there are still rare cases where one want to limit the number
      of processing nodes, to minimize latency of high-priority activities.
      """
      catalog_kw = kw.copy()
      select_method_id = catalog_kw.pop('select_method_id', None)
      if select_method_id:
        packet_size = catalog_kw.pop('packet_size', 30)
        limit = packet_size * catalog_kw.pop('activity_count', 100)
      elif 'packet_size' in catalog_kw: # BBB
        assert not group_kw, (kw, group_kw)
        packet_size = catalog_kw.pop('packet_size')
        group_method_cost = 1. / packet_size
        limit = packet_size * catalog_kw.pop('activity_count', 100)
      else:
        group_method_cost = group_kw.get('group_method_cost', .034) # 30 objects
        limit = catalog_kw.pop('activity_count', None) or \
          100 * int(ceil(1 / group_method_cost))
      if min_uid:
        catalog_kw['min_uid'] = SimpleQuery(uid=min_uid,
                                            comparison_operator='>')
      if catalog_kw.pop('restricted', False):
        search = self
      else:
        search = self.unrestrictedSearchResults
      r = search(sort_on=(('uid','ascending'),), limit=limit, **catalog_kw)
      result_count = len(r)
      if result_count:
        if result_count == limit:
          next_kw = activate_kw.copy()
          next_kw['priority'] = 1 + next_kw.get('priority', 1)
          self.activate(activity='SQLQueue', **next_kw) \
              ._searchAndActivate(method_id,method_args, method_kw,
                                  activate_kw, r[-1].getUid(),
                                  group_kw=group_kw, **kw)
        if select_method_id:
          portal_activities = self.getPortalObject().portal_activities
          active_portal_activities = portal_activities.activate(
            activity='SQLQueue', **activate_kw)
          r = getattr(portal_activities, select_method_id)(r)
          activate = getattr(active_portal_activities, method_id)
          for i in xrange(0, result_count, packet_size):
            activate(r[i:i+packet_size], *method_args, **method_kw)
        else:
          kw = activate_kw.copy()
          kw['activity'] = 'SQLQueue'
          if group_method_cost < 1:
            kw['group_method_cost'] = group_method_cost
            kw['group_method_id'] = None
            kw.update(group_kw)
          for r in r:
            getattr(r.activate(**kw), method_id)(*method_args, **method_kw)

    security.declarePublic('searchAndActivate')
    def searchAndActivate(self, *args, **kw):
      """Restricted version of _searchAndActivate"""
      return self._searchAndActivate(restricted=True, *args, **kw)

    security.declareProtected(Permissions.ManagePortal, 'upgradeSchema')
    def upgradeSchema(self, sql_catalog_id=None, src__=0):
      """Upgrade all catalog tables, with ALTER or CREATE queries"""
      catalog = self.getSQLCatalog(sql_catalog_id)
      connection_id = catalog.z_create_catalog.connection_id
      src = []
      db = self.getPortalObject()[connection_id]()
      with db.lock():
        for clear_method in catalog.sql_clear_catalog:
          r = catalog[clear_method]._upgradeSchema(
            connection_id, create_if_not_exists=1, src__=1)
          if r:
            src.append(r)
        if not src__:
          for r in src:
            db.query(r)
      return src


InitializeClass(CatalogTool)
