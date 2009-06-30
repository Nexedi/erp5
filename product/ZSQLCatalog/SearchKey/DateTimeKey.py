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

import sys
from SearchKey import SearchKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.Query.ComplexQuery import ComplexQuery
from zLOG import LOG
from DateTime.DateTime import DateTime, DateTimeError, _cache
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.SQLCatalog import profiler_decorator
from Products.ZSQLCatalog.SearchText import parse

MARKER = []

timezone_dict = _cache._zmap

date_completion_format_dict = {
  None: ['01/01/%s', '01/%s'],
  'international': ['%s/01/01', '%s/01']
}

@profiler_decorator
def _DateTime(*args, **kw):
  return DateTime(*args, **kw)

@profiler_decorator
def castDate(value):
  if value is None:
    return None
  date_kw = {'datefmt': 'international'}
  if isinstance(value, dict):
    # Convert value into a DateTime, and guess desired delta from what user
    # input.
    assert value['type'] == 'date'
    format = value.get('format')
    value = value['query']
    if format == '%m/%d/%Y':
      date_kw.pop('datefmt')
  if isinstance(value, DateTime):
    pass
  elif isinstance(value, basestring):
    try:
      value = _DateTime(value, **date_kw)
    except DateTimeError:
      delimiter_count = countDelimiters(value)
      if delimiter_count < 3:
        split_value = value.split()
        if split_value[-1].lower() in timezone_dict:
          value = '%s %s' % (date_completion_format_dict[date_kw.get('datefmt')][delimiter_count] % (' '.join(split_value[:-1]), ), split_value[-1])
        else:
          value = date_completion_format_dict[date_kw.get('datefmt')][delimiter_count] % (value, )
        value = _DateTime(value, **date_kw)
      else:
        raise
  else:
    raise TypeError, 'Unknown date type: %r' % (value)
  return value.toZone('UTC')

# (strongly) inspired from DateTime.DateTime.py
delimiter_list = ' -/.:,+'

def getMonthLen(datetime):
  return datetime._month_len[datetime.isLeapYear()][datetime.month()]

def getYearLen(datetime):
  return 365 + datetime.isLeapYear()

delta_list = [getYearLen, getMonthLen, 1, 1.0 / 24, 1.0 / (24 * 60), 1.0 / (24 * 60 * 60)]

@profiler_decorator
def countDelimiters(value):
  assert isinstance(value, basestring)
  # Detect if timezone was provided, to avoid counting it as in precision computation.
  split_value = value.split()
  if split_value[-1].lower() in timezone_dict:
    value = ' '.join(split_value[:-1])
  # Count delimiters
  delimiter_count = 0
  for char in value:
    if char in delimiter_list:
      delimiter_count += 1
  return delimiter_count

@profiler_decorator
def getPeriodBoundaries(value):
  first_date = castDate(value)
  if isinstance(value, dict):
    value = value['query']
  # Try to guess how much was given in query.
  if isinstance(value, basestring):
    delimiter_count = countDelimiters(value)
  elif isinstance(value, DateTime):
    raise TypeError, 'Impossible to guess a precision from a DateTime type.'
  else:
    raise TypeError, 'Unknown date type: %r' % (value)
  delta = delta_list[delimiter_count]
  if callable(delta):
    delta = delta(first_date)
  return first_date, first_date + delta

@profiler_decorator
def wholePeriod(search_key, group, column, value_list, exclude=False):
  if exclude:
    first_operator = '<'
    second_operator = '>='
    logical_operator = 'or'
  else:
    first_operator = '>='
    second_operator = '<'
    logical_operator = 'and'
  query_list = []
  append = query_list.append
  for value in value_list:
    first_date, second_date = getPeriodBoundaries(value)
    append(ComplexQuery([SimpleQuery(search_key=search_key, comparison_operator=first_operator, group=group, **{column: first_date}),
                         SimpleQuery(search_key=search_key, comparison_operator=second_operator, group=group, **{column: second_date})],
                        operator=logical_operator))
  return query_list

def matchWholePeriod(search_key, group, column, value_list, *ignored):
  return wholePeriod(search_key, group, column, value_list)

def matchNotWholePeriod(search_key, group, column, value_list, *ignored):
  return wholePeriod(search_key, group, column, value_list, exclude=True)

