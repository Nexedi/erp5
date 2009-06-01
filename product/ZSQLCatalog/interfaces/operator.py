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

class IOperator(Interface):
  """
    An operator is responsible for rendering a value and a column name as SQL
    or Search Text.

    This class is designed to be used as a singleton-per-operator.
  """

  def __init__(operator):
    """
      operator (string)
        Operator's text representation. It is used both for SQL and SearchText
        rendering.
    """

  def asSearchText(value):
    """
      Render given value as Search Text

      value (see _renderValue)
        Value to render as a string for use in a Search Text expression.
    """

  def asSQLExpression(column, value_list, only_group_columns):
    """
      Construct a SQLExpression instance from given column and value, with
      contained glue text.
      value_list can be a non-list instance, which must be handled that same
      way as a list of one item.
      only_group_columns (bool)
        If false, the operator can add group columns in the "select_dict" of
        returned SLQExpression.
        Otherwise, it must not (SQL would be invalid).
    """

  def getOperator():
    """
      Accessor for operator's SQL representation.
    """

  def getOperatorSearchText():
    """
      Accessor for operator's SearchText representation.
    """

