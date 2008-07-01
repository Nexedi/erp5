##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

class RawKey(SearchKey):
  """ RawKey key is an ERP5 portal_catalog search key which is used to render
      SQL expression that will match exactly what's passed to it using equality ."""

  def build(self, **kwargs):
    # this key doesn't require parsing
    # It's required to implement it as it's used ONLY for ExactMath
    pass

  def buildSQLExpression(self, key, value, 
                         format=None, mode=None, range_value=None, stat__=None):
    if value is not None:
      where_expression = "%s = '%s'" % (key, value)
    else:
      where_expression = "%s is NULL" % (key)
    return where_expression, []
