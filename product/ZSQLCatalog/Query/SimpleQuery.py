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
from Products.ZSQLCatalog.interfaces.query import IQuery
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator
from zLOG import LOG, WARNING

class SimpleQuery(Query):
  """
    A SimpleQuery represents a single comparison between a single column and
    one or more values.
  """
  @profiler_decorator
  def __init__(self, search_key=None, comparison_operator='=', group=None, **kw):
    """
      search_key (None, SearchKey instance)
        If given, the instance of SearchKey which is responsible for column
        map registration and rendering (SQL and SearchText).
      comparison_operator (string)
        The comparison operator which will be applied between column and
        values.
        See Operator/ComparisonOperator.py for possible values.
      group
        See ColumnMap.
      **kw
        Must contain exactly one item.
        item key (string)
          column name
        item value
          one or more values
    """
    self.search_key = search_key
    if len(kw) != 1:
      raise ValueError, 'SimpleQuery can support one and one only column. Got %r.' % (kw, )
    self.column, value = kw.popitem()
    # Usability improvement code (those changes should not be needed when
    # this Query is instanciated by a SearchKey, as operator should be correct
    # already).
    comparison_operator = comparison_operator.lower()
    if comparison_operator == 'in':
      if isinstance(value, (list, tuple)):
        if len(value) == 0:
          raise ValueError, 'Empty lists are not allowed.'
        elif len(value) == 1:
          value = value[0]
          comparison_operator = '='
      else:
        comparison_operator = '='
    elif comparison_operator == '=':
      if isinstance(value, (list, tuple)):
        if len(value) == 0:
          raise ValueError, 'Empty lists are not allowed.'
        elif len(value) == 1:
          value = value[0]
        else:
          comparison_operator = 'in'
    if value is None:
      if comparison_operator == '=':
        comparison_operator = 'is'
      elif comparison_operator != 'is':
        raise ValueError, 'None value with a non-"=" comparison_operator (%r). Not sure what to do.' % (comparison_operator, )
    elif comparison_operator == 'is':
      raise ValueError, 'Non-None value (%r) with "is" comparison_operator. Not sure what to do.' % (value, )
    self.value = value
    self.comparison_operator = comparison_operator
    self.group = group

  @profiler_decorator
  def _asSearchTextExpression(self, sql_catalog, column=None):
    return False, self.getSearchKey(sql_catalog).buildSearchTextExpression(self.getOperator(sql_catalog), self.getValue(), column=column)

  @profiler_decorator
  def asSQLExpression(self, sql_catalog, column_map, only_group_columns):
    return self.getSearchKey(sql_catalog).buildSQLExpression(
      self.getOperator(sql_catalog), self.getValue(),
      column_map, only_group_columns, group=self.group)

  @profiler_decorator
  def registerColumnMap(self, sql_catalog, column_map):
    self.group = self.getSearchKey(sql_catalog).registerColumnMap(column_map, group=self.group, simple_query=self)

  def getOperator(self, sql_catalog):
    """
      Return an instance of OperatorBase class.
    """
    return sql_catalog.getComparisonOperator(self.comparison_operator)

  def getSearchKey(self, sql_catalog):
    """
      Return an instance of SearchKey class.
    """
    if self.search_key is None:
      self.search_key = sql_catalog.getSearchKey(self.getColumn())
    return self.search_key

  def getColumn(self):
    return self.column

  def getValue(self):
    return self.value

  def __repr__(self):
    return '<%s %r %s %r>' % (self.__class__.__name__, self.getColumn(), self.comparison_operator, self.getValue())

  def setGroup(self, group):
    self.group = group

verifyClass(IQuery, SimpleQuery)

