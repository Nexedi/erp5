from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SARL and Contributors. All Rights Reserved.
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

from six import string_types as basestring
import warnings
from .interfaces.sql_expression import ISQLExpression
from zope.interface.verify import verifyClass
from zope.interface import implementer
import six
try:
  from types import NoneType
except ImportError: # six.PY3 < 3.10
  NoneType = type(None)

SQL_LIST_SEPARATOR = ', '
SQL_TABLE_FORMAT = '%s' # XXX: should be changed to '`%s`', but this breaks some ZSQLMethods.
SQL_SELECT_ALIAS_FORMAT = '%s AS `%s`'

"""
  TODO:
    - change table_alias_dict in internals to represent computed tables:
       ie: '(SELECT * FROM `bar` WHERE `baz` = "hoge") AS `foo`'
           '`foo` LEFT JOIN `bar` WHERE (`baz` = "hoge")'
"""

# Set to true to keep a reference to the query which created us.
# Set to false to avoid keeping a reference to an object.
DEBUG = True

def defaultDict(value):
  if value is None:
    return {}
  assert isinstance(value, dict)
  return value.copy()

class MergeConflictError(ValueError):
  pass

class MergeConflict(object):
  """
  This class allows lazy errors.

  SQLExpression detects merge conflicts when 2 different values exist for the
  same key in 2 SQLExpression tree nodes.
  This class allows to postpone raising an exception, to allow conflicting
  values as long as they are not actualy used.
  """
  # TODO (?): Include the traceback as of instanciation in error message,
  #           if it can help debugging.
  def __init__(self, message):
    self._message = message

  def __call__(self):
    raise MergeConflictError(self._message)

def conflictSafeGet(dikt, key, default=None):
  result = dikt.get(key, default)
  if isinstance(result, MergeConflict):
    result() # Raises
  return result

