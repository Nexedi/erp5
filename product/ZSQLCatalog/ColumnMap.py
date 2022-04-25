from __future__ import absolute_import
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

import re
import itertools
from zLOG import LOG, WARNING, INFO
from .interfaces.column_map import IColumnMap
from zope.interface.verify import verifyClass
from zope.interface import implementer
from Products.ZSQLCatalog.interfaces.column_map import IColumnMap
from Products.ZSQLCatalog.TableDefinition import (PlaceHolderTableDefinition,
                                                  TableAlias,
                                                  InnerJoin,
                                                  LeftJoin)
import six

DEFAULT_GROUP_ID = None

MAPPING_TRACE = False

# TODO: handle left joins
# TODO: handle straight joins
# TODO: make it possible to do: query=ComplexQuery(Query(source_title='foo'), Query(source_title='bar')), sort_on=[('source_title_1', )]
#       currently, it's not possible because related_key_dict is indexed by related key name, which makes 'source_title_1' lookup fail. It should be indexed by group (probably).
# TODO: rename all "related_key" references into "virtual_column"

re_sql_as = re.compile("\s+AS\s[^)]+$", re.IGNORECASE | re.MULTILINE)

@implementer(IColumnMap)
class ColumnMap(object):

  def __init__(self,
               catalog_table_name=None,
               table_override_map=None,
               left_join_list=None,
               inner_join_list=None,
               implicit_join=False):
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
    self.join_table_map = {}
    # BBB: Remove join_query_list and its uses when all RelatedKey
    # methods have been converted to properly return each Join
    # condition separately, and all uses of catalog's from_expression
    # have been removed.
    self.join_query_list = []
    self.table_override_map = table_override_map or {}
    self.table_definition = PlaceHolderTableDefinition()
    # We need to keep track of the original definition to do inner joins on it
    self._inner_table_definition = self.table_definition
    self.left_join_list = left_join_list
    self.implicit_join = implicit_join
    assert not (self.implicit_join and self.left_join_list), (
      "Cannot do left_joins while forcing implicit join"
    )
    self.inner_join_list = inner_join_list
    assert not set(left_join_list).intersection(inner_join_list), (
      "left_join_list and inner_join_list intersect"
    )

  def registerColumn(self, raw_column, group=DEFAULT_GROUP_ID, simple_query=None):
    assert ' as ' not in raw_column.lower(), raw_column
    # Sanitize input: extract column from raw column (might contain COUNT, ...).
    # XXX This is not enough to parse something like:
    # GROUP_CONCAT(DISTINCT foo ORDER BY bar)
    if '(' in raw_column:
      function, column = raw_column.split('(')
      column = column.strip()
      assert column[-1] == ')', column
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
        self._addJoinTableForColumn(table, table + "." + column, group)

  def ignoreColumn(self, column):
    self.column_ignore_set.add(column)

  def registerRelatedKey(self, related_column, column):
    # XXX: should we store the group, or directly the table on which the column is mapped ?
    # The former avoids duplicating data, but requires one more lookup (group + column -> table)
    # The latter makes it harder (?) to split the mapping in multiple queries (if splitting by groups turns out to be a good idea)
    real_related_column = related_column
    order = self.related_key_order_dict.get(real_related_column, 0) + 1
    related_column = '%s_%s' % (related_column, order)
    group = 'related_%s' % (related_column, )
    assert group not in self.registry, (group, self.registry)
    assert group not in self.related_group_dict, (group,
      self.related_group_dict)
    self.related_key_order_dict[real_related_column] = order
    self.related_key_dict[real_related_column] = (group, column)
    self.registerColumn(column, group=group)
    self.related_group_dict[group] = related_column
    return group

  def registerRelatedKeyColumn(self, related_column, position, group):
    assert group in self.related_group_dict, (group, self.related_group_dict)
    group = self.getRelatedKeyGroup(position, group)
    assert group not in self.related_group_dict, (group,
      self.related_group_dict)
    self.related_group_dict[group] = related_column
    return group

  def getRelatedKeyGroup(self, position, group):
    return '%s_column_%s' % (group, position)

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
      raise ValueError(
        "Table %r for group %r is aliased as %r, can't alias it now as %r"
        % (table_name, group, existing_value, alias))

  def _mapColumns(self, column_table_map, table_usage_dict, column_name_set, group, vote_result_dict):
    mapping_dict = {}
    catalog_table_name = self.catalog_table_name

    # Map all columns to tables decided by vote.
    for column_name, candidate_dict in six.iteritems(vote_result_dict):
      # candidate_dict is never empty
      max_score = 0
      for table_name, score in six.iteritems(candidate_dict):
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
      for table_name, column_set in six.iteritems(table_usage_dict):
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
    weighted_table_list = sorted(six.iteritems(table_usage_dict), key=table_weight)
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
          #     _addJoinTableForColumn)
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
    if column_name_set:
      raise ValueError('Could not map those columns: %r' % column_name_set)

    # Do the actual mapping
    for column_name, table_name in six.iteritems(mapping_dict):
      # Mark this column as resolved
      if MAPPING_TRACE:
        LOG('ColumnMap', INFO, 'Mapping column %s to table %s' % (column_name, table_name))
      self.registerTable(table_name, group=group)
      self.resolveColumn(column_name, table_name, group=group)
      if table_name != catalog_table_name:
        self._addJoinTableForColumn(table_name, column_name, group)

  def build(self, sql_catalog):
    join_query_to_build_list = []
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
          join_query_to_build_list.append(join_query)

    # List all possible tables, with all used column for each
    for group, column_set in six.iteritems(self.registry):
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
          for column, table in six.iteritems(vote_dict):
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

    for (group, table_name), alias in six.iteritems(self.table_alias_dict):
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

    # now that we have all aliases, calculate missing joins comming from
    # non-RelatedKey relationships (like full_text).
    self._calculateMissingJoins()
    # and all left joins that did not come from explicit queries
    # (i.e. joins comming from 'sort_on', 'select_dict', etc.)
    for join_query in join_query_to_build_list:
      # XXX ugly use of inner attribute of join_query. Please Refactor:
      # search_keys don't actually return SQLExpressions, but they add
      # join definitions in the column_map
      join_query.search_key.buildSQLExpression(sql_catalog=sql_catalog,
                                               column_map=self,
                                               only_group_columns=False,
                                               group=join_query.group,)
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
      for (group, column), table_name in six.iteritems(self.column_map):
        column_dict = summary_dict.setdefault(group, ({}, {}))[0]
        assert column not in column_dict, '%r in %r' % (column, column_dict)
        column_dict[column] = table_name
      for (group, table_name), table_alias in six.iteritems(self.table_alias_dict):
        table_dict = summary_dict.setdefault(group, ({}, {}))[1]
        assert table_name not in table_dict, '%r in %r' % (table_name, table_dict)
        table_dict[table_name] = table_alias
      for group, (column_dict, table_dict) in six.iteritems(summary_dict):
        LOG('ColumnMap', INFO, 'Group %r:' % (group, ))
        LOG('ColumnMap', INFO, ' Columns:')
        for column, table_name in six.iteritems(column_dict):
          LOG('ColumnMap', INFO, '  %r from table %r' % (column, table_name))
        LOG('ColumnMap', INFO, ' Tables:')
        for table_name, table_alias in six.iteritems(table_dict):
          LOG('ColumnMap', INFO, '  %r as %r' % (table_name, table_alias))

  def asSQLColumn(self, raw_column, group=DEFAULT_GROUP_ID):
    if self.catalog_table_name is None or '.' in raw_column or '*' in raw_column:
      if raw_column.endswith('__score__'):
        return raw_column.replace('.', '_')
      return raw_column
    if raw_column.endswith('__score__'):
      raw_column = raw_column[:-9]
      column_suffix = '__score__'
    else:
      column_suffix = ''
    function, column = self.raw_column_dict.get(raw_column, (None, raw_column))
    if group is DEFAULT_GROUP_ID:
      group, column = self.related_key_dict.get(column, (group, raw_column))
    try:
      table_name = self.column_map[(group, column)]
    except KeyError:
      if raw_column not in self.column_ignore_set:
        raise
      result = raw_column
    else:
      table_alias = self.table_alias_dict[(group, table_name)]
      if column_suffix:
        result = '%s_%s%s' % (table_alias, column, column_suffix)
      else:
        result = '`%s`.`%s`' % (table_alias, column)
    if function is not None:
      result = '%s(%s)' % (function, result)
    return result

  def getCatalogTableAlias(self, group=DEFAULT_GROUP_ID):
    return self.table_alias_dict[(group, self.catalog_table_name)]

  def _isBackwardCompatibilityRequired(self):
    return bool(
      # if they explicitly ask for implicit
      self.implicit_join or
      # if they don't pass a catalog alias, we cannot do explicit joins
      not self._setMinimalTableDefinition() or
      # If one or more RelatedKey methods weren't converted, we'll get
      # queries for an implicit inner join, so we have to do all joins
      # as implicit.
      self.join_query_list or
      # for now, work in BW compat mode if a table_override
      # is passed.  It only works for simple subselect
      # definitions anyway, and it's being used primarily
      # for writing left-joins manually.
      self.table_override_map)

  def getTableAliasDict(self):
    if self._isBackwardCompatibilityRequired():
      # BBB: Using implicit joins or explicit from_expression
      return self.table_map.copy()
    else:
      return None

  def resolveColumn(self, column, table_name, group=DEFAULT_GROUP_ID):
    assert group in self.registry, (group, self.registry)
    assert column in self.registry[group], (column, group,
      self.registry[group])
    assert table_name
    assert column
    column_map_key = (group, column)
    column_map = self.column_map
    assert (group, table_name) in self.table_alias_dict, (group, table_name,
      self.table_alias_dict)
    previous_value = column_map.get(column_map_key)
    if previous_value is None:
      column_map[column_map_key] = table_name
    elif previous_value != table_name:
      if column == 'uid':
        LOG('ColumnMap', WARNING, 'Attempt to remap uid from %r to %r ignored.' % (previous_value, table_name))
      else:
        raise ValueError('Cannot remap a column to another table. column_map[%r] = %r, new = %r' % (column_map_key, previous_value, table_name))

  def resolveTable(self, table_name, alias, group=DEFAULT_GROUP_ID):
    table_alias_key = (group, table_name)
    assert table_alias_key in self.table_alias_dict, (table_alias_key,
      self.table_alias_dict)
    assert self.table_alias_dict[table_alias_key] in (None, alias), (
      table_alias_key, self.table_alias_dict[table_alias_key], alias)
    self.table_alias_dict[table_alias_key] = alias
    assert self.table_map.get(alias) in (None, table_name), (alias,
      self.table_map.get(alias), table_name)
    self.table_map[alias] = table_name

  def getTableAlias(self, table_name, group=DEFAULT_GROUP_ID):
    return self.table_alias_dict[(group, table_name)]

  def _addJoinQueryForColumn(self, column, query):
    # BBB: This is a backward compatibility method that will be
    # removed in the future, when all related key methods have been adapted
    # to provide all Join conditions separately
    if column in self.left_join_list:
      raise RuntimeError('Left Join requested for column: %r, but rendered '
                         'join query is not compatible and would result in an '
                         'Implicit Inner Join:\n%s' %
                         (column, query,))
    self.join_query_list.append(query)

  def iterJoinQueryList(self):
    if self._isBackwardCompatibilityRequired():
      # Return all join queries for implicit join, and all the other
      # queries we were using to build explicit joins, but won't be able to.
      return itertools.chain(self.join_query_list,
                             self.table_definition.getJoinConditionQueryList())
    return []


  def _addJoinTableForColumn(self, table_name, column, group=DEFAULT_GROUP_ID):
    """
      Declare given table as requiring to be joined with catalog table on uid.

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
      self.join_table_map.setdefault((group, table_name), set()).add(column)

  def getJoinTableAliasList(self):
    return [self.getTableAlias(table_name, group=group)
            for (group, table_name) in self.join_table_map.keys()]

  def _getTableOverride(self, table_name):
    # self.table_override_map is a dictionary mapping table names to
    # strings containing aliases of arbitrary table definitions
    # (including subselects). So we split the alias and discard it
    # since we do our own aliasing.
    table_override_w_alias = self.table_override_map.get(table_name)
    if table_override_w_alias is None:
      return table_name
    # XXX move the cleanup of table alias overrides to EntireQuery
    # class or ZSQLCatalog, so we don't need SQL syntax knowledge in
    # ColumnMap.
    #
    # Normalise the AS sql keyword to remove the last
    # aliasing in the string if present. E.g.:
    #
    # '(SELECT sub_catalog.*
    #   FROM catalog AS sub_catalog
    #   WHERE sub_catalog.parent_uid=183) AS catalog'
    #
    # becomes:
    #
    # '(SELECT sub_catalog.*
    #   FROM catalog AS sub_catalog
    #   WHERE sub_catalog.parent_uid=183)'
    table_override, removed = re_sql_as.subn('', table_override_w_alias)
    assert removed < 2, ('More than one table aliasing was removed from %r' %
                        table_override_w_alias)
    if removed:
      LOG('ColumnMap', WARNING,
          'Table overrides should not contain aliasing: %r' % table_override)
    return table_override

  def makeTableAliasDefinition(self, table_name, table_alias):
    """Make a table alias, giving a change to ColumnMap to override
    the original table definition with another expression"""
    table_name = self._getTableOverride(table_name)
    assert table_name and table_alias, ("table_name (%r) and table_alias (%r) "
                                        "must both be defined" %
                                        (table_name, table_alias))
    return TableAlias(table_name, table_alias)

  def _setMinimalTableDefinition(self):
    """ Set a minimal table definition: the main catalog alias

    We don't do this at __init__ because we have neither the catalog
    table name nor its intended alias at that point.
    """
    inner_def = self._inner_table_definition
    if inner_def.table_definition is None:
      try:
        catalog_table_alias = self.getCatalogTableAlias()
      except KeyError:
        LOG('ColumnMap', WARNING,
            '_setMinimalTableDefinition called but the main catalog has not '
            'yet received an alias!')
        return False
      inner_def.replace(self.makeTableAliasDefinition(self.catalog_table_name,
                                                      catalog_table_alias))
    return True

  def getTableDefinition(self):
    if self._isBackwardCompatibilityRequired():
      # BBB: One of the RelatedKeys registered an implicit join, do
      # not return a table definition, self.getTableAliasDict() should
      # be used instead
      return None
    self.table_definition.checkTableAliases()
    return self.table_definition

  def addRelatedKeyJoin(self, column, right_side, condition):
    """ Wraps the current table_definition in the left-side of a new
    join.  Use an InnerJoin or a LeftJoin depending on whether the
    column is in the left_join_list or not.
    """
    # XXX: to fix TestERP5Catalog.test_52_QueryAndTableAlias, create
    # here a list of joins and try to merge each new entry into one of
    # the pre-existing entries by comparing their right-sides.
    #
    # XXX 2: This is the place were we could do ordering of inner and left
    # joins so as to get better performance. For instance, a quick win is to
    # add all inner-joins first, and all left-joins later. We could also decide
    # on the order of left-joins based on the order of self.left_join_list or
    # even a catalog property/configuration/script.
    #
    # XXX 3: This is also the place where we could check if explicit
    # table aliases should cause some of these table definitions to be
    # collapsed into others.
    assert self._setMinimalTableDefinition()
    Join = column not in self.inner_join_list and (column in self.left_join_list or
     (not self.implicit_join and column in self.registry.get(DEFAULT_GROUP_ID, ())))\
      and LeftJoin or InnerJoin
    join_definition = Join(self.table_definition, right_side,
                           condition=condition)
    self.table_definition = join_definition

  # def getFinalTableDefinition(self):
  #   self._calculateMissingJoins()
  #   return self.getTableDefinition()

  def _calculateMissingJoins(self):
    left_join_set = set(self.left_join_list)
    self._setMinimalTableDefinition()
    catalog_table_alias = self.getCatalogTableAlias()
    for (group, table_name), column_set in self.join_table_map.items():
      # if any of the columns for this implicit join was requested as a
      # left-join, then all columns will be subject to a left-join.
      # XXX What if one of the columns was an actual query, as opposed to a
      # sort column or select_dict? This would cause results in the main
      # catalog that don't match the query to be present as well. We expect
      # the user which passes a left_join_list to know what he is doing.
      if column_set.intersection(left_join_set):
        Join = LeftJoin
      else:
        Join = InnerJoin
      table_alias = self.getTableAlias(table_name, group=group)
      table_alias_def = self.makeTableAliasDefinition(table_name, table_alias)
      # XXX: perhaps refactor some of the code below to do:
      # self._inner_table_definition.addInnerJoin(TableAlias(...),
      #                                           condition=(...))
      self._inner_table_definition.replace(
        Join(self._inner_table_definition.table_definition,
                  table_alias_def,
                  # XXX ColumnMap shouldn't have SQL knowledge
                  condition=('`%s`.`uid` = `%s`.`uid`' %
                             (table_alias, catalog_table_alias)),
                  )
        )

verifyClass(IColumnMap, ColumnMap)

