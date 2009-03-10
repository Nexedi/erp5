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

class DefaultKey(SearchKey):
  """
    This SearchKey behaves like an ExactMatch SearchKey, except if value is a
    string and contains a '%' sign, in which case it behaves like a
    KeywordKey.
  """
  default_comparison_operator = '='
  get_operator_from_value = True

  def parseSearchText(self, value, is_column):
    return parse(value, is_column)

  def _guessComparisonOperator(self, value):
    if isinstance(value, basestring) and '%' in value:
      operator = 'like'
    else:
      operator = SearchKey._guessComparisonOperator(self, value)
    return operator

  def buildSearchTextExpression(self, operator, value, column=None):
    operator_text = operator.getOperator()
    if column is None:
      column = self.getColumn()
    if operator_text == 'like':
      assert isinstance(value, basestring)
      assert '%' in value
      result = '%s:%s' % (column, value)
    else:
      result = SearchKey.buildSearchTextExpression(self, operator, value, column=column)
    return result

verifyClass(ISearchKey, DefaultKey)
