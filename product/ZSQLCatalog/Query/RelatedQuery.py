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

from Query import Query
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.interfaces.query import IQuery
from zope.interface.verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

class RelatedQuery(Query):
  """
    A RelatedQuery represents the is a container for a join condition.
  """
  @profiler_decorator
  def __init__(self, search_key, join_condition=None, table_alias_list=None):
    """
      search_key (SearchKey)
      join_condition (Query)
        If given, it will be registered and rendered by this query.

      Deprecated
        table_alias_list (list of 2-tuple of strings)
          See setTableAliasList.
    """
    self.search_key = search_key
    self.join_condition = join_condition
    self.table_alias_list = table_alias_list

  @profiler_decorator
  def setTableAliasList(self, table_alias_list):
    """
      This function is here for backward compatibility.

      table_alias_list (list of 2-tuples of strings)
        Each 2-tuple contains the name of a related key parameter and the
        table alias it must be mapped on (respectively).
    """
    self.table_alias_list = table_alias_list

  @profiler_decorator
  def _asSearchTextExpression(self, sql_catalog, column=None):
    assert column is None
    join_condition = self.join_condition
    if join_condition is None:
      result = None
    else:
      result = join_condition.asSearchTextExpression(sql_catalog, column=self.search_key.getColumn())
    return False, result

  @profiler_decorator
  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    sql_expression_list = [self.search_key.buildSQLExpression(sql_catalog, column_map, only_group_columns, self.group)]
    join_condition = self.join_condition
    if join_condition is not None:
      sql_expression_list.append(join_condition.asSQLExpression(sql_catalog, column_map, only_group_columns))
    return SQLExpression(self, sql_expression_list=sql_expression_list, where_expression_operator='and')

  @profiler_decorator
  def registerColumnMap(self, sql_catalog, column_map):
    self.group = self.search_key.registerColumnMap(column_map, table_alias_list=self.table_alias_list)
    join_condition = self.join_condition
    if join_condition is not None:
      # Update its group
      join_condition.setGroup(self.group)
      # Propagate registration to embeded query
      join_condition.registerColumnMap(sql_catalog, column_map)

  def __repr__(self):
    return '<%s on %r with %r>' % (self.__class__.__name__, self.search_key.getColumn(), self.join_condition)

verifyClass(IQuery, RelatedQuery)

