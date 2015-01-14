# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014-2006 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from KeywordKey import KeywordKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from Products.ZSQLCatalog.SearchText import dequote
from zope.interface.verify import verifyClass

class MroongaFullTextKey(KeywordKey):
  default_fulltext_comparison_operator = 'mroonga'

  def dequoteParsedText(self):
    return False

  def _renderValueAsSearchText(self, value, operator):
    # XXX:
    # return value for 'a b' here is '(a b), but keyword search with
    # '(a b)' means fulltext search with (a OR b), that is different
    # from fulltext='a b' that means fulltext search with (a AND b).
    return '(%s)' % (value, )

  def _guessComparisonOperator(self, value):
    if isinstance(value, basestring) and value[:1] in ('+', '-'):
      operator = self.default_fulltext_comparison_operator
    else:
      operator = super(MroongaFullTextKey,
                       self)._guessComparisonOperator(value)
    return operator

  def _processSearchValue(self, search_value, logical_operator,
                          comparison_operator):
    operator_value_dict, logical_operator, parsed = \
      super(MroongaFullTextKey, self)._processSearchValue(
        search_value, logical_operator, comparison_operator)
    # Dequote for non full-text queries.
    for comparison_operator, value_list in operator_value_dict.iteritems():
      if comparison_operator not in ('mroonga', 'mroonga_boolean'):
        operator_value_dict[comparison_operator] = [
          isinstance(value, basestring) and dequote(value) or value
          for value in value_list
        ]
    return operator_value_dict, logical_operator, parsed

  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    """
      Special Query builder for FullText queries: merge all values having the
      same operator into just one query, to save SQL server from the burden to
      do multiple fulltext lookups when one would suit the purpose.
    """
    column = self.getColumn()
    query_list = []
    append = query_list.append
    for comparison_operator in ('mroonga', 'mroonga_boolean'):
      value_list = operator_value_dict.pop(comparison_operator, [])
      if not value_list:
        continue
      if logical_operator == 'and':
        joined_value = ' '.join(value_list)
        append(SimpleQuery(search_key=self,
                           comparison_operator=comparison_operator,
                           group=group, **{column:joined_value}))
      else:
        # TODO : We can join to one query like 'aaa OR (bbb ccc) OR "ddd eee"'.
        for value in value_list:
          append(SimpleQuery(search_key=self,
                             comparison_operator=comparison_operator,
                             group=group, **{column:value}))
    # Other comparison operators are handled by the super class.
    if operator_value_dict:
      query_list += super(MroongaFullTextKey, self)._buildQuery(
        operator_value_dict, logical_operator, parsed, group)
    return query_list

verifyClass(ISearchKey, MroongaFullTextKey)
