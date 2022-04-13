from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

import six

from .SearchKey import SearchKey
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery
from Products.ZSQLCatalog.SearchText import parse
from Products.ZSQLCatalog.interfaces.search_key import ISearchKey
from zope.interface.verify import verifyClass

class SphinxSEFullTextKey(SearchKey):
  """
    This SearchKey generates SQL fulltext comparisons.
  """
  default_comparison_operator = 'sphinxse'
  get_operator_from_value = False

  def parseSearchText(self, value, is_column):
    return parse(value, is_column)

  def dequoteParsedText(self):
    return False

  def _renderValueAsSearchText(self, value, operator):
    return '(%s)' % (value, )

  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    """
      Special Query builder for FullText queries: merge all values having the
      same operator into just one query, to save SQL server from the burden to
      do multiple fulltext lookups when one would suit the purpose.

      Here We wrap each phrase or word with double quotes, as the
      workaround of 1-gram search specification in current Sphinx.

      Example:
      'aaa bbb' : '"aaa" "bbb"'
      '"aaa bbb"' : '"aaa bbb"'
      '"aaa bbb" ccc' : '"aaa bbb" "ccc"'
    """
    column = self.getColumn()
    query_list = []
    append = query_list.append
    for comparison_operator, value_list in six.iteritems(operator_value_dict):
      if len(value_list) == 1:
        value_list = value_list[0].split()
      append(SimpleQuery(search_key=self,
                         comparison_operator=comparison_operator,
                         group=group, **{column:' '.join(['"%s"' % x.replace('"', '') for x in value_list])}))
    return query_list

verifyClass(ISearchKey, SphinxSEFullTextKey)
