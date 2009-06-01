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

from zLOG import LOG
from interfaces.sql_expression import ISQLExpression
from Interface.Verify import verifyClass
from types import NoneType
from SQLCatalog import profiler_decorator

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

class SQLExpression(object):

  __implements__ = ISQLExpression

  @profiler_decorator
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
    self.can_merge_select_dict = can_merge_select_dict
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
      sql_expression_list = [x for x in sql_expression_list if x is not None]
    self.sql_expression_list = list(sql_expression_list)
    self.select_dict = defaultDict(select_dict)
    if limit is None:
      self.limit = ()
    elif isinstance(limit, (list, tuple)):
      if len(limit) < 3:
        self.limit = limit
      else:
        raise ValueError, 'Unrecognized "limit" value: %r' % (limit, )
    else:
      self.limit = (limit, )
    if from_expression is not None:
      LOG('SQLExpression', 0, 'Providing a from_expression is deprecated.')
    self.from_expression = from_expression

  @profiler_decorator
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
      for alias, table_name in sql_expression.getTableAliasDict().iteritems():
        existing_value = result.get(alias)
        if existing_value not in (None, table_name):
          message = '%r is a known alias for table %r, can\'t alias it now to table %r' % (alias, existing_value, table_name)
          if DEBUG:
            message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
              self.query,
              sql_expression,
              sql_expression.query,
              ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
          raise ValueError, message
        result[alias] = table_name
    return result

  @profiler_decorator
  def getFromExpression(self):
    """
      Returns a string.

      If there are nested SQLExpression, it checks that they either don't
      define any from_expression or the exact same from_expression. Otherwise,
      it raises a ValueError.
    """
    result = self.from_expression
    for sql_expression in self.sql_expression_list:
      from_expression = sql_expression.getFromExpression()
      if None not in (result, from_expression):
        message = 'I don\'t know how to merge from_expressions'
        if DEBUG:
          message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
            self.query,
            sql_expression,
            sql_expression.query,
            ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
        raise ValueError, message
    return result

  @profiler_decorator
  def getOrderByList(self):
    """
      Returns a list of strings.

      If there are nested SQLExpression, it checks that they don't define
      sorts for columns which are already sorted. If they do, it raises a
      ValueError.
    """
    result = self.order_by_list[:]
    known_column_set = set([x[0] for x in result])
    for sql_expression in self.sql_expression_list:
      for order_by in sql_expression.getOrderByList():
        if order_by[0] in known_column_set:
          raise ValueError, 'I don\'t know how to merge order_by yet'
        else:
          result.append(order_by)
          known_column_set.add(order_by[0])
    return result

  @profiler_decorator
  def getOrderByDict(self):
    result_dict = self.order_by_dict.copy()
    for sql_expression in self.sql_expression_list:
      order_by_dict = sql_expression.getOrderByDict()
      for key, value in order_by_dict.iteritems():
        if key in result_dict and value != result_dict[key]:
          message = 'I don\'t know how to merge order_by_dict with ' \
                    'conflicting entries for key %r: %r vs. %r' % (key, result_dict[key], value)
          if DEBUG:
            message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
              self.query,
              sql_expression,
              sql_expression.query,
              ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
          raise ValueError, message
      result_dict.update(order_by_dict)
    return result_dict

  @profiler_decorator
  def getOrderByExpression(self):
    """
      Returns a string.

      Returns a rendered "order by" expression. See getOrderByList.
    """
    order_by_dict = self.getOrderByDict()
    get = order_by_dict.get
    return SQL_LIST_SEPARATOR.join(get(x, str(x)) \
                                   for x in self.getOrderByList())

  @profiler_decorator
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

  @profiler_decorator
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
        raise ValueError, message
    return result

  @profiler_decorator
  def getLimitExpression(self):
    """
      Returns a string.
      
      Returns a rendered "limit" expression. See getLimit.
    """
    return SQL_LIST_SEPARATOR.join(str(x) for x in self.getLimit())

  @profiler_decorator
  def getGroupByset(self):
    """
      Returns a set of strings.

      If there are nested SQLExpression, it merges (union of sets) them with
      local value.
    """
    result = set(self.group_by_list)
    for sql_expression in self.sql_expression_list:
      result.update(sql_expression.getGroupByset())
    return result

  @profiler_decorator
  def getGroupByExpression(self):
    """
      Returns a string.

      Returns a rendered "group by" expression. See getGroupBySet.
    """
    return SQL_LIST_SEPARATOR.join(self.getGroupByset())

  def canMergeSelectDict(self):
    return self.can_merge_select_dict

  @profiler_decorator
  def _getSelectDict(self):
    result = self.select_dict.copy()
    mergeable_set = set()
    if self.canMergeSelectDict():
      mergeable_set.update(result)
    for sql_expression in self.sql_expression_list:
      can_merge_sql_expression = sql_expression.canMergeSelectDict()
      sql_expression_select_dict, sql_expression_mergeable_set = \
        sql_expression._getSelectDict()
      mergeable_set.update(sql_expression_mergeable_set)
      for alias, column in sql_expression_select_dict.iteritems():
        existing_value = result.get(alias)
        if existing_value not in (None, column):
          if can_merge_sql_expression and alias in mergeable_set:
            # Custom conflict resolution
            column = '%s + %s' % (existing_value, column)
          else:
            message = '%r is a known alias for column %r, can\'t alias it now to column %r' % (alias, existing_value, column)
            if DEBUG:
              message = message + '. I was created by %r, and I am working on %r (%r) out of [%s]' % (
                self.query,
                sql_expression,
                sql_expression.query,
                ', '.join('%r (%r)' % (x, x.query) for x in self.sql_expression_list))
            raise ValueError, message
        result[alias] = column
        if can_merge_sql_expression:
          mergeable_set.add(alias)
    return result, mergeable_set

  @profiler_decorator
  def getSelectDict(self):
    """
      Returns a dict:
        key: alias (string)
        value: column (string) or None

      If there are nested SQLExpression, it aggregates their mappings and
      checks that they don't alias different columns with the same name. If
      they do, it raises a ValueError.
    """
    return self._getSelectDict()[0]

  @profiler_decorator
  def getSelectExpression(self):
    """
      Returns a string.

      Returns a rendered "select" expression. See getSelectDict.
    """
    return SQL_LIST_SEPARATOR.join(
      SQL_SELECT_ALIAS_FORMAT % (column, alias)
      for alias, column in self.getSelectDict().iteritems())

  @profiler_decorator
  def asSQLExpressionDict(self):
    table_alias_dict = self.getTableAliasDict()
    from_table_list = []
    append = from_table_list.append
    for alias, table in table_alias_dict.iteritems():
      append((SQL_TABLE_FORMAT % (alias, ), SQL_TABLE_FORMAT % (table, )))
    from_expression_dict = self.getFromExpression()
    if from_expression_dict is not None:
      from_expression = SQL_LIST_SEPARATOR.join(
        from_expression_dict.get(table, '`%s` AS `%s`' % (table, alias))
        for alias, table in table_alias_dict.iteritems())
    else:
      from_expression = None
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

