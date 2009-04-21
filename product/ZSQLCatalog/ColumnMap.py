##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SARL and Contributors. All Rights Reserved.
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

from zLOG import LOG, WARNING, INFO
from Interface.IColumnMap import IColumnMap
from Interface.Verify import verifyClass
from SQLCatalog import profiler_decorator

DEFAULT_GROUP_ID = None

MAPPING_TRACE = False

# TODO: handle left joins
# TODO: handle straight joins
# TODO: make it possible to do: query=ComplexQuery(Query(source_title='foo'), Query(source_title='bar')), sort_on=[('source_title_1', )]
#       currently, it's not possible because related_key_dict is indexed by related key name, which makes 'source_title_1' lookup fail. It should be indexed by group (probably).
# TODO: rename all "related_key" references into "virtual_column"

class ColumnMap(object):

  __implements__ = IColumnMap

  @profiler_decorator
  def __init__(self, catalog_table_name=None):
    self.catalog_table_name = catalog_table_name
    # Key: group
    # Value: set of column names
    self.registry = {}
    # Key: group
    # Value: dict
    #  Key: column name
    #  Value: set of SimpleQuery
    self.simple_query_dict = {}
    # Key: (group, column name)
    # Value: table name
    self.column_map = {}
    # Key: (group, table name)
    # Value: table alias
    self.table_alias_dict = {}
    # Key: related key name
    # Value: (group, column name)
    self.related_key_dict = {}
    # Key: related_column
    # Value: last used alias order
    self.related_key_order_dict = {}
    # Key: group
    # Value: relate_key
    self.related_group_dict = {}
    # Key: table alias
    # Value: table name
    self.table_map = {}
    # Key: raw column
    # Value: (function, column)
    self.raw_column_dict = {}
    # Entries: column name
    self.column_ignore_set = set()
    self.join_table_set = set()
    self.straight_join_table_list = []
    self.left_join_table_list = []
    self.join_query_list = []

  @profiler_decorator
  def registerColumn(self, raw_column, group=DEFAULT_GROUP_ID, simple_query=None):
    assert ' as ' not in raw_column.lower()
    # Sanitize input: extract column from raw column (might contain COUNT, ...).
    if '(' in raw_column:
      function, column = raw_column.split('(')
      column = column.strip()
      assert column[-1] == ')'
      column = column[:-1].strip()
    else:
      function = None
      column = raw_column
    # Remove 'DISTINCT ' etc. from column.
    column = column.split()[-1]
    # Remove '`' from column.
    column = column.replace('`', '')
    # Extract table name from column, if any.
    if '.' in column:
      # Assuming the part before the dot is a real table name, not an alias.
      table, column = column.split('.')
    else:
      table = None

    self.raw_column_dict[raw_column] = (function, column)
    self.registry.setdefault(group, set()).add(column)
    self.simple_query_dict.setdefault(group, {}).setdefault(column, set()).add(simple_query)
    if table is not None:
      # Register table alias and mark column as resolved.
      self.registerTable(table, alias=table, group=group)
      self.resolveColumn(column, table, group=group)
      if group is DEFAULT_GROUP_ID and table != self.catalog_table_name:
        # When a column is registered  in default group and is explicitely
        # mapped to a table, we must mark its table as requiring a join with
        # catalog table (unless it's the catalog table, of course).
        self._addJoinTable(table, group)

  def ignoreColumn(self, column):
    self.column_ignore_set.add(column)

  @profiler_decorator
  def registerRelatedKey(self, related_column, column):
    # XXX: should we store the group, or directly the table on which the column is mapped ?
    # The former avoids duplicating data, but requires one more lookup (group + column -> table)
    # The latter makes it harder (?) to split the mapping in multiple queries (if splitting by groups turns out to be a good idea)
    real_related_column = related_column
    order = self.related_key_order_dict.get(real_related_column, 0) + 1
    related_column = '%s_%s' % (related_column, order)
    group = 'related_%s' % (related_column, )
    assert group not in self.registry
    assert group not in self.related_group_dict
    self.related_key_order_dict[real_related_column] = order
    self.related_key_dict[real_related_column] = (group, column)
    self.registerColumn(column, group=group)
    self.related_group_dict[group] = related_column
    # XXX: hardcoded translation table column names: they are not present in sql_catalog.getColumnMap(), and this table cannot be joined by uid, forbidding implicit join.
    if column in ('translated_message', 'language', 'message_context', 'original_message'):
      self.registerTable('translation', group=group)
      self.resolveColumn(column, 'translation', group=group)
    # Likewise, for measure table. Moreover, there is a related key named the same way as a column of that table (designed to do the join).
    elif column in ('metric_type_uid', ):
      self.registerTable('measure', group=group)
      self.resolveColumn(column, 'measure', group=group)
    return group

  @profiler_decorator
  def registerCatalog(self):
    """
      Register catalog as being in use in query, and aliased with its own
      name.

      This is used by SearchKey/RelatedKey.py: there is no way to reliably
      detect if catalog table is used in a related key, so the catalog table
      might be absent from final table mapping.
      DO NOT USE IT ANYWHERE ELSE, this will go away...

      This must be changed by designing a new related key API, which must:
      - state *all* tables they use in their definition
      - return Query instances instead of raw SQL code
      This will allow chaining related keys and consequently allow
      simplifying redundant code.
    """
    assert self.catalog_table_name is not None
    self.registerTable(self.catalog_table_name)
    self.resolveTable(self.catalog_table_name, self.catalog_table_name)

  @profiler_decorator
  def registerRelatedKeyColumn(self, related_column, position, group):
    assert group in self.related_group_dict
    group = self.getRelatedKeyGroup(position, group)
    assert group not in self.related_group_dict
    self.related_group_dict[group] = related_column
    return group

  def getRelatedKeyGroup(self, position, group):
    return '%s_column_%s' % (group, position)

  @profiler_decorator
  def registerTable(self, table_name, alias=None, group=DEFAULT_GROUP_ID):
    table_alias_dict = self.table_alias_dict
    table_alias_key = (group, table_name)
    existing_value = table_alias_dict.get(table_alias_key)
    # alias = None, existing = None -> store
    # alias = None, existing ! None -> skip
    # alias ! None, existing = None -> store & resolve
    # alias ! None, existing ! None -> skip if alias = existing, raise otherwise
    if existing_value is None:
      table_alias_dict[table_alias_key] = alias
      if alias is not None:
        self.resolveTable(table_name, alias, group=group)
    elif alias is not None and alias != existing_value:
      raise ValueError, 'Table %r for group %r is aliased as %r, can\'t alias it now as %r' % (table_name, group, existing_value, alias)

  @profiler_decorator
  def _mapColumns(self, column_table_map, table_usage_dict, column_name_set, group, vote_result_dict):
    mapping_dict = {}
    catalog_table_name = self.catalog_table_name

    # Map all columns to tables decided by vote.
    for column_name, candidate_dict in vote_result_dict.iteritems():
      # candidate_dict is never empty
      max_score = 0
      for table_name, score in candidate_dict.iteritems():
        if score > max_score:
          max_score = score
          best_count = 0
          best_choice = table_name
        elif score == max_score:
          best_count += 1
      if best_count:
        LOG('ColumnMap', WARNING, 'Mapping vote led to a tie. Mapping to %r' % (best_choice, ))
      if MAPPING_TRACE:
        LOG('ColumnMap', INFO, 'Mapping by vote %r to %r' % (column_name, best_choice))
      mapping_dict[column_name] = best_choice
      column_name_set.remove(column_name)
      for table_name, column_set in table_usage_dict.iteritems():
        if table_name != best_choice:
          column_set.discard(column_name)

    # Map all remaning columns.
    def table_weight(a):
      """
        Compute each table weight.
      """
      if (group, a[0]) in self.table_alias_dict:
        result = (2, )
      elif a[0] == catalog_table_name:
        result = (1, )
      else:
        result = (0, len(a[1]))
      return result
    # Sort table name list, first has the most required columns
    weighted_table_list = sorted(table_usage_dict.iteritems(), key=table_weight)
    while len(weighted_table_list):
      table_name, column_set = weighted_table_list.pop()
      if len(column_set):
        common_column_set = column_name_set.intersection(column_set)
        if len(common_column_set):
          # Only allow usage of this table if any of those is true:
          # - current table is the catalog  (if any catalog was provided)
          # - there are column used on that table which are already mapped
          #   (this does not include columns mapped by this code)
          #   If columns are mapped to this table in current group, then using
          #   it will not require a new join, so it should be allowed.
          #   Note: it would be good to take indexes into account when there
          #   are multiple candidate tables.
          # - any of those columns belongs exclusively to this table
          #   Although the list of tables those columns belong to is known
          #   earlier (in "build"), mapping them here
          #   - avoids code duplication (registerTable, resolveColumn,
          #     _addJoinTable)
          #   - offers user to vote for an unknown table, overriding this
          #     forced mapping.
          use_allowed = table_name == catalog_table_name or \
                        len(common_column_set) < len(column_set)
          if not use_allowed:
            for column_name in column_set:
              if len(column_table_map.get(column_name, [])) == 1:
                # There is no alternative, mark as required
                use_allowed = True
                break
          if use_allowed:
            for column_name in common_column_set:
              if MAPPING_TRACE:
                LOG('ColumnMap', INFO, 'Mapping by default %r to %r' % \
                    (column_name, table_name))
              mapping_dict[column_name] = table_name
              # This column must not be resolved any longer
              column_name_set.remove(column_name)
              # Remove this column from sets containing it. This prevents from
              # giving a high score to a table which columns would already have
              # been mapped to another table.
              for ignored, other_column_set in weighted_table_list:
                other_column_set.discard(column_name)
            weighted_table_list.sort(key=table_weight)
          else:
            # All column which are mappable on that table are to-be-mapped
            # columns. This means that this table was not explicitely used, and
            # as each table contain a different amount of lines, we should not
            # join with any non-explicit table. Hence, we skip this mapping.
            LOG('ColumnMap', INFO, 'Skipping possible map of %r on %r as that table' \
                ' is not explicitely used.' % (common_column_set, table_name))

    # Detect incomplete mappings
    if len(column_name_set):
      raise ValueError, 'Could not map those columns: %r' % (column_name_set, )

    # Do the actual mapping
    for column_name, table_name in mapping_dict.iteritems():
      # Mark this column as resolved
      if MAPPING_TRACE:
        LOG('ColumnMap', INFO, 'Mapping column %s to table %s' % (column_name, table_name))
      self.registerTable(table_name, group=group)
      self.resolveColumn(column_name, table_name, group=group)
      if table_name != catalog_table_name:
        self._addJoinTable(table_name, group)

  @profiler_decorator
  def build(self, sql_catalog):
    catalog_table_name = self.catalog_table_name
    if catalog_table_name is None:
      return

    column_table_map = sql_catalog.getColumnMap()
    table_vote_method_list = [getattr(sql_catalog, x) for x in sql_catalog.sql_catalog_table_vote_scripts]

    # Generate missing joins from default group (this is required to allow using related keys outside of queries: order_by, sort_on, ...)
    column_set = self.registry.get(DEFAULT_GROUP_ID, [])
    for column_name in column_set:
      if column_name not in column_table_map and column_name not in self.related_key_dict:
        related_key_definition = sql_catalog.getRelatedKeyDefinition(column_name)
        if related_key_definition is not None:
          join_query = sql_catalog.getSearchKey(column_name, 'RelatedKey').buildQuery(sql_catalog=sql_catalog, related_key_definition=related_key_definition)
          join_query.registerColumnMap(sql_catalog, self)
          self._addJoinQuery(join_query)

    # List all possible tables, with all used column for each
    for group, column_set in self.registry.iteritems():
      # unique needed column name set
      column_name_set = set()
      # table -> column_set, including alternatives
      table_usage_dict = {}

      for column_name in column_set:
        if column_name == '*' or column_name in self.column_ignore_set:
          continue
        table_name_list = column_table_map.get(column_name, [])
        if len(table_name_list) == 0:
          if not(group is DEFAULT_GROUP_ID and column_name in self.related_key_dict):
            LOG('ColumnMap', WARNING, 'Not a known column name: %r' % (column_name, ))
          continue
        column_map_key = (group, column_name)
        if column_map_key in self.column_map:
          # Column is already mapped, so we must count this column as being available only on that table. Its mapping will not change, and it will impact table schema choice.
          table_name = self.column_map[column_map_key]
          assert table_name in table_name_list, '%r not in %r' % (table_name, table_name_list)
          table_name_list = [table_name]
        else:
          # Mark this column as requiring to be mapped.
          column_name_set.add(column_name)
        for table_name in table_name_list:
          table_usage_dict.setdefault(table_name, set()).add(column_name)
      # XXX: mutable datatypes are provided to vote method. if it modifies
      # them, it can introduce mapping bugs. Copying them might be costly,
      # especialy if done before each call, since they also contain mutable
      # types.
      # XXX: the API of vote methods is not stable yet. Parameters should
      # always be passed and expected by name, to make it less painful to
      # change API.
      # XXX: there is no check that the table voted for contains mapped
      # column. It is up to the user not to do stupid things.
      vote_result_dict = {}
      simple_query_dict = self.simple_query_dict[group]
      for table_vote_method in table_vote_method_list:
        vote_dict = table_vote_method(column_name_set=column_name_set,
                                      simple_query_dict=simple_query_dict,
                                      table_usage_dict=table_usage_dict,
                                      group=group)
        if isinstance(vote_dict, dict):
          for column, table in vote_dict.iteritems():
            if column in column_name_set:
              column_vote_dict = vote_result_dict.setdefault(column, {})
              column_vote_dict[table] = column_vote_dict.get(table, 0) + 1
            else:
              LOG('ColumnMap', WARNING, 'Vote script %r voted for a ' \
                  'non-candidate column: %r, candidates are: %r. Ignored.' %
                  (table_vote_method, column, column_name_set))
        else:
          LOG('ColumnMap', WARNING, 'Vote script %r returned invalid data: %r. ' \
              'Ignored.' % (table_vote_method, vote_dict))
      self._mapColumns(column_table_map, table_usage_dict, column_name_set, group, vote_result_dict)

    table_alias_number_dict = {}

    for (group, table_name), alias in self.table_alias_dict.iteritems():
      if alias is None:
        if group in self.related_group_dict:
          alias_table_name = 'related_%s_%s' % (self.related_group_dict[group], table_name)
        else:
          alias_table_name = table_name
        table_alias_number = table_alias_number_dict.get(alias_table_name, 0)
        while True:
          if table_alias_number == 0:
            alias = alias_table_name
          else:
            alias = '%s_%s' % (alias_table_name, table_alias_number)
          table_alias_number += 1
          if alias not in self.table_map:
            break
        table_alias_number_dict[alias_table_name] = table_alias_number
      self.resolveTable(table_name, alias, group=group)

    if MAPPING_TRACE:
      # Key: group
      # Value: 2-tuple
      #  dict
      #   Key: column
      #   Value: table name
      #  dict
      #   Key: table name
      #   Value: table alias
      summary_dict = {}
      for (group, column), table_name in self.column_map.iteritems():
        column_dict = summary_dict.setdefault(group, ({}, {}))[0]
        assert column not in column_dict, '%r in %r' % (column, column_dict)
        column_dict[column] = table_name
      for (group, table_name), table_alias in self.table_alias_dict.iteritems():
        table_dict = summary_dict.setdefault(group, ({}, {}))[1]
        assert table_name not in table_dict, '%r in %r' % (table_name, table_dict)
        table_dict[table_name] = table_alias
      for group, (column_dict, table_dict) in summary_dict.iteritems():
        LOG('ColumnMap', INFO, 'Group %r:' % (group, ))
        LOG('ColumnMap', INFO, ' Columns:')
        for column, table_name in column_dict.iteritems():
          LOG('ColumnMap', INFO, '  %r from table %r' % (column, table_name))
        LOG('ColumnMap', INFO, ' Tables:')
        for table_name, table_alias in table_dict.iteritems():
          LOG('ColumnMap', INFO, '  %r as %r' % (table_name, table_alias))

  def asSQLColumn(self, raw_column, group=DEFAULT_GROUP_ID):
    if self.catalog_table_name is None or raw_column in self.column_ignore_set or \
       '.' in raw_column or '*' in raw_column:
      result = raw_column
    else:
      function, column = self.raw_column_dict.get(raw_column, (None, raw_column))
      if group is DEFAULT_GROUP_ID:
        group, column = self.related_key_dict.get(column, (group, raw_column))
      alias = self.table_alias_dict[(group, self.column_map[(group, column)])]
      result = '`%s`.`%s`' % (alias, column)
      if function is not None:
        result = '%s(%s)' % (function, result)
    return result

  def getCatalogTableAlias(self, group=DEFAULT_GROUP_ID):
    return self.table_alias_dict[(group, self.catalog_table_name)]

  def getTableAliasDict(self):
    return self.table_map.copy()

  @profiler_decorator
  def resolveColumn(self, column, table_name, group=DEFAULT_GROUP_ID):
    assert group in self.registry
    assert column in self.registry[group]
    column_map_key = (group, column)
    column_map = self.column_map
    assert (group, table_name) in self.table_alias_dict
    previous_value = column_map.get(column_map_key)
    if previous_value is None:
      column_map[column_map_key] = table_name
    elif previous_value != table_name:
      if column == 'uid':
        LOG('ColumnMap', WARNING, 'Attempt to remap uid from %r to %r ignored.' % (previous_value, table_name))
      else:
        raise ValueError, 'Cannot remap a column to another table. column_map[%r] = %r, new = %r' % (column_map_key, column_map.get(column_map_key), table_name)

  @profiler_decorator
  def resolveTable(self, table_name, alias, group=DEFAULT_GROUP_ID):
    table_alias_key = (group, table_name)
    assert table_alias_key in self.table_alias_dict
    assert self.table_alias_dict[table_alias_key] in (None, alias)
    self.table_alias_dict[table_alias_key] = alias
    assert self.table_map.get(alias) in (None, table_name)
    self.table_map[alias] = table_name

  def getTableAlias(self, table_name, group=DEFAULT_GROUP_ID):
    return self.table_alias_dict[(group, table_name)]

  def _addJoinQuery(self, query):
    self.join_query_list.append(query)

  def addJoinQuery(self, query):
    LOG('ColumnMap', INFO, 'addJoinQuery use is discouraged')
    self._addJoinQuery(query)

  def iterJoinQueryList(self):
    return iter(self.join_query_list)

  @profiler_decorator
  def _addJoinTable(self, table_name, group=DEFAULT_GROUP_ID):
    """
      Declare given table as requiring to be joined with catalog table.

      table_name (string)
        Table name.
      group (string)
        Group id of given table.
    """
    catalog_table = self.catalog_table_name
    if catalog_table is not None:
      # Only join tables when there is a catalog table
      # Register unconditionaly catalog table
      self.registerTable(catalog_table)
      if 'uid' not in self.registry.get(DEFAULT_GROUP_ID, ()):
        # Register uid column if it is not already
        self.registerColumn('uid')
        self.resolveColumn('uid', catalog_table)
      self.join_table_set.add((group, table_name))

  def getJoinTableAliasList(self):
    return [self.getTableAlias(table_name, group=group)
            for (group, table_name) in self.join_table_set]

  def getStraightJoinTableList(self):
    return self.straight_join_table_list[:]

  def getLeftJoinTableList(self):
    return self.left_join_table_list[:]

verifyClass(IColumnMap, ColumnMap)

