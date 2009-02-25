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

class IEntireQuery(Interface):
  """
    A EntireQuery represents an entire SQL expression, where a Query
    represents only the "WHERE" part of that expression.
    A EntireQuery contains:
     - a Query instance
     - a limit expression
     - a group-by expression
     - an order-by expression
     - a select expression
    It internaly uses a ColumnMap instance to resolve tables to use to
    generate a "from" expression.
  """

  def __init__(query, order_by_list=None, group_by_list=None,
    select_dict=None, limit=None, catalog_table_name=None,
    extra_column_list=None, from_expression=None,
    order_by_override_list=None):
    """
      query (Query instance)
        The root of the Query tree this query will contain.
      order_by_list (list of 1-tuple, 2-tuple or 3-tuple)
        The list of columns which will be sorted by SQL.
        Tuple values are:
        - mandatory: column name
        - optionnal: sort order (can be "ASC" or "DESC", "ASC" by default)
        - optionnal: type cast (no cast by default, see "CAST" SQL method)
      group_by_list (list of string)
        The list of columns which will be groupped by value by SQL.
      select_dict (dict, key: string, value: string, None)
        Given values describe columns to make available in SQL result.
        If column is aliased in result set, key is the alias and value is the
        column.
        Otherwise, key is the column, and value must be None.
      limit
        See SQLExpression.
      catalog_table_name (string)
        Name of the table to use as a catalog.

      Deprecated parameters.
      extra_column_list (list of string)
        The list of columns to register to column map. They will not be used
        in final rendering, but are hint on which table are supposed to be
        used when mapping columns.
      from_expression
        See SQLExpression.
      order_by_override_list (list of string)
        If a column is in order_by_list, cannot be mapped to a table column
        but is present in this list, it will be passed through to
        SQLExpression.
    """

  def asSQLExpression(sql_catalog, only_group_columns):
    """
      Instantiate a column map, process parameters given at instantiation and
      register them to column map.
      Register query to column map.
      Build column map.
      Generate extra SQLExpressions from column map.
      Generate SQLExpression instance and return it.
    """

  def asSearchTextExpression(sql_catalog):
    """
      This is just a passthrough to embeded Query's asSearchTextExpression
      method.
      This means that only the where expression can be represented as a
      SearchText, but not sort, limits, ...
    """

