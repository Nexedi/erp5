from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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

import sqlite3
from contextlib import contextmanager
from random import getrandbits
import six
from six.moves import xrange
from Products.ERP5Type.Utils import str2bytes
from Shared.DC.ZRDB.Results import Results
from Products.CMFActivity.ActivityTool import Message
from ..Common.SQLBase import (
  SQLBase as _SQLBase,
  sort_message_key,
  render_datetime,
  sqltest_dict,
  INVOKE_ERROR_STATE,
  DEPENDENCY_IGNORED_ERROR_STATE,
  MAX_VALIDATED_LIMIT,
  READ_MESSAGE_LIMIT,
  UID_SAFE_BITSIZE,
  UID_ALLOCATION_TRY_COUNT,
)


class SQLBase(_SQLBase):

  # SQLite's SQLITE_MAX_COMPOUND_SELECT defaults to 500. Keep some margin.
  _MAX_DEPENDENCY_UNION_SUBQUERY_COUNT = -400

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, node, group_method_id, tag, serialization_tag,"
    b" message) VALUES\n")
  _insert_separator = b",\n"

  def _dependencySubqueryPrefix(self, column_list):
    # SQLite does not accept parenthesized SELECTs as compound-SELECT legs,
    # and disallows LIMIT on intermediate legs. Wrap each leg in a FROM
    # subquery instead.
    return b'SELECT * FROM (SELECT %s FROM ' % (
      b','.join([str2bytes(c) for c in column_list]),
    )

  def hasActivitySQL(self, quote, only_valid=False, only_invalid=False, **kw):
    # Joined with UNION ALL by ActivityTool.hasActivity. SQLite disallows
    # LIMIT on intermediate compound-SELECT legs, so push it inside a
    # FROM-subquery.
    where = [sqltest_dict[k](v, quote) for (k, v) in six.iteritems(kw) if v]
    if only_valid:
      where.append(b'processing_node > %d' % INVOKE_ERROR_STATE)
    if only_invalid:
      where.append(b'processing_node <= %d' % INVOKE_ERROR_STATE)
    return b"SELECT * FROM (SELECT 1 FROM %s WHERE %s LIMIT 1)" % (
      str2bytes(self.sql_table), b" AND ".join(where) or b"1")

  def prepareQueueMessageList(self, activity_tool, message_list):
    db = activity_tool.getSQLConnection()
    insert_prefix = self._insert_template % str2bytes(self.sql_table)
    sep = self._insert_separator
    hasDependency = self._hasDependency
    def insert(rows):
      for _ in xrange(UID_ALLOCATION_TRY_COUNT):
        base = getrandbits(UID_SAFE_BITSIZE)
        row_sql_list = []
        all_args = []
        for i, (row_sql, row_args) in enumerate(rows):
          row_sql_list.append(row_sql)
          all_args.append(base + i)
          all_args.extend(row_args)
        sql = insert_prefix + sep.join(row_sql_list)
        try:
          db.query(sql, args=tuple(all_args))
        except sqlite3.IntegrityError as e:
          msg = str(e)
          if 'UNIQUE constraint failed' not in msg and 'PRIMARY KEY' not in msg:
            raise
        else:
          return
      raise ValueError("Maximum retry for prepareQueueMessageList reached")
    rows_list = []
    for m in message_list:
      if m.is_registered:
        date = m.activity_kw.get('at_date')
        if date is None:
          date_sql = b"UTC_TIMESTAMP(6)"
          date_args = ()
        else:
          date_sql = b'?'
          date_args = (render_datetime(date),)
        row_sql = b'(?,?,?,' + date_sql + b',?,?,?,?,?,?,?,?)'
        row_args = (
          '/'.join(m.object_path),
          m.active_process_uid,
          ) + date_args + (
          m.method_id,
          -1 if hasDependency(m) else 0,
          m.activity_kw.get('priority', 1),
          m.activity_kw.get('node', 0),
          m.getGroupId(),
          m.activity_kw.get('tag', b''),
          m.activity_kw.get('serialization_tag', b''),
          Message.dump(m))
        rows_list.append((row_sql, row_args))
    if rows_list:
      insert(rows_list)

  def assignMessageList(self, db, state, uid_list):
    uid_list = tuple(uid_list)
    placeholders = b",".join([b"?"] * len(uid_list))
    sql = (b"UPDATE %s SET processing_node=? WHERE uid IN (%s)"
           % (str2bytes(self.sql_table), placeholders))
    db.query(sql, args=(state,) + uid_list)
    db.query(b"COMMIT")

  def deleteMessageList(self, db, uid_list):
    uid_list = tuple(uid_list)
    placeholders = b",".join([b"?"] * len(uid_list))
    sql = (b"DELETE FROM %s WHERE uid IN (%s)"
           % (str2bytes(self.sql_table), placeholders))
    db.query(sql, args=uid_list)

  def reactivateMessageList(self, db, uid_list, delay, retry):
    uid_list = tuple(uid_list)
    placeholders = b",".join([b"?"] * len(uid_list))
    date_sql = (b"strftime('%Y-%m-%d %H:%M:%f','now','+"
                + str2bytes(str(delay)) + b" seconds')")
    sql = (b"UPDATE %s SET date = %s%s WHERE uid IN (%s)"
           % (str2bytes(self.sql_table),
              date_sql,
              b", retry = retry + 1" if retry else b"",
              placeholders))
    db.query(sql, args=uid_list)

  def timeShift(self, activity_tool, delay, processing_node=None):
    db = activity_tool.getSQLConnection()
    date_sql = b"datetime(date, '-" + str2bytes(str(delay)) + b" seconds')"
    if processing_node is None:
      sql = b"UPDATE %s SET date = %s" % (
        str2bytes(self.sql_table), date_sql)
      db.query(sql)
    else:
      sql = b"UPDATE %s SET date = %s WHERE processing_node=?" % (
        str2bytes(self.sql_table), date_sql)
      db.query(sql, args=(processing_node,))

  def _selectPriority(self, db, processing_node, node_set):
    table = str2bytes(self.sql_table)
    if node_set is None:
      sql = (b"SELECT 3*priority, date FROM %s"
        b" WHERE processing_node=0 AND date <= UTC_TIMESTAMP(6)"
        b" ORDER BY priority, date LIMIT 1") % table
      return db.query(sql, 0)[1]
    def subquery(prio_suffix, cond_sql):
      # SQLite forbids ORDER BY / LIMIT on intermediate compound-SELECT legs,
      # so wrap each leg as a FROM-subquery.
      return (b"SELECT * FROM ("
        b"SELECT 3*priority" + prio_suffix + b" AS effective_priority, date"
        b" FROM " + table +
        b" WHERE " + cond_sql +
        b" AND processing_node=0 AND date <= UTC_TIMESTAMP(6)"
        b" ORDER BY priority, date LIMIT 1)")
    subqueries = [
      subquery(b'-1', b'node = ?'),
      subquery(b'', b'node=0'),
    ]
    args = [processing_node]
    for x in node_set:
      subqueries.append(subquery(b'-1', b'node = ?'))
      args.append(x)
    sql = (b"SELECT * FROM (" + b" UNION ALL ".join(subqueries) + b")"
      b" ORDER BY effective_priority, date LIMIT 1")
    result = db.query(sql, 0, args=tuple(args))[1]
    if not result:
      fallback = subquery(b'+1', b'node>0')
      result = db.query(fallback, 0)[1]
    return result

  def _selectReservedMessageList(self, db, date, processing_node, limit,
                                 group_method_id, node_set):
    table = str2bytes(self.sql_table)
    to_date_sql = b"date <= ?"
    # getNow(db) returns a string on SQLite (UDF result); tests may pass a
    # DateTime instance which needs rendering.
    base_args = [date if isinstance(date, str) else render_datetime(date)]
    if group_method_id:
      group_clause = b" AND group_method_id=?"
      group_args = [group_method_id]
    else:
      group_clause = b""
      group_args = []
    if node_set is None:
      sql = (b"SELECT * FROM " + table +
        b" WHERE processing_node=0 AND " + to_date_sql + group_clause +
        b" ORDER BY priority, date LIMIT ?")
      args = tuple(base_args + group_args + [limit])
      return Results(db.query(sql, 0, args=args))
    def subquery(prio_suffix, cond_sql):
      # SQLite forbids ORDER BY / LIMIT on intermediate compound-SELECT legs,
      # so wrap each leg as a FROM-subquery.
      return (b"SELECT * FROM ("
        b"SELECT *, 3*priority" + prio_suffix + b" AS effective_priority"
        b" FROM " + table +
        b" WHERE " + cond_sql +
        b" AND processing_node=0 AND " + to_date_sql + group_clause +
        b" ORDER BY priority, date LIMIT ?)")
    subqueries = [
      subquery(b'-1', b'node = ?'),
      subquery(b'', b'node=0'),
    ]
    # subquery 1: node = processing_node
    args = [processing_node] + base_args + group_args + [limit]
    # subquery 2: node = 0
    args += base_args + group_args + [limit]
    for x in node_set:
      subqueries.append(subquery(b'-1', b'node = ?'))
      args += [x] + base_args + group_args + [limit]
    sql = (b"SELECT * FROM (" + b" UNION ALL ".join(subqueries) + b")"
      b" ORDER BY effective_priority, date LIMIT ?")
    args.append(limit)
    result = Results(db.query(sql, 0, args=tuple(args)))
    if not result:
      fallback = subquery(b'+1', b'node>0')
      fallback_args = tuple(base_args + group_args + [limit])
      result = Results(db.query(fallback, 0, args=fallback_args))
    return result

  @contextmanager
  def SQLLock(self, db, lock_name, timeout):
    """
    SQLite approximation of MySQL GET_LOCK / RELEASE_LOCK.
    Yields 1 if write lock acquired, 0 on timeout.
    """
    acquired = 0
    try:
      # busy_timeout is in milliseconds
      db.query(b"PRAGMA busy_timeout = %d" % int(timeout * 1000), max_rows=0)
      db.query(b"BEGIN IMMEDIATE", max_rows=0)
      acquired = 1
    except sqlite3.OperationalError:
      acquired = 0
    try:
      yield acquired
    finally:
      if acquired:
        db.query(b"COMMIT", max_rows=0)

  def createTableSQL(self):
    return """\
CREATE TABLE %s (
  uid INTEGER NOT NULL,
  date TEXT NOT NULL,
  path TEXT NOT NULL,
  active_process_uid INTEGER,
  method_id TEXT NOT NULL,
  processing_node INTEGER NOT NULL DEFAULT -1,
  priority INTEGER NOT NULL DEFAULT 0,
  node INTEGER NOT NULL DEFAULT 0,
  group_method_id TEXT NOT NULL DEFAULT '',
  tag TEXT NOT NULL,
  serialization_tag TEXT NOT NULL,
  retry INTEGER NOT NULL DEFAULT 0,
  message BLOB NOT NULL,
  PRIMARY KEY (uid)
);
\0
CREATE INDEX IF NOT EXISTS %s_idx_processing_node_priority_date ON %s (processing_node, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_node2_priority_date ON %s (processing_node, node, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_node_group_priority_date ON  %s (processing_node, group_method_id, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_node2_group_priority_date ON  %s (processing_node, node, group_method_id, priority, date);
\0
CREATE INDEX IF NOT EXISTS %s_idx_serialization_tag_processing_node ON  %s (serialization_tag, processing_node);
\0
CREATE INDEX IF NOT EXISTS %s_idx_path_processing_node ON  %s (path, processing_node);
\0
CREATE INDEX IF NOT EXISTS %s_idx_active_process_uid ON  %s (active_process_uid);
\0
CREATE INDEX IF NOT EXISTS %s_idx_method_id_processing_node ON  %s (method_id, processing_node);
\0
CREATE INDEX IF NOT EXISTS %s_idx_tag_processing_node ON  %s (tag, processing_node);
""" % ((self.sql_table,) * 19)
