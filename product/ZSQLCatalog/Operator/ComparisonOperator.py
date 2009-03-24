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

from OperatorBase import OperatorBase
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.Interface.IOperator import IOperator
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

class ComparisonOperatorBase(OperatorBase):
  @profiler_decorator
  def asSQLExpression(self, column, value_list, only_group_columns):
    """
      In a Comparison Operator, rendering order is:
        <column> <operator> <value_list>
    """
    column, value_list = self.render(column, value_list)
    return SQLExpression(self, where_expression='%s %s %s' % (column, self.getOperator().upper(), value_list))

  def render(self, column, value_list):
    raise NotImplementedError, 'This method must be overloaded by a subclass.'

  def renderValue(self, value_list):
    raise NotImplementedError, 'This method must be overloaded by a subclass.'

verifyClass(IOperator, ComparisonOperatorBase)

class MonovaluedComparisonOperator(ComparisonOperatorBase):
  @profiler_decorator
  def renderValue(self, value_list):
    """
      value_list must either be a non-list or a single-value list.
    """
    if isinstance(value_list, (tuple, list)):
      if len(value_list) > 1:
        raise ValueError, '%r: value_list must not contain more than one item. Got %r' % (self, value_list)
      value_list = value_list[0]
    return self._renderValue(value_list)

  @profiler_decorator
  def render(self, column, value_list):
    """
      value_list must either be a non-list or a single-value list.
    """
    if isinstance(value_list, (tuple, list)):
      if len(value_list) > 1:
        raise ValueError, '%r: value_list must not contain more than one item. Got %r' % (self, value_list)
      value_list = value_list[0]
    return self._render(column, value_list)

verifyClass(IOperator, MonovaluedComparisonOperator)

class MultivaluedComparisonOperator(ComparisonOperatorBase):
  @profiler_decorator
  def renderValue(self, value_list):
    """
      value_list must be a multi-value list (more than one item).
    """
    if not isinstance(value_list, (tuple, list)) or len(value_list) < 2:
      raise ValueError, '%r: value_list must be a list of more than one item. Got %r' % (self, value_list)
    return '(%s)' % (', '.join([self._renderValue(x) for x in value_list]), )

  @profiler_decorator
  def render(self, column, value_list):
    """
      value_list must be a multi-value list (more than one item).
    """
    if not isinstance(value_list, (tuple, list)) or len(value_list) < 2:
      raise ValueError, '%r: value_list must be a list of more than one item. Got %r' % (self, value_list)
    return column, '(%s)' % (', '.join([self._renderValue(x) for x in value_list]), )

verifyClass(IOperator, MultivaluedComparisonOperator)

class MatchComparisonOperator(MonovaluedComparisonOperator):
  def __init__(self, operator, mode=''):
    MonovaluedComparisonOperator.__init__(self, operator)
    self.where_expression_format_string = 'MATCH (%%(column)s) AGAINST (%%(value_list)s%s)' % (mode, )

  @profiler_decorator
  def asSQLExpression(self, column, value_list, only_group_columns):
    """
      This operator can emit a select expression, so it overrides
      asSQLExpression inseatd of just defining a render method.
    """
    match_string = self.where_expression_format_string % {
      'column': column,
      'value_list': self.renderValue(value_list),
    }
    select_dict = {}
    if not only_group_columns:
      select_dict[column.replace('`', '').split('.')[-1]] = match_string
    # Sort on this column uses relevance.
    # TODO: Add a way to allow sorting by raw column value.
    order_by_dict = {
      column: self.where_expression_format_string,
    }
    return SQLExpression(
      self,
      select_dict=select_dict,
      where_expression=match_string,
      order_by_dict=order_by_dict,
      can_merge_select_dict=True,
    )

verifyClass(IOperator, MatchComparisonOperator)

operator_dict = {
  '=': MonovaluedComparisonOperator('='),
  '!=': MonovaluedComparisonOperator('!='),
  '>': MonovaluedComparisonOperator('>'),
  '<': MonovaluedComparisonOperator('<'),
  '<=': MonovaluedComparisonOperator('<='),
  '>=': MonovaluedComparisonOperator('>='),
  'like': MonovaluedComparisonOperator('like'),
  'not like': MonovaluedComparisonOperator('not like', '!='),
  'match': MatchComparisonOperator('match'),
  'match_boolean': MatchComparisonOperator('match_boolean', mode=' IN BOOLEAN MODE'),
  'match_expansion': MatchComparisonOperator('match_expansion', mode=' WITH QUERY EXPANSION'),
  'in': MultivaluedComparisonOperator('in'),
  'is': MonovaluedComparisonOperator('is'),
}

