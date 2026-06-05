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
from six.moves import xrange
from Products.ERP5Type.Utils import str2bytes
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

  _force_index_node2_sql = ""
  _MAX_DEPENDENCY_UNION_SUBQUERY_COUNT = -100
  _dependency_subquery_open = b""
  _dependency_subquery_close = b""

  _insert_template = (b"INSERT INTO %s (uid,"
    b" path, active_process_uid, date, method_id, processing_node,"
    b" priority, node, group_method_id, tag, serialization_tag,"
    b" message) VALUES\n")
  _insert_separator = b",\n"

  def _executeQuery(self, db, sql, args=(), max_rows=1000):
    return db.query(sql, max_rows, args=tuple(args) if args else None)

  def _forUpdateSQL(self, db):
    return b""

  def prepareQueueMessageList(self, activity_tool, message_list):
    db = activity_tool.getSQLConnection()
    now_sql = self._now_sql_expr
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
          self._executeQuery(db, sql, tuple(all_args))
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
          date_sql = now_sql
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

  def _wrapSubquery(self, sql):
    return b'SELECT * FROM (' + sql + b')'

  def _reactivateDateSQL(self, delay):
    return b"strftime('%Y-%m-%d %H:%M:%f','now',?)", \
      ('+%s seconds' % delay,)

  def _timeShiftDateSQL(self, delay):
    return b"datetime(date, ?)", ('-%s seconds' % delay,)

  def _dependencyUnionSuffixSQL(self):
    return b'LIMIT %d' % self._MAX_DEPENDENCY_UNION_SUBQUERY_COUNT

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
