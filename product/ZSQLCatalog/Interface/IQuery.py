##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Interface import Interface

class IQuery(Interface):
  """
    A Query contains:
    - a value
    - an operator
    - a column

    It is the python representation of a predicate, independently of its
    rendering (SQL or SearchText).
    For SQL rendering to be possible, it is necesary for some data to be
    centralized in a data structure known at EntireQuery level (to be able to
    generate unique table aliases, for exemple). This is the role of
    ColumnMap, and registerColumnMap method on this interface.

    This interface also offers various rendering methods, one per rendering
    format.
  """

  def asSearchTextExpression(sql_catalog, column=None):
    """
      Render a query in a user-oriented SearchText.
      Returns None if there is this query has no SearchText representation,
      but is SearchText-aware.
      If column is provided, it must be used instead of local knowledge of
      column name. It is used to make queries inside a related key render
      correctly.
    """

  def asSQLExpression(sql_catalog, column_map, only_group_columns):
    """
      Render a query as an SQLExpression instance.
    """

  def registerColumnMap(sql_catalog, column_map):
    """
      Register a query to given column_map.
    """

