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
from Products.ZSQLCatalog.interfaces.search_key import IRelatedKey
from zope.interface.verify import verifyClass
from zope.interface import implements
from Products.ZSQLCatalog.TableDefinition import TableAlias, InnerJoin, LeftJoin

from logging import getLogger
log = getLogger(__name__)

BACKWARD_COMPATIBILITY = True

RELATED_QUERY_SEPARATOR = "\nAND -- related query separator\n"

RELATED_KEY_MISMATCH_MESSAGE = "\
A rendered related key must contain the same number of querying \
conditions as the tables it relates, properly separated by \
RELATED_QUERY_SEPARATOR. \n\
Offending related key: %r, for column %r, table_alias_list: %r, \
rendered_related_key: \n%s"


class RelatedKey(SearchKey):
  """
    This SearchKey handles searches on virtual columns of RelatedKey type.
    It generates joins required by the virtual column to reach the actual
    column to compare, plus a regular query on that column if needed.
  """

  implements(IRelatedKey)

  related_key_definition = None

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

  def _getSearchKey(self, sql_catalog, search_key_name):
    """
      Get search key relevant to the actual column.

      sql_catalog (SQLCatalog)
        Used to access SearchKey provider.
      search_key_name (string, None)
        See SQLCatalog.getSearchKey.
    """
    return sql_catalog.getSearchKey(self.real_column, search_key_name)

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

  def buildQuery(self, sql_catalog, related_key_definition,
                 search_value=None):
    self._buildRelatedKey(related_key_definition)
    if isinstance(search_value, Query):
      search_value.setGroup(self.getColumn())
    return RelatedQuery(search_key=self,
                        join_condition=search_value)

  def registerColumnMap(self, column_map, table_alias_list=None):
    related_column = self.getColumn()
    group = column_map.registerRelatedKey(related_column, self.real_column)
    # Each table except last one must be registered to their own
    # group, so that the same table can be used multiple times (and
    # aliased multiple times) in the same related key. The last one
    # must be registered to the related key "main" group (ie, the
    # value of the "group" variable) to be the same as the table used
    # in join_condition.
    assert table_alias_list is None or len(self.table_list) == len(table_alias_list), (
            self.table_list, table_alias_list)
    for table_position in xrange(len(self.table_list) - 1):
      table_name = self.table_list[table_position]
      local_group = column_map.registerRelatedKeyColumn(related_column, table_position, group)
      column_map.registerTable(table_name, group=local_group)
      if table_alias_list is not None:
        # Pre-resolve all tables with given aliases
        given_name, given_alias = table_alias_list[table_position]
        assert table_name == given_name, (table_name, given_name)
        column_map.resolveTable(table_name, given_alias, group=local_group)
    table_name = self.table_list[-1]
    column_map.registerTable(table_name, group=group)
    if table_alias_list is not None:
      given_name, given_alias = table_alias_list[-1]
      assert table_name == given_name, (table_name, given_name)
      column_map.resolveTable(table_name, given_alias, group=group)
    # Resolve (and register) related key column in related key group with its last table.
    column_map.registerColumn(self.real_column, group=group)
    column_map.resolveColumn(self.real_column, table_name, group=group)
    return group

  def stitchJoinDefinition(self, table_alias_list, join_query_list, column_map):
    alias, table = table_alias_list[-1]
    right = column_map.makeTableAliasDefinition(table, alias)
    if not join_query_list:
      # nothing to do, just return the table alias
      assert len(table_alias_list) == 1, table_alias_list
      return right
    else:
      # create an InnerJoin of the last element of the alias list with
      # a chain of InnerJoins of the rest of the list conditioned on
      # the the last element of the join_query_list
      left = self.stitchJoinDefinition(table_alias_list[:-1],
                                       join_query_list[:-1],
                                       column_map)
      condition = join_query_list[-1]
      return InnerJoin(left, right, condition)

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

    # related key is defined in catalog
    related_table_list, destination_table = self.table_list[:-1], self.table_list[-1]

    # method caching
    getTableAlias = column_map.getTableAlias
    getRelatedKeyGroup = column_map.getRelatedKeyGroup

    # table aliases for related tables
    table_alias_list = [(getTableAlias(related_table, group=getRelatedKeyGroup(index, group)), related_table)
                        for (index, related_table) in enumerate(related_table_list)]
    # table alias for destination table
    table_alias_list.append((getTableAlias(destination_table, group=group),
                             destination_table))

    # map aliases to use in ZSQLMethod.
    table_alias_dict = {'table_%s' % index: alias[0]
                        for index, alias in enumerate(table_alias_list)}

    assert len(table_alias_list) == len(table_alias_dict), (table_alias_list,
      table_alias_dict)

    query_table=column_map.getCatalogTableAlias()
    rendered_related_key = related_key(
      query_table=query_table,
      RELATED_QUERY_SEPARATOR=RELATED_QUERY_SEPARATOR,
      src__=1,
      **table_alias_dict)
    join_condition_list = rendered_related_key.split(RELATED_QUERY_SEPARATOR)

    # Important:
    # Previously the catalog separated join condition from the related query.
    # Example:
    #   ComplexQuery(Query(title="foo"),
    #                Query(subordination_title="bar")
    #                , logical_operator='OR')
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
    #
    # Because of this, we never return an SQLExpression here, as it
    # would mix join definition with column condition in the body of
    # the WHERE clause. Instead we explicitly define a Join to the
    # catalog. The ColumnMap defines whether this is an Inner Join or
    # a Left Outer Join. Notice that if an Inner Join is decided,
    # objects lacking a relationship will never appear in the result.

    if len(join_condition_list) == len(table_alias_list):
      # Good! we got a compatible method that splits the join
      # conditions according to the related tables.
      #
      # Add a join on this related key, based on the chain of
      # inner-joins of the related key tables.
      query_table_join_condition = join_condition_list.pop()
      right_side = self.stitchJoinDefinition(table_alias_list,
                                             join_condition_list,
                                             column_map)
      column_map.addRelatedKeyJoin(self.column,
                                   right_side=right_side,
                                   condition=query_table_join_condition)
    else:
      # Method did not render the related key condition with the
      # appropriate separators so we could split it

      # XXX: Can we try to parse rendered_related_key to select which
      # conditions go with each table? Maybe we could still use
      # explicit joins this way...

      msg = RELATED_KEY_MISMATCH_MESSAGE % (self.related_key_id,
                                            self.column,
                                            table_alias_list,
                                            rendered_related_key)
      if BACKWARD_COMPATIBILITY:
        # BBB: remove this branch of the condition, and the above
        # constant, when all zsql_methods have been adapted to return
        # the join queries properly separated by the
        # RELATED_QUERY_SEPARATOR.

        # The rendered related key doesn't have the separators for each
        # joined table, so we revert to doing implicit inner joins:
        log.warning(msg + "\n\nAdding an Implicit Join Condition...")
        column_map._addJoinQueryForColumn(self.column,
                                          SQLQuery(rendered_related_key))
      else:
        raise RuntimeError(msg)
    return None

verifyClass(IRelatedKey, RelatedKey)

