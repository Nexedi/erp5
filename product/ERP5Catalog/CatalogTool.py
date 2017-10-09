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
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery
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
from Products import ERP5Security
from Products.ZSQLCatalog.Utils import sqlquote

import warnings
from zLOG import LOG, PROBLEM, WARNING, INFO

ACQUIRE_PERMISSION_VALUE = []
DYNAMIC_METHOD_NAME = 'z_related_'
DYNAMIC_METHOD_NAME_LEN = len(DYNAMIC_METHOD_NAME)
STRICT_METHOD_NAME = 'strict_'
STRICT_METHOD_NAME_LEN = len(STRICT_METHOD_NAME)
PARENT_METHOD_NAME = 'parent_'
PARENT_METHOD_NAME_LEN = len(PARENT_METHOD_NAME)
RELATED_DYNAMIC_METHOD_NAME = '_related'
# Negative as it's used as a slice end offset
RELATED_DYNAMIC_METHOD_NAME_LEN = -len(RELATED_DYNAMIC_METHOD_NAME)
ZOPE_SECURITY_SUFFIX = '__roles__'
IGNORE_BASE_CATEGORY_UID = 'any'

SECURITY_QUERY_ARGUMENT_NAME = 'ERP5Catalog_security_query'

DYNAMIC_RELATED_KEY_FLAG_PARENT    = 1 << 0
DYNAMIC_RELATED_KEY_FLAG_STRICT    = 1 << 1
DYNAMIC_RELATED_KEY_FLAG_PREDICATE = 1 << 2
# Note: parsing flags backward as "pop()" is O(1), so this list contains flags
# in right to left order.
DYNAMIC_RELATED_KEY_FLAG_LIST = (
  ('parent', DYNAMIC_RELATED_KEY_FLAG_PARENT),
  ('strict', DYNAMIC_RELATED_KEY_FLAG_STRICT),
  ('predicate', DYNAMIC_RELATED_KEY_FLAG_PREDICATE),
)
EMPTY_SET = ()

class IndexableObjectWrapper(object):
    __security_parameter_cache = None
    __local_role_cache = None

    def __init__(self, ob, user_set, role_dict):
        self.__ob = ob
        self.__user_set = user_set
        self.__role_dict = role_dict

    def __getattr__(self, name):
        return getattr(self.__ob, name)

    # We need to update the uid during the cataloging process
    uid = property(lambda self: self.__ob.getUid(),
                   lambda self, value: setattr(self.__ob, 'uid', value))

    def __getLocalRoleDict(self):
      local_role_dict = self.__local_role_cache
      if local_role_dict is None:
        ob = self.__ob
        # For each group or user, we have a list of roles, this list
        # give in this order : [roles on object, roles acquired on the parent,
        # roles acquired on the parent of the parent....]
        # So if we have ['-Author','Author'] we should remove the role 'Author'
        # but if we have ['Author','-Author'] we have to keep the role 'Author'
        local_role_dict = {}
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
            local_role_dict[key] = [new_role_list, False]
        self.__local_role_cache = local_role_dict
      return local_role_dict

    def _getSecurityGroupIdList(self):
      """
      Return the list of security group identifiers this document is
      interested in. They may be actual user identifiers or not.
      Supposed to be accessed by CatalogTool.
      """
      return self.__getLocalRoleDict().keys()

    def _getSecurityParameterList(self):
      result = self.__security_parameter_cache
      if result is None:
        ob = self.__ob
        local_role_dict = self.__getLocalRoleDict()

        role_dict = self.__role_dict
        user_set = self.__user_set
        for security_group_id, security_group_data in local_role_dict.iteritems():
          security_group_data[1] = security_group_id in user_set

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
        for user, (roles, user_exists) in local_role_dict.iteritems():
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

        self.__security_parameter_cache = result = (
          sorted_allowed_by_local_roles_group_id,
          user_role_dict,
          user_view_permission_role_dict,
        )
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
    def __init__(self, id, strict_membership=0, related=0, query_table_column='uid'):
      self._id = id
      if self._id == IGNORE_BASE_CATEGORY_UID:
        base_category_sql = ''
      else:
        base_category_sql = "%(category_table)s.base_category_uid = %(base_category_uid)s AND\n"
      if strict_membership:
        strict = '%(category_table)s.category_strict_membership = 1 AND\n'
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
%(base_category)s%(strict)s%%(foreign_catalog)s.uid = %%(category_table)s.%(foreign_side)s
%%(RELATED_QUERY_SEPARATOR)s
%%(category_table)s.%(query_table_side)s = %%(query_table)s.%(query_table_column)s""" % {
          'base_category': base_category_sql,
          'strict': strict,
          'foreign_side': foreign_side,
          'query_table_side': query_table_side,
          'query_table_column': query_table_column
      }
      self._monotable_template = """\
