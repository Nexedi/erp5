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

from zope.interface import Interface

class IColumnMap(Interface):
  """
    The role of the column mapper is to make possible to have a "flat"
    overview of all columns used in a query, to choose how they will be
    mapped to catalog tables, and how those tables will be aliased in the SQL
    rendering of that query.

    Typical usage:
    - Instanciate (with or without a catalog table)
    - Register all columns the query will use
    - Build the column map
    - Fetch SQL representation of each registered column.
    - Fetch table alias mapping
    - Fetch the list of table aliases which require a join with catalog
    - Fetch the list of queries implied by columns. This happens when there
      are virtual columns registered which were not expanded in the query
      already. In that case, column map generate queries required to reach
      the real column behind the virtual one.

    Note that, although it's not enforced, it is meaningless to:
    - call build more than once
    - register columns after build happened
    - fetch SQL representation before build happened (this will most probably
      lead to KeyErrors anyway)

    Groups.
      All references to a given table withing a given group will cause all
      columns referencing that table to be resolved to the same table alias
      in resulting query.
      Ex:
        Note: instead of resolving columns by hand, it is also possible to
        call "build", but this way it makes .
        Registration:
          registerColumn('bar')
          registerColumn('baz')
          resolveColumn('bar', 'foo')
          resolveColumn('baz', 'foo')
        Result:
          asSQLColumn('bar') -> 'foo_alias.bar'
          asSQLColumn('baz') -> 'foo_alias.baz'
      Complementary, any reference to a given table from one group to
      another will cause columns to be resolved to distinct table aliases
      in resulting query.
      Ex:
        Registration:
          registerColumn('bar')
          registerColumn('baz', group='hoge')
          resolveColumn('bar', 'foo')
          resolveColumn('baz', 'foo', group='hoge')
        Result:
          asSQLColumn('bar')               -> 'foo_alias.bar'
          asSQLColumn('baz', group='hoge') -> 'other_foo_alias.baz'
  """

  def __init__(catalog_table_name=None):
    """
      Create a column map.

      Initialises internal data structures and set the table name to use as
      catalog table.
    """

  def registerColumn(column, group=None, simple_query=None):
    """
      Register a column in given group on this column map.

      column (string)
        Contains the name of the column to register.

        This name might contain a dot, in which case a table name is extracted
        from it and that column is resolved to that table within its group.
        Note that this practice is discouraged, but not deprecated.
      group (string)
        Group id of given column.
      simple_query (SimpleQuery)
        The SimpleQuery doing a comparison on given column. This can be
        accessed from vote script at ColumnMap build time.
    """

  def ignoreColumn(column):
    """
      Act as if given column was valid and its mapping succeeded.
      ie: supresses all warnings relative to that column, and all mapping
      attemps.
      It is supposed to be used when given value is an SQL alias for a
      separately registered column.

      column (string)
        The value to ignore.
    """

  def registerRelatedKey(related_column, column):
    """
      Register a "virtual column".
      This method is to be called when registering any virtual column.
      A virtual column makes use internaly of multiple catalog columns.
      A related key is an example of a virtual column.

      This method internaly generates a new group id that caller must pass to
      registerRelatedKeyColumn when registering those internal (and real)
      columns. This is because the same virtual column can be used more than
      once in a query without interferences from other uses, and hence must be
      put in separate groups, without having to know that there are other uses
      for the same virtual column.

      virtual_column
        Name of the virtual column to register.
      column
        Name of the "last" real column behind the virtual column. Comparisons
        done on the virtual column will happen on that real column instead.
        For example, it's "title" for "source_title" related key.
    """

  def registerCatalog():
    """
      Register catalog table as being used in default group.

      This is for backward compatibility with text-only related keys, since
      they often hardcode catalog table name.
    """

  def registerRelatedKeyColumn(related_column, position, group):
    """
      Register given column as part of already registered virtual column.

      related_column (string)
        Name of the virtual column registered column is a part of.
      position (int)
        Unique id of this column in the list of all columns used by the
        virtual column it is a part of (it might use the same column name
        while expecting uses to be mapped to different aliases or evne
        different tables).
        Typically, this is table position in the parameter list the related
        key expects.
      group (string)
        Group id as returned by registerRelatedKey of given virtual column.
    """

  def getRelatedKeyGroup(position, group):
    """
      For given virtual key position and group, return a group.

      This is here so that all group generation code is inside ColumnMap
      class.
    """

  def registerTable(table_name, alias=None, group=None):
    """
      Register given table name as being used in given group.

      This method should not be called outside of this class except for
      backward compatibility purposes.

      It is implicitely done most of the time, and should only be used only
      when there is no control over chosen table alias or when table
      registration cannot be done by a Query.
      There are 2 cases where it cas required:
      - pre-mapped columns which won't be actually used, but which force table
        alias choice (see EntireQuery).
      - related keys, where the Related Query cannot register columns it uses
        by itself (since its content is not based on Queries but on raw SQL
        text).
    """

  def build(sql_catalog):
    """
      Resolve all unresolved registered columns (ie, not mapped to tables).
      Resolve all used tables to unique aliases.

      Chosen table aliases are based on table name and virtual column name the
      column comes from, if applicable. This is done to make final SQL more
      reader-friendly.
    """

  def asSQLColumn(column, group=None):
    """
      Return an SQL rendering of given column, with the table alias it has
      been mapped to.

      column (string)
        Column name. Can be the name of a virtual column.

        This name might contain a dot, in which case a table name is extracted
        from it and that column is resolved to that table within its group.
        Note that this practice is discouraged, but not deprecated.
        Note also that it does not apply to virtual columns (they cannot
        contain a dot).
      group (string)
        Group id of given column.
    """

  def getCatalogTableAlias(group=None):
    """
      Return the alias of catalog table name given at instantiation.
    """

  def getTableAliasDict():
    """
      Return a copy of table mapping.

      returned value (dict)
        key (string)
          Table alias.
        value (string)
          Table name.
    """

  def resolveColumn(column, table_name, group=None):
    """
      Map given column to given table within given group.

      column (string)
        Name of the column to map to a table. This cannot be a virtual column.
      table_name (string)
        Name of the table column must be mapped to. This is not an alias.
        It must be already known to be used within given group.
      group (string)
        Name of the group column and table are in.
    """

  def resolveTable(table_name, alias, group=None):
    """
      Resolve given table of given group as given alias.

      table_name (string)
        Table to alias.
      alias (string)
        Table alias. It must be unique at query scope to work as intended.
      gorup (string)
        Group the table belongs to.
    """

  def getTableAlias(table_name, group=None):
    """
      Get table alias in given group.

      table_name (string)
        Table name.
      group (string)
        Group id of given table.
    """

  def iterJoinQueryList():
    """
      Get an iterator over queries internally generated when resolving column
      map. Those queries are generated when a virtual column was registered as
      a real one. Queries required to map virtual columns to real ones are
      put in that list by build.
    """

  def getJoinTableAliasList():
    """
      Return a copy of the table alias list for tables requiring a join with
      catalog table.
    """

  def getStraightJoinTableList():
    """
      Returns the list of tables used this search and which
      need to be joined with the main table using explicit
      indices.
    """

  def getLeftJoinTableList():
    """
      Returns the list of tables used this search and which
      need to be LEFT joined with the main table using explicit
      indices.
    """

