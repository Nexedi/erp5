from __future__ import absolute_import
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

from .OperatorBase import OperatorBase
from Products.ZSQLCatalog.SQLExpression import SQLExpression
from Products.ZSQLCatalog.interfaces.operator import IOperator
from zope.interface.verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import list_type_list
import re

class ComparisonOperatorBase(OperatorBase):
  def asSQLExpression(self, column, value_list, only_group_columns):
    """
      In a Comparison Operator, rendering order is:
        <column> <operator> <value_list>
    """
    column, value_list = self.render(column, value_list)
    return SQLExpression(self, where_expression='%s %s %s' % (column, self.getOperator().upper(), value_list))

  def render(self, column, value_list):
    raise NotImplementedError('This method must be overloaded by a subclass.')

  def renderValue(self, value_list):
    raise NotImplementedError('This method must be overloaded by a subclass.')

verifyClass(IOperator, ComparisonOperatorBase)

class MonovaluedComparisonOperator(ComparisonOperatorBase):
  def renderValue(self, value_list):
    """
      value_list must either be a non-list or a single-value list.
    """
    if isinstance(value_list, list_type_list):
      try:
        value_list, = value_list
      except ValueError:
        raise ValueError('%r: value_list must not contain more than one item. Got %r' % (self, value_list))
    return self._renderValue(value_list)

  def render(self, column, value_list):
    """
      value_list must either be a non-list or a single-value list.
    """
    if isinstance(value_list, list_type_list):
      try:
        value_list, = value_list
      except ValueError:
        raise ValueError('%r: value_list must not contain more than one item. Got %r' % (self, value_list))
    return self._render(column, value_list)

verifyClass(IOperator, MonovaluedComparisonOperator)

class MultivaluedComparisonOperator(ComparisonOperatorBase):
  def renderValue(self, value_list):
    """
      value_list must be a multi-value list (more than one item).
    """
    if not isinstance(value_list, list_type_list) or len(value_list) < 2:
      raise ValueError('%r: value_list must be a list of more than one item. Got %r' % (self, value_list))
    return '(%s)' % ', '.join(map(self._renderValue, value_list))

  def render(self, column, value_list):
    """
      value_list must be a multi-value list (more than one item).
    """
    if not isinstance(value_list, list_type_list) or len(value_list) < 2:
      raise ValueError('%r: value_list must be a list of more than one item. Got %r' % (self, value_list))
    return column, '(%s)' % ', '.join(map(self._renderValue, value_list))

verifyClass(IOperator, MultivaluedComparisonOperator)

class MatchComparisonOperator(MonovaluedComparisonOperator):
  def __init__(self, operator, mode=''):
    MonovaluedComparisonOperator.__init__(self, operator, '')
    self.where_expression_format_string = 'MATCH (%%(column)s) AGAINST (%%(value_list)s%s)' % (mode, )

  def asSQLExpression(self, column, value_list, only_group_columns):
    """
      This operator can emit a select expression, so it overrides
      asSQLExpression inseatd of just defining a render method.
    """
    # No need to do full text search for an empty string.
    if value_list == '':
      column, value_list = self.render(column, value_list)
      return SQLExpression(self, where_expression='%s %s %s' % (column, '=', value_list))
    match_string = self.where_expression_format_string % {
      'column': column,
      'value_list': self.renderValue(value_list),
    }
    select_dict = {}
    if not only_group_columns:
      select_dict['%s__score__' % column.replace('`', '').replace('.', '_')] = match_string
    order_by_dict = {
      '%s__score__' % column.replace('`', '').replace('.', '_'): match_string,
    }
    return SQLExpression(
      self,
      select_dict=select_dict,
      where_expression=match_string,
      order_by_dict=order_by_dict,
      can_merge_select_dict=True,
    )

verifyClass(IOperator, MatchComparisonOperator)

class MroongaComparisonOperator(MatchComparisonOperator):
  fulltext_boolean_splitter = re.compile(r'(\s|\(.+?\)|".+?")')
  fulltext_boolean_detector = re.compile(r'(^[+-]|^.+\*$|^["(].+[")]$)')

  def __init__(self, operator, force_boolean=False):
    MatchComparisonOperator.__init__(self, operator, ' IN BOOLEAN MODE')
    self.force_boolean = force_boolean

  def _escape(self, query_string):
    # TODO : We need to escape more invalid boolean operator usage
    # like '+' or '-' without any letter.
    return re.compile(r'([()])').sub(r'\\\g<1>', query_string)

  def renderValue(self, value_list):
    """
      Special Query renderer for MroongaFullText queries:
      * by default 'AND' search by using '*D+' pragma.
      * similarity search for non-boolean queries by using '*S"..."' operator.
    """
    if isinstance(value_list, list_type_list):
      try:
        value_list, = value_list
      except ValueError:
        raise ValueError('%r: value_list must not contain more than one item. Got %r' % (self, value_list))

    if self.force_boolean:
      fulltext_query = '*D+ %s' % value_list
      return self._renderValue(self._escape(fulltext_query))
    else:
      match_query_list = []
      match_boolean_query_list = []
      for token in self.fulltext_boolean_splitter.split(value_list):
        token = token.strip()
        if not token:
          continue
        elif self.fulltext_boolean_detector.match(token):
          match_boolean_query_list.append(token)
        else:
          match_query_list.append(token)
      # Always use BOOLEAN MODE to combine similarity search and boolean search.
      fulltext_query = '*D+'
      if match_query_list:
        fulltext_query += ' *S"%s"' % ' '.join(match_query_list)
      if match_boolean_query_list:
        fulltext_query += ' %s' % self._escape(' '.join(match_boolean_query_list))
      return self._renderValue(fulltext_query)

verifyClass(IOperator, MroongaComparisonOperator)

class SphinxSEComparisonOperator(MonovaluedComparisonOperator):
  def __init__(self, operator, mode=''):
    MonovaluedComparisonOperator.__init__(self, operator, '')
    self.where_expression_format_string = '%(column)s=%(value_list)s'

  def renderValue(self, value_list):
    """
    * add ';mode=extended2' to invoke extended search
    """
    if isinstance(value_list, list_type_list):
      try:
        value_list, = value_list
      except ValueError:
        raise ValueError('%r: value_list must not contain more than one item. Got %r' % (self, value_list))
    value_list = '%s;mode=extended2;limit=1000' % value_list
    return self._renderValue(value_list)

  def asSQLExpression(self, column, value_list, only_group_columns):
    """
      This operator can emit a select expression, so it overrides
      asSQLExpression inseatd of just defining a render method.
    """
    match_string = self.where_expression_format_string % {
      'column': column,
      'value_list': self.renderValue(value_list)
    }
    return SQLExpression(
      self,
      where_expression=match_string,
      can_merge_select_dict=True,
    )

verifyClass(IOperator, SphinxSEComparisonOperator)

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
  'mroonga': MroongaComparisonOperator('mroonga'),
  'mroonga_boolean': MroongaComparisonOperator('mroonga_boolean', force_boolean=True),
  'sphinxse': SphinxSEComparisonOperator('sphinxse'),
  'in': MultivaluedComparisonOperator('in'),
  'is': MonovaluedComparisonOperator('is'),
  'is not': MonovaluedComparisonOperator('is not', '!='),
}
