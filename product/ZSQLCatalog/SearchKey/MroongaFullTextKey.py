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

from DefaultKey import DefaultKey
from FullTextKey import FullTextKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from SearchKey import SearchKey
from zope.interface.verify import verifyClass
import re
 
class MroongaFullTextKey(FullTextKey):
  """
    This SearchKey generates SQL fulltext comparisons for Mroonga.
  """
  default_comparison_operator = 'match'
  fulltext_boolean_splitter = re.compile(r'(\s|\(.+?\)|".+?")')
  fulltext_boolean_detector = re.compile(r'(^[+-]|^.+\*$|^["(].+[")]$)')

  def _processSearchValue(self, search_value, logical_operator,
                          comparison_operator):
    """
      Special SearchValue processor for MroongaFullText queries:
      if a searched token from 'match' operator group contains an
      operator recognised in boolean mode, make the operator for
      that value be 'match_boolean'.
    """
    operator_value_dict, logical_operator, parsed = \
      SearchKey._processSearchValue(self, search_value, logical_operator,
                                    comparison_operator)
    new_value_list = []
    append = new_value_list.append
    for value in operator_value_dict.pop('match', []):
      if isinstance(value, basestring):
        for token in self.fulltext_boolean_splitter.split(value):
          token = token.strip()
          if not token:
            continue
          elif self.fulltext_boolean_detector.match(token):
            operator_value_dict.setdefault('match_boolean', []).append(token)
          else:
            append(token)
      else:
        append(value)
    operator_value_dict['match'] = new_value_list
    return operator_value_dict, logical_operator, parsed

  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    """
      Special Query builder for MroongaFullText queries:
      * by default 'AND' search by using '*D+' pragma.
      * similarity search for non-boolean queries by using '*S"..."' operator.
    """
    column = self.getColumn()
    query_list = []
    append = query_list.append
    match_query = operator_value_dict.pop('match', [])
    match_boolean_query = operator_value_dict.pop('match_boolean', [])
    fulltext_query = '*D+'
    if match_query:
      fulltext_query += ' *S"%s"' % ' '.join(x.replace('"', '\\"') for x in match_query)
    if match_boolean_query:
      fulltext_query += ' %s' % ' '.join(match_boolean_query)
    if match_query or match_boolean_query:
      append(SimpleQuery(search_key=self,
                         comparison_operator='match_boolean',
                         group=group, **{column: fulltext_query}))
    # other comparison operators are handled by DefaultKey.
    if operator_value_dict:
      query_list += DefaultKey._buildQuery(
        self, operator_value_dict, logical_operator, parsed, group)
    return query_list

verifyClass(ISearchKey, MroongaFullTextKey)
