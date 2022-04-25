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

from six import string_types as basestring
from .DefaultKey import DefaultKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from Products.ZSQLCatalog.SearchText import dequote
from zope.interface.verify import verifyClass
import re

FULLTEXT_BOOLEAN_DETECTOR = re.compile(r'.*((^|\s)[\+\-<>\(\~]|[\*\)](\s|$))')

class FullTextKey(DefaultKey):
  """
    This SearchKey generates SQL fulltext comparisons.
  """
  default_comparison_operator = 'match'
  get_operator_from_value = False

  def dequoteParsedText(self):
    return False

  def _renderValueAsSearchText(self, value, operator):
    # XXX:
    # return value for 'a b' here is '(a b), but keyword search with
    # '(a b)' means fulltext search with (a OR b), that is different
    # from fulltext='a b' that means fulltext search with (a AND b).
    return '(%s)' % (value, )

  def _processSearchValue(self, search_value, logical_operator,
                          comparison_operator):
    """
      Special SearchValue processor for FullText queries: if a searched value
      from 'match' operator group contains an operator recognised in boolean
      mode, make the operator for that value be 'match_boolean'.
    """
    operator_value_dict, logical_operator, parsed = \
      super(FullTextKey, self)._processSearchValue(
        search_value, logical_operator, comparison_operator)
    new_value_list = []
    append = new_value_list.append
    for value in operator_value_dict.pop('match', []):
      if isinstance(value, basestring) and \
         FULLTEXT_BOOLEAN_DETECTOR.match(value) is not None:
        operator_value_dict.setdefault('match_boolean', []).append(value)
      else:
        append(value)
    if len(new_value_list):
      if 'match_boolean' in operator_value_dict:
        # use boolean mode for all expressions
        operator_value_dict['match_boolean'].extend(new_value_list)
      else:
        operator_value_dict['match'] = new_value_list
    # Dequote for non full-text queries.
    for comparison_operator, value_list in operator_value_dict.iteritems():
      if comparison_operator not in ('match', 'match_boolean'):
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
    for comparison_operator in ('match', 'match_boolean'):
      value_list = operator_value_dict.pop(comparison_operator, [])
      if not value_list:
        continue
      # XXX:
      # In MySQL FTS, no operator implies OR so that we should not merge
      # AND queries into one...
      append(SimpleQuery(search_key=self,
                         comparison_operator=comparison_operator,
                         group=group, **{column: ' '.join(value_list)}))
    # Other comparison operators are handled by the super class.
    if operator_value_dict:
      query_list += super(FullTextKey, self)._buildQuery(
        operator_value_dict, logical_operator, parsed, group)
    return query_list

verifyClass(ISearchKey, FullTextKey)

