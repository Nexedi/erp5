##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
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

# TODO:
# * collapse of parentheses around chains of inner-joins
# * indentation on rendering

SQL_SELECT_ALIAS_FORMAT = '%s AS `%s`'

TESTDEBUG = False

def escapeTable(table):
  return "`%s`" % table.replace('`', r'\`')

class TableDefinition(object):
  """Base class for all TableDefinition objects. Used for
  typechecking (which should become interface checking later) and
  for dumping common code (if there is any).

  TableDefinition objects describe the table aliasing and joining on
  the "FROM" expression of an SQL query. It is supposed to be
  decoded by an SQLExpressionObject into a string.
  """

  def checkTableAliases(self, current_aliases=None):
    """Check that aliases defined in this table definition don't try
    to alias different tables to the same name.

    Add all aliases defined to the current_aliases mapping if it is passed in.
    """
    if current_aliases is None:
      current_aliases = {}
    self._checkTableAliases(current_aliases)

  def _checkTableAliases(self, current_aliases):
    raise NotImplementedError('should be implemented by subclasses')

  def render(self):
    raise NotImplementedError('should be implemented by subclasses')

class PlaceHolderTableDefinition(TableDefinition):
  """Table Definition that simply holds an inner table definition and
  delegates to it the rendering.

  This object can be used when you need to change a table definition
  in the future, (like replacing a simple table aliasing with an inner
  join) but don't know who is going to be holding a reference to the
  original table definition to replace it.
  """

  def __init__(self, table_definition=None):
    self.table_definition = table_definition

  replace = __init__

  def __repr__(self):
    return '<%s for %r>' % (self.__class__.__name__, self.table_definition)

  def _checkTableAliases(self, current_aliases):
    assert self.table_definition is not None, "table definition wasn't set"
    return self.table_definition._checkTableAliases(current_aliases)

  def render(self):
    assert self.table_definition is not None, "table definition wasn't set"
    return self.table_definition.render()


class TableAlias(TableDefinition):
  """Definition of a table alias as a FROM expression"""

  def __init__(self, table, alias=None):
    self.table = table
    self.alias = alias or table

  def _checkTableAliases(self, current_aliases):
    #table_name = current_aliases.setdefault(self.alias, self.table)
    table_name = current_aliases.get(self.alias)
    if table_name is None:
      current_aliases[self.alias] = self.table
      return
    if table_name != self.table:
      message = ("Attempted to alias both %r and %r to %r" %
                 (table_name, self.table, self.alias,))
    else:
      message = ("Attempted to  alias %r to %r more than once" %
                 (self.table, self.alias,))
    raise ValueError(message)

  def render(self):
    """Render this table definition into an actual FROM expression"""
    return SQL_SELECT_ALIAS_FORMAT % (self.table, self.alias)

  def __repr__(self):
    return '<%s %r AS %r>' % (self.__class__.__name__, self.table, self.alias)

JOIN_FORMAT = """
  (
    %(left)s 
  %(join)s
    %(right)s
  ON 
    %(condition)s
  )
""".strip()

class InnerJoin(TableDefinition):
  """Definition of an inner-join as a FROM expression"""

  JOIN_TYPE = "INNER JOIN"

  def __init__(self, left_tabledef, right_tabledef, condition):
    assert isinstance(left_tabledef, (TableDefinition, None.__class__))
    assert isinstance(right_tabledef, (TableDefinition, None.__class__))
    self.left_tabledef = left_tabledef
    self.right_tabledef = right_tabledef
    # perhaps expect condition to be a SQLExpression?
    self.condition = condition

  def render(self):
    """Render the join as an actual FROM expression, delegating
    the rendering of each table to its own object.
    """
    assert None not in (self.left_tabledef, self.right_tabledef, self.condition)
    return JOIN_FORMAT % dict(left=self.left_tabledef.render(),
                              right=self.right_tabledef.render(),
                              join=self.JOIN_TYPE,
                              condition=self.condition)

  def _checkTableAliases(self, current_aliases):
    self.left_tabledef._checkTableAliases(current_aliases)
    self.right_tabledef._checkTableAliases(current_aliases)

  def __repr__(self):
    return '<%s of %r and %r on %r>' % (self.__class__.__name__,
                                        self.left_tabledef,
                                        self.right_tabledef,
                                        self.condition)

class LeftJoin(InnerJoin):
  """Definition of a left-join as a FROM expression"""
  
  JOIN_TYPE = "LEFT JOIN"
