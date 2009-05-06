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

from zLOG import LOG
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.Query.ComplexQuery import ComplexQuery
from Products.ZSQLCatalog.Interface.ISearchKey import ISearchKey
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator

single_operator_dict = {
  'min': '>=',
  'max': '<',
  'ngt': '<=',
  'nlt': '>'
}

dual_operator_dict = {
  'minmax': ('>=', '<'),
  'minngt': ('>=', '<=')
}

# List of operators searched for at value's begnining when it's a basestring.
# Order is important: an operator whose left part would be matching another
# operator of lower index would never be used.
operator_list = ('>=', '<=', '>', '<', '=', '!=')

def preprocessLikeValue(value):
  if '%' not in value:
    value = '%%%s%%' % (value, )
  return value

operator_value_preprocessor_dict = {
  'like': preprocessLikeValue
}

def deprocessLikeValue(value):
  assert isinstance(value, basestring)
  if len(value) >= 2 and value[0] == '%' and value[-1] == '%':
    value = value.strip('%')
  return value

operator_value_deprocessor_dict = {
  'like': deprocessLikeValue
}

class SearchKey(object):

  __implements__ = ISearchKey

  # Comparison operator to use when parsing a string value and no operator is
  # found.
  # Note: for non-string values, "=" is always used by default.
  default_comparison_operator = '='
  # Wether or not to allow a basestring value to be searched for a comparison
  # operator.
  get_operator_from_value = True

  def __init__(self, column):
    self.column = column

  def getColumn(self):
    return self.column

  @profiler_decorator
  def buildSQLExpression(self, operator, value, column_map, only_group_columns,
                         group):
    column_name = self.getColumn()
    rendered_column = column_map.asSQLColumn(column_name, group=group)
    return operator.asSQLExpression(rendered_column, value, only_group_columns)

  @profiler_decorator
  def _renderValueAsSearchText(self, value, operator):
    """
      Render a single value as valid SearchText using provided operator.
      This is also responsible for undoing any formatting the value received
      from the SearchKey.

      value (anything)
      operator (Operator)
        The operator used to render value.
    """
    operator_value_deprocessor = operator_value_deprocessor_dict.get(
      operator.getOperator())
    if operator_value_deprocessor is not None:
      value = operator_value_deprocessor(value)
    return operator.asSearchText(value)

  @profiler_decorator
  def buildSearchTextExpression(self, operator, value, column=None):
    operator_text = operator.getOperatorSearchText()
    if column is None:
      column = self.getColumn()
    if isinstance(value, (list, tuple)):
      assert operator_text == 'in'
      assert len(value)
      value = [self._renderValueAsSearchText(x, operator) for x in value]
      if self.default_comparison_operator != '=':
        value = ['=%s' % (x, ) for x in value]
      # XXX: operator used to join value elements should be reused from
      # parser data (?)
      result = '(%s)' % (' OR '.join(value), )
    else:
      result = self._renderValueAsSearchText(value, operator)
      if operator_text != self.default_comparison_operator:
        result = '%s%s' % (operator_text, result)
    if len(column):
      result = '%s:%s' % (column, result)
    return result

  @profiler_decorator
  def registerColumnMap(self, column_map, group, simple_query):
    column_map.registerColumn(self.getColumn(), group=group,
                              simple_query=simple_query)
    return group

  @profiler_decorator
  def _getComparisonOperator(self, value):
    """
      From a basestring instance, return a contained operator and value
      without that operator.

      value (string)
      
      Returns: 2-tuple of strings
        First element is the operator. None if there was no operator in value.
        Second element is the value without the operator.
    """
    startswith = value.startswith
    for operator in operator_list:
      if startswith(operator):
        value = value[len(operator):].lstrip()
        break
    else:
      operator = self._guessComparisonOperator(value)
    return operator, value

  @profiler_decorator
  def _guessComparisonOperator(self, value):
    """
      From a basestring instance, return a contained operator.
      Value cannot be altered in the process.

      value (string)
      
      Returns: 2-tuple of strings
        First element is the operator. None if there was no operator in value.
        Second element is the value without the operator.
    """
    return self.default_comparison_operator

  @profiler_decorator
  def _preprocessValue(self, value, operator):
    operator_value_preprocessor = operator_value_preprocessor_dict.get(
      operator)
    if operator_value_preprocessor is not None:
      value = operator_value_preprocessor(value)
    return value

  @profiler_decorator
  def _processSearchValue(self, search_value, default_logical_operator,
                          comparison_operator):
    """
      Change search_value into a list of values, one or more logical operators,
      and a comparison operator. If no default_logical_operator is given, 
      'or' is used.

      search_value
        basestring
        int
        dict
        list or tuple
          Non-empty
          Composed of homogeneous items
      Returns: 3-tuple
        dict:
          key (string)
            Comparison operator
          value (list of anything)
            List of values applying to this operator.
        string:
          Logical operator applied to all elements of returned dict.
        bool:
          True if logical operators were searched for in values, False
          otherwise. Useful to give different meanings to in-value operators
          and others.
    """
    if comparison_operator == '':
      comparison_operator = None
      get_operator_from_value = False
    else:
      get_operator_from_value = self.get_operator_from_value
    logical_operator = None
    if default_logical_operator is None:
      default_logical_operator = 'or'
    parsed = False
    if isinstance(search_value, dict):
      # comparison_operator parameter collides with dict's 'operator' key.
      # Fail loudly.
      assert comparison_operator is None
      actual_value = search_value['query']
      if search_value.get('key') not in (None, self.__class__.__name__):
        LOG(self.__class__.__name__, 100,
            '"key" dict entry does not match current class: %r' % \
            (search_value, ))
      if 'type' in search_value:
        assert 'operator' not in search_value, search_value
        assert 'range' not in search_value, search_value
      else:
        value_operator = search_value.get('operator')
        value_range = search_value.get('range')
        if value_range is not None:
          if value_operator is not None:
            LOG('SearchKey', 100,
                '"range" and "operator" are mutualy exclusive, ignoring '\
                'operator: %r' % (search_value, ))
          if value_range in single_operator_dict:
            comparison_operator = single_operator_dict[value_range]
          elif value_range in dual_operator_dict:
            if not isinstance(actual_value, (tuple, list)):
              raise TypeError, 'Operator %r requires value to be a '\
                               'tuple/list. (%r)' % (value_range,
                               search_value)
            if len(actual_value) != 2:
              raise TypeError, 'Operator %r requires value to have a length '\
                               'of 2. len(%r) = %i (%r)' % (value_range,
                               actual_value, len(actual_value), search_value)
            comparison_operator = dual_operator_dict[value_range]
            logical_operator = 'and'
          else:
            raise ValueError, 'Unknown "range" value in %r' % (search_value, )
        if value_operator is not None:
          if not isinstance(value_operator, basestring):
            raise TypeError, 'Operator must be of a string type. Got a %r' % \
                             (type(value_operator), )
          value_operator = value_operator.lower()
          if not isinstance(actual_value, (tuple, list)):
            raise TypeError, 'When specifying an operator, query must be a list.'
          if value_operator == 'in':
            comparison_operator = '='
            logical_operator = 'or'
          else:
            logical_operator = value_operator
        search_value = actual_value
    # Cast to list
    if isinstance(search_value, (tuple, list)):
      # Check list content (not empty, homogenous)
      search_value_len = len(search_value)
      if search_value_len == 0:
        raise ValueError, 'Value cannot be an empty list/tuple: %r' % \
                          (search_value, )
      reference_class = search_value[0].__class__
      for x in search_value[1:]:
        if x.__class__ != reference_class:
          raise TypeError, 'List elements must be of the same class: %r' % \
                           (search_value, )
    else:
      assert logical_operator is None
      if isinstance(search_value, dict):
        reference_class = search_value['query'].__class__
      else:
        reference_class = search_value.__class__
      search_value = [search_value]
    if logical_operator is None:
      logical_operator = default_logical_operator
    operator_value_dict = {}
    if None in search_value:
      if comparison_operator not in (None, 'is'):
        LOG('KeywordKey', 100,
            'None value requires an "is" comparison operator. Fixed.')
      operator_value_dict['is'] = search_value
    elif comparison_operator is None:
      if issubclass(reference_class, basestring):
        if get_operator_from_value:
          parsed = True
          for value in search_value:
            if isinstance(value, dict):
              operator, value['query'] = self._getComparisonOperator(
                value['query'])
            else:
              operator, value = self._getComparisonOperator(value)
            operator_value_dict.setdefault(operator, []).append(
              self._preprocessValue(value, operator))
        else:
          for value in search_value:
            if isinstance(value, dict):
              operator = self._guessComparisonOperator(value['query'])
            else:
              operator = self._guessComparisonOperator(value)
            operator_value_dict.setdefault(operator, []).append(
              self._preprocessValue(value, operator))
      else:
        # XXX: comparison operator is hardcoded for non-strings.
        operator_value_dict['='] = search_value
    elif isinstance(comparison_operator, (tuple, list)):
      assert len(comparison_operator) == len(search_value)
      for operator, value in zip(comparison_operator, search_value):
        operator_value_dict.setdefault(operator, []).append(value)
    else:
      operator_value_dict[comparison_operator] = search_value
    return operator_value_dict, logical_operator, parsed

  @profiler_decorator
  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    """
      Create Queries from values, logical and comparison operators.

      operator_value_dict (dict)
        See _processSearchValue.
      logical_operator (string)
        See _processSearchValue.
      parsed (bool)
        See _processSearchValue.
      group (string)
        The gorup all queries will belong to.
    """
    column = self.getColumn()
    query_list = []
    append = query_list.append
    if logical_operator == 'or' and '=' in operator_value_dict:
      # Special case for equality with an 'or' logical operator: use SQL 'in'.
      append(SimpleQuery(search_key=self, comparison_operator='in',
                         group=group,
                         **{column: operator_value_dict.pop('=')}))
    for comparison_operator, value_list in operator_value_dict.iteritems():
      for value in value_list:
        append(SimpleQuery(search_key=self,
                           comparison_operator=comparison_operator,
                           group=group, **{column: value}))
    return query_list

  @profiler_decorator
  def buildQuery(self, search_value, group=None, logical_operator=None,
                 comparison_operator=None):
    assert logical_operator in (None, 'and', 'or'), repr(logical_operator)
    operator_value_dict, logical_operator, parsed = self._processSearchValue(
      search_value, logical_operator, comparison_operator)
    query_list = self._buildQuery(operator_value_dict, logical_operator,
                                  parsed, group)
    if len(query_list) == 1:
      query = query_list[0]
    else:
      query = ComplexQuery(query_list, operator=logical_operator)
    return query

  def parseSearchText(self, value, is_column):
    return None

verifyClass(ISearchKey, SearchKey)

