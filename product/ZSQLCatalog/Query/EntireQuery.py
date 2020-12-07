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

import functools
import re
import warnings
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.ColumnMap import ColumnMap
from zLOG import LOG, WARNING
from Products.ZSQLCatalog.interfaces.entire_query import IEntireQuery
from zope.interface.verify import verifyClass
from zope.interface import implementer
from Products.ZSQLCatalog.TableDefinition import LegacyTableDefinition

# SQL identifier
# ZSQLCatalog only allows unquote-safe identifiers as table and column names,
# even though it may internally quote them.
# Also, this is a subset of what is accepted as SQL99 identifier: we restrict
# ourselves to ASCII.
UNQUOTED_SQL99_IDENTIFIER = '[0-9a-z$_]+'
COLUMN = '(' + UNQUOTED_SQL99_IDENTIFIER + r'\.)?' + UNQUOTED_SQL99_IDENTIFIER
def _check(value, match):
  if value is not None and match(value) is None:
    raise ValueError(repr(value))
  return value
checkIdentifier = functools.partial(
  _check,
  match=re.compile('^' + UNQUOTED_SQL99_IDENTIFIER + '$', re.I).match,
)
checkColumn = functools.partial(
  _check,
  match=re.compile('^' + COLUMN + '$', re.I).match,
)
# Are selectable:
# - "<identifier>([DISTINCT ]{<column>,*})" (ex: "COUNT(DISTINCT foo.reference)")
# - "<column>" (ex: "foo.reference" or "reference")
# - "''", a dirty hack to block acquisition on brain of values which should
#   not be available (see stat methods in ListBox)
checkSelectable = functools.partial(
  _check,
  match=re.compile(
    '^(' + UNQUOTED_SQL99_IDENTIFIER + r'\((DISTINCT )?(' + COLUMN + r'|\*)\)|' + COLUMN + "|'')$",
    re.I,
  ).match,
)
del _check
del COLUMN
del UNQUOTED_SQL99_IDENTIFIER

def defaultDict(value):
  if value is None:
    return {}
  assert isinstance(value, dict)
  return value