@profiler_decorator
def matchExact(search_key, group, column, value_list, comparison_operator, logical_operator):
  if comparison_operator is None:
    comparison_operator = '='
  value_list = [castDate(x) for x in value_list]
  if logical_operator == 'or' and comparison_operator == '=':
    query_list = [SimpleQuery(search_key=search_key, comparison_operator='in', group=group, **{column: value_list})]
  else:
    query_list = [SimpleQuery(search_key=search_key, comparison_operator=comparison_operator, group=group, **{column: x}) for x in value_list]
  return query_list

def getNextPeriod(value):
  return getPeriodBoundaries(value)[1]

@profiler_decorator
def matchBeforeNextPeriod(search_key, group, column, value_list, comparison_operator, logical_operator):
  return matchExact(search_key, group, column, [getNextPeriod(x) for x in value_list], '<', logical_operator)

@profiler_decorator
def matchAfterPeriod(search_key, group, column, value_list, comparison_operator, logical_operator):
  return matchExact(search_key, group, column, [getNextPeriod(x) for x in value_list], '>=', logical_operator)

operator_matcher_dict = {
  None: matchWholePeriod,
  '=': matchWholePeriod,
  '!=': matchNotWholePeriod,
  '<': matchExact,
  '>=': matchExact,
  '<=': matchBeforeNextPeriod,
  '>': matchAfterPeriod,
}

# Behaviour of date time operators
# Objects:
#   2005/03/14 23:59:59
#   2005/03/15 00:00:00
#   2005/03/15 00:00:01
#   2005/03/15 23:59:59
#   2005/03/16 00:00:00
#   2005/03/16 00:00:01
#
# Searches:
#   "2005/03/15" (operator = None)
#     Implicitely matches the whole period.
#     2005/03/15 00:00:00
#     2005/03/15 00:00:01
#     2005/03/15 23:59:59
#
#   "=2005/03/15" (operator = '=')
#     Behaves the same way as None operator.
#     2005/03/15 00:00:00
#     2005/03/15 00:00:01
#     2005/03/15 23:59:59
#
#   "!=2005/03/15" (operator = '!=')
#     Complementary of '=' operator.
#     2005/03/14 23:59:59
#     2005/03/16 00:00:00
#     2005/03/16 00:00:01
#
#   "<2005/03/15" (operator = '<')
#     Non-ambiguous (no difference wether time is considered as a period or a single point in time).
#     2005/03/14 23:59:59
#
#   ">=2005/03/15" (operator = '>=')
#     Complementary of '<' operator, and also non-ambiguous.
#     2005/03/15 00:00:00
#     2005/03/15 00:00:01
#     2005/03/15 23:59:59
#     2005/03/16 00:00:00
#     2005/03/16 00:00:01
#
#   "<=2005/03/15" (operator = '<=')
#     Union of results from '=' and '<' operators.
#     2005/03/14 23:59:59
#     2005/03/15 00:00:00
#     2005/03/15 00:00:01
#     2005/03/15 23:59:59
#
#   ">2005/03/15" (operator = '>')
#     Complementary of '<=' operator.
#     2005/03/16 00:00:00
#     2005/03/16 00:00:01

class DateTimeKey(SearchKey):
  """
    This SearchKey allows generating date ranges from single, user-input dates.
  """

  default_comparison_operator = None
  get_operator_from_value = True

  def parseSearchText(self, value, is_column):
    return parse(value, is_column)

  def _renderValueAsSearchText(self, value, operator):
    return '"%s"' % (DateTime(value).ISO(), )

  @profiler_decorator
  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    column = self.getColumn()
    query_list = []
    extend = query_list.extend
    for comparison_operator, value_list in operator_value_dict.iteritems():
      try:
        if parsed:
          subquery_list = operator_matcher_dict[comparison_operator](
                   self, group, column, value_list, comparison_operator,
                   logical_operator)
        else:
          subquery_list = matchExact(self, group, column, value_list, comparison_operator, logical_operator)
      except DateTimeError:
        LOG('DateTimeKey', 100, 'Got an exception while generating a query for %r %r.' % (comparison_operator, value_list), error=sys.exc_info())
      else:
        extend(subquery_list)
    return query_list

verifyClass(ISearchKey, DateTimeKey)