%(base_category)s%(strict)s%%(category_table)s.%(query_table_side)s = %%(query_table)s.%(query_table_column)s""" % {
          'base_category': base_category_sql,
          'strict': strict,
          'query_table_side': query_table_side,
          'query_table_column': query_table_column,
      }

    def __call__(self, instance, table_0, table_1=None, query_table='catalog',
        RELATED_QUERY_SEPARATOR=' AND ', **kw):
      """Create the sql code for this related key."""
      format_dict = {
        'query_table': query_table,
        'category_table': table_0,
        'foreign_catalog': table_1,
        'RELATED_QUERY_SEPARATOR': RELATED_QUERY_SEPARATOR,
      }
      if self._id != IGNORE_BASE_CATEGORY_UID:
        # Note: in normal conditions, our category's uid will not change from
        # one invocation to the next.
        format_dict['base_category_uid'] = instance.getPortalObject().portal_categories.\
          _getOb(self._id).getUid()
      return (
        self._monotable_template if table_1 is None else self._template
      ) % format_dict

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
        archive_path = self.portal_preferences.getPreferredArchive(sql_catalog_id=self.getDefaultSqlCatalogId())
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
      user_is_superuser = (user == system_user) or (user_str == ERP5Security.SUPER_USER)
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
                select_list=["security_uid"],
                group_by=["security_uid"])] }
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
    def getSecurityQuery(self, sql_catalog_id=None, local_roles=None, **kw):
      """
        Build a query based on allowed roles or on a list of security_uid
        values. The query takes into account the fact that some roles are
        catalogued with columns.
      """
      user = _getAuthenticatedUser(self)
      user_str = user.getIdOrUserName()
      user_is_superuser = (user == system_user) or (user_str == ERP5Security.SUPER_USER)
      if user_is_superuser:
        # We need no security check for super user.
        return
      security_uid_dict, role_column_dict, local_role_column_dict = \
          self.getSecurityUidDictAndRoleColumnDict(
            sql_catalog_id=sql_catalog_id,
            local_roles=local_roles,
          )
      query_list = []
      append = query_list.append
      for key, value in role_column_dict.iteritems():
        append(SimpleQuery(**{key : value}))
      if security_uid_dict:
        catalog_security_uid_groups_columns_dict = self.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict()
        for local_roles_group_id, security_uid_list in security_uid_dict.iteritems():
          assert security_uid_list
          append(SimpleQuery(
            **{catalog_security_uid_groups_columns_dict[local_roles_group_id]: security_uid_list}
          ))
      if query_list:
        query = ComplexQuery(query_list, logical_operator='OR')
        if local_role_column_dict:
          query = ComplexQuery(
            [
              SimpleQuery(**{key : value})
              for key, value in local_role_column_dict.items()
            ] + [query],
            logical_operator='AND',
          )
      else:
        # XXX A false query has to be generated.
        # As it is not possible to use SQLKey for now, pass impossible value
        # on uid (which will be detected as False by MySQL, as it is not in the
        # column range)
        # Do not pass security_uid_list as empty in order to prevent useless
        # overhead
        query = SimpleQuery(uid=-1)
      return query

    # searchResults has inherited security assertions.
    def searchResults(self, sql_catalog_id=None, local_roles=None, **kw):
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
          sql_catalog_id=catalog_id,
          local_roles=local_roles,
        )
        if SECURITY_QUERY_ARGUMENT_NAME in kw:
          # Note: we must *not* create a ComplexQuery on behalf of caller.
          # ComplexQueries bypass SearchKey mechanism, which would make passed
          # "security_query" argument behave differently from arbitrary names.
          raise ValueError('%r is a reserved argument.' % SECURITY_QUERY_ARGUMENT_NAME)
        if query is not None:
          kw[SECURITY_QUERY_ARGUMENT_NAME] = query
        kw.setdefault('limit', self.default_result_limit)
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

    def countResults(self, sql_catalog_id=None, local_roles=None, **kw):
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
          sql_catalog_id=catalog_id,
          local_roles=local_roles,
        )
        if SECURITY_QUERY_ARGUMENT_NAME in kw:
          # Note: we must *not* create a ComplexQuery on behalf of caller.
          # ComplexQueries bypass SearchKey mechanism, which would make passed
          # "security_query" argument behave differently from arbitrary names.
          raise ValueError('%r is a reserved argument.' % SECURITY_QUERY_ARGUMENT_NAME)
        if query is not None:
          kw[SECURITY_QUERY_ARGUMENT_NAME] = query
        kw.setdefault('limit', self.default_count_limit)
        return ZCatalog.countResults(self, sql_catalog_id=catalog_id, **kw)

    security.declarePrivate('unrestrictedCountResults')
    def unrestrictedCountResults(self, REQUEST=None, **kw):
        """Calls ZSQLCatalog.countResults directly without restrictions.
        """
        return ZCatalog.countResults(self, REQUEST, **kw)

    def wrapObjectList(self, object_value_list, catalog_value):
      """
        Return a list of wrapped objects for reindexing.
      """
      portal = self.getPortalObject()

      user_set = set()
      role_dict = dict(catalog_value.getSQLCatalogRoleKeysList())
      catalog_security_uid_groups_columns_dict = catalog_value.getSQLCatalogSecurityUidGroupsColumnsDict()
      default_security_uid_column = catalog_security_uid_groups_columns_dict['']
      getPredicatePropertyDict = catalog_value.getPredicatePropertyDict
      security_group_set = set()
      wrapper_list = []
      for object_value in object_value_list:
        document_object = aq_inner(object_value)
        w = IndexableObjectWrapper(document_object, user_set, role_dict)
        w.predicate_property_dict = getPredicatePropertyDict(object_value) or {}
        security_group_set.update(w._getSecurityGroupIdList())

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
          document_w = IndexableObjectWrapper(document_object, user_set, role_dict)
          security_group_set.update(document_w._getSecurityGroupIdList())
        else:
          document_w = w
        wrapper_list.append((document_object, w, document_w))

      # Note: we mutate the set, so all related wrappers get (purposedly)
      # affected by this, which must happen before _getSecurityParameterList
      # is called (which happens when calling getSecurityUidDict below).
      user_set.update(
        x['id'] for x in portal.acl_users.searchUsers(
          id=list(security_group_set),
          exact_match=True,
        )
      )

      getSecurityUidDict = catalog_value.getSecurityUidDict
      getSubjectSetUid = catalog_value.getSubjectSetUid
      wrapped_object_list = []
      for (document_object, w, document_w) in wrapper_list:
        (
          security_uid_dict,
          w.optimised_roles_and_users,
        ) = getSecurityUidDict(document_w)
        for local_roles_group_id, security_uid in security_uid_dict.iteritems():
          catalog_column = catalog_security_uid_groups_columns_dict.get(
            local_roles_group_id,
            default_security_uid_column,
          )
          setattr(w, catalog_column, security_uid)
        (
          w.subject_set_uid,
          w.optimised_subject_list,
        ) = getSubjectSetUid(document_w)

        wrapped_object_list.append(ImplicitAcquisitionWrapper(w, aq_parent(document_object)))
      return wrapped_object_list

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

      Syntax:
        [[predicate_][strict_][parent_]_]<base category id>__[related__]<column id>
      "predicate": Use predicate_category as relation table, otherwise category table.
      "strict": Match only strict relation members, otherwise match non-strict too.
      "parent": Search for documents whose parent have described relation, otherwise search for their immediate relations.
      <base_category_id>: The id of an existing Base Category document, or "any" to not restrict by relation type.
      "related": Search for reverse relationships, otherwise search for direct relationships.
      <column_id>: The name of the column to compare values against.

      Old syntax is supported for backward-compatibility, but will not receive
      further extensions:
        [default_][strict_][parent_]<base category id>_[related_]<column id>
      """
      base_category_id_set = set(
        self.getPortalObject().portal_categories.getBaseCategoryList()
      )
      base_category_id_set.discard('parent')
      column_map = self.getSQLCatalog(sql_catalog_id).getColumnMap()
      related_key_list = []
      for key in key_list:
        flag_bitmap = 0
        if '__' in key:
          split_key = key.split('__')
          column_id = split_key.pop()
          if 'catalog' not in column_map.get(column_id, ()):
            continue
          base_category_id = split_key.pop()
          related = base_category_id == 'related'
          if related:
            base_category_id = split_key.pop()
          if split_key:
            flag_string, = split_key
            flag_list = flag_string.split('_')
            pop = flag_list.pop
            for flag_name, flag in DYNAMIC_RELATED_KEY_FLAG_LIST:
              if flag_list[-1] == flag_name:
                flag_bitmap |= flag
                pop()
                if not flag_list:
                  break
            else:
              continue
        else:
          # BBB: legacy related key format
          default_string = 'default_'
          related_string = 'related_'
          prefix = key
          if prefix.startswith(default_string):
            prefix = prefix[len(default_string):]
          if prefix.startswith(STRICT_METHOD_NAME):
            prefix = prefix[len(STRICT_METHOD_NAME):]
            flag_bitmap |= DYNAMIC_RELATED_KEY_FLAG_STRICT
          if prefix.startswith(PARENT_METHOD_NAME):
            prefix = prefix[len(PARENT_METHOD_NAME):]
            flag_bitmap |= DYNAMIC_RELATED_KEY_FLAG_PARENT
          split_key = prefix.split('_')
          for i in xrange(len(split_key) - 1, 0, -1):
            base_category_id = '_'.join(split_key[0:i])
            if base_category_id in base_category_id_set or (
              i == len(split_key) - 1 and base_category_id == IGNORE_BASE_CATEGORY_UID
            ):
              # We have found a base_category
              column_id = '_'.join(split_key[i:])
              related = column_id.startswith(related_string)
              if related:
                column_id = column_id[len(related_string):]
              # XXX: joining with non-catalog tables is not trivial and requires
              # ZSQLCatalog's ColumnMapper cooperation, so only allow catalog
              # columns.
              if 'catalog' in column_map.get(column_id, ()):
                break
          else:
            continue
        is_uid = column_id == 'uid'
        if is_uid:
          column_id = 'uid' if related else 'category_uid'
        related_key_list.append(
          key + ' | ' +
          ('predicate_' if flag_bitmap & DYNAMIC_RELATED_KEY_FLAG_PREDICATE else '') + 'category' +
          ('' if is_uid else ',catalog') +
          '/' +
          column_id +
          '/' + DYNAMIC_METHOD_NAME +
          (STRICT_METHOD_NAME if flag_bitmap & DYNAMIC_RELATED_KEY_FLAG_STRICT else '') +
          (PARENT_METHOD_NAME if flag_bitmap & DYNAMIC_RELATED_KEY_FLAG_PARENT else '') +
          base_category_id +
          (RELATED_DYNAMIC_METHOD_NAME if related else '')
        )
      return related_key_list

    security.declarePublic('getCategoryValueDictParameterDict')
    def getCategoryValueDictParameterDict(self, base_category_dict, category_table='category', strict_membership=True, forward=True, onJoin=lambda x: None):
      """
      From a mapping from base category ids to lists of documents, produce a
      query tree testing (strict or not, forward or reverse relation)
      membership to these documents with their respective base categories.

      base_category_dict (dict with base category ids as keys and document sets
      as values)
        Note: mutated by this method.
      category_table ('category' or 'predicate_category')
        Controls the table to use for membership lookup.
      strict_membership (bool)
        Whether intermediate relation members should be excluded (true) or
        included (false).
      forward (bool)
        Whether document being looked up bears the relation (true) or is its
        target (false).
      onJoin(column_name) -> None or query
        Called for each generated query which imply a join. Specifically, this
        will not be called for "parent" relation, as it does not involve a
        join.
        Receives pseudo-column name of the relation as argument.
        If return value is not None, it must be a query tree, OR-ed with
        existing conditions for given pseudo-column.
        This last form should very rarely be needed (ex: when joining with
        predicate_category table as it contains non-standard uid values).

      Return a query tree.
      """
      flag_list = []
      if category_table == 'predicate_category':
        flag_list.append('predicate')
      elif category_table != 'category':
        raise ValueError('Unknown category table %r' % (category_table, ))
      if strict_membership:
        flag_list.append('strict')
      prefix = ('_'.join(flag_list) + '__') if flag_list else ''
      suffix = ('' if forward else '__related') + '__uid'
      parent_document_set = base_category_dict.pop('parent', None)
      query_list = []
      for base_category_id, document_set in base_category_dict.iteritems():
        column = prefix + base_category_id + suffix
        category_query = SimpleQuery(**{
          column: {document.getUid() for document in document_set},
        })
        extra_query = onJoin(column)
        if extra_query is not None:
          category_query = ComplexQuery(
            category_query,
            extra_query,
            logical_operator='OR',
          )
        query_list.append(category_query)
      if parent_document_set is not None:
        if forward:
          if strict_membership:
            query_list.append(SimpleQuery(
              parent_uid={
                document.getUid()
                for document in parent_document_set
              },
            ))
          else:
            query_list.append(SimpleQuery(
              path={
                x.getPath().replace('_', r'\_').replace('%', r'\%') + '/%'
                for x in parent_document_set
              },
              comparison_operator='like',
            ))
        else:
          parent_uid_set = {
            document.getUid()
            for document in parent_document_set
          }
          if not strict_membership:
            for document in parent_document_set:
              while True:
                document = document.getParentValue()
                uid = getattr(document, 'getUid', lambda: None)()
                if uid is None:
                  break
                parent_uid_set.add(uid)
          query_list.append(SimpleQuery(uid=parent_uid_set))
      return ComplexQuery(query_list)

    security.declarePublic('getCategoryParameterDict')
    def getCategoryParameterDict(self, category_list, onMissing=lambda category: True, **kw):
      """
      From a list of categories, produce a query tree testing (strict or not,
      forward or reverse relation) membership to these documents with their
      respective base categories.

      category_list (list of category relative urls with their base categories)
      onMissing (callable)
        Called for each category which does not exist.
        Receives faulty relative url as "category" argument.
        False return value skips the entry.
        True return value causes a None placeholder to be inserted.
        Raised exceptions will propagate.

      Other arguments & return value: see getCategoryValueDictParameterDict.
      """
      base_category_dict = defaultdict(set)
      portal_categories = self.getPortalObject().portal_categories
      getBaseCategoryId = portal_categories.getBaseCategoryId
      getCategoryValue = portal_categories.getCategoryValue
      for relative_url in category_list:
        category_uid = getCategoryValue(relative_url)
        if category_uid is not None or onMissing(category=relative_url):
          base_category_dict[getBaseCategoryId(relative_url)].add(category_uid)
      return self.getCategoryValueDictParameterDict(
        base_category_dict,
        **kw
      )

    def _aq_dynamic(self, name):
      """
      Automatic related key generation.
      Will generate z_related_[base_category_id] if possible
      """
      result = None
      if name.startswith(DYNAMIC_METHOD_NAME) and \
          not name.endswith(ZOPE_SECURITY_SUFFIX):
        base_name = name[DYNAMIC_METHOD_NAME_LEN:]
        kw = {}
        if base_name.endswith(RELATED_DYNAMIC_METHOD_NAME):
          base_name = base_name[:RELATED_DYNAMIC_METHOD_NAME_LEN]
          kw['related'] = 1
        if base_name.startswith(STRICT_METHOD_NAME):
          base_name = base_name[STRICT_METHOD_NAME_LEN:]
          kw['strict_membership'] = 1
        if base_name.startswith(PARENT_METHOD_NAME):
          base_name = base_name[PARENT_METHOD_NAME_LEN:]
          kw['query_table_column'] = 'parent_uid'
        method = RelatedBaseCategory(base_name, **kw)
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
          for i in xrange(0, len(r), packet_size):
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
      if 'uid' in kw:
        raise TypeError("'uid' cannot be used to select documents as it is "
          "used internally")
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

    security.declarePublic('getDocumentValueList')
    def getDocumentValueList(self, sql_catalog_id=None,
                             search_context=None, language=None,
                             strict_language=True, all_languages=None,
                             all_versions=None, now=None, **kw):
      """
        Return the list of documents which belong to the
        current section. The API is designed to
        support additional parameters so that it is possible
        to group documents by reference, version, language, etc.
        or to implement filtering of documents.

        This method must be implemented through a
        catalog method script :
          SQLCatalog_getDocumentValueList

        Here is the list of arguments :
          * search_context
          * language
          * strict_language
          * all_languages
          * all_versions
          * now

        If you specify search_context, its predicate will be
        respected,
        i.e. web_section.WebSection_getDocumentValueList is
        equivalent to
        portal_catalog.getDocumentValueList(search_context=web_section)
      """
      catalog = self.getSQLCatalog(sql_catalog_id)
      return catalog.SQLCatalog_getDocumentValueList(
          search_context=search_context,
          language=language,
          strict_language=strict_language,
          all_languages=all_languages,
          all_versions=all_versions,
          now=now,
          **kw)

InitializeClass(CatalogTool)