@implementer(IEntireQuery)
class EntireQuery(object):
  """
    This is not a Query subclass, since it does not define a
    registerColumnMap method, and instead does the ColumnMap handling
    internally.
  """

  column_map = None
  limit = None

  def __init__(self, query,
               order_by_list=(),
               group_by_list=(),
               select_dict=None,
               left_join_list=(),
               inner_join_list=(),
               limit=None,
               catalog_table_name=None,
               catalog_table_alias=None,
               extra_column_list=(),
               implicit_join=False):
    self.query = query
    self.order_by_list = my_order_by_list = []
    for order_by in order_by_list:
      assert isinstance(order_by, (tuple, list))
      column, direction, cast = (tuple(order_by) + (None, None))[:3]
      my_order_by_list.append((
        checkColumn(column),
        checkIdentifier(direction),
        checkIdentifier(cast) if cast else None,
      ))
    self.group_by_list = [checkColumn(x) for x in group_by_list]
    self.select_dict = {
      # Ideally, keys should only satisfy checkIdentifier, but as SQLCatalog
      # builds select_dict from select_list in which case keys equal values,
      # so align with the lowest denominator: selectable also cover columns,
      # which when there is no table name is an identifier.
      checkSelectable(alias): checkSelectable(column)
      for alias, column in defaultDict(select_dict).iteritems()
    }
    # No need to sanitize, it's compared against columns and not included in SQL
    self.left_join_list = left_join_list
    # No need to sanitize, it's compared against columns and not included in SQL
    self.inner_join_list = inner_join_list
    if limit:
      if not isinstance(limit, (list, tuple)):
        limit = (limit, )
      self.limit = [int(x) for x in limit]
    self.catalog_table_name = checkIdentifier(catalog_table_name)
    self.catalog_table_alias = checkIdentifier(catalog_table_alias) # XXX: check as quoted identifier ?
    self.extra_column_list = my_extra_column_list = []
    for extra_column in extra_column_list:
      table, column = extra_column.replace('`', '').split('.')
      if table != self.catalog_table_name:
        raise ValueError('Extra columns must be catalog columns. %r does not follow this rule (catalog=%r, extra_column_list=%r)' % (extra_column, self.catalog_table_name, extra_column_list))
      my_extra_column_list.append(
        '`%s`.`%s`' % (
          # table == self.catalog_table_name, and self.catalog_table_name
          # is already checked.
          table,
          # Note: this is really and identifier and not a column as we
          # stripped table name
          checkIdentifier(column),
        ),
      )
    self.implicit_join = bool(implicit_join)

  def asSearchTextExpression(self, sql_catalog):
    return self.query.asSearchTextExpression(sql_catalog)

  def asSQLExpression(self, sql_catalog, only_group_columns):
    column_map = self.column_map
    if column_map is None:
      # XXX: should we provide a way to register column map as a separate
      # method or do it here ?
      # Column Map was not built yet, do it.
      column_map = ColumnMap(catalog_table_name=self.catalog_table_name,
                             left_join_list=self.left_join_list,
                             inner_join_list=self.inner_join_list,
                             implicit_join=self.implicit_join,
                            )
      self.column_map = column_map
    if 1:
      column_map.registerTable(
        self.catalog_table_name,
        self.catalog_table_alias,
      )
      for extra_column in self.extra_column_list:
        column_map.registerColumn(extra_column)
      for column in self.group_by_list:
        column_map.registerColumn(column)
      for alias, column in self.select_dict.iteritems():
        if column is None:
          column = alias
        else:
          column_map.ignoreColumn(alias)
        column_map.registerColumn(column)
      for order_by in self.order_by_list:
        column_map.registerColumn(order_by[0])
      self.query.registerColumnMap(sql_catalog, column_map)
      column_map.build(sql_catalog)
      # Replace given group_by_list entries by their mapped representations.
      new_column_list = []
      append = new_column_list.append
      for column in self.group_by_list:
        try:
          append(column_map.asSQLColumn(column))
        except KeyError:
          LOG('EntireQuery', WARNING, 'Group-by column %r could not be mapped, but is passed through. This use is strongly discouraged.' % (column, ))
          append(column)
      self.group_by_list = new_column_list
      # Build a dictionnary from select_dict aliasing their mapped representations
      self.final_select_dict = select_dict = {}
      for alias, raw_column in self.select_dict.iteritems():
        if raw_column is None:
          column = alias
          if '.' in alias:
            # If given column is pre-mapped, strip table name from its alias.
            _, alias = alias.split('.')
            alias = alias.strip('`()')
        else:
          column = raw_column
        try:
          rendered = column_map.asSQLColumn(column)
        except KeyError:
          LOG('EntireQuery', WARNING, 'Select column %r could not be mapped, but is passed through. This use is strongly discouraged.' % (column, ))
          rendered = column
        select_dict[alias] = rendered
      # Replace given order_by_list entries by their mapped representations.
      new_order_by_list = []
      append = new_order_by_list.append
      for order_by in self.order_by_list:
        column = order_by[0]
        try:
          rendered = column_map.asSQLColumn(column)
        except KeyError:
          LOG('EntireQuery', WARNING, 'Order by %r ignored: it could not be mapped to a known column.' % (order_by, ))
          rendered = None
        if rendered is not None:
          append((rendered, ) + tuple(order_by[1:]))
      self.order_by_list = new_order_by_list
      # generate SQLExpression from query
      sql_expression_list = [self.query.asSQLExpression(sql_catalog,
                                                        column_map,
                                                        only_group_columns)]
      append = sql_expression_list.append
      for join_query in column_map.iterJoinQueryList():
        append(join_query.asSQLExpression(sql_catalog,
                                          column_map,
                                          only_group_columns))
      # generate join expression based on column_map.getJoinTableAliasList
      # XXX: This is now done by ColumnMap to its table_definition,
      # during build()
      #
      # join_table_list = column_map.getJoinTableAliasList()
      # if len(join_table_list):
      #   # XXX: Is there any special rule to observe when joining tables ?
      #   # Maybe we could check which column is a primary key instead of
      #   # hardcoding "uid".
      #   where_pattern = '`%s`.`uid` = `%%s`.`uid`' % \
      #     (column_map.getCatalogTableAlias(), )
      #   # XXX: It would cleaner from completeness point of view to use column
      #   # mapper to render column, but makes code much more complex to just do
      #   # a simple text rendering. If there is any reason why we should have
      #   # those column in the mapper, then we should use the clean way.
      #   append(SQLExpression(self, where_expression=' AND '.join(
      #     where_pattern % (x, ) for x in join_table_list
      #   )))

      table_alias_dict = column_map.getTableAliasDict()
      from_expression = column_map.getTableDefinition()
      assert ((from_expression is None) !=
              (table_alias_dict is None)), ("Got both a from_expression "
                                            "and a table_alias_dict")
      self.sql_expression_list = sql_expression_list
      # TODO: wrap the table_alias_dict above into a TableDefinition as well,
      # even without a legacy_table_definition.
    return SQLExpression(
      self,
      table_alias_dict=table_alias_dict,
      from_expression=from_expression,
      order_by_list=self.order_by_list,
      group_by_list=self.group_by_list,
      select_dict=self.final_select_dict,
      limit=self.limit,
      where_expression_operator='and',
      sql_expression_list=self.sql_expression_list)

verifyClass(IEntireQuery, EntireQuery)

