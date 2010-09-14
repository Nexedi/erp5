##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from lexer import update_docstrings
from AdvancedSearchTextParser import ValueNode, NotNode, LogicalNode
from AdvancedSearchTextParser import ColumnNode, AdvancedSearchTextParser

class FullTextSearchTextParser(AdvancedSearchTextParser):

  # IMPORTANT:
  # In short: Don't remove any token definition below even if they look
  # useless.
  # In detail: The lex methods below are redefined here because of ply nice
  # feature of prioritizing tokens using the *line* *number* at which they
  # are defined. As we inherit those methods from another class from another
  # file (which doesn't match this file's content, of course) we must redefine
  # wrapper methods to enforce token priority. Kudos to ply for so much
  # customisable behaviour. Not.

  def t_LEFT_PARENTHESE(self, t):
    return AdvancedSearchTextParser.t_LEFT_PARENTHESE(self, t)

  def t_RIGHT_PARENTHESE(self, t):
    return AdvancedSearchTextParser.t_RIGHT_PARENTHESE(self, t)

  def t_OPERATOR(self, t):
    return AdvancedSearchTextParser.t_OPERATOR(self, t)

  def t_STRING(self, t):
    # Here is the only difference between AdvancedSearchTextParser and this
    # class: strings are kept escaped (ie, they are considered as WORDs).
    return AdvancedSearchTextParser.t_WORD(self, t)

  def t_COLUMN(self, t):
    return AdvancedSearchTextParser.t_COLUMN(self, t)

  def t_OR(self, t):
    return AdvancedSearchTextParser.t_OR(self, t)

  def t_AND(self, t):
    return AdvancedSearchTextParser.t_AND(self, t)

  def t_NOT(self, t):
    return AdvancedSearchTextParser.t_NOT(self, t)

  def t_WORD(self, t):
    return AdvancedSearchTextParser.t_WORD(self, t)

update_docstrings(FullTextSearchTextParser)

