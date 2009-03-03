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

from SearchKey import SearchKey
from Products.ZSQLCatalog.SearchText import parse
from Products.ZSQLCatalog.Interface.ISearchKey import ISearchKey
from Interface.Verify import verifyClass
from Products.ZSQLCatalog.Query.SimpleQuery import SimpleQuery

class KeywordKey(SearchKey):
  """
    This SearchKey generates matching comparison Queries suited for strings
    with wilcards.
  """
  default_comparison_operator = 'like'
  get_operator_from_value = True
 
  def parseSearchText(self, value):
    return parse(value)

  def _buildQuery(self, operator_value_dict, logical_operator, parsed, group):
    """
      Treat "!=" operator specialy:
       - if the value contains at least one "%", change operator into "not like"
       - otherwise, let it go untouched
    """
    result = []
    if '!=' in operator_value_dict:
      column = self.getColumn()
      original_different_list = operator_value_dict.pop('!=')
      different_list = []
      for value in original_different_list:
        if isinstance(value, basestring) and '%' in value:
          result.append(SimpleQuery(search_key=self, group=group, operator='not like', **{column: value}))
        else:
          different_list.append(value)
        if len(different_list):
          operator_value_dict['!='] = different_list
    return result + SearchKey._buildQuery(self, operator_value_dict, logical_operator, parsed, group)

verifyClass(ISearchKey, KeywordKey)

