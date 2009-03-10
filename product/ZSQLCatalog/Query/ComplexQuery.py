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
from SQLQuery import SQLQuery
from Products.ZSQLCatalog.Interface.IQuery import IQuery
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

logical_operator_search_text_dict = {
  'and': 'AND',
  'or': 'OR',
}

class ComplexQuery(Query):
  """
    A ComplexQuery represents logical operations between Query instances.
  """
  @profiler_decorator
  def __init__(self, *args, **kw):
    """
      *args (tuple of Query or of list of Query)
        list-type entry will extend subquery list, other entries will be
        appended.
      logical_operator ('and', 'or', 'not')
        Logical operator.
        Default: 'and'

      Deprecated 
        operator ('and', 'or', 'not')
          See logical_operator.
          logical_operator takes precedence if given.
        unknown_column_dict (dict)
          Only one key of this dictionnary is used here:
            key: 'from_expression'
            value: string
            This value will be passed through to SQLExpression. If it is
            provided, this ComplexQuery must have no subquery (regular
            SQLExpression limitation)
        implicit_table_list (list of strings)
          Each entry in this list will be registered to column map. This is
          used to make column mapper choose tables differently.
    """
    self.logical_operator = kw.pop('logical_operator', kw.pop('operator', 'and')).lower()
    assert self.logical_operator in ('and', 'or', 'not'), self.logical_operator
    unknown_column_dict = kw.pop('unknown_column_dict', {})
    self.from_expression = unknown_column_dict.pop('from_expression', None)
    self.implicit_table_list = kw.pop('implicit_table_list', [])
    query_list = []
    append = query_list.append
    extend = query_list.extend
    # Flaten the first level of list-type arguments
    for arg in args:
      if isinstance(arg, (list, tuple)):
        extend(arg)
      else:
        append(arg)
    new_query_list = []
    append = new_query_list.append
    # Iterate over the flaten argument list to cast each into a query type.
    for query in query_list:
      if not isinstance(query, Query):
        query = SQLQuery(query)
      append(query)
    self.query_list = new_query_list

  @profiler_decorator
  def asSearchTextExpression(self, sql_catalog, column=None):
    if column in (None, ''):
      query_column = column
    else:
      query_column = ''
    search_text_list = [y for y in [x.asSearchTextExpression(sql_catalog, column=query_column) for x in self.query_list] if y is not None]
    if len(search_text_list) == 0:
      result = ''
    else:
      if self.logical_operator in logical_operator_search_text_dict:
        if len(search_text_list) == 1:
          result = search_text_list[0]
        else:
          logical_operator = ' %s ' % (logical_operator_search_text_dict[self.logical_operator], )
          result = '(%s)' % (logical_operator.join(search_text_list), )
      elif self.logical_operator == 'not':
        assert len(search_text_list) == 1
        result = '(NOT %s)' % (search_text_list[0], )
      else:
        raise ValueError, 'Unknown operator %r' % (self.logical_operator, )
      if column not in (None, ''):
        result = '%s:%s' % (column, result)
    return result

  @profiler_decorator
  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    sql_expression_list = [x.asSQLExpression(sql_catalog, column_map, only_group_columns)
                           for x in self.query_list]
    if len(sql_expression_list) == 0:
      sql_expression_list = [SQLExpression(self, where_expression='1')]
    return SQLExpression(self,
      sql_expression_list=sql_expression_list,
      where_expression_operator=self.logical_operator,
      from_expression=self.from_expression)

  @profiler_decorator
  def registerColumnMap(self, sql_catalog, column_map):
    for implicit_table_column in self.implicit_table_list:
      column_map.registerColumn(implicit_table_column)
    for query in self.query_list:
      query.registerColumnMap(sql_catalog, column_map)

  def __repr__(self):
    return '<%s of %r.join(%r)>' % (self.__class__.__name__, self.logical_operator, self.query_list)

  @profiler_decorator
  def setTableAliasList(self, table_alias_list):
    """
      This function is here for backward compatibility.
      This can only be used when there is one and only one subquery which
      defines a setTableAliasList method.
      
      See RelatedQuery.
    """
    assert len(self.query_list) == 1
    self.query_list[0].setTableAliasList(table_alias_list)

  @profiler_decorator
  def setGroup(self, group):
    for query in self.query_list:
      query.setGroup(group)

verifyClass(IQuery, ComplexQuery)