@implementer(ISQLExpression)
class SQLExpression(object):

  def __init__(self,
               query,
               table_alias_dict=None,
               order_by_list=(),
               order_by_dict=None,
               group_by_list=(),
               where_expression=None,
               where_expression_operator=None,
               sql_expression_list=(),
               select_dict=None,
               limit=None,
               from_expression=None,
               can_merge_select_dict=False):
    if DEBUG:
      self.query = query
    self.table_alias_dict = defaultDict(table_alias_dict)
    self.order_by_list = list(order_by_list)
    self.group_by_list = list(group_by_list)
    self.order_by_dict = defaultDict(order_by_dict)
    # Only one of (where_expression, where_expression_operator) must be given (never both)
    assert None in (where_expression, where_expression_operator)
    # Exactly one of (where_expression, where_expression_operator) must be given, except if sql_expression_list is given and contains exactly one entry
    assert where_expression is not None or where_expression_operator is not None or (sql_expression_list is not None and len(sql_expression_list) == 1)
    # where_expression must be a basestring instance if given
    assert isinstance(where_expression, (NoneType, basestring))
    # where_expression_operator must be 'and', 'or' or 'not' (if given)
    assert where_expression_operator in (None, 'and', 'or', 'not'), where_expression_operator
    self.where_expression = where_expression
    self.where_expression_operator = where_expression_operator
    # Exactly one of (where_expression, sql_expression_list) must be given (XXX: duplicate of previous conditions ?)
    assert where_expression is not None or sql_expression_list is not None
    if isinstance(sql_expression_list, (list, tuple)):
      self.sql_expression_list = [x for x in sql_expression_list if x is not None]
    else:
      self.sql_expression_list = list(sql_expression_list)
    if limit is None:
      self.limit = ()
    elif isinstance(limit, (list, tuple)):
      if len(limit) < 3:
        self.limit = limit
      else:
        raise ValueError('Unrecognized "limit" value: %r' % (limit, ))
    else:
      self.limit = (limit, )
    if from_expression is not None:
      warnings.warn("Providing a 'from_expression' is deprecated.",
                    DeprecationWarning)
    self.from_expression = from_expression

    select_dict = defaultDict(select_dict)
    mergeable_set = set()
    self.can_merge_select_dict = can_merge_select_dict
    if can_merge_select_dict:
      mergeable_set.update(select_dict)
    for sql_expression in self.sql_expression_list:
      can_merge_sql_expression = sql_expression.can_merge_select_dict
      mergeable_set.update(sql_expression._mergeable_set)
      for alias, column in six.iteritems(sql_expression._select_dict):
        existing_value = select_dict.get(alias)
        if existing_value not in (None, column):
          if can_merge_sql_expression and alias in mergeable_set:
            # Custom conflict resolution
            column = '%s + %s' % (existing_value, column)
          elif alias.endswith('__score__'):
            # We only support the first full text score in select dict.
            pass
          else:
            message = '%r is a known alias for column %r, can\'t alias it now to column %r' % (alias, existing_value, column)
            if DEBUG:
              message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
                self.query,
                sql_expression,
                sql_expression.query,
                ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
            raise ValueError(message)
        select_dict[alias] = column
        if can_merge_sql_expression:
          mergeable_set.add(alias)
    self._select_dict = select_dict
    self._mergeable_set = mergeable_set
    self._reversed_select_dict = {y: x for x, y in six.iteritems(select_dict)}

  def getTableAliasDict(self):
    """
      Returns a dictionary:
        key: table alias (string)
        value: table name (string)

      If there are nested SQLExpressions, it aggregates their mappings and
      checks that they don't alias different table with the same name. If they
      do, it raises a ValueError.
    """
    result = self.table_alias_dict.copy()
    for sql_expression in self.sql_expression_list:
      for alias, table_name in six.iteritems(sql_expression.getTableAliasDict()):
        existing_value = result.get(alias)
        if existing_value not in (None, table_name):
          message = '%r is a known alias for table %r, can\'t alias it now to table %r' % (alias, existing_value, table_name)
          if DEBUG:
            message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
              self.query,
              sql_expression,
              sql_expression.query,
              ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
          raise ValueError(message)
        result[alias] = table_name
    return result

  def getFromExpression(self):
    """
      Returns a TableDefinition stored in one of the from_expressions or None

      If there are nested SQLExpression, it checks that they either don't
      define any from_expression or the exact same from_expression. Otherwise,
      it raises a ValueError.
    """
    result = self.from_expression
    for sql_expression in self.sql_expression_list:
      from_expression = sql_expression.getFromExpression()
      if from_expression not in (result, None):
        message = 'I don\'t know how to merge from_expressions'
        if DEBUG:
          message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
            self.query,
            sql_expression,
            sql_expression.query,
            ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
        raise ValueError(message)
    return result

  def getOrderByList(self):
    """
      Returns a list of strings.

      If there are nested SQLExpression, it checks that they don't define
      sorts for columns which are already sorted. If they do, it raises a
      ValueError.
    """
    result = self.order_by_list[:]
    known_column_set = {x[0] for x in result}
    for sql_expression in self.sql_expression_list:
      for order_by in sql_expression.getOrderByList():
        if order_by[0] in known_column_set:
          raise ValueError("I don't know how to merge order_by yet")
        else:
          result.append(order_by)
          known_column_set.add(order_by[0])
    return result

  def _getOrderByDict(self, delay_error=True):
    result_dict = self.order_by_dict.copy()
    for sql_expression in self.sql_expression_list:
      order_by_dict = sql_expression._getOrderByDict(delay_error=delay_error)
      for key, value in six.iteritems(order_by_dict):
        if key in result_dict and value != result_dict[key] \
            and not isinstance(value, MergeConflict):
          message = 'I don\'t know how to merge order_by_dict with ' \
                    'conflicting entries for key %r: %r vs. %r' % (key, result_dict[key], value)
          if DEBUG:
            message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
              self.query,
              sql_expression,
              sql_expression.query,
              ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
          if delay_error:
            order_by_dict[key] = MergeConflict(message)
          else:
            raise MergeConflictError(message)
      result_dict.update(order_by_dict)
    return result_dict

  def getOrderByDict(self):
    return self._getOrderByDict(delay_error=False)

  def getOrderByExpression(self):
    """
      Returns a string.

      Returns a rendered "order by" expression. See getOrderByList.
    """
    result = []
    append = result.append
    order_by_dict = self._getOrderByDict()
    for (column, direction, cast) in self.getOrderByList():
      expression = conflictSafeGet(order_by_dict, column, str(column))
      expression = self._reversed_select_dict.get(expression, expression)
      if cast is not None:
        expression = 'CAST(%s AS %s)' % (expression, cast)
      if direction is not None:
        expression = '%s %s' % (expression, direction)
      append(expression)
    return SQL_LIST_SEPARATOR.join(result)

  def getWhereExpression(self):
    """
      Returns a string.

      Returns a rendered "where" expression.
    """
    if self.where_expression is not None:
      result = self.where_expression
    else:
      if self.where_expression_operator == 'not':
        assert len(self.sql_expression_list) == 1
        result = '(NOT %s)' % (self.sql_expression_list[0].getWhereExpression())
      elif len(self.sql_expression_list) == 1:
        result = self.sql_expression_list[0].getWhereExpression()
      elif len(self.sql_expression_list) == 0:
        result = '(1)'
      else:
        operator = '\n  ' + self.where_expression_operator.upper() + ' '
        result = '(%s)' % (operator.join(x.getWhereExpression() for x in self.sql_expression_list), )
    return result

  def getLimit(self):
    """
      Returns a list of 1 or 2 items (int or string).

      If there are nested SQLExpression, it checks that they either don't
      define any limit or the exact same limit. Otherwise it raises a
      ValueError.
    """
    result = list(self.limit)
    for sql_expression in self.sql_expression_list:
      other_limit = sql_expression.getLimit()
      if other_limit not in ([], result):
        message = 'I don\'t know how to merge limits yet'
        if DEBUG:
          message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
            self.query,
            sql_expression,
            sql_expression.query,
            ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
        raise ValueError(message)
    return result

  def getLimitExpression(self):
    """
      Returns a string.

      Returns a rendered "limit" expression. See getLimit.
    """
    return SQL_LIST_SEPARATOR.join(str(x) for x in self.getLimit())

  def getGroupBySet(self):
    """
      Returns a set of strings.

      If there are nested SQLExpression, it merges (union of sets) them with
      local value.
    """
    result = {self._reversed_select_dict.get(x, x) for x in self.group_by_list}
    for sql_expression in self.sql_expression_list:
      result.update(sql_expression.getGroupBySet())
    return result

  def getGroupByExpression(self):
    """
      Returns a string.

      Returns a rendered "group by" expression. See getGroupBySet.
    """
    return SQL_LIST_SEPARATOR.join(self.getGroupBySet())

  def getSelectDict(self):
    """
      Returns a dict:
        key: alias (string)
        value: column (string) or None

      If there are nested SQLExpression, it aggregates their mappings and
      checks that they don't alias different columns with the same name. If
      they do, it raises a ValueError.
    """
    return self._select_dict

  def getSelectExpression(self):
    """
      Returns a string.

      Returns a rendered "select" expression. See getSelectDict.
    """
    return SQL_LIST_SEPARATOR.join(
      SQL_SELECT_ALIAS_FORMAT % (column, alias)
      for alias, column in six.iteritems(self.getSelectDict()))

  def getFromTableList(self):
    table_alias_dict = self.getTableAliasDict()
    if not table_alias_dict:
      return None
    from_table_list = []
    append = from_table_list.append
    for alias, table in six.iteritems(table_alias_dict):
      append((SQL_TABLE_FORMAT % (alias, ), SQL_TABLE_FORMAT % (table, )))
    return from_table_list

  def asSQLExpressionDict(self):
    from_expression = self.getFromExpression()
    from_table_list = self.getFromTableList()
    assert None in (from_expression,
                    from_table_list), ("Cannot return both a from_expression "
                                       "and a from_table_list")
    if from_expression is not None:
      from_expression = from_expression.render()
    return {
      'where_expression': self.getWhereExpression(),
      'order_by_expression': self.getOrderByExpression(),
      'from_table_list': from_table_list,
      'from_expression': from_expression,
      'limit_expression': self.getLimitExpression(),
      'select_expression': self.getSelectExpression(),
      'group_by_expression': self.getGroupByExpression()
    }

verifyClass(ISQLExpression, SQLExpression)

