##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Vincent Pelletier <vincent@nexedi.com>
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

from SearchKey import SearchKey
from Products.ZSQLCatalog.Query.Query import Query
from Products.ZSQLCatalog.Query.RelatedQuery import RelatedQuery
from Products.ZSQLCatalog.Query.SQLQuery import SQLQuery
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.Interface.ISearchKey import IRelatedKey
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

BACKWARD_COMPATIBILITY = True

class RelatedKey(SearchKey):
  """
    This SearchKey handles searched on virtual columns of RelatedKey type.
    It generates joins required by the virtual column to reach the actual
    column to compare, plus a regular query on that column if needed.
  """

  __implements__ = IRelatedKey

  related_key_definition = None

  @profiler_decorator
  def _buildRelatedKey(self, related_key_definition):
    """
      Extract RelatedKey parameters from its definition, and cache this
      result. If related_key_definition changes since last computation, cached
      values will be refreshed.

      related_key_definition (string)
        Describes parameters of a RelatedKey. It is composed of 3 mains parts,
        separated by '/':
        - a list of table names
          Table names are separated by ','
        - a column name
        - the name of the related key ZSQLMethod
    """
    assert related_key_definition is not None
    if self.related_key_definition != related_key_definition:
      self.related_key_definition = related_key_definition
      # Extract related_key_id, column_id and table_list from related_key_definition
      table_list, self.real_column, self.related_key_id = related_key_definition.split('/')
      self.table_list = table_list.split(',')

  @profiler_decorator
  def _getSearchKey(self, sql_catalog, search_key_name):
    """
      Get search key relevant to the actual column.

      sql_catalog (SQLCatalog)
        Used to access SearchKey provider.
      search_key_name (string, None)
        See SQLCatalog.getSearchKey.
    """
    return sql_catalog.getSearchKey(self.real_column, search_key_name)

  @profiler_decorator
  def getSearchKey(self, sql_catalog, related_key_definition, search_key_name=None):
    """
      Get search key relevant to the actual column, extracting information
      about that column first if needed.

      sql_catalog (SQLCatalog)
        Used to access SearchKey provider.
      related_key_definition (string)
        See _buildRelatedKey.
      search_key_name (string, None)
        See SQLCatalog.getSearchKey.
    """
    self._buildRelatedKey(related_key_definition)
    return self._getSearchKey(sql_catalog, search_key_name)

  @profiler_decorator
  def buildQuery(self, sql_catalog, related_key_definition,
                 search_value=None):
    self._buildRelatedKey(related_key_definition)
    if isinstance(search_value, Query):
      search_value.setGroup(self.getColumn())
    join_condition = search_value
    return RelatedQuery(search_key=self,
                        join_condition=join_condition)

  @profiler_decorator
  def registerColumnMap(self, column_map, table_alias_list=None):
    related_column = self.getColumn()
    group = column_map.registerRelatedKey(related_column, self.real_column)
    # Each table except last one must be registered to their own group, so that
    # the same table can be used multiple time (and aliased multiple times)
    # in the same related key. The last one must be register to related key
    # "main" group (ie, the value of the "group" variable) to be the same as
    # the ta ble used in join_condition.
    if table_alias_list is not None:
      assert len(self.table_list) == len(table_alias_list)
    for table_position in xrange(len(self.table_list) - 1):
      table_name = self.table_list[table_position]
      local_group = column_map.registerRelatedKeyColumn(related_column, table_position, group)
      column_map.registerTable(table_name, group=local_group)
      if table_alias_list is not None:
        # Pre-resolve all tables with given aliases
        given_name, given_alias = table_alias_list[table_position]
        assert table_name == given_name
        column_map.resolveTable(table_name, given_alias, group=local_group)
    table_name = self.table_list[-1]
    column_map.registerTable(table_name, group=group)
    if table_alias_list is not None:
      given_name, given_alias = table_alias_list[-1]
      assert table_name == given_name
      column_map.resolveTable(table_name, given_alias, group=group)
    # Resolve (and register) related key column in related key group with its last table.
    column_map.registerColumn(self.real_column, group=group)
    column_map.resolveColumn(self.real_column, table_name, group=group)
    # Always register catalog, since it is always the "base" table of
    # RelatedKeys.
    column_map.registerCatalog()
    return group

  @profiler_decorator
  def buildSQLExpression(self, sql_catalog, column_map, only_group_columns, group):
    """
      Render RelatedKey's ZSQLMethod by providing it table aliases from
      ColumnMap.

      sql_catalog (SQLCatalog)
      column_map (ColumnMap)
      group (string)
      only_group_columns (bool)
        Ignored.
    """
    related_key = getattr(sql_catalog, self.related_key_id)
    table_alias_dict = dict(
      [('table_%s' % (x, ), column_map.getTableAlias(self.table_list[x], group=column_map.getRelatedKeyGroup(x, group)))
       for x in xrange(len(self.table_list) - 1)])
    x = len(table_alias_dict)
    assert x == len(self.table_list) - 1
    table_alias_dict['table_%s' % (x, )] = column_map.getTableAlias(self.table_list[x], group=group)
    rendered_related_key = related_key(
      query_table=column_map.getCatalogTableAlias(),
      src__=1,
      **table_alias_dict)
    # Important:
    # Former catalog separated join condition from related query.
    # Example:
    #   ComplexQuery(Query(title="foo"),
    #                Query(subordination_title="bar")
    #                , operator='OR')
    # Former catalog rendering (truncated where-expression):
    #   AND ((catalog.title LIKE '%foo%') OR
    #        (related_catalog_1.title LIKE '%bar%'))
    #   AND (related_catalog_1.uid = related_category_0.category_uid AND
    #        related_category_0.base_category_uid = 873 AND
    #        related_category_0.uid = catalog.uid)
    # As you can see, the part of the query joining the tables is *out* of the
    # OR expression, and therefor applies to the entire query.
    # This was done on purpose, because doing otherwise gives very poor
    # performances (on a simple data set, similar query can take *minutes* to
    # execute - as of MySQL 5.x).
    # Doing the same way as the former catalog is required for backward
    # compatibility, until a decent alternative is found (like spliting the
    # "OR" expression into ensemblist operations at query level).
    # Note that doing this has a side effect on result list, as objects
    # lacking a relation will never appear in the result.
    if BACKWARD_COMPATIBILITY:
      column_map.addJoinQuery(SQLQuery(rendered_related_key))
      return None
    else:
      return SQLExpression(self, where_expression=rendered_related_key)

verifyClass(IRelatedKey, RelatedKey)

