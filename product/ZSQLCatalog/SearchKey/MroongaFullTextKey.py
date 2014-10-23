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

from FullTextKey import FullTextKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from zope.interface.verify import verifyClass
import re
 
class MroongaFullTextKey(FullTextKey):
  """
    This SearchKey generates SQL fulltext comparisons for Mroonga.
  """
  default_comparison_operator = 'match'
  fulltext_boolean_detector = re.compile(r'.*((^|\s)[\+\-\("]|[\*\)"](\s|$))')

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
    append(SimpleQuery(search_key=self,
                       comparison_operator='match_boolean',
                       group=group, **{column: fulltext_query}))
    return query_list

verifyClass(ISearchKey, MroongaFullTextKey)
