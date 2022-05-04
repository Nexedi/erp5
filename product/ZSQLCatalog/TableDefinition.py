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

import six

SQL_LIST_SEPARATOR = ', '
SQL_SELECT_ALIAS_FORMAT = '%s AS `%s`'

from Products.ZSQLCatalog.Query.SQLQuery import SQLQuery

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

  def getJoinConditionQueryList(self):
    """Return a list of SQLQuery objects containing all conditions
    used in this table definition.

    This is a deprecated method that is here only to accomodate the
    fact that not all RelatedKey methods have been migrated.
    """
    query_list = []
    self._extendJoinConditionQueryList(query_list)
    return query_list

  def _extendJoinConditionQueryList(self, query_list):
    raise NotImplementedError('should be implemented by subclasses')

  def getSuperSet(self, other):
    """Checks if this TableDefinition is a subset of the other table
    definition or vice-versa. Return which one is the superset.

    Returns whichever is the superset of the other or None
    """
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

  def _extendJoinConditionQueryList(self, query_list):
    # XXX _extendJoinConditionQueryList
    #assert self.table_definition is not None, "table definition wasn't set"
    if self.table_definition is not None:
      return self.table_definition._extendJoinConditionQueryList(query_list)

  def getSuperSet(self, other):
    assert self.table_definition is not None, "table definition wasn't set"
    return self.table_definition.getSuperSet(other)

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

  def _extendJoinConditionQueryList(self, query_list):
    pass

  def __eq__(self, other):
    return (isinstance(other, TableAlias) and
            self.table == other.table and
            self.alias == other.alias)

  def getSuperSet(self, other):
    """A TableAlias is a subset of another table Alias if either:
     - the other is an equivalent TableAlias
     - the other is an InnerJoin where the left-side is an equivalent TableAlias
    """
    if isinstance(other, TableAlias) and self == other:
      # we're just like the other guy, we could return self or other
      return self
    # delegate the rest of the job to InnerJoin
    return other.getSuperSet(self)

JOIN_FORMAT = """
  (
    %(left)s
  %(join)s
    %(right)s
  ON
    %(condition)s
  )
""".strip()

class Join(TableDefinition):

  JOIN_TYPE = None

  def __init__(self, left_tabledef, right_tabledef, condition):
    assert self.JOIN_TYPE, ('Join must be subclassed and self.JOIN_TYPE '
                            'must be defined.')
    assert isinstance(left_tabledef, (TableDefinition, None.__class__))
    assert isinstance(right_tabledef, (TableDefinition, None.__class__))
    self.left_tabledef = left_tabledef
    self.right_tabledef = right_tabledef
    # perhaps assert condition is an SQLExpression?
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

  def _extendJoinConditionQueryList(self, query_list):
    self.left_tabledef._extendJoinConditionQueryList(query_list)
    self.right_tabledef._extendJoinConditionQueryList(query_list)
    query_list.append(SQLQuery(self.condition))

  def getSuperSet(self, other):
    return None

class InnerJoin(Join):
  """Definition of an inner-join as a FROM expression"""

  JOIN_TYPE = "INNER JOIN"

  def getSuperSet(self, other):
    """This InnerJoin is a superset of another TableDefinition if either:

     - other is a TableAlias (or None) equal to our
       left_side. I.e. "other" is at the end of it's inner-join chain.

     - other is an InnerJoin, and it's left-side is equal to our
       left-side (both TableAliases or None), and our right-side is a
       super-set of it's right-side.
    """
    if self.left_tabledef == other:
      # other and left-side are both None or matching TableAliases
      return self
    if (isinstance(other, InnerJoin) and
        self.left_tabledef == other.left_tabledef):
      # our left-sides match. If one of our right sides is a superset of the
      # other right side, then we found the superset
      sub_superset = self.right_tabledef.getSuperSet(other.right_tabledef)
      if sub_superset is self.right_tabledef:
        return self
      elif sub_superset is other.right_tabledef:
        return other
      return None
    return None

class LeftJoin(InnerJoin):
  """Definition of a left-join as a FROM expression"""

  JOIN_TYPE = "LEFT JOIN"

  def _extendJoinConditionQueryList(self, query_list):
    """ The condition from a left-join cannot be meaningfully
    extracted to be used in an implicit Inner Join, as is done when a
    query contains a related key that is not formatted to separate the
    join conditions for each related table."""
    raise RuntimeError("Attempted to collapse table definition for implicit "
                       "inner join, but this table definition contains a Left "
                       "Join: %r" % self)

class LegacyTableDefinition(TableDefinition):
  """Table Definition used when a from_expression is passed explicitly.
  Mostly used for manual left-join definitions. Deprecated
  """

  def __init__(self, from_expression, table_alias_map):
    self.from_expression = from_expression
    self.table_alias_map = table_alias_map

  def render(self):
    from_expression_dict = self.from_expression
    table_alias_map = self.table_alias_map
    from_expression = SQL_LIST_SEPARATOR.join(
      from_expression_dict.get(alias, '`%s` AS `%s`' % (table, alias))
      for alias, table in six.iteritems(table_alias_map))
    return from_expression
