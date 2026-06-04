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

  _now_sql_expr = b"strftime('%Y-%m-%d %H:%M:%f', 'now')"
  _for_update_sql = b""
  _force_index_node2_sql = ""
  _MAX_DEPENDENCY_UNION_SUBQUERY_COUNT = -100
  _integrity_error_class = sqlite3.IntegrityError
  _dependency_subquery_open = b""
  _dependency_subquery_close = b""

  def _executeQuery(self, db, sql, args=(), max_rows=1000):
    return db.query(sql, max_rows, args=tuple(args) if args else None)

  def _skip_locked_sql(self, db):
    return b""

  def _wrapSubquery(self, sql):
    return b'SELECT * FROM (' + sql + b')'

  def _isDuplicateEntryError(self, exc):
    message = str(exc)
    return 'UNIQUE constraint failed' in message or 'PRIMARY KEY' in message

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

  def getNow(self, db):
    """ Return the UTC date from the point of view of the SQL server. """
    return db.query(b"SELECT strftime('%Y-%m-%d %H:%M:%f', 'now')", 0)[1][0][0]

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
